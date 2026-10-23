# Summary of internal review

**What this is.** A public summary of the internal checks made on this manuscript before release. They were AI-assisted: AI agents reviewed the draft in five roles, a different AI model ran an adversarial audit, and after revision an AI agent ran a verification re-review while the same external model ran a second adversarial audit. A final pass fixed the points from both. All of this happened inside one Evidence Press workflow. **It is not peer review, it is not independent reproduction by an unaffiliated party, and it is not formal verification.** The original reports are kept privately. This summary keeps the substantive objections, what was done about each, and what remains open. It reports no scores or verdicts.

Section, theorem and table numbers refer to the released [paper/paper.pdf](paper/paper.pdf) unless stated otherwise. The reviewed draft (19 October 2026, Markdown, 27 pages) had different numbering.

## Rounds

| Round | Date | Who | What was checked |
|---|---|---|---|
| Multi-perspective review of the draft | 23 Oct 2026 | AI-assisted reviewers in five roles: editor, methodology, domain, perspective (practical use), devil's advocate | Proofs, positioning against the source, literature, readability, significance. Two reviewers wrote their own value iteration or dynamic programme; others re-derived identities in sympy and by hand. |
| Adversarial audit of the draft | 23 Oct 2026 | A different AI model (configured as OpenAI gpt-6-astra) | Line-by-line attacks on the proofs, new exact-arithmetic checks, arbitrary-control integrations, a heavy-tail numerical attack, and source fidelity. It worked from selective copies and did not see the other reviews. |
| Revision | 23 Oct 2026 | Producer | All points below; the paper moved to LaTeX (21 pages). |
| Verification re-review of the revision | 23 Oct 2026 | AI-assisted reviewer | Traceability of every fix, claim scope, source fidelity, references, simulation reporting, package hygiene; a clean replay; a 15-case quadrature probe outside the tested set. |
| Second adversarial audit of the revision | 23 Oct 2026 | The same external model (configured as OpenAI gpt-6-astra) | New proofs line by line; its earlier exact harnesses rerun against the revised solver; an independent Pareto 1.5 certificate; an independent labelled-workload DP; inspection of the simulation code. It did not see the other reviews. |
| Final pass | 23 Oct 2026 | Producer | The re-review's reporting fixes and the second audit's corrections; the paper is 21 pages. |

## What the reviewers confirmed

* No reviewer and neither audit found a mathematical error in the main results: the exact value and its verification over all admissible controls (including idling and reflection), the every-optimal-path statement of the conjecture, uniqueness, the finite-support recurrence, the bin-policy certificate and the Wasserstein estimate.
* Independent numerical checks matched the value formula. Two reviewers' own dynamic programmes (one with a full grid of fractional allocations and genuine reflection, with no threshold structure imposed) reproduced 33/28 for the running example, several loads, a zero-size atom and the deterministic case. High-precision evaluation reproduced the exponential row of the gain table. The audit ran 259 law–load cases of new rational checks and 6,000 exact arbitrary-control segments without a failure of the verification inequality.
* The deterministic exception is genuine: with S ≡ 1 there are optimal controls that decrease the imbalance.
* The source's Proposition 3 discrepancy (an extra factor 2ρ in the axis term) was found independently by the devil's advocate and the domain reviewer, and confirmed by the re-review against a public copy of the published issue.

## Objections and how they were handled

### Positioning against the source (domain reviewer, devil's advocate, editor)

1. **The conjecture was not quoted, and its sign needs reconciling.** XHR write "the optimal ŷ′ ≥ 0", with ′ = d/dx; read literally, the imbalance would not grow as the backlog falls. *Done:* Section 1 quotes both the symbolic form (XHR §5) and the verbal form (XHR §6.1). It explains the sign, proves the forward-time statement (Theorem 4) and says that the literal inequality is false.
2. **"Necessary qualification" overstated the deterministic exception.** XHR assume sizes with a density. *Done:* the paper now says the conjecture is proved as posed and extended to all nondegenerate laws; deterministic sizes lie outside the hypotheses (Section 1, Section 7).
3. **The source's Corollary 4 and Proposition 3 were not discussed.** *Done:* Section 8 shows that, in the interior, no straight-to-origin segment and no balanced dwelling is optimal for nondegenerate laws (the optimal axis phase is itself straight-to-origin), gives the corrected most-work-left value (eq. 8.1), and reports the printed and corrected values (1.19401 vs 1.10851; 3/2 vs 21/16). Section 9 shows the effect on XHR's heavy-traffic agreement with CARD.
4. **How much of the route does XHR's variational problem already contain?** *Done:* Table 1 compares XHR's results with the new ones. The paragraph "How much is new" says plainly that the Beltrami first integral gives the candidate in a few lines; the work is the global verification, all optimal controls, the edge cases and the extensions.
5. **Proposition 5 needs ρ ≥ 1/2.** The devil's advocate noted that the low-load counterexample depends on how "work-conserving" is read past absorption. *Done:* Section 7 states that both costs accrue before any queue empties, so the difference does not depend on stopping at absorption.

