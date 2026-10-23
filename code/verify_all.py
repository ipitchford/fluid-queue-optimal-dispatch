#!/usr/bin/env python3
"""Single entry point for every computational check reported in the paper.

Usage:  python3 -B -I code/verify_all.py OUTPUT_DIR

Writes deterministic JSON files (sorted keys, floats rounded to 8 significant
digits, exact rationals as strings) into OUTPUT_DIR and prints a one-line
status per section. All checks are explicit and survive ``python -O``.
Exact sections use only fractions.Fraction. Floating-point sections are
numerical evidence; the proofs in the paper supply the universal statements.
"""
import argparse
import json
import math
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:      # needed under python -I
    sys.path.insert(0, str(HERE))

from fluid_exact import FiniteFluidSolver  # noqa: E402


class CheckFailed(RuntimeError):
    pass


def check(condition, message):
    if not condition:
        raise CheckFailed(message)


def sig(x, digits=8):
    if isinstance(x, bool) or x is None or isinstance(x, (int, str)):
        return x
    if isinstance(x, F):
        return str(x)
    if isinstance(x, float):
        if x == 0 or not math.isfinite(x):
            return x if math.isfinite(x) else str(x)
        return float(f"{x:.{digits}g}")
    if isinstance(x, dict):
        return {str(k): sig(v, digits) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [sig(v, digits) for v in x]
    if hasattr(x, "item"):
        return sig(x.item(), digits)
    raise TypeError(type(x))


def dec(q, places=10, direction="nearest"):
    """Decimal string of a Fraction, rounded down/up/nearest at `places`."""
    scale = 10 ** places
    v = q * scale
    if direction == "down":
        n = math.floor(v)
    elif direction == "up":
        n = math.ceil(v)
    else:
        n = round(v)
    sign = "-" if n < 0 else ""
    n = abs(n)
    return f"{sign}{n // scale}.{n % scale:0{places}d}"


# ------------------------------------------------------------------ 1
def exact_finite_support():
    examples = [
        ("two_point", [F(1, 2), F(3, 2)], [F(1, 2), F(1, 2)]),
        ("zero_atom", [F(0), F(2)], [F(1, 2), F(1, 2)]),
        ("three_point", [F(1, 4), F(1), F(7, 4)], [F(1, 4), F(1, 2), F(1, 4)]),
        ("zero_skew", [F(0), F(1, 2), F(2)], [F(1, 4), F(1, 3), F(5, 12)]),
    ]
    vertex = optimal = matching = 0
    cases = []
    for name, sizes, probs in examples:
        for rho in [F(1, 4), F(1, 2), F(3, 4), F(9, 10)]:
            s = FiniteFluidSolver(sizes, probs, rho)
            zs = {F(0), F(1)}
            for sec in s.sectors:
                zs |= {sec.zlo, (sec.zlo + sec.zhi) / 2, sec.zhi}
            for z in sorted(zs):
                for q in product([F(0), F(1)], repeat=len(s.atoms)):
                    check(s.hamiltonian(1, z, q) >= 0, f"negative Hamiltonian {name} {rho} {z}")
                    vertex += 1
                check(s.hamiltonian(1, z, s.optimal_allocation(1, z)) == 0, "optimal residual")
                optimal += 1
                check(s.evaluate(1, z)["value"] >= 0, "negative value")
            for left, right in zip(s.sectors, s.sectors[1:]):
                z = left.zhi
                check(left.value(1, z) == right.value(1, z), "value mismatch")
                check(left.gradient(1, z) == right.gradient(1, z), "gradient mismatch")
                matching += 1
            cases.append({"law": name, "rho": str(rho), "sectors": len(s.sectors),
                          "axis_coefficient": str(s.axis_coefficient)})
    ex = FiniteFluidSolver([F(1, 2), F(3, 2)], [F(1, 2), F(1, 2)], F(3, 4))
    check(ex.sectors[0].zhi == F(3, 13), "switch 3/13")
    check((ex.sectors[0].cxx, ex.sectors[0].cxy, ex.sectors[0].cyy) == (F(33, 28), -F(3, 14), -F(15, 28)), "sector 1")
    check((ex.sectors[1].cxx, ex.sectors[1].cxy, ex.sectors[1].cyy) == (F(6, 5), -F(2, 5), -F(2, 15)), "sector 2")
    check(ex.evaluate(1, 0)["value"] == F(33, 28), "33/28")
    check(ex.evaluate(1, 1)["value"] == F(2, 3), "axis 2/3")
    check(ex.theta == F(5, 9), "theta 5/9")
    return {"arithmetic": "exact rational", "law_load_cases": len(cases),
            "allocation_vertex_hamiltonian_checks": vertex,
            "optimal_residual_equalities": optimal,
            "adjacent_value_gradient_matches": matching,
            "two_point_rho_3_4": {"switch_z": "3/13", "value_at_x1_y0": "33/28",
                                  "axis_value_at_x1": "2/3", "terminal_large_atom_fraction": "5/9"},
            "cases": cases}


# ------------------------------------------------------------------ 2
def segment(u, w, a, duration):
    """Exact cost of a constant-rate segment with both queues positive."""
    end = tuple(ui + (wi - F(1, 2)) * duration for ui, wi in zip(u, w))
    check(min(u + end) >= 0, "segment leaves the orthant")
    cost = sum(2 * ai * (ui * duration + (wi - F(1, 2)) * duration ** 2 / 2) for ui, wi, ai in zip(u, w, a))
    return end, cost


def two_point_certificate():
    """Direct physical integration of the running example; no quadrature."""
    rho = F(3, 4)
    polys = [(F(33, 28), F(-6, 28), F(-15, 28)), (F(18, 15), F(-6, 15), F(-2, 15))]
    regions = [(F(0), F(3, 13), (0, 0)), (F(3, 13), F(1), (1, 0))]
    hamiltonian_rows = []
    for (a, b, c), (lo, hi, qopt) in zip(polys, regions):
        for qs, ql in product((0, 1), repeat=2):
            ydot = rho - 2 * rho * (F(1, 4) * qs + F(3, 4) * ql)
            hx = rho + 2 * a * (rho - 1) + b * ydot
            hy = rho * (1 - qs - ql) + b * (rho - 1) + 2 * c * ydot
            low = min(hx + hy * lo, hx + hy * hi)
            check(low >= 0, "two-point Hamiltonian")
            if (qs, ql) == qopt:
                check(hx == 0 and hy == 0, "two-point optimal residual")
            hamiltonian_rows.append({"q_small": qs, "q_large": ql, "region": [str(lo), str(hi)],
                                     "min_H_over_x": str(low)})
    u = (F(1, 2), F(1, 2))
    u, c1 = segment(u, (rho, F(0)), (rho, F(0)), F(2, 7))
    check(u == (F(4, 7), F(5, 14)), "phase 1 end")
    u, c2 = segment(u, (F(9, 16), F(3, 16)), (F(3, 8), F(3, 8)), F(8, 7))
    check(u == (F(9, 14), F(0)), "phase 2 end")
    theta = F(5, 9)
    w_short = rho * (F(1, 4) + F(3, 4) * theta)
    a_short = rho * (F(1, 2) + F(1, 2) * theta)
    check(w_short == F(1, 2), "axis balance")
    u, c3 = segment(u, (rho - w_short, w_short), (rho - a_short, a_short), F(18, 7))
    check(u == (0, 0), "axis drains")
    opt = c1 + c2 + c3
    check(opt == F(33, 28), "optimum 33/28")
    u2, m1 = segment((F(1, 2), F(1, 2)), (rho, F(0)), (rho, F(0)), F(1))
    u2, m2 = segment(u2, (F(1, 4), F(1, 2)), (F(1, 6), F(7, 12)), F(3))
    mwl = m1 + m2
    balanced = rho * F(1) ** 2 / (2 * (1 - rho))
    check(mwl == F(21, 16) and balanced == F(3, 2), "comparators")
    return {"phase_costs": [str(c1), str(c2), str(c3)], "optimal": str(opt),
            "most_work_left": str(mwl), "balanced_routing": str(balanced),
            "reduction_vs_balanced": str(1 - opt / balanced),
            "reduction_vs_most_work_left": str(1 - opt / mwl),
            "hamiltonian_vertex_checks": hamiltonian_rows}


# ------------------------------------------------------------------ 3
def certified_binning():
    rho = F(3, 4)
    r = rho / (1 - rho)
    c_rho = r * r / 2
    rows = []
    prev = {}
    for bins in [2, 4, 8, 16, 32, 64]:
        mids = [F(2 * i + 1, bins) for i in range(bins)]
        upper_model = FiniteFluidSolver(mids, [F(1, bins)] * bins, rho)
        nodes = [F(2 * i, bins) for i in range(bins + 1)]
        masses = [F(1, 2 * bins)] + [F(1, bins)] * (bins - 1) + [F(1, 2 * bins)]
        lower_model = FiniteFluidSolver(nodes, masses, rho)
        for z in [F(0), F(1, 3), F(4, 5)]:
            up = upper_model.evaluate(1, z)["value"]
            lo = lower_model.evaluate(1, z)["value"]
            check(0 <= lo <= up, "bracket order")
            if z in prev:
                check(prev[z][0] <= lo <= up <= prev[z][1], "nesting")
            prev[z] = (lo, up)
            alloc = upper_model.optimal_allocation(1, z)
            jobs = sum(F(1, bins) * q for q in alloc)
            work = sum(F(2 * i + 1, bins * bins) * q for i, q in enumerate(alloc))
            check(jobs == sum(p * q for (_, p), q in zip(upper_model.atoms, alloc)), "job transfer")
            check(work == sum(s * p * q for (s, p), q in zip(upper_model.atoms, alloc)), "work transfer")
            rows.append({"bins": bins, "z": str(z), "lower_rounded_down": dec(lo, 10, "down"),
                         "upper_rounded_up": dec(up, 10, "up"),
                         "width_rounded_up": dec(up - lo, 10, "up"),
                         "a_priori_width_bound": dec(c_rho * F(2, bins) / 2, 10, "up")})
    return {"law": "Uniform[0,2]", "rho": "3/4", "x": 1,
            "certificate": "V(endpoint law) <= V(true) <= V(midpoint law) = cost of bin policy",
            "rows": rows}


# ------------------------------------------------------------------ 4
def quadrature_checks():
    import numpy as np
    from fluid_quadrature import Law, FluidSolution
    laws = [Law("exponential"), Law("uniform"), Law("gamma", 4), Law("pareto", 1.5),
            Law("lognormal", 1), Law("two_point")]
    loads = [0.3, 0.5, 0.75, 0.9]
    err = {"direct_path_cost": 0.0, "gradient": 0.0, "homogeneity": 0.0,
           "optimal_hamiltonian": 0.0, "axis_optimal_hamiltonian": 0.0}
    min_h = min_axis = float("inf")
    table = []
    for law in laws:
        for rho in loads:
            m = FluidSolution(law, rho)
            allocs = [(a, a) for a in [0.0, 0.2, 0.5, 0.8, 1.0]]
            for h in [0.4, 1.0, 2.5]:
                allocs += [(law.F(h), law.M(h)), (1 - law.F(h), 1 - law.M(h))]
            for x, y in [(1.0, 0.0), (1.7, 0.391), (0.9, 0.657)]:
                st = m.state(x, y)
                err["direct_path_cost"] = max(err["direct_path_cost"], abs(m.independent_path_cost(x, y) - st["value"]))
                check(st["value"] >= 0.0, "value sign")
                if y == 0.0:
                    check(st["value"] >= rho * x * x / 2 - 1e-12, "universal bound V(x,0) >= rho x^2/2")
                    check(m.B0 >= 1 + 1 / m.r - 1e-12, "universal bound B(0) >= 1 + 1/r")
                check(st["value"] <= min(m.mwl_cost(x, y), m.random_split_cost(x, y)) + 2e-8, "comparator")
                err["homogeneity"] = max(err["homogeneity"], abs(m.state(2.3 * x, 2.3 * y)["value"] - 2.3 ** 2 * st["value"]))
                if y > 0:
                    def ham(a, w):
                        return rho * (x + y * (1 - 2 * a)) + st["Vx"] * (rho - 1) + st["Vy"] * rho * (1 - 2 * w)
                    err["optimal_hamiltonian"] = max(err["optimal_hamiltonian"], abs(ham(law.F(st["h"]), law.M(st["h"]))))
                    for a, w in allocs:
                        min_h = min(min_h, ham(a, w))
                    e = 1e-5
                    vx = (m.state(x + e, y)["value"] - m.state(x - e, y)["value"]) / (2 * e)
                    vy = (m.state(x, y + e)["value"] - m.state(x, y - e)["value"]) / (2 * e)
                    err["gradient"] = max(err["gradient"], abs(vx - st["Vx"]), abs(vy - st["Vy"]))
            ax = m.state(1.0, 1.0)
            v1, v2 = ax["Vx"] + ax["Vy"], ax["Vx"] - ax["Vy"]

            def axis_ham(a, w):
                return 2 * rho * (1 - a) + v1 * (rho * (1 - w) - 0.5) + v2 * max(rho * w - 0.5, 0.0)
            for a, w in allocs:
                min_axis = min(min_axis, axis_ham(a, w))
            a_star = 1 - m.boundary_tail()
            w_star = 1 / (2 * rho) if math.isfinite(m.hs) else 1.0
            err["axis_optimal_hamiltonian"] = max(err["axis_optimal_hamiltonian"], abs(axis_ham(a_star, w_star)))
            path = m.path(1.0, 0.0, count=35)
            ratios = path[:, 1] / path[:, 0]
            check(bool(np.all(np.diff(ratios) >= -2e-9)), "imbalance monotone")
            check(abs(ratios[-1] - 1.0) < 2e-9, "path reaches axis")
            if rho == 0.75:
                opt = m.state(1.0, 0.0)["value"]
                mwl = m.mwl_cost(1.0, 0.0)
                bal = rho / (2 * (1 - rho))
                table.append({"law": law.name, "parameter": law.parameter, "H": m.hs,
                              "optimal": opt, "most_work_left": mwl, "balanced": bal,
                              "reduction_vs_balanced_percent": 100 * (bal - opt) / bal,
                              "reduction_vs_most_work_left_percent": 100 * (mwl - opt) / mwl})
    check(err["direct_path_cost"] < 2e-7 and err["gradient"] < 2e-7, str(err))
    check(err["homogeneity"] < 2e-8 and err["optimal_hamiltonian"] < 2e-8, str(err))
    check(err["axis_optimal_hamiltonian"] < 2e-8, str(err))
    check(min_h >= -2e-8 and min_axis >= -2e-8, "arbitrary allocations")
    tol = {k: ("below 1e-6" if v < 1e-6 else v) for k, v in err.items()}
    return {"laws": [l.name for l in laws], "loads": loads, "max_errors": tol,
            "universal_bounds_checked": "V(1,0) >= rho/2 and B(0) >= 1+1/r for every law and load",
            "min_interior_hamiltonian_nonnegative": min_h >= -2e-8,
            "min_axis_hamiltonian_nonnegative": min_axis >= -2e-8,
            "table_rho_0_75_state_half_half": table}


# ------------------------------------------------------------------ 5
def heavy_traffic():
    from fluid_quadrature import Law, FluidSolution
    from scipy.optimize import brentq
    rows = []
    for law in [Law("exponential"), Law("uniform"), Law("gamma", 4), Law("pareto", 1.5),
                Law("lognormal", 1)]:
        hi = 2.0
        while law.M(hi) < 0.5:
            hi *= 2
        med = brentq(lambda h: law.M(h) - 0.5, 0.0, hi, xtol=1e-14)
        pbar = 1 - law.F(med)
        rec = {"law": law.name, "parameter": law.parameter, "work_median_m": med,
               "limit_constant_P_S_ge_m": pbar, "loads": []}
        for rho in [0.9, 0.99, 0.999]:
            mdl = FluidSolution(law, rho)
            v0 = (1 - rho) * mdl.state(1.0, 0.0)["value"]
            v1 = (1 - rho) * mdl.state(1.0, 1.0)["value"]
            lower = rho * mdl.boundary_tail()
            upper = rho / 2 * (1 - 1 / mdl.B0)
            check(lower - 1e-9 <= v1 <= v0 <= upper + 1e-9, "heavy-traffic sandwich")
            rec["loads"].append({"rho": rho, "scaled_value_balanced_start": v0,
                                 "scaled_value_axis_start": v1, "lower_bound": lower,
                                 "upper_bound": upper})
        rows.append(rec)
    # Exact two-point sequence.
    exact = []
    for rho in [F(9, 10), F(99, 100), F(999, 1000), F(9999, 10000)]:
        s = FiniteFluidSolver([F(1, 2), F(3, 2)], [F(1, 2), F(1, 2)], rho)
        exact.append({"rho": str(rho), "scaled_value_balanced_start": str((1 - rho) * s.evaluate(1, 0)["value"]),
                      "scaled_value_axis_start": str((1 - rho) * s.evaluate(1, 1)["value"])})
    return {"theorem": "(1-rho) V(x,y) -> P(S >= m) x^2, m = work median (atom split)",
            "continuous_laws": rows,
            "two_point_exact": {"limit_constant": "1/3", "sequence": exact},
            "balanced_routing_limit_constant": 0.5,
            "card_heavy_traffic_constant_xgs": "K_CARD = 2 P(S >= m); ratio to LWL constant 1 equals fluid ratio 2 P(S>=m)"}


# ------------------------------------------------------------------ 6
def source_comparison():
    from fluid_quadrature import Law, FluidSolution
    out = []
    for law in [Law("exponential"), Law("two_point")]:
        rho = 0.75
        m = FluidSolution(law, rho)
        u1 = u2 = 0.5
        pbar = m.boundary_tail()
        printed = 2 * rho * (2 * u1 * u2 + (2 * rho - 1) * u2 ** 2
                             + rho * pbar / (1 - rho) * (u1 + u2 * (2 * rho - 1)) ** 2)
        direct = 2 * rho * (2 * u1 * u2 + (2 * rho - 1) * u2 ** 2) + rho * pbar / (1 - rho) * (u1 + u2 * (2 * rho - 1)) ** 2
        check(abs(direct - m.mwl_cost(1.0, 0.0)) < 1e-12, "MWL integration")
        out.append({"law": law.name, "rho": rho, "state": [u1, u2],
                    "xhr_prop3_as_printed": printed, "direct_integration": direct,
                    "optimal": m.state(1.0, 0.0)["value"]})
    rho = F(3, 4)
    pbar = F(1, 2) * (1 - F(5, 9))
    printed = 2 * rho * (F(1, 2) + (2 * rho - 1) / 4 + rho * pbar / (1 - rho) * (F(1, 2) + (2 * rho - 1) / 2) ** 2)
    direct = 2 * rho * (F(1, 2) + (2 * rho - 1) / 4) + rho * pbar / (1 - rho) * (F(1, 2) + (2 * rho - 1) / 2) ** 2
    check(printed == F(3, 2) and direct == F(21, 16), "two-point exact MWL")
    rnd = rho * 2 * (F(1, 4) + F(1, 4)) / (2 * (1 - rho))
    check(rnd == F(3, 2), "random split matches source Remark 1")
    return {"most_work_left": out, "two_point_exact": {"printed": str(printed), "direct": str(direct)},
            "random_split_source_remark1": str(rnd),
            "heavy_traffic": "printed: (1-rho)v -> 2 rho Pbar x^2; direct: (1-rho)v -> rho Pbar x^2"}


# ------------------------------------------------------------------ 7
def pareto_certificate():
    """Pareto shape 3/2, scale 1/3: exact rational enclosure without truncation.

    At t = q^2/3 with q >= 1 rational: P(S>t) = q^-3, E[S;S>t] = 1/q,
    D(t) = t - 1 + 4/(3q).  For t <= 1/3, D(t) = 1 - t.  D is convex, so
    1/D^2 is quasi-concave and its minimum (maximum) over a grid cell is
    bounded below by the smaller endpoint value (above by ... see below).
    """
    rho = F(3, 4)
    r = rho / (1 - rho)

    def d_at_q(q):
        return q * q / 3 - 1 + F(4, 3) / q

    def round_down(v, den=10 ** 40):
        return F(math.floor(v * den), den)

    def round_up(v, den=10 ** 40):
        return F(math.ceil(v * den), den)

    # Exact terminal threshold: E[S; S<=H] = 1/(2 rho) = 2/3  <=>  1/q = 1/3, q = 3.
    q_h = F(3)
    H = q_h * q_h / 3
    DH = d_at_q(q_h)
    first = F(1, 2)  # int_0^{1/3} dt/(1-t)^2, exactly
    rows = []
    for cells in [16, 64, 256, 1024]:
        qs = [1 + (q_h - 1) * F(i, cells) for i in range(cells + 1)]
        ts = [q * q / 3 for q in qs]
        inv = [1 / d_at_q(q) ** 2 for q in qs]
        # D is decreasing on [1/3, t_min] and increasing after; 1/D^2 is
        # unimodal, so per cell min(endpoints) <= 1/D^2 everywhere in the cell.
        # For an upper sum use max(endpoints) except on the cell holding the
        # minimiser of D, where the bound 1/D_min^2 is used with
        # D_min >= max over the two tangent lower bounds (exact, see paper).
        lower_sum = F(0)
        upper_sum = F(0)
        best_lower_b = None
        # minimiser of D: D'(t)=2P(S<=t)-1=0 -> q^-3 = 1/2 -> q = 2^(1/3).
        for i in range(cells):
            width = ts[i + 1] - ts[i]
            lo_v, hi_v = min(inv[i], inv[i + 1]), max(inv[i], inv[i + 1])
            if qs[i] ** 3 <= 2 <= qs[i + 1] ** 3:
                # Lower bound for D on the cell from convexity: tangent lines at
                # the two endpoints, D' = 1 - 2 q^-3 at t=q^2/3.
                d0, d1 = d_at_q(qs[i]), d_at_q(qs[i + 1])
                s0, s1 = 1 - 2 / qs[i] ** 3, 1 - 2 / qs[i + 1] ** 3
                # intersection of tangents gives the minimum of their maximum
                tstar = (d1 - d0 + s0 * ts[i] - s1 * ts[i + 1]) / (s0 - s1)
                dmin = d0 + s0 * (tstar - ts[i])
                check(dmin > 0, "positive D lower bound")
                hi_v = 1 / dmin ** 2
            lower_sum = round_down(lower_sum + width * lo_v)
            upper_sum = round_up(upper_sum + width * hi_v)
            cand = round_down(ts[i + 1] / d_at_q(qs[i + 1]) + (first + lower_sum) / r)
            best_lower_b = cand if best_lower_b is None or cand > best_lower_b else best_lower_b
        b_upper = round_up(H / DH + (first + upper_sum) / r)
        b_lower = best_lower_b
        check(b_lower <= b_upper, "bracket for B(0)")
        v_low = r / 2 * (1 - 1 / b_lower)
        v_up = r / 2 * (1 - 1 / b_upper)
        rows.append({"grid_cells": cells, "lower_rounded_down": dec(v_low, 10, "down"),
                     "upper_rounded_up": dec(v_up, 10, "up"), "width_rounded_up": dec(v_up - v_low, 10, "up")})
    # Implementable bin policy: conditional means on q-bins plus one tail atom.
    def bin_law(step_den, q_max_fine, q_tail):
        qs = [1 + F(i, step_den) for i in range(int((q_max_fine - 1) * step_den) + 1)]
        q = qs[-1]
        while q < q_tail:
            q = 2 * q
            qs.append(q)
        sizes, probs = [], []
        for a, b in zip(qs, qs[1:]):
            mass = 1 / a ** 3 - 1 / b ** 3
            work = 1 / a - 1 / b
            sizes.append(work / mass)
            probs.append(mass)
        sizes.append(qs[-1] ** 2)
        probs.append(1 / qs[-1] ** 3)
        return sizes, probs, qs[-1]
    bin_rows = []
    best_lower = max(F(rw["lower_rounded_down"]) for rw in rows)
    for step_den, q_tail in [(4, 64), (16, 256), (32, 1024)]:
        sizes, probs, qt = bin_law(step_den, 8, q_tail)
        solver = FiniteFluidSolver(sizes, probs, rho)
        cost = solver.evaluate(1, 0)["value"]
        check(cost >= best_lower, "bin policy above certified lower bound")
        bin_rows.append({"atoms": len(sizes), "tail_cut_R": dec(qt * qt / 3, 2), "tail_first_moment": str(1 / qt),
                         "bin_policy_cost_rounded_up": dec(cost, 10, "up"),
                         "regret_bound_rounded_up": dec(cost - best_lower, 10, "up")})
    # Wasserstein route for comparison: needs C_rho [Delta + 2 tau(R)] <= target.
    c_rho = r * r / 2
    target = F(1, 100) * F(rows[-1]["upper_rounded_up"])
    return {"law": "Pareto shape 3/2, scale 1/3 (mean 1, infinite variance)", "rho": "3/4",
            "state": "x=1, y=0 (workloads 1/2,1/2)", "H": str(H), "D_H": str(DH),
            "value_enclosure": rows, "bin_policy": bin_rows,
            "wasserstein_route_for_one_percent": {
                "C_rho": str(c_rho),
                "required_tail_moment_at_most": dec(target / (2 * c_rho), 12),
                "required_mesh_at_most": dec(target / c_rho, 12),
                "comment": "tau(R)=0.577/sqrt(R): R ~ 4e5 and ~1e9 bins"}}


# ------------------------------------------------------------------ 8
def wasserstein_looseness():
    from fluid_quadrature import Law, FluidSolution
    from scipy.integrate import quad
    e, u = Law("exponential"), Law("uniform")
    w1 = quad(lambda t: abs(e.F(t) - u.F(t)), 0, 2, epsabs=1e-13, limit=200)[0] + \
        quad(lambda t: abs(e.F(t) - u.F(t)), 2, 60, epsabs=1e-13, limit=200)[0]
    rows = []
    for rho in [0.3, 0.75, 0.9]:
        gap = abs(FluidSolution(e, rho).state(1.0, 0.0)["value"] - FluidSolution(u, rho).state(1.0, 0.0)["value"])
        r = rho / (1 - rho)
        c = rho * r / (2 * min(1 - rho, 0.5))
        check(gap <= c * w1, "Wasserstein bound holds")
        rows.append({"rho": rho, "true_gap": gap, "bound": c * w1, "ratio_bound_to_gap": c * w1 / gap})
    return {"W1_exponential_uniform": w1, "rows": rows}


# ------------------------------------------------------------------ 9
def dp_cross_check():
    import numpy as np
    from dp_check import extrapolated_value
    cases = [("two_point", [0.5, 1.5], [0.5, 0.5], [F(1, 2), F(3, 2)], [F(1, 2), F(1, 2)], 36,
              [F(1, 4), F(1, 2), F(3, 4), F(9, 10)]),
             ("three_point_zero_atom", [0.0, 1.0, 3.0], [0.4, 0.4, 0.2], [F(0), F(1), F(3)],
              [F(2, 5), F(2, 5), F(1, 5)], 12, [F(1, 4), F(3, 4), F(9, 10)]),
             ("deterministic", [1.0], [1.0], None, None, 36, [F(1, 4), F(3, 4)])]
    rows = []
    for name, sz, pr, fsz, fpr, grid, loads in cases:
        for rho in loads:
            z, v_ext, v_fine = extrapolated_value(sz, pr, float(rho), grid)
            if fsz is None:
                r = rho / (1 - rho)
                exact = []
                for zz in z:
                    q = F(float(zz)).limit_denominator(10 ** 9)
                    if r >= 1 or q <= r:
                        exact.append(float((r - q * q) / 2))
                    else:
                        exact.append(float(r * (1 - q) ** 2 / (2 * (1 - r))))
            else:
                s = FiniteFluidSolver(fsz, fpr, rho)
                exact = [float(s.evaluate(1, F(float(zz)).limit_denominator(10 ** 9))["value"]) for zz in z]
            exact = np.array(exact)
            scale = float(exact.max())
            rel_ext = float(np.max(np.abs(v_ext - exact))) / scale
            rel_fine = float(np.max(np.abs(v_fine - exact))) / scale
            check(rel_ext < 2e-3, f"DP disagrees with value formula: {name} {rho} {rel_ext}")
            rows.append({"law": name, "rho": str(rho), "allocation_grid_per_class": grid,
                         "max_rel_error_finest": rel_fine, "max_rel_error_extrapolated": rel_ext,
                         "dp_value_at_z0": float(v_ext[0]), "formula_value_at_z0": float(exact[0])})
    return {"method": "semi-Lagrangian Bellman operator in z, full fractional allocation grid, exact reflection; policy iteration; Richardson over dt=0.02,0.01,0.005",
            "uses_value_formula": False, "rows": rows}


# ------------------------------------------------------------------ 10
def deterministic_checks():
    rho = F(1, 4)
    bal = rho * F(1) / (2 * (1 - rho))
    # All to the longer queue until the other empties, then all to the empty queue.
    u, c1 = segment((F(1, 2), F(1, 2)), (rho, F(0)), (rho, F(0)), F(1))
    check(u == (F(1, 4), F(0)), "deterministic phase")
    mwl = c1  # no further cost: rho <= 1/2 sends everything to the empty queue
    check(bal == F(1, 6) and mwl == F(3, 16), "deterministic low-load costs")
    r = rho / (1 - rho)
    check(r / 2 == F(1, 6), "value (17) at balanced start")
    # Counterexample to strict monotonicity at rho = 3/4 from (x,y)=(1,1/2).
    rho2 = F(3, 4)
    zdot = (1 - rho2) * (F(1, 2) - rho2 / (1 - rho2))  # (1-rho)(z - p) with p = r
    check(zdot < 0, "imbalance decreases")
    return {"balanced_cost_rho_1_4": str(bal), "most_work_left_cost_rho_1_4": str(mwl),
            "zdot_all_to_short_rho_3_4_at_z_half": str(zdot)}


# ------------------------------------------------------------------ 11
def pareto_101_regression():
    """Regression for the quadrature code on an extreme heavy tail.

    Pareto shape 101/100, minimum 1/101, rho = 3/4.  With h = t^100/101,
    D(h) = P(t)/(101 t), P(t) = t^101 - 101 t + 200, the terminal cutoff is
    H = 3^100/101 (t = 3) and
        int_0^H D^-2 dh = 1/100 + 10100 int_1^3 g(t) dt,  g = t^101/P(t)^2.
    g' has the sign of 200 - 99 t - t^101 (decreasing), so g is unimodal and
    its minimum and maximum on a cell without the peak are at the endpoints.
    The unique maximiser t0 satisfies t0^101 + 99 t0 = 200, so
    P(t0) = 200 (2 - t0) and g(t0) = (200 - 99 t0) / (40000 (2 - t0)^2).
    This rational function is increasing for t < 202/99, so on the cell
    [a, b] holding t0 its value at b bounds g from above.
    Exact rational Riemann bounds give an enclosure of V(1,0).
    """
    from fluid_quadrature import Law, FluidSolution
    rho = F(3, 4)
    r = rho / (1 - rho)

    def P(t):
        return t ** 101 - 101 * t + 200

    def rd(v, den=10 ** 40):
        return F(math.floor(v * den), den)

    def ru(v, den=10 ** 40):
        return F(math.ceil(v * den), den)
    # Dyadic grid, fine where g is concentrated (t near 1).
    ts = [1 + F(i, 2 ** 13) for i in range(2 ** 11)] + [F(5, 4) + F(i, 2 ** 8) for i in range(7 * 2 ** 6 + 1)]
    n = len(ts) - 1
    gs = [t ** 101 / P(t) ** 2 for t in ts]
    sign = [200 - 99 * t - t ** 101 for t in ts]
    low = up = F(0)
    for i in range(n):
        w = ts[i + 1] - ts[i]
        lo_v, hi_v = min(gs[i], gs[i + 1]), max(gs[i], gs[i + 1])
        if sign[i] > 0 >= sign[i + 1]:
            a, b = ts[i], ts[i + 1]
            # Peak-equation bound: g(t0) = (200 - 99 t0)/(40000 (2 - t0)^2) with
            # a < t0 <= b, and this function is increasing on [a, b].
            check(b < F(202, 99) and b < 2, "peak bound monotone on the cell")
            hi_v = (200 - 99 * b) / (40000 * (2 - b) ** 2)
            check(hi_v >= gs[i] and hi_v >= gs[i + 1], "peak bound below a cell endpoint value")
            peak_cell = {"a": str(a), "b": str(b), "peak_bound": dec(hi_v, 15, "up"),
                         "g_a": dec(gs[i], 15, "down"), "g_b": dec(gs[i + 1], 15, "down")}
        low = rd(low + w * lo_v)
        up = ru(up + w * hi_v)
    head = F(3) ** 101 / P(F(3))
    b_lo = head + (F(1, 100) + 10100 * low) / r
    b_hi = head + (F(1, 100) + 10100 * up) / r
    v_lo = r / 2 * (1 - 1 / b_lo)
    v_hi = r / 2 * (1 - 1 / b_hi)
    num = FluidSolution(Law("pareto", 1.01), 0.75).state(1.0, 0.0)["value"]
    check(float(v_lo) <= num <= float(v_hi), "quadrature outside the rational enclosure")
    check(num >= 0.375, "universal bound V(1,0) >= rho/2")
    # At z = 1 the true value is positive but far below rounding level; the
    # solver clamps the rounding residue at 0 (V >= 0 is proved).
    axis_value = FluidSolution(Law("pareto", 1.01), 0.75).state(1.0, 1.0)["value"]
    check(axis_value >= 0.0, "negative value at the axis")
    unsupported = []
    for alpha, load in [(1.001, 0.75), (1.001, 0.9)]:
        try:
            FluidSolution(Law("pareto", alpha), load)
            unsupported.append({"alpha": alpha, "rho": load, "result": "accepted"})
        except ValueError as exc:
            unsupported.append({"alpha": alpha, "rho": load, "result": "rejected: " + str(exc)})
    check(all(u["result"].startswith("rejected") for u in unsupported), "unsupported case accepted silently")
    concentrated = []
    for law in [Law("lognormal", 0.05), Law("lognormal", 0.02), Law("gamma", 400)]:
        for load in [0.3, 0.75, 0.9]:
            m = FluidSolution(law, load)
            v = m.state(1.0, 0.0)["value"]
            check(v >= load / 2 and abs(m.independent_path_cost(1.0, 0.0) - v) < 1e-9, "concentrated law")
            concentrated.append({"law": law.name, "parameter": law.parameter, "rho": load, "value_x1_y0": v})
    return {"law": "Pareto shape 101/100 (mean 1)", "rho": "3/4", "H": "3^100/101",
            "enclosure_lower_rounded_down": dec(v_lo, 12, "down"),
            "enclosure_upper_rounded_up": dec(v_hi, 12, "up"),
            "quadrature_value": num, "peak_cell": peak_cell,
            "quadrature_value_axis_x1_y1": axis_value, "unsupported_cases": unsupported,
            "concentrated_laws": concentrated}


# ------------------------------------------------------------------ 12
def symbolic_identities():
    """Symbolic checks of the gradient identity and the sector formulas."""
    import sympy as sp
    k, h, r = sp.symbols("k h r", positive=True)
    Df = sp.Function("D")(h)
    Bf = sp.Function("B")(h)
    x = k * Bf
    y = k * h / Df
    V = r / 2 * (x ** 2 - k * x) - y ** 2 / (2 * h)
    sub = {sp.Derivative(Bf, h): -1 / (r * Df ** 2)}
    res = []
    for var in (k, h):
        lhs = sp.diff(V, var).subs(sub)
        rhs = (r * (x - k) * sp.diff(x, var) - (y / h) * sp.diff(y, var)).subs(sub)
        res.append(sp.simplify(lhs - rhs))
    check(all(e == 0 for e in res), "gradient identity dV = r(x-k)dx - (y/h)dy")
    al, be, ga = sp.symbols("alpha beta gamma", nonzero=True)
    D = al * h + be
    B = ga + 1 / (r * al * D)
    om = be * ga + 1 / (r * al)
    xs, ys = k * B, k * h / D
    V2 = r / 2 * (xs ** 2 - k * xs) - ys ** 2 / (2 * h)
    F7 = (r * (om - be) * xs ** 2 - 2 * xs * ys + al * ga * ys ** 2) / (2 * om)
    check(sp.simplify(V2 - F7) == 0, "sector formula alpha != 0")
    check(sp.simplify(sp.diff(B, h) + 1 / (r * D ** 2)) == 0, "B' alpha != 0")
    D0 = be
    B0 = ga - h / (r * be ** 2)
    xs0, ys0 = k * B0, k * h / D0
    V0 = r / 2 * (xs0 ** 2 - k * xs0) - ys0 ** 2 / (2 * h)
    F8 = r / 2 * xs0 ** 2 - r / (2 * ga) * (xs0 + ys0 / (r * be)) ** 2
    check(sp.simplify(V0 - F8) == 0, "sector formula alpha = 0")
    return {"gradient_identity": "verified with generic D and B, B' = -1/(r D^2)",
            "sector_formula_alpha_nonzero": "verified", "sector_formula_alpha_zero": "verified"}


SECTIONS = [("exact_finite_support", exact_finite_support), ("two_point_certificate", two_point_certificate),
            ("certified_binning", certified_binning), ("quadrature_checks", quadrature_checks),
            ("heavy_traffic", heavy_traffic), ("source_comparison", source_comparison),
            ("pareto_certificate", pareto_certificate), ("wasserstein_looseness", wasserstein_looseness),
            ("dp_cross_check", dp_cross_check), ("deterministic_checks", deterministic_checks),
            ("pareto_101_regression", pareto_101_regression),
            ("symbolic_identities", symbolic_identities)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out", type=Path, help="output directory (created if absent)")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    status = {}
    for name, fn in SECTIONS:
        result = fn()
        result["status"] = "PASS"
        (args.out / f"{name}.json").write_text(json.dumps(sig(result), indent=1, sort_keys=True) + "\n")
        status[name] = "PASS"
        print(f"{name}: PASS", flush=True)
    (args.out / "summary.json").write_text(json.dumps(status, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
