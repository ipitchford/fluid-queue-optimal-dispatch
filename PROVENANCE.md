# Provenance

* Scholarly creator: **Anonymous**, the standing Evidence Press attribution. No human research contribution is claimed or inferred. There is no ORCID and no affiliation.
* Publisher: Evidence Press (https://evidencepress.org; release page https://evidencepress.org/releases/fluid-queue-optimal-dispatch/). Ian Pitchford maintains the repository and carries out publication operations under the repository owner's account. That role is not authorship.
* Production: AI-assisted research. AI research agents produced the manuscript, proofs and code. Errors were sought in five ways:
  * internal checks by separate AI agents of the first draft (19 October 2026), recorded in the research ledger;
  * an internal multi-perspective AI-assisted review of that draft in five roles (23 October 2026);
  * an AI-assisted adversarial audit of the same draft by a different model (configured as OpenAI gpt-6-astra, 23 October 2026). It found a major defect in the floating-point quadrature code and two wording points;
  * a verification re-review of the revised version (23 October 2026), which traced every fix, replayed the code and raised four reporting points;
  * a second AI-assisted adversarial audit of the revised version by the same external model (23 October 2026). It found no counterexample to the main theorems and asked for three local corrections and three scope fixes.

  Their substantive points and how each was handled are in [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md). The original reports are kept privately.
* Target: Xie, Hyytiä and Righter, *Size-aware dispatching to fluid queues*, ACM SIGMETRICS Performance Evaluation Review 53(4) (2026) 42–48, doi:10.1145/3797823.3797843. Open version: arXiv:2509.21693v1 (25 September 2025), whose section numbering is used. Section 1 of the manuscript quotes the conjecture from XHR Sections 5 and 6.1, with attribution.
* History:
  * A research draft (Markdown, 27-page PDF) and its bounded novelty search are dated 19 October 2026.
  * On 23 October 2026 the draft was reviewed and audited. It was then revised: moved to LaTeX (21 pages), restructured, given heavy-traffic, noisy-estimate and exact-enclosure results, a comparison with XHR's Propositions 3 and 5 and Corollary 4, an independent dynamic-programming check, a repaired quadrature code with regression tests, and a stochastic simulation study.
  * The revision was re-reviewed and audited again the same day. A final pass applied the re-review's four reporting fixes and the second audit's corrections: Remark 6 (closed-loop selection), Proposition 15 (uninformative estimates), the Pareto 1.01 peak-cell certificate in `verify_all.py` (enclosure now 0.401013 < V(1,0) < 0.402732), the E S² < ∞ qualifier for the CARD comparison, the CARD grid description, interior qualifiers, and a rounding clamp in the quadrature code. Only `results/pareto_101_regression.json` changed among the results. The paper is 21 pages.
  * The revised package was replayed from a clean copy before freezing ([REPLAY_RECEIPT.md](REPLAY_RECEIPT.md)).
  * Only the revised version is published.
* Publication edits:
  * the reserved DOI and repository URL inserted in the manuscript's date line and its reproducibility appendix, and the PDF rebuilt with pdflatex;
  * README.md replaced by the release README;
  * the release records listed in README.md added, together with `negative_controls.py`, `tools/compare_results.py`, `.github/workflows/replay.yml`, `LICENSE`, `LICENSES.md` and `PUBLIC_DOMAIN.md`;
  * `requirements.txt` replaced by exact pins of the tested versions;
  * SHA256SUMS generated.

  No computation script and no results file was changed by publication.
