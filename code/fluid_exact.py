#!/usr/bin/env python3
"""Exact rational solver for two size-aware fluid queues (finite size laws).

No floating-point arithmetic or third-party dependencies. Sizes have mean one;
rho is total work intensity, each server's rate is 1/2, and arrival waiting cost
is twice job-arrival rate times destination workload.
"""
from __future__ import annotations
from bisect import bisect_right
from dataclasses import dataclass
from fractions import Fraction as F


@dataclass(frozen=True)
class Sector:
    lo: F
    hi: F | None
    alpha: F
    beta: F
    gamma: F
    delta: F | None
    zlo: F
    zhi: F
    cxx: F
    cxy: F
    cyy: F

    def value(self, x: F, y: F) -> F:
        return self.cxx*x*x + self.cxy*x*y + self.cyy*y*y

    def gradient(self, x: F, y: F) -> tuple[F, F]:
        return 2*self.cxx*x+self.cxy*y, self.cxy*x+2*self.cyy*y


def _require(condition, message="internal consistency check failed"):
    """Explicit check that survives python -O."""
    if not condition:
        raise ArithmeticError(message)


class FiniteFluidSolver:
    def __init__(self, sizes, probabilities, rho):
        rho = F(rho)
        merged = {}
        for a, p in zip(sizes, probabilities, strict=True):
            a, p = F(a), F(p)
            if a < 0 or p < 0:
                raise ValueError("Sizes and probabilities must be nonnegative.")
            if p:
                merged[a] = merged.get(a, F(0)) + p
        self.atoms = sorted(merged.items())
        if not self.atoms or sum(p for _, p in self.atoms) != 1:
            raise ValueError("Probabilities must sum exactly to one.")
        if sum(a*p for a, p in self.atoms) != 1:
            raise ValueError("Sizes must have mean exactly one.")
        if not 0 < rho < 1:
            raise ValueError("rho must be strictly between zero and one.")
        if len(self.atoms) == 1:
            raise ValueError("Use the separate deterministic formula.")
        self.rho, self.r = rho, rho/(1-rho)
        self.H = None
        self.DH = None
        self.FH = F(1)
        self.theta = None
        if rho >= F(1, 2):
            target = 1/(2*rho)
            cum_f = cum_m = F(0)
            for a, p in self.atoms:
                if cum_m+a*p >= target:
                    self.H = a
                    self.theta = (target-cum_m)/(a*p)
                    self.FH = cum_f+self.theta*p
                    break
                cum_f += p
                cum_m += a*p
            _require(self.H is not None)
        # Affine coefficients of D to the right of each breakpoint.
        affine = {}
        cum_f = cum_m = F(0)
        for a, p in self.atoms:
            if a == 0:
                cum_f += p
            else:
                break
        affine[F(0)] = (2*cum_f-1, F(1))
        for a, p in self.atoms:
            if a == 0:
                continue
            cum_f += p
            cum_m += a*p
            affine[a] = (2*cum_f-1, 1-2*cum_m)

        max_size = self.atoms[-1][0]
        points = [F(0)] + [a for a, _ in self.atoms if a > 0
                           and (self.H is None or a <= self.H)]
        tail = []
        if self.H is None:
            # Here rho<1/2. D=h-1 and B=1+1/[r(h-1)] in the tail.
            alpha, beta, gamma = F(1), F(-1), F(1)
            b_at_right = 1+1/(self.r*(max_size-1))
            tail = [self._make_sector(max_size, None, alpha, beta, gamma)]
        else:
            dH = sum(p*abs(a-self.H) for a, p in self.atoms)
            self.DH = dH
            b_at_right = self.H/dH
        reversed_rows = []
        for lo, hi in reversed(list(zip(points[:-1], points[1:]))):
            alpha, beta = affine[lo]
            d_hi = alpha*hi+beta
            if alpha:
                gamma = b_at_right-1/(self.r*alpha*d_hi)
                b_at_lo = gamma+1/(self.r*alpha*(alpha*lo+beta))
            else:
                gamma = b_at_right+hi/(self.r*beta*beta)
                b_at_lo = gamma-lo/(self.r*beta*beta)
            reversed_rows.append(self._make_sector(lo, hi, alpha, beta, gamma))
            b_at_right = b_at_lo
        self.sectors = list(reversed(reversed_rows)) + tail
        self.zlos = [s.zlo for s in self.sectors]
        _require(self.sectors[0].zlo == 0)
        _require(self.sectors[-1].zhi == 1)
        for first, second in zip(self.sectors, self.sectors[1:]):
            _require(first.zhi == second.zlo)
        self.axis_coefficient = self.r*(1-self.FH)

    def _make_sector(self, lo, hi, alpha, beta, gamma):
        r = self.r
        if alpha:
            delta = beta*gamma+1/(r*alpha)
            _require(delta > 0)
            cxx = r*(delta-beta)/(2*delta)
            cxy = -1/delta
            cyy = alpha*gamma/(2*delta)
            def b(h):
                return gamma+1/(r*alpha*(alpha*h+beta))
        else:
            delta = None
            _require(beta > 0 and gamma > 0)
            cxx = r*(1-1/gamma)/2
            cxy = -1/(beta*gamma)
            cyy = -1/(2*r*beta*beta*gamma)
            def b(h):
                return gamma-h/(r*beta*beta)
        zlo = lo/((alpha*lo+beta)*b(lo))
        zhi = F(1) if hi is None else hi/((alpha*hi+beta)*b(hi))
        _require(0 <= zlo < zhi <= 1)
        return Sector(lo, hi, alpha, beta, gamma, delta,
                      zlo, zhi, cxx, cxy, cyy)

    def evaluate(self, x, y):
        x, y = F(x), F(y)
        if not 0 <= y <= x:
            raise ValueError("Require 0<=y<=x.")
        if x == 0:
            return dict(value=F(0), h=None, k=F(0),
                        vx=F(0), vy=F(0), sector=None)
        if x == y:
            if self.H is None:
                vx = vy = F(0)
                k = x
            else:
                k = x*self.DH/self.H
                vx, vy = self.r*(x-k), -x/self.H
            return dict(value=self.axis_coefficient*x*x, h=self.H,
                        k=k, vx=vx, vy=vy, sector=None)
        idx = bisect_right(self.zlos, y/x)-1
        sec = self.sectors[idx]
        if sec.alpha:
            ell = (x-sec.alpha*sec.gamma*y)/sec.delta
            h = y/ell
            k = sec.alpha*y+sec.beta*ell
        else:
            k = (x+y/(self.r*sec.beta))/sec.gamma
            ell = k/sec.beta
            h = y/ell
        _require(sec.lo <= h and (sec.hi is None or h <= sec.hi))
        vx, vy = sec.gradient(x, y)
        _require(vx == self.r*(x-k))
        _require(vy == -ell)
        return dict(value=sec.value(x, y), h=h, k=k,
                    vx=vx, vy=vy, sector=idx)

    def optimal_allocation(self, x, y):
        x, y = F(x), F(y)
        if x == y:
            if self.H is None:
                return [F(1)]*len(self.atoms)
            return [F(1) if a < self.H else
                    self.theta if a == self.H else F(0)
                    for a, _ in self.atoms]
        h = self.evaluate(x, y)["h"]
        # Full allocation of an atom at an interior switch is one minimiser.
        return [F(a <= h) for a, _ in self.atoms]

    def hamiltonian(self, x, y, allocations):
        x, y = F(x), F(y)
        q = list(map(F, allocations))
        result = self.evaluate(x, y)
        jobs = sum(p*qi for (_, p), qi in zip(self.atoms, q))
        work = self.rho*sum(a*p*qi for (a, p), qi in zip(self.atoms, q))
        c = self.rho*(x+y*(1-2*jobs))
        if y == 0:
            return c-(1-self.rho)*result["vx"]+abs(self.rho-2*work)*result["vy"]
        if y == x:
            du_long = self.rho-work-F(1, 2)
            du_short = max(work-F(1, 2), F(0))
            return (c+(result["vx"]+result["vy"])*du_long
                    +(result["vx"]-result["vy"])*du_short)
        return c-(1-self.rho)*result["vx"]+(self.rho-2*work)*result["vy"]

    def serialise(self):
        def frac(v):
            return None if v is None else str(v)
        return dict(
            rho=str(self.rho), atoms=[[str(a), str(p)] for a, p in self.atoms],
            H=frac(self.H), theta=frac(self.theta), FH=str(self.FH),
            axis_coefficient=str(self.axis_coefficient),
            sectors=[{k: frac(v) for k, v in vars(s).items()} for s in self.sectors],
        )