### Significance and extensions (editor, perspective, devil's advocate)

6. **No evidence beyond the fluid model.** The perspective reviewer's own simulation found that the fluid rule used directly beats JSW for hyperexponential sizes but loses badly for exponential and two-point sizes at high load. *Done:* a new simulation study (Section 11; Tables 6–7) with seven policies, four laws and three loads, common random numbers and t-intervals. It explains why the direct rule fails, and adds a stabilised rule (FLUID-S) with a safety band. Everything there is labelled numerical evidence. No policy dominates in every cell.
7. **No heavy-traffic analysis.** *Done:* Theorem 10 proves (1 − ρ)V → P̄x² with explicit bounds, and reconciles it with the CARD constant of Xie, Grosof and Scully. The passage to the stochastic queue is labelled heuristic.
8. **Gains reported against the wrong baseline.** *Done:* Table 3 reports savings against balanced routing (21–43%), which JSW, random splitting and SITA all coincide with in the fluid model, as well as against most-work-left (7–18%).
9. **Certificates for unbounded laws were impractical, and the Wasserstein constant is very loose.** The devil's advocate estimated about 10⁹ bins for a 1% certificate at Pareto 1.5. The methodology reviewer measured looseness of 5–16×. *Done:* Section 10.3 quantifies the looseness and says the theorem proves convergence only. Section 10.4 adds an exact rational enclosure that keeps the tail analytic (Table 5).
10. **Robustness to noisy sizes and a misspecified load.** *Done:* Proposition 15 (proved; its uninformative-estimate case was completed after the second audit) for routing on estimates; Table 7 (numerical) for size noise and load error.
11. **Only two identical servers.** *Not done:* stated as a limitation and an open question (Section 12).

### Rigour and evidence design (methodology reviewer)

12. **The bundled "independent" check only tested attainment, not optimality.** *Done:* a dynamic-programming check (`code/dp_check.py`) that does not use the formula, with no threshold structure, exact reflection and policy iteration; relative error at most 3.1×10⁻⁵ after extrapolation.
13. **The C¹ regularity and chain-rule step at the diagonal and axes was compressed.** *Done:* Lemma 7 (regularity in sorted coordinates), with the chain-rule step written out.
14. **Admissible controls and the feedback reading were informal.** *Done:* Definition 1 (admissible pairs; Skorokhod uniqueness) and Remark 6 (every closed-loop solution is optimal).

### Software and wording (adversarial audit)

15. **Major software defect: the quadrature silently lost almost the whole integral for a heavy tail.** For Pareto shape 1.01 at load 3/4 the old code returned about 0.005, below the bound ρ/2 = 0.375 that every admissible control must pay. *Done:* the quadrature now integrates in a log variable beyond a fixed scale, treats the far tail analytically, raises on any quadrature warning, rejects cutoffs beyond floating-point range, and enforces V(1,0) ≥ ρ/2 and B(0) ≥ 1 + 1/r. A regression test compares it with an exact rational enclosure (0.401013 < V(1,0) < 0.402732); the code now gives 0.401873. The paper and README separate the tested numerical domain from the theorem domain. The audit stressed that this defect did not affect the theorems or the exact solver.
16. **An axis "incurs no further cost" at low load was overstated.** A control *can* stop paying; others may continue. *Done* (Section 2).
17. **The strict derivative inequality holds only almost everywhere.** In the running example dz/dx has one-sided values −588/169 and −315/169 at the switch. *Done* (Theorem 4 and the sentence after it).

### Literature and readability (all reviewers)

18. **Seven references were far too few.** *Done:* 24 references covering SITA, size- and state-aware dispatching, fluid control and its stochastic translation, verification with state constraints, stochastic orders and predicted sizes. All DOIs were checked ([CITATION_AUDIT.md](CITATION_AUDIT.md)).
19. **The draft read as an assembly of components.** *Done:* a plain-language policy box, a results list with status labels, the heuristic derivation and its "break-even size" reading before the proofs, one running example throughout, a notation table mapped to XHR's symbols, consecutive numbering, and removal of duplicated proofs.
20. **Process language in the paper and README.** *Done:* removed.

