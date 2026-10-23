"""Independent dynamic-programming check of the optimal fluid value.

This module does not use the value formula, the threshold rule or the scalar
quadrature. It discretises the original reflected two-queue control problem
directly: a semi-Lagrangian Bellman operator on the relative imbalance
z = |u1-u2|/(u1+u2), using only quadratic homogeneity V(u) = x^2 v(z).
The control set is a full grid of fractional allocations of every size class
to the shorter queue (no threshold structure is imposed). Reflection at an
empty queue, and hence idling, is modelled exactly for each constant-control
step. The Bellman equation is solved by policy iteration; results at three
step sizes are combined by Richardson extrapolation (first-order scheme).
"""
from itertools import product
import numpy as np


def _controls(sizes, probs, grid):
    fracs = np.linspace(0.0, 1.0, grid + 1)
    jobs, work = [], []
    for q in product(fracs, repeat=len(sizes)):
        q = np.array(q)
        jobs.append(float(np.dot(probs, q)))
        work.append(float(np.dot(probs * sizes, q)))
    pairs = np.unique(np.round(np.column_stack([jobs, work]), 14), axis=0)
    return pairs[:, 0], pairs[:, 1]


def bellman_tables(sizes, probs, rho, dt, npts, grid):
    sizes = np.asarray(sizes, float)
    probs = np.asarray(probs, float)
    jf, wf = _controls(sizes, probs, grid)
    a_s = rho * jf[None, :]              # job rate to the shorter queue
    w_s = rho * wf[None, :]              # work rate to the shorter queue
    z = np.linspace(0.0, 1.0, npts)[:, None]
    u_l, u_s = (1 + z) / 2, (1 - z) / 2  # total workload normalised to one
    b_s = w_s - 0.5
    b_l = (rho - w_s) - 0.5
    # Short queue: linear until it empties, then reflected at zero.
    with np.errstate(divide="ignore", invalid="ignore"):
        t_hit = np.where(b_s < 0, u_s / (-b_s), np.inf)
    hits = t_hit < dt
    us_end = np.where(hits, 0.0, u_s + b_s * dt)
    int_us = np.where(hits, u_s * np.minimum(t_hit, dt) / 2, dt * (u_s + b_s * dt / 2))
    ul_end = u_l + b_l * dt
    if np.any(ul_end < 0):
        raise ValueError("step too large")
    int_ul = dt * (u_l + b_l * dt / 2)
    cost = 2 * (a_s * int_us + (rho - a_s) * int_ul)
    x_end = us_end + ul_end
    z_end = np.abs(ul_end - us_end) / x_end
    pos = z_end * (npts - 1)
    idx = np.minimum(np.floor(pos).astype(int), npts - 2)
    wt = pos - idx
    disc = x_end ** 2
    return cost, disc, idx, wt


def solve(sizes, probs, rho, dt, npts, grid, iterations=200):
    cost, disc, idx, wt = bellman_tables(sizes, probs, rho, dt, npts, grid)
    n = npts
    rows = np.arange(n)
    policy = disc.argmin(axis=1)
    v = np.zeros(n)
    for _ in range(iterations):
        p = np.zeros((n, n))
        c = cost[rows, policy]
        d = disc[rows, policy]
        i = idx[rows, policy]
        w = wt[rows, policy]
        np.add.at(p, (rows, i), d * (1 - w))
        np.add.at(p, (rows, i + 1), d * w)
        v = np.linalg.solve(np.eye(n) - p, c)
        q = cost + disc * ((1 - wt) * v[idx] + wt * v[idx + 1])
        best = q.min(axis=1)
        new_policy = np.where(q[rows, policy] <= best + 1e-13, policy, q.argmin(axis=1))
        if np.array_equal(new_policy, policy):
            break
        policy = new_policy
    return v


def extrapolated_value(sizes, probs, rho, grid, base_dt=0.02, base_pts=51):
    """Return v at z-grid points shared by all three resolutions, extrapolated."""
    sols = []
    for level in range(3):
        dt = base_dt / 2 ** level
        npts = (base_pts - 1) * 2 ** level + 1
        v = solve(sizes, probs, rho, dt, npts, grid)
        sols.append(v[:: 2 ** level])
    v1, v2, v3 = sols
    # First-order Richardson using the two finest levels.
    return np.linspace(0.0, 1.0, base_pts), 2 * v3 - v2, v3
