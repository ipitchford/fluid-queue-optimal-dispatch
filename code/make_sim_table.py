#!/usr/bin/env python3
"""Render the simulation tables of the paper from results/simulation.json.

Usage: python3 make_sim_table.py SIMULATION_JSON OUTPUT_TEX
"""
import json
import sys

NAMES = {"exponential": "Exponential", "two_point": "Two-point", "hyperexponential": "H$_2$, SCV 10",
         "bounded_pareto": "Bounded Pareto"}


def fmt(c):
    m, h = c["mean"], c["ci95_half_width"]
    if m >= 1000:
        return r"$>10^3$"
    return f"{m:.3f}" if h < 0.0005 else f"{m:.3f}\\,$\\pm${h:.3f}" if h < 0.01 else f"{m:.2f}\\,$\\pm${h:.2f}"


def main():
    data = json.load(open(sys.argv[1]))
    cells = {(c["law"], c["rho"], c["policy"]): c for c in data["cells"]}
    pols = ["SITA", "DICE", "CARD", "FLUID", "FLUID-S"]
    out = [r"\begin{table}[t]", r"\centering\footnotesize\setlength{\tabcolsep}{3.2pt}",
           r"\caption{Simulated mean waiting time under JSW (with 95\% interval) and, for the other policies, the mean"
           r" per-replication ratio of mean waiting time to JSW (common random numbers; 20 replications of $10^6$"
           r" arrivals). Ratios below one beat JSW; the best ratio in each row is in bold. Numerical evidence only.}\label{tab:sim}",
           r"\begin{tabular}{@{}llcccccccc@{}}", r"\toprule",
           r"Law & $\rho$ & JSW wait & RND & SITA & Dice & CARD & FLUID & FLUID-S\\", r"\midrule"]
    for law in ["exponential", "two_point", "hyperexponential", "bounded_pareto"]:
        for rho in [0.5, 0.75, 0.9]:
            ratios = {p: cells[(law, rho, p)]["ratio_to_JSW"] for p in ["RND"] + pols}
            best = min(round(ratios[p]["mean"], 3) for p in pols)
            row = [NAMES[law] if rho == 0.5 else "", f"{rho}", fmt(cells[(law, rho, "JSW")]["mean_wait"])]
            for p in ["RND"] + pols:
                r = ratios[p]
                s = r"$>10^3$" if r["mean"] >= 1000 else f"{r['mean']:.3f}" if r["mean"] < 10 else f"{r['mean']:.1f}"
                if p != "RND" and round(r["mean"], 3) == best:
                    s = r"\textbf{" + s + "}"
                row.append(s)
            out.append(" & ".join(row) + r"\\")
        out.append(r"\addlinespace[2pt]")
    out[-1] = r"\bottomrule"
    out += [r"\end{tabular}", r"\end{table}", ""]
    # Robustness table.
    out += [r"\begin{table}[t]", r"\centering\footnotesize",
            r"\caption{Robustness (ratio to JSW). Noise: routing on $\hat S=Se^{\sigma N-\sigma^2/2}$ with tuned"
            r" parameters left unchanged. Design load: FLUID-S built for $\hat\rho=\rho\pm0.05$.}\label{tab:robust}",
            r"\begin{tabular}{@{}llccccccc@{}}", r"\toprule",
            r"Law & $\rho$ & \multicolumn{2}{c}{SITA, $\sigma=$} & \multicolumn{2}{c}{CARD, $\sigma=$} & \multicolumn{2}{c}{FLUID-S, $\sigma=$} & FLUID-S, $\hat\rho=$\\",
            r"& & 0.5 & 1 & 0.5 & 1 & 0.5 & 1 & $\rho-0.05$ / $\rho+0.05$\\", r"\midrule"]
    for law in ["exponential", "hyperexponential"]:
        for rho in [0.75, 0.9]:
            row = [NAMES[law] if rho == 0.75 else "", f"{rho}"]
            for p in ["SITA", "CARD", "FLUID-S"]:
                for sg in ["0.5", "1.0"]:
                    r = cells[(law, rho, f"{p}|noise={sg}")]["ratio_to_JSW"]["mean"]
                    row.append(r"$>10^3$" if r >= 1000 else f"{r:.3f}")
            lo = cells[(law, rho, f"FLUID-S|design_load={round(rho - 0.05, 4)}")]["ratio_to_JSW"]["mean"]
            hi = cells[(law, rho, f"FLUID-S|design_load={round(rho + 0.05, 4)}")]["ratio_to_JSW"]["mean"]
            row.append(f"{lo:.3f} / {hi:.3f}")
            out.append(" & ".join(row) + r"\\")
    out += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    open(sys.argv[2], "w").write("\n".join(out))


if __name__ == "__main__":
    main()
