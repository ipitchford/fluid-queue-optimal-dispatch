#!/usr/bin/env python3
"""Seeded simulation of two-server size- and state-aware dispatching.

Numerical evidence only: no statement in the paper is proved by these runs.

Model: Poisson arrivals at rate rho (mean size one), two FCFS servers each of
rate 1/2, so a job of size s needs 2s units of service time and a job that
joins a queue holding work u waits 2u.  Each replication starts empty, the
first 10% of arrivals are discarded, and the mean waiting time of the rest is
recorded.  All policies in a (law, load, replication) cell see the same
arrival and size stream (common random numbers).

Policies
  RND      uniformly random queue
  JSW      join the shortest workload (least work left)
  SITA     static size interval split at the work median m (E[S;S<m]=1/2)
  DICE     shorter queue iff (its work + s) < tau            [tuned: tau]
  CARD     flexible CARD of Xie, Grosof and Scully           [tuned: a, b, c]
  FLUID    the exact fluid-optimal feedback rule applied directly
  FLUID-S  the stabilised fluid rule of the paper            [tuned: band]

Tuned parameters are chosen on separate tuning seeds and then frozen.
Standard library only; output is deterministic JSON.

Usage: python3 simulate.py OUTPUT_DIR [--quick]
"""
import argparse
import json
import math
import random
import sys
from bisect import bisect_left
from multiprocessing import Pool
from pathlib import Path

# --------------------------------------------------------------- size laws

H2_P = 0.5 * (1 + math.sqrt((10 - 1) / (10 + 1)))  # SCV 10, balanced means
H2_M1 = 1 / (2 * H2_P)
H2_M2 = 1 / (2 * (1 - H2_P))
BP_A, BP_RATIO = 1.5, 1.0e4                          # bounded Pareto shape, U/L


def _bp_raw_mean():
    a, lo, hi = BP_A, 1.0, BP_RATIO
    norm = 1 - (lo / hi) ** a
    return a * lo ** a * (lo ** (1 - a) - hi ** (1 - a)) / ((a - 1) * norm)


BP_L = 1.0 / _bp_raw_mean()
BP_U = BP_L * BP_RATIO
BP_NORM = 1 - (BP_L / BP_U) ** BP_A


class Law:
    def __init__(self, name):
        self.name = name

    def sample(self, rng):
        n = self.name
        if n == "exponential":
            return -math.log(1.0 - rng.random())
        if n == "two_point":
            return 0.5 if rng.random() < 0.5 else 1.5
        if n == "hyperexponential":
            mean = H2_M1 if rng.random() < H2_P else H2_M2
            return -mean * math.log(1.0 - rng.random())
        if n == "bounded_pareto":
            u = rng.random()
            return BP_L * (1 - u * BP_NORM) ** (-1 / BP_A)
        raise ValueError(n)

    def tail_work(self, h):
        """E[S 1{S > h}]."""
        n = self.name
        if n == "exponential":
            return (1 + h) * math.exp(-h)
        if n == "two_point":
            return (0.25 if h < 0.5 else 0.0) + (0.75 if h < 1.5 else 0.0)
        if n == "hyperexponential":
            return sum(p * (m + h) * math.exp(-h / m) for p, m in ((H2_P, H2_M1), (1 - H2_P, H2_M2)))
        if n == "bounded_pareto":
            a, lo, hi = BP_A, BP_L, BP_U
            t = min(max(h, lo), hi)
            return a * lo ** a * (t ** (1 - a) - hi ** (1 - a)) / ((a - 1) * BP_NORM)
        raise ValueError(n)

    def tail_prob(self, h):
        n = self.name
        if n == "exponential":
            return math.exp(-h)
        if n == "two_point":
            return (0.5 if h < 0.5 else 0.0) + (0.5 if h < 1.5 else 0.0)
        if n == "hyperexponential":
            return sum(p * math.exp(-h / m) for p, m in ((H2_P, H2_M1), (1 - H2_P, H2_M2)))
        if n == "bounded_pareto":
            t = min(max(h, BP_L), BP_U)
            return ((BP_L / t) ** BP_A - (BP_L / BP_U) ** BP_A) / BP_NORM
        raise ValueError(n)

    def D(self, h):
        """E|S-h| = h - 1 + 2 E(S-h)^+."""
        return h - 1 + 2 * (self.tail_work(h) - h * self.tail_prob(h))

    def work_below(self, h):
        return 1.0 - self.tail_work(h)

    def atoms(self):
        return [0.5, 1.5] if self.name == "two_point" else []


