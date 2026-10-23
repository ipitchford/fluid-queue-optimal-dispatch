# Agent navigation

## Identity

- Release slug: `fluid-queue-optimal-dispatch`. Version `1.0.0-candidate`, tag `v1.0.0-candidate`. DOI 10.5281/zenodo.23586955; concept DOI 10.5281/zenodo.23586954.
- Repository: https://github.com/ipitchford/fluid-queue-optimal-dispatch. Release page: https://evidencepress.org/releases/fluid-queue-optimal-dispatch/
- Title: *Exact optimal dispatching to two fluid queues: closed form, heavy traffic and stochastic evidence*. Scholarly creator: Anonymous. Status: unrefereed candidate ([STATUS.md](STATUS.md)).
- Manuscript: [PDF](paper/paper.pdf) (21 pages) and [LaTeX source](paper/paper.tex), with [paper/sim_table.tex](paper/sim_table.tex) and [paper/sim_findings.tex](paper/sim_findings.tex). Figures: [figures/two_point_policy.png](figures/two_point_policy.png), [figures/optimal_paths.png](figures/optimal_paths.png) (illustrations only).
- Machine-readable claims: [CLAIMS.json](CLAIMS.json). Overview for humans: [README.md](README.md).
- Assurance limits: [ASSURANCE.md](ASSURANCE.md). Internal review summary: [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md).
- Provenance: [PROVENANCE.md](PROVENANCE.md). Sources: [SOURCES.md](SOURCES.md), [CITATION_AUDIT.md](CITATION_AUDIT.md), [RESEARCH_GATES.json](RESEARCH_GATES.json).
- Citation: [CITATION.cff](CITATION.cff) and [Zenodo metadata](.zenodo.json). Licences: [LICENSES.md](LICENSES.md), [PUBLIC_DOMAIN.md](PUBLIC_DOMAIN.md).

## Model in one paragraph

Two identical FCFS servers of rate 1/2. Fluid of job sizes S ≥ 0 with E S = 1 (not a point mass) arrives at rate ρ ∈ (0, 1). A control q(s, t) sends the fraction q_i of size-s jobs to queue i; servers may idle (reflection at zero, eq. (2.1)). Cost J = ∫ 2(a₁u₁ + a₂u₂) dt. Coordinates x = u₁ + u₂, y = |u₁ − u₂|, z = y/x, r = ρ/(1 − ρ). Key function D(h) = E|S − h|. Source: Xie, Hyytiä and Righter ("XHR"), ACM SIGMETRICS PER 53(4) (2026) 42–48, doi:10.1145/3797823.3797843; arXiv:2509.21693v1.

## Scientific map

Each line: claim, status, paper location, code section, result file. Code sections are functions of [code/verify_all.py](code/verify_all.py).

