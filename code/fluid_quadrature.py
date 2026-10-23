"""Quadrature solver for two size-aware fluid queues.

Service rates are 1/2 each;
job sizes have mean one, and arrival rate equals load rho.
Only NumPy/SciPy are needed. Numerical calculations support, not prove,
the accompanying analytical verification theorem.
"""
from dataclasses import dataclass
from math import exp, inf, isfinite, log, sqrt
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import gammainc, ndtr


@dataclass(frozen=True)
class Law:
    name: str
    parameter: float = 1.0

    def F(self, h):
        if h <= 0:
            return 0.0
        if not isfinite(h):
            return 1.0
        if self.name == "exponential":
            return -np.expm1(-h)
        if self.name == "uniform":
            return min(h / 2.0, 1.0)
        if self.name == "gamma":
            return float(gammainc(self.parameter, self.parameter*h))
        if self.name == "pareto":
            a = self.parameter
            b = (a-1.0)/a
            return 0.0 if h < b else -np.expm1(a*log(b/h))
        if self.name == "lognormal":
            s = self.parameter
            return float(ndtr((log(h)+s*s/2.0)/s))
        if self.name == "two_point":
            return 0.0 if h < 0.5 else 0.5 if h < 1.5 else 1.0
        raise ValueError(self.name)

    def M(self, h):
        """Truncated first moment E[X 1_{X<=h}]."""
        if h <= 0:
            return 0.0
        if not isfinite(h):
            return 1.0
        if self.name == "exponential":
            return 1.0-(1.0+h)*exp(-h)
        if self.name == "uniform":
            return min(h*h/4.0, 1.0)
        if self.name == "gamma":
            return float(gammainc(self.parameter+1.0, self.parameter*h))
        if self.name == "pareto":
            a = self.parameter
            b = (a-1.0)/a
            return 0.0 if h < b else -np.expm1((a-1.0)*log(b/h))
        if self.name == "lognormal":
            s = self.parameter
            return float(ndtr((log(h)-s*s/2.0)/s))
        if self.name == "two_point":
            return 0.0 if h < 0.5 else 0.25 if h < 1.5 else 1.0
        raise ValueError(self.name)

    def D(self, h):
        """Mean absolute deviation E|X-h|, evaluated without tail cancellation."""
        if self.name == "exponential":
            return h-1.0+2.0*exp(-h)
        if self.name == "uniform":
            return 1.0-h+h*h/2.0 if h <= 2 else h-1.0
        if self.name == "pareto":
            a = self.parameter
            b = (a-1.0)/a
            return 1.0-h if h < b else h-1.0+2.0/a*(b/h)**(a-1.0)
        if self.name == "two_point":
            return 0.5*(abs(h-0.5)+abs(h-1.5))
        return 1.0-h+2.0*(h*self.F(h)-self.M(h))

    def breaks(self):
        if self.name == "uniform":
            return [2.0]
        if self.name == "pareto":
            return [(self.parameter-1.0)/self.parameter]
        if self.name == "two_point":
            return [0.5,1.5]
        if self.name in ("lognormal", "gamma"):
            # Split around the region where D is small for concentrated laws.
            spread = self.parameter if self.name == "lognormal" else 1.0/sqrt(self.parameter)
            return sorted({1.0+j*spread/4 for j in range(-12, 13) if 1.0+j*spread/4 > 0})
        return []