def work_quantile(law, target):
    """Smallest h with E[S 1{S<=h}] >= target, and the atom fraction there."""
    lo, hi = 0.0, 1.0
    while law.work_below(hi) < target:
        hi *= 2
        if hi > 1e9:
            return math.inf, 1.0
    for a in law.atoms():
        below = law.work_below(a - 1e-12)
        at = law.work_below(a)
        if below < target <= at + 1e-15:
            return a, (target - below) / (at - below)
    for _ in range(200):
        mid = (lo + hi) / 2
        if law.work_below(mid) >= target:
            hi = mid
        else:
            lo = mid
    return hi, 0.0


class FluidRule:
    """Cutoff h(z) of the exact fluid-optimal policy, tabulated in z."""

    def __init__(self, law, rho, points=6000):
        self.law, self.rho = law, rho
        r = rho / (1 - rho)
        if rho > 0.5 or (rho == 0.5 and law.name in ("two_point", "bounded_pareto")):
            self.H, self.theta = work_quantile(law, 1 / (2 * rho))
        else:
            self.H, self.theta = math.inf, 1.0
        if math.isfinite(self.H):
            top, b_top = self.H, self.H / law.D(self.H)
        else:
            top = 60.0 if law.name != "hyperexponential" else 60.0 * H2_M2
            b_top = 1 + 1 / (r * (top - 1))   # D(h) = h - 1 beyond the bulk
        hs = [top * (i / points) ** 2 for i in range(points + 1)]
        f = [1 / law.D(h) ** 2 for h in hs]
        b = [0.0] * (points + 1)
        b[-1] = b_top
        for i in range(points - 1, -1, -1):
            b[i] = b[i + 1] + (hs[i + 1] - hs[i]) * (f[i] + f[i + 1]) / (2 * r)
        self.hs = hs
        self.zs = [h / (law.D(h) * bb) for h, bb in zip(hs, b)]
        for z0, z1 in zip(self.zs, self.zs[1:]):
            if not z1 > z0:
                raise ArithmeticError("tabulated Z is not increasing")

    def cutoff(self, z):
        i = bisect_left(self.zs, z)
        if i <= 0:
            return 0.0
        if i >= len(self.zs):
            return self.H
        z0, z1 = self.zs[i - 1], self.zs[i]
        return self.hs[i - 1] + (self.hs[i] - self.hs[i - 1]) * (z - z0) / (z1 - z0)


def surplus_cutoff(law, rho, kappa):
    """Cutoff giving the short queue work rate min(rho, 1/2 + kappa(1-rho))."""
    target = min(rho, 0.5 + kappa * (1 - rho)) / rho
    if target >= 1.0:
        return math.inf, 1.0
    return work_quantile(law, target)


# ----------------------------------------------------------------- runner