- **Exact optimum.** V of eq. (4.4) is the value for every nondegenerate mean-one law and 0 < ρ < 1; threshold policy π*. *Proved.* Theorem 3, Lemma 2, Sections 4–5, Appendix A. Checks: `exact_finite_support` ([results/exact_finite_support.json](results/exact_finite_support.json)), `quadrature_checks` ([results/quadrature_checks.json](results/quadrature_checks.json)), `symbolic_identities` ([results/symbolic_identities.json](results/symbolic_identities.json)); independent DP `dp_cross_check` ([results/dp_cross_check.json](results/dp_cross_check.json), [code/dp_check.py](code/dp_check.py)).
- **The conjecture.** Relative imbalance nondecreasing along every optimal path, strictly while 0 < y < x; dz/dx < 0 a.e. Proved as posed (density) and extended to all nondegenerate laws. *Proved.* Theorem 4, Section 6. Illustrated (not proved) by the path monotonicity check in `quadrature_checks` and by [figures/optimal_paths.png](figures/optimal_paths.png).
- **Unique optimal path.** *Proved.* Theorem 5, eq. (4.5), Appendix B. Remark 6: every closed-loop solution is optimal, but from a positive tie the closed loop has two solutions even with a fixed diagonal action.
- **Running example** (sizes 1/2, 3/2; ρ = 3/4; start (1/2, 1/2)): optimal 33/28, switch z = 3/13, θ = 5/9, balanced 3/2, most-work-left 21/16. *Exact.* Section 4, Figure 1. `two_point_certificate` ([results/two_point_certificate.json](results/two_point_certificate.json)) and `exact_finite_support`.
- **Deterministic sizes.** Exact value eq. (7.1); conjecture fails; XHR Prop. 5 needs ρ ≥ 1/2 (costs 1/6 vs 3/16 at ρ = 1/4). *Proved; small cases exact.* Section 7. `deterministic_checks` ([results/deterministic_checks.json](results/deterministic_checks.json)).
- **XHR Proposition 3 correction.** Corrected most-work-left value eq. (8.1); printed 1.19401 vs direct 1.10851 (exponential), 3/2 vs 21/16 (two-point). *Proved; comparison exact for two-point.* Section 8. `source_comparison` ([results/source_comparison.json](results/source_comparison.json)).
- **Heavy traffic.** (1 − ρ)V_ρ → P̄x², P̄ < 1/2; P̄ = P(S ≥ m) for continuous laws (m the work median), with an atom at m split as in Theorem 10; same limit for most-work-left; ratio 2P̄ equals the CARD / least-work-left constant ratio of Xie–Grosof–Scully. *Fluid limit proved; stochastic link heuristic.* Theorem 10, Section 9, Table 4. `heavy_traffic` ([results/heavy_traffic.json](results/heavy_traffic.json)).
- **Finite-support controller.** Piecewise quadratic value, rational O(K) recurrence. *Proved; exact.* Theorem 11, eq. (10.1), Appendix C. [code/fluid_exact.py](code/fluid_exact.py); `exact_finite_support`.
- **Envelope formula, convex order, certified bracket and bin policy.** *Proved; brackets exact.* Proposition 12, Corollary 13, eq. (10.3), Appendix D. `certified_binning` ([results/certified_binning.json](results/certified_binning.json)).
- **Wasserstein stability.** |V_X − V_Y| ≤ C_ρ x² W₁; constant qualitative (looseness 5.4–16.4×; 42× and 656× for bracket widths). *Proved; looseness numerical.* Theorem 14, Section 10.3. `wasserstein_looseness` ([results/wasserstein_looseness.json](results/wasserstein_looseness.json)).
- **Pareto enclosures.** Shape 1.5: Table 5. Shape 1.01: 0.401013 < V(1,0) < 0.402732, used as a regression test for the quadrature. *Exact rational.* Section 10.4. `pareto_certificate` ([results/pareto_certificate.json](results/pareto_certificate.json)), `pareto_101_regression` ([results/pareto_101_regression.json](results/pareto_101_regression.json)).
- **Noisy size estimates.** Optimal value is V for E[S | Ŝ]; loss ≤ 2C_ρ x² E|S − Ŝ|; if E[S | Ŝ] ≡ 1 the deterministic controller applies. *Proved.* Proposition 15, Section 10.5.
- **Stochastic simulation.** Seven policies, four laws, three loads, 20 × 10⁶ arrivals per cell. *Numerical evidence only; no policy dominates in every cell.* Section 11, Tables 6–7. [code/simulate.py](code/simulate.py), [results/simulation.json](results/simulation.json), [code/make_sim_table.py](code/make_sim_table.py).

Do not read:
- any statement as a theorem about the stochastic queue;
- the heavy-traffic agreement with CARD as a proved stochastic result (it also assumes E S² < ∞);
- the simulation as showing that FLUID-S, Dice or CARD is best overall;
- XHR's symbolic ŷ′ ≥ 0 as proved (it is false read literally; the verbal forward-time statement is proved);
- the conjecture as holding for deterministic sizes;
- "no straight-to-origin path is optimal" outside the interior (the optimal axis phase is one);
- the diagonal tie-break as selecting a unique closed-loop solution;
- the Wasserstein constant as a practical error bound;
- the floating-point code as valid outside its tested domain (Section 12); for Pareto 1.01 only V(x, 0) is regression-tested;
- internal AI-assisted review as peer review.

## Code

- [code/verify_all.py](code/verify_all.py): 12 sections, writes 13 deterministic JSON files. Exact sections use `fractions.Fraction`.
- [code/fluid_exact.py](code/fluid_exact.py): exact rational solver. [code/fluid_quadrature.py](code/fluid_quadrature.py): quadrature solver (log-variable integration, warnings raise, universal bounds enforced). [code/dp_check.py](code/dp_check.py): independent Bellman/DP check.
- [code/simulate.py](code/simulate.py): seeded simulation. [code/make_sim_table.py](code/make_sim_table.py), [code/build_figures.py](code/build_figures.py): tables and figures.
- [tools/compare_results.py](tools/compare_results.py): replay comparator. [negative_controls.py](negative_controls.py): semantic negative controls.

## Replay

Python 3.13 with the pins in [requirements.txt](requirements.txt):

```sh
sha256sum -c SHA256SUMS                          # or: shasum -a 256 -c SHA256SUMS
python -B -O -I code/verify_all.py OUT           # about 1 minute
python -B -I tools/compare_results.py results OUT --bytes   # byte-identical on the release host
python -B -O negative_controls.py                # about 1-3 minutes
python -B -I code/simulate.py OUT --quick        # smoke test; the full run takes about 50 CPU-minutes
```

Results of the release replay: [REPLAY_RECEIPT.md](REPLAY_RECEIPT.md). Environment: [ENVIRONMENT.txt](ENVIRONMENT.txt). CI: [.github/workflows/replay.yml](.github/workflows/replay.yml).

## Useful next research questions

Is a stabilised fluid rule such as FLUID-S stable, or asymptotically optimal at fluid scale or in heavy traffic, in the stochastic two-server queue? What survives for three or more servers, where the scalar reduction is lost, or for heterogeneous rates (Section 12)?
