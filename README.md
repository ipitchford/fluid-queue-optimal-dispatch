# Exact optimal dispatching to two fluid queues

**Release 1.0.0-candidate (23 October 2026). Unrefereed research candidate.**
DOI: [10.5281/zenodo.23586955](https://doi.org/10.5281/zenodo.23586955) (this version) ·
concept DOI [10.5281/zenodo.23586954](https://doi.org/10.5281/zenodo.23586954) (all versions) ·
repository <https://github.com/ipitchford/fluid-queue-optimal-dispatch> (tag `v1.0.0-candidate`) ·
Evidence Press page <https://evidencepress.org/releases/fluid-queue-optimal-dispatch/>.

Full title: *Exact optimal dispatching to two fluid queues: closed form, heavy traffic and stochastic evidence*.
Author: Anonymous. Text, figures and results CC0-1.0; code MIT (see [LICENSES.md](LICENSES.md)).

Checked by internal AI-assisted review only: five review roles, an AI-assisted adversarial audit by a
different model, a revision, a verification re-review, and a second AI-assisted adversarial audit of the
revision, whose points were fixed in a final pass. This is not peer review, not independent reproduction
and not formal verification. See [STATUS.md](STATUS.md) and [ASSURANCE.md](ASSURANCE.md).

## The question

A dispatcher sends each arriving job to one of two identical first-come first-served servers. It knows the
job's size and how much work each queue holds. Which rule makes the total waiting time smallest?

Xie, Hyytiä and Righter studied a fluid version of this question (ACM SIGMETRICS Perform. Eval. Rev. 53(4),
2026, 42–48, doi:[10.1145/3797823.3797843](https://doi.org/10.1145/3797823.3797843); arXiv:2509.21693v1).
They reduced it to a one-dimensional variational problem, computed optimal paths numerically, and
conjectured that the *relative imbalance* between the two queues increases along every optimal path.

## What the paper shows, in words

* **The problem has an exact solution.** For every job-size law with mean one that is not a single point,
  and every load below one, one integral of the function D(h) = E|S − h| gives the optimal cost, the optimal
  policy and the optimal path from every starting state. The proof checks the formula against every
  admissible control, including controls that let a server idle.
* **The optimal policy is simple.** While both queues hold work, jobs smaller than a cutoff go to the
  shorter queue and larger jobs go to the longer one. The cutoff depends only on the relative imbalance and
  rises as the queues drift apart. Once one queue is empty, it is kept exactly busy when the load is at least 1/2;
  at lower loads it receives all arriving work.
* **The conjecture is true.** It is proved as posed (sizes with a density) and extended to every law that is
  not a single point, including laws with atoms. The optimal workload path is unique (two mirror images from
  a tied start). For deterministic sizes, which lie outside the conjecture's hypotheses, it fails.
* **Heavy traffic.** As the load tends to one (fluid model, first moment only), (1 − ρ)V → P̄x². For continuous laws P̄ = P(S ≥ m), where m is the
  work median; with an atom at m, the atom is split (Theorem 10). This
  corrects a factor in the source's Proposition 3. The limit matches the heavy-traffic constant of the CARD
  policy of Xie, Grosof and Scully. The fluid limit is proved; the link to the stochastic queue is a
  heuristic only, and the CARD comparison assumes E S² < ∞ as Xie, Grosof and Scully do.
* **Exact computation.** For finite size laws the value is piecewise quadratic with rational coefficients,
  computed in one backward pass. Further proved results: certified two-sided bounds with an implementable bin
  policy, stability in the Wasserstein distance, an exact rational enclosure for an infinite-variance Pareto
  law, and the cost of routing on noisy size estimates.
* **Simulation of the real (stochastic) queue: numerical evidence only.** Used directly, the fluid rule beats
  join-the-shortest-workload (JSW) by a wide margin for highly variable sizes, but fails badly at high load
  for exponential and two-point sizes. A stabilised version with a safety band repairs most of this and is
  competitive with tuned CARD and Dice. **No policy is best in every cell.** No theorem rests on the
  simulation.

The running example: sizes 1/2 and 3/2 with equal probability, load 3/4, start (1/2, 1/2). The optimal cost
is 33/28 ≈ 1.179, against 3/2 for balanced routing (a 21% saving) and 21/16 for most-work-left.

## Status of each result

| Result | Where | Status |
|---|---|---|
| Closed-form value and feedback policy, all nondegenerate mean-one laws, all loads below one | Theorem 3, Lemma 2 | proved |
| Relative imbalance increases along every optimal path (the conjecture), as posed and extended | Theorem 4 | proved |
| Unique optimal workload path | Theorem 5 | proved |
| Deterministic sizes: exact value; the conjecture fails; the source's Proposition 5 needs ρ ≥ 1/2 | Section 7 | proved; small cases exact |
| Corrected most-work-left value (source Proposition 3) | Section 8, eq. (8.1) | proved; comparison exact |
| Heavy-traffic limit (1 − ρ)V → P̄x² (P̄ = P(S ≥ m) for continuous laws); agreement with the CARD constant | Theorem 10 | fluid limit proved; stochastic link heuristic |
| Exact rational controller for finite size laws | Theorem 11 | proved; checked in exact arithmetic |
| Envelope formula, convex order, certified bracket and bin policy | Proposition 12, Corollary 13 | proved; brackets exact |
| Wasserstein stability (qualitative constant) | Theorem 14 | proved |
| Exact enclosures for Pareto shape 1.5 and 1.01 | Section 10.4, Table 5 | exact rational computation |
| Routing on noisy size estimates | Proposition 15 | proved |
| Six-law quadrature table, heavy-traffic table | Tables 3–4 | floating point, checked against the theory |
| Independent dynamic-programming check (does not use the formula) | Section 10.1 | numerical |
| Stochastic two-server simulation (RND, JSW, SITA, Dice, CARD, FLUID, FLUID-S) | Section 11, Tables 6–7 | numerical evidence only |

## Contents

| Path | Contents |
|---|---|
| [paper/paper.pdf](paper/paper.pdf), [paper/paper.tex](paper/paper.tex) | The paper (21 pages including appendices). `sim_table.tex` and `sim_findings.tex` are included by `paper.tex`. |
| [code/verify_all.py](code/verify_all.py) | One entry point for every computational check in the paper (12 sections, 13 JSON files). |
| [code/fluid_exact.py](code/fluid_exact.py) | Exact rational solver for finite size laws (standard library only). |
| [code/fluid_quadrature.py](code/fluid_quadrature.py) | Floating-point quadrature solver for continuous laws. |
| [code/dp_check.py](code/dp_check.py) | Independent dynamic-programming check; it does not use the value formula. |
| [code/simulate.py](code/simulate.py) | Seeded stochastic simulation (standard library only). |
| [code/make_sim_table.py](code/make_sim_table.py), [code/build_figures.py](code/build_figures.py) | Simulation tables and the two figures. |
| [results/](results/) | Recorded JSON outputs. |
| [figures/](figures/) | The two figures. |
| [tools/compare_results.py](tools/compare_results.py) | Compares a fresh replay with `results/`. |
| [negative_controls.py](negative_controls.py) | Semantic negative controls. |

## Reproduce

Use Python 3.13 (3.12 or later should work) and the pinned packages in [requirements.txt](requirements.txt).

```bash
sha256sum -c SHA256SUMS                          # macOS: shasum -a 256 -c SHA256SUMS
python -m pip install -r requirements.txt
python -B -O -I code/verify_all.py OUT           # about 1 minute; writes 13 JSON files
python -B -I tools/compare_results.py results OUT          # exact fields exact, floats to 1e-6
python -B -I tools/compare_results.py results OUT --bytes  # byte-identical on the release host
python -B -O negative_controls.py                # about 1-3 minutes
python -B -I code/simulate.py OUT --quick        # 10-second smoke test of the simulation
python -B -I code/simulate.py OUT                # full simulation, about 50 CPU-minutes, 4 processes
```

Each script writes only into the directory you give it. The JSON output is deterministic: keys are sorted,
there are no timestamps, versions or paths, floats are rounded to 8 significant digits, and exact rationals
are written as strings or as decimals rounded outwards. All checks are explicit, so `python -O` disables
nothing. On another platform the 8-digit floating-point fields may differ in the last digit; the exact fields
do not. Build the paper with `pdflatex paper.tex`, run three times inside `paper/`.

The quadrature code is tested on exponential, uniform, gamma (shapes 4 and 400), Pareto (shapes 1.5 and
1.01), lognormal (σ = 1, 0.05, 0.02) and two-point laws, at loads 0.3 to 0.999. For Pareto shape 1.01 and the
concentrated laws only the balanced state V(x, 0) is regression-tested; for Pareto 1.01 some states with larger
imbalance raise an error rather than return a value. The code rejects terminal cutoffs beyond floating-point
range (for example Pareto shape 1.001 at load 3/4 or above). The theorems cover every nondegenerate mean-one
law; the numerical domain is narrower. The exact finite-support solver has no such limit.

## Assurance boundary

* Proofs are written in the paper. No proof assistant was used.
* Exact sections use rational arithmetic only. Floating-point sections are supporting evidence.
* The release replay of `verify_all.py` was byte-identical to `results/` on the release host
  ([REPLAY_RECEIPT.md](REPLAY_RECEIPT.md)). That shows the outputs come from the shipped code; it does not show
  that the code matches the paper's definitions.
* Internal AI-assisted review and an AI-assisted adversarial audit found one major software defect (a heavy-tail
  quadrature failure) and two wording points. All three were fixed. A verification re-review found no open
  mathematical issue. A second audit of the revision found no counterexample to the main theorems and three
  local corrections (a closed-loop selection claim, the uninformative-estimate controller, a certificate
  justification), all fixed
  ([REVIEW_SUMMARY.md](REVIEW_SUMMARY.md)). No external peer review or independent reproduction has taken place.
* The simulation is numerical evidence. Some tuned parameters lie at the edge of their grid.
* The paper's quotations use arXiv v1; the publisher's DOI page returned HTTP 403 during revision. A public copy
  of the published issue, read in review, prints the same Proposition 3 and most-work-left definition, and the
  paper says so (Section 8; [SOURCES.md](SOURCES.md)).
* The novelty statements rest on a bounded search ([RESEARCH_GATES.json](RESEARCH_GATES.json)). No priority
  claim is made.

## Release records

* [STATUS.md](STATUS.md): what is proved, exact, heuristic or numerical, and what is open.
* [ASSURANCE.md](ASSURANCE.md): what has and has not been checked.
* [CLAIMS.json](CLAIMS.json): machine-readable claims. [AI_INDEX.md](AI_INDEX.md): a navigation page for agents.
* [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md): objections raised in internal AI-assisted review and how each was handled.
* [REPLAY_RECEIPT.md](REPLAY_RECEIPT.md), [ENVIRONMENT.txt](ENVIRONMENT.txt), [requirements.txt](requirements.txt),
  [.github/workflows/replay.yml](.github/workflows/replay.yml): replay record, environment and CI.
* [SOURCES.md](SOURCES.md), [CITATION_AUDIT.md](CITATION_AUDIT.md), [RESEARCH_GATES.json](RESEARCH_GATES.json):
  sources, citation checks and the bounded novelty search.
* [PROVENANCE.md](PROVENANCE.md), [LICENSES.md](LICENSES.md), [PUBLIC_DOMAIN.md](PUBLIC_DOMAIN.md),
  [LICENSE](LICENSE), [LICENSE-TEXT](LICENSE-TEXT), [LICENSE-CODE](LICENSE-CODE): provenance and licences.
* `SHA256SUMS`: hashes of every file.

## Licences

The text, figures, results and documentation are dedicated to the public domain under CC0 1.0
([LICENSE-TEXT](LICENSE-TEXT)). The code (`code/`, `tools/`, `negative_controls.py`, the CI workflow) is under
the MIT licence ([LICENSE-CODE](LICENSE-CODE)). Short quotations of the source's conjecture keep their own terms.

## Citation

Anonymous (2026). *Exact optimal dispatching to two fluid queues: closed form, heavy traffic and stochastic
evidence* (Version 1.0.0-candidate) [Unrefereed research candidate]. Evidence Press.
https://doi.org/10.5281/zenodo.23586955

Machine-readable metadata: [CITATION.cff](CITATION.cff) and [.zenodo.json](.zenodo.json). Scholarly creator:
Anonymous. Ian Pitchford maintains the repository and publishes it; that role is not authorship.