def run_one(args):
    law_name, rho, policy, params, seed, n_jobs, noise, rho_design = args
    law = Law(law_name)
    arr = random.Random(seed)
    aux = random.Random(seed + 7777777)
    noisy = random.Random(seed + 3333333)
    design = rho if rho_design is None else rho_design
    u = [0.0, 0.0]
    burn = n_jobs // 10
    total = 0.0
    count = 0
    if policy == "SITA":
        m_med, th_med = work_quantile(law, 0.5)
    if policy == "FLUID" or policy == "FLUID-S":
        rule = FluidRule(law, design)
    if policy == "FLUID-S":
        band = params["band"]
        h_plus, th_plus = surplus_cutoff(law, design, params["kappa"])
    if policy == "CARD":
        a, b, c = params["a"], params["b"], params["c"]
        b = min(b, rho / (2 * (1 - rho)))
        rs = max(rho / 2 - a * (1 - rho), 0.0) / rho
        rl = max(rho / 2 - b * (1 - rho), 0.0) / rho
        m_minus, th_minus = work_quantile(law, rs) if rs > 0 else (0.0, 0.0)
        m_plus, th_plus_c = work_quantile(law, 1 - rl) if rl > 0 else (math.inf, 1.0)
    if policy == "DICE":
        tau = params["tau"]
    sig = noise
    for j in range(n_jobs):
        dt = -math.log(1.0 - arr.random()) / rho
        s = law.sample(arr)
        if sig:
            est = s * math.exp(sig * noisy.gauss(0.0, 1.0) - sig * sig / 2)
        else:
            est = s
        d = dt / 2
        u0 = u[0] - d
        u1 = u[1] - d
        u0 = u0 if u0 > 0.0 else 0.0
        u1 = u1 if u1 > 0.0 else 0.0
        short = 0 if u0 <= u1 else 1
        us, ul = (u0, u1) if short == 0 else (u1, u0)
        if policy == "JSW":
            to_short = True
        elif policy == "RND":
            to_short = aux.random() < 0.5
        elif policy == "SITA":
            small = est < m_med or (est == m_med and aux.random() < th_med)
            target = 0 if small else 1
            to_short = target == short
        elif policy == "DICE":
            to_short = us + est < tau
        elif policy == "CARD":
            if est < m_minus or (est == m_minus and aux.random() < th_minus):
                to_short = True
            elif est > m_plus or (est == m_plus and aux.random() >= th_plus_c):
                to_short = False
            else:
                to_short = us <= c
        elif policy == "FLUID":
            if us == 0.0:
                if ul == 0.0:
                    to_short = True
                else:
                    h = rule.H
                    to_short = est < h or (est == h and aux.random() < rule.theta)
            else:
                h = rule.cutoff((ul - us) / (ul + us))
                to_short = est < h
        elif policy == "FLUID-S":
            if us <= band:
                to_short = est < h_plus or (est == h_plus and aux.random() < th_plus)
            else:
                h = rule.cutoff((ul - us) / (ul + us - 2 * band))
                to_short = est < h
        else:
            raise ValueError(policy)
        dest = short if to_short else 1 - short
        w = u0 if dest == 0 else u1
        if dest == 0:
            u0 += s
        else:
            u1 += s
        u[0], u[1] = u0, u1
        if j >= burn:
            total += 2 * w
            count += 1
    return total / count


# ------------------------------------------------------------- experiment

LAWS = ["exponential", "two_point", "hyperexponential", "bounded_pareto"]
LOADS = [0.5, 0.75, 0.9]
T975 = {9: 2.262157, 19: 2.093024, 4: 2.776445}


def sig(x, digits=8):
    if isinstance(x, float):
        if x == 0 or not math.isfinite(x):
            return x
        return float(f"{x:.{digits}g}")
    if isinstance(x, dict):
        return {k: sig(v, digits) for k, v in x.items()}
    if isinstance(x, list):
        return [sig(v, digits) for v in x]
    return x


def grids(rho):
    eps = 1 - rho
    scale = math.sqrt(1 / eps) * math.log(1 / eps)
    return {
        "DICE": [{"tau": eta * eps ** (-1 / 3)} for eta in (1, 2, 4, 8, 16)],
        "CARD": [{"a": a, "b": b, "c": g * scale}
                 for a in (0.0, 0.25) for b in (0.75, 1.0) for g in (0.125, 0.25, 0.5, 1.0, 2.0, 4.0)],
        "FLUID-S": [{"band": g * scale, "kappa": k}
                    for g in (0.0625, 0.25, 0.5, 1.0, 2.0, 4.0) for k in (0.25, 0.5)],
    }


def seed_of(law, rho, rep, tuning):
    return 1_000_003 * (rep + 1) + 10_007 * LAWS.index(law) + int(round(rho * 1000)) + (500_000_000 if tuning else 0)


