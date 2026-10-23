# Assurance

This file says what has been checked and what has not. Each row is a separate kind of assurance, and no row implies another.

| Dimension | State | Evidence |
|---|---|---|
| Availability | Public GitHub release and Zenodo DOI 10.5281/zenodo.23586955 | Release assets and [SHA256SUMS](SHA256SUMS) |
| Written proofs | Complete proofs in the manuscript for every result marked "proved" | [paper/paper.pdf](paper/paper.pdf), Sections 5–10 and Appendices A–D. The verification argument is the classical sufficiency half of dynamic programming, adapted to reflection at empty queues and a kink on the diagonal. |
| Exact certificates | Rational arithmetic only (`fractions.Fraction`) | [code/verify_all.py](code/verify_all.py) sections `exact_finite_support`, `two_point_certificate`, `certified_binning`, `pareto_certificate`, `deterministic_checks`, and the rational part of `pareto_101_regression`; [code/fluid_exact.py](code/fluid_exact.py). Every check is explicit, so `python -O` disables nothing. |
| Symbolic checks | sympy | `symbolic_identities`: the gradient identity of Lemma 7 and the sector formulas of Theorem 11. |
| Floating-point checks | Supporting evidence, labelled as such | `quadrature_checks`, `heavy_traffic`, `source_comparison`, `wasserstein_looseness`. The quadrature code raises on any quadrature warning, rejects cutoffs beyond floating-point range, and enforces the universal bounds V(1,0) ≥ ρ/2 and B(0) ≥ 1 + 1/r. |
| Independent optimality check | Numerical, does not use the formula | [code/dp_check.py](code/dp_check.py): a semi-Lagrangian Bellman scheme over a full grid of fractional allocations, with exact reflection and policy iteration. Agreement with the value formula to at most 3.1×10⁻⁵ relative error ([results/dp_cross_check.json](results/dp_cross_check.json)). |
| Stochastic simulation | Numerical evidence only | [code/simulate.py](code/simulate.py), [results/simulation.json](results/simulation.json), Tables 6–7. Seeded, common random numbers, 95% Student-t intervals. No policy dominates in every cell. No theorem rests on it. |
| Internal replay | Passed, byte-identical | A clean pre-freeze replay of `verify_all.py` on 23 October 2026 reproduced all 13 files byte for byte. See [REPLAY_RECEIPT.md](REPLAY_RECEIPT.md). The final frozen-archive replay is recorded by the publisher. |
| Semantic negative controls | Passed | [negative_controls.py](negative_controls.py) runs an unmodified baseline, then checks that each of these is rejected: five tampered result values (including 33/28 and the switching ratio 3/13), a missing section, six inadmissible inputs (deterministic law, wrong mean, wrong probabilities, ρ = 1 in both solvers, Pareto 1.001), fourteen injected code or claim errors (wrong sign in D, wrong terminal cutoff, wrong r, wrong F_H, wrong cost integral, wrong optimum, wrong load, flipped conjecture check, flipped deterministic counterexample, wrong quadrature D, the audited heavy-tail quadrature defect, a biased DP, a too-tight DP tolerance, a wrong symbolic formula), and three tampered files or hash entries. A positive control checks that a 1e-9 float change is accepted. |
| Continuous integration | Configured | [.github/workflows/replay.yml](.github/workflows/replay.yml): SHA256SUMS, pinned install, full `verify_all.py`, comparison by [tools/compare_results.py](tools/compare_results.py) (exact fields exact, floats to relative 1e-6), negative controls, a simulation smoke test (not compared), and a clean working tree. |
| Implementation diversity | Partial | The dynamic-programming check is a separate method. Two internal reviewers wrote their own value iteration or DP and matched the value. The adversarial audit wrote its own rational checks (259 law–load cases) and arbitrary-control integrations. All of this is inside one producer workflow, not independent reimplementation. |
| Internal AI-assisted review | Done | Five review roles (editor, methodology, domain, perspective, devil's advocate), an AI-assisted adversarial audit by a different model (configured as OpenAI gpt-6-astra, 23 October 2026), a verification re-review of the revision, which replayed the code byte-identically and probed 15 extra quadrature cases, and a second AI-assisted adversarial audit of the revision by the same external model, whose corrections were applied in a final pass. Summary in [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md). This is not peer review. |
| Independent rerun or reimplementation by an unaffiliated party | Not established | |
| Specialist (human) review | Not established | |
| Editorial peer review | Not established | |
| Formal verification | Not attempted | No proof assistant was used. |
| Source fidelity | arXiv v1, plus a public copy of the published issue | The conjecture is quoted from arXiv:2509.21693v1, Sections 5 and 6.1. The publisher's DOI page returned HTTP 403 during revision, so the paper says the Proposition 3 comparison uses arXiv v1. The verification re-review read a public copy of the published issue and found the conjecture wording and Proposition 3 identical to arXiv v1; see [SOURCES.md](SOURCES.md). |
| Environment | Pinned Python packages; deterministic JSON | [ENVIRONMENT.txt](ENVIRONMENT.txt), [requirements.txt](requirements.txt) |
| Novelty | Bounded search only | [RESEARCH_GATES.json](RESEARCH_GATES.json), [SOURCES.md](SOURCES.md) |
| Citations | All 24 DOIs resolved | [CITATION_AUDIT.md](CITATION_AUDIT.md) |

## Scope and limits

* The theorems are about the fluid model. Nothing here proves optimality, stability or asymptotic optimality of any rule in the stochastic queue.
* The heavy-traffic agreement with CARD is exact for the fluid constant; the link to the stochastic system is heuristic, and the CARD constants assume E S² < ∞.
* The floating-point quadrature code is tested on a stated family of laws and loads (Section 12). It rejects some extreme heavy tails. The exact finite-support solver has no such limit.
* The Wasserstein constant proves convergence of discretisations; it is not a practical error estimate.
* The simulation uses small tuning grids; some tuned parameters lie at a grid edge, so tuned policies may do slightly better than reported.
* Byte-identical replay shows that the shipped outputs are exactly what the shipped programs produce. It does not by itself show that the programs implement the manuscript's definitions. That rests on the proofs, the independent DP check, the negative controls and the independent recomputations in the internal reviews.