class FluidSolution:
    def __init__(self, law, rho, eps=2e-11):
        if not 0 < rho < 1:
            raise ValueError("0 < rho < 1 required")
        self.law, self.rho, self.r, self.eps = law, rho, rho/(1-rho), eps
        if rho == 0.5 and law.name in ("uniform", "two_point"):
            self.hs = 2.0 if law.name == "uniform" else 1.5
            self.Hs = self.hs/law.D(self.hs)
        elif rho <= 0.5:
            self.hs, self.Hs = inf, 1.0
        elif law.name == "two_point":
            self.hs = 1.5
            self.Hs = self.hs/law.D(self.hs)
        else:
            target = 1.0/(2*rho)
            hi = 2.0
            while law.M(hi) < target:
                hi *= 2.0
                if hi > 1e200:
                    raise ValueError("unsupported: terminal cutoff beyond floating-point range")
            self.hs = brentq(lambda h:law.M(h)-target, 0.0, hi, xtol=5e-14, rtol=1e-15)
            self.Hs = self.hs/law.D(self.hs)
        self.B0 = self.B(0.0)
        # Universal sanity bound (Lemma on gradients): B(0) >= 1 + 1/r.
        if not self.B0 >= 1.0 + 1.0/self.r - 1e-9:
            raise ArithmeticError("B(0) violates the universal lower bound 1+1/r")

    def integral(self, f, a, b):
        """Integral of f over [a,b] (b may be infinite), robust on huge ranges.

        Below SCALE the integral is split at the law's breakpoints. Above
        SCALE the substitution t = exp(v) is used on unit chunks of v, so
        that the contribution of sizes of order one is never lost on an
        enormous interval. Every quad call is checked; a warning raises.
        """
        SCALE = 4.0
        pieces = []
        lo_part = (a, min(b, SCALE))
        if lo_part[0] < lo_part[1]:
            stops = [lo_part[0]]+[q for q in self.law.breaks() if lo_part[0] < q < lo_part[1]]+[lo_part[1]]
            pieces += [("lin", s, t) for s, t in zip(stops[:-1], stops[1:])]
        if b > SCALE:
            v0 = log(max(a, SCALE))
            v1 = log(b) if isfinite(b) else inf
            v = v0
            tail = 0.0
            while v < v1:
                if v >= 60.0 and not isfinite(v1):
                    # Beyond e^60: D(h) >= h-1, and h-1 >= D(h)-2e^-30 here, so the
                    # remaining integral equals 1/(e^60-1) to relative error < 1e-25.
                    tail = 1.0/(exp(60.0)-1.0)
                    break
                nxt = min(v+1.0, v1) if v < 60.0 else v1
                pieces.append(("log", v, nxt))
                v = nxt
        total = 0.0
        for kind, s, t in pieces:
            g = f if kind == "lin" else (lambda v: f(exp(v))*exp(v))
            out = quad(g, s, t, epsabs=self.eps, epsrel=self.eps, limit=400, full_output=1)
            if len(out) > 3:
                raise ArithmeticError(f"quadrature warning on [{s},{t}] ({kind}): {out[3]}")
            total += out[0]
        if b > SCALE:
            total += tail
        return total

    def B(self, h):
        if h == inf:
            return 1.0
        return self.Hs + self.integral(lambda t:1.0/self.law.D(t)**2,h,self.hs)/self.r

    def H(self, h):
        return 1.0 if h == inf else h/self.law.D(h)

    def z(self, h):
        return self.H(h)/self.B(h)

    def threshold(self, z):
        if not 0 <= z <= 1:
            raise ValueError("0 <= relative imbalance <= 1 required")
        if z == 0:
            return 0.0
        if z == 1:
            return self.hs
        hi = self.hs if isfinite(self.hs) else 2.0
        while self.z(hi) < z:
            hi *= 2.0
        return brentq(lambda h:self.H(h)-z*self.B(h),0.0,hi,xtol=5e-13)

    def boundary_tail(self):
        if self.rho <= 0.5:
            return 0.0
        if self.law.name == "two_point":
            # Short server takes all small jobs and a fraction of the large atom.
            fraction = (1/(2*self.rho)-0.25)/0.75
            return 0.5*(1-fraction)
        return 1.0-self.law.F(self.hs)

    def state(self, x, y):
        if x == 0:
            return dict(h=0.0,k=0.0,value=0.0,Vx=0.0,Vy=0.0,p=-self.r)
        h = self.threshold(y/x)
        k = x/self.B(h)
        yh = k if h == 0 else 0.0 if h == inf else y/h
        value = self.r/2.0*(x*x-k*x)-y*yh/2.0
        # V >= 0 is proved.  A tiny negative result is rounding residue (about
        # -1e-46 at z = 1 for Pareto shape 1.01, rho = 3/4) and is clamped to 0;
        # a larger one signals a numerical failure.
        if value < 0.0:
            if value < -1e-9*x*x:
                raise ArithmeticError(f"negative value {value} at ({x}, {y})")
            value = 0.0
        p = self.r*(2*self.law.M(h)-1)
        if y == x and isfinite(self.hs):
            p = 1.0
        return dict(h=h,k=k,value=value,Vx=self.r*(x-k),Vy=-yh,p=p)

    def path(self, x, y, count=160):
        s = self.state(x,y)
        k, h0 = s["k"],s["h"]
        if h0 == inf:
            return np.array([[x,y,inf]])
        if isfinite(self.hs):
            hs = np.linspace(h0,self.hs,count)
        else:
            # The last point is the analytically known limiting contact point.
            hs = h0+np.geomspace(1e-7,2e4,count)-1e-7
        out = np.array([[k*self.B(h), k*self.H(h),h] for h in hs])
        if not isfinite(self.hs):
            out = np.vstack([out,[k,k,inf]])
        return out

    def independent_path_cost(self,x,y):
        s = self.state(x,y)
        h0,k=s["h"],s["k"]
        if h0 == inf:
            return 0.0
        def integrand(h):
            xx,yy=k*self.B(h),k*self.H(h)
            # All terms here come directly from arrival waiting costs and dt/dh.
            return k*(xx+(1-2*self.law.F(h))*yy)/self.law.D(h)**2
        pre=self.integral(integrand,h0,self.hs)
        return pre+self.r*self.boundary_tail()*(k*self.Hs)**2

    def mwl_cost(self,x,y):
        u,v=(x+y)/2.0,(x-y)/2.0
        xb=u+(2*self.rho-1)*v
        return 2*self.rho*(2*u*v+(2*self.rho-1)*v*v)+self.r*self.boundary_tail()*xb*xb

    def random_split_cost(self,x,y):
        # Fixed size-blind equal splitting throughout: each queue drains separately.
        u,v=(x+y)/2.0,(x-y)/2.0
        return self.r*(u*u+v*v)