def summary(values):
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    half = T975[n - 1] * math.sqrt(var / n)
    return {"mean": mean, "ci95_half_width": half, "replications": n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--quick", action="store_true", help="small smoke test")
    ap.add_argument("--processes", type=int, default=4)
    args = ap.parse_args()
    n_eval, n_tune, reps, tune_reps = (1_000_000, 300_000, 20, 3)
    if args.quick:
        n_eval, n_tune, reps, tune_reps = (20_000, 10_000, 5, 2)
    args.out.mkdir(parents=True, exist_ok=True)
    pool = Pool(args.processes)

    # 1. tuning on separate seeds
    tasks, keys = [], []
    for law in LAWS:
        for rho in LOADS:
            for pol, grid in grids(rho).items():
                for gi, params in enumerate(grid):
                    for rep in range(tune_reps):
                        tasks.append((law, rho, pol, params, seed_of(law, rho, rep, True), n_tune, 0.0, None))
                        keys.append((law, rho, pol, gi))
    out = pool.map(run_one, tasks, chunksize=4)
    acc = {}
    for k, v in zip(keys, out):
        acc.setdefault(k, []).append(v)
    tuned = {}
    for law in LAWS:
        for rho in LOADS:
            for pol, grid in grids(rho).items():
                scores = [sum(acc[(law, rho, pol, gi)]) for gi in range(len(grid))]
                best = min(range(len(grid)), key=lambda i: (scores[i], i))
                tuned[(law, rho, pol)] = grid[best]

    # 2. evaluation on fresh seeds, common random numbers across policies
    policies = ["RND", "JSW", "SITA", "DICE", "CARD", "FLUID", "FLUID-S"]
    tasks, keys = [], []
    for law in LAWS:
        for rho in LOADS:
            for pol in policies:
                params = tuned.get((law, rho, pol), {})
                for rep in range(reps):
                    tasks.append((law, rho, pol, params, seed_of(law, rho, rep, False), n_eval, 0.0, None))
                    keys.append((law, rho, pol))
    # 3. robustness: noisy size estimates and misspecified design load
    for law in ("exponential", "hyperexponential"):
        for rho in (0.75, 0.9):
            for pol in ("SITA", "CARD", "FLUID-S"):
                for sgm in (0.5, 1.0):
                    params = tuned.get((law, rho, pol), {})
                    for rep in range(reps):
                        tasks.append((law, rho, pol, params, seed_of(law, rho, rep, False), n_eval, sgm, None))
                        keys.append((law, rho, pol + f"|noise={sgm}"))
            for drho in (-0.05, 0.05):
                params = tuned[(law, rho, "FLUID-S")]
                for rep in range(reps):
                    tasks.append((law, rho, "FLUID-S", params, seed_of(law, rho, rep, False), n_eval, 0.0,
                                  round(rho + drho, 4)))
                    keys.append((law, rho, f"FLUID-S|design_load={round(rho + drho, 4)}"))
    out = pool.map(run_one, tasks, chunksize=4)
    pool.close()
    pool.join()
    acc = {}
    for k, v in zip(keys, out):
        acc.setdefault(k, []).append(v)
    cells = []
    for (law, rho, pol), vals in sorted(acc.items(), key=lambda kv: (LAWS.index(kv[0][0]), kv[0][1], kv[0][2])):
        base = acc[(law, rho, "JSW")]
        diffs = [p / q for p, q in zip(vals, base)]
        rec = {"law": law, "rho": rho, "policy": pol, "mean_wait": summary(vals),
               "ratio_to_JSW": summary(diffs)}
        if "|" not in pol:
            rec["tuned_parameters"] = tuned.get((law, rho, pol), {})
        cells.append(rec)
    result = {
        "status": "numerical evidence only",
        "model": "Poisson arrivals rate rho, mean size 1, two FCFS servers of rate 1/2; waiting time = 2 x work found",
        "laws": {
            "exponential": "mean 1",
            "two_point": "1/2 or 3/2 with probability 1/2",
            "hyperexponential": "balanced-means H2, SCV 10, p=%.8g" % H2_P,
            "bounded_pareto": "shape 1.5 on [L, 1e4 L], scaled to mean 1, L=%.8g" % BP_L,
        },
        "arrivals_per_replication": n_eval, "burn_in_fraction": 0.1,
        "replications": reps, "tuning_arrivals": n_tune, "tuning_replications": tune_reps,
        "confidence_intervals": "Student t, 95%, across independent replications",
        "ratio_to_JSW": "per-replication ratio of mean waits under common random numbers",
        "cells": sig(cells),
    }
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    (args.out / ("simulation_quick.json" if args.quick else "simulation.json")).write_text(text)
    print("wrote", len(cells), "cells")


if __name__ == "__main__":
    sys.exit(main())