## Points from the verification re-review (all applied)

The re-review traced every item above and found each addressed. It found no open mathematical issue. It raised four reporting points, all applied in the final pass:

* **Simulation interval sentence.** The draft said the ratio intervals are at most ±0.01 except for the bounded Pareto law; the JSON shows wider intervals for the direct FLUID rule, RND and SITA. The sentence was rewritten from the JSON ([paper/sim_findings.tex](paper/sim_findings.tex)).
* **A count in the simulation findings.** FLUID-S is within 0.08 of the best in nine cells, not eight, and the two-point losses are 6% and 13%. Corrected.
* **Heavy-traffic constant with an atom at the work median.** The short form "P(S ≥ m)" is exact only for continuous laws. The abstract and results list now use the atom-split fraction P̄ of Theorem 10 (in the running example P̄ = 1/3 while P(S ≥ 3/2) = 1/2).
* **Numerical domain and source availability.** Section 12 now says that for Pareto shape 1.01 and the concentrated laws only V(x, 0) is tested, and that the code raises an error at larger imbalances for Pareto 1.01. Section 8 now says the published PER version prints the same Proposition 3 and most-work-left definition as arXiv v1.

## Points from the second adversarial audit (all addressed)

The second audit found no counterexample to the main value, monotonicity, optimal-path uniqueness, heavy-traffic or Wasserstein theorems. It confirmed that the earlier quadrature defect is repaired within the disclosed numerical domain. It raised:

* **R1. A fixed diagonal tie-break does not select a unique closed-loop solution.** In the running example, two mirror-image paths both solve the same closed-loop equation almost everywhere from (1/2, 1/2). *Fixed:* Remark 6 now says so, with the explicit example. Every closed-loop solution is still optimal, and Theorem 5 (exactly two optimal paths from a tie) is unaffected.
* **R2. The noisy-estimate controller is undefined when the estimate is uninformative.** If E[S | Ŝ] ≡ 1 the scalar construction does not apply; the right value is the deterministic one (3/2 instead of 33/28 in the running example). *Fixed:* Proposition 15 now branches and gives the deterministic controller of Section 7 in that case.
* **R3. The Pareto 1.01 peak-cell argument was invalid, though its bound was valid.** The tangent-intersection height used on the cell holding the peak is not a lower bound there. *Fixed:* `verify_all.py` now uses an exact peak-equation bound and checks it in rational arithmetic. The regenerated enclosure is 0.401013 < V(1,0) < 0.402732; only `results/pareto_101_regression.json` changed.
* **P1. Moment assumptions in the stochastic statements.** The CARD constants assume E S² < ∞; the fluid theorem needs only the mean. A sentence saying that infinite variance gives infinite mean waiting under every policy is false in general. *Fixed:* Section 9 states the assumption; the sentence was removed.
* **P2. The stated CARD tuning grid included negative workload targets that the code clips to zero.** *Fixed:* the text now writes the targets with positive parts and explains the convention; at ρ = 1/2 the 24 grid points give 12 distinct policies.
* **P3. Some summaries overstated interior conclusions.** "No straight-to-origin path is optimal" holds in the interior only; the running example's cutoff below z = 3/13 is h = 14z/(3(1 + 5z)), not zero (any cutoff below 1/2 gives the same allocation); "kept exactly busy" needs load at least 1/2; a typo in Definition 1. *Fixed.*
* In addition the quadrature code now clamps rounding-size negative values to zero (about −1e−46 at the axis for Pareto 1.01) and raises on anything larger.

The audit also noted limits of its own checks: it did not rerun the full simulation or recompute every stored interval, the stored JSON holds aggregates rather than raw replications, and cells described as unstable are empirical observations.

## Remaining limitations

* No proof of stability or asymptotic optimality for FLUID-S in the stochastic queue; "unstable" simulation cells are empirical.
* Small simulation tuning grids; some tuned parameters lie at a grid edge.
* Two identical servers only; heterogeneous rates and more servers are open.
* Whether V is a viscosity solution in the classical sense is left open; it is not needed.
* The quadrature code's tested domain is narrower than the theorem domain.
* No human specialist, no unaffiliated reproduction and no proof assistant.
