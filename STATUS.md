# Status

Version: 1.0.0-candidate (23 October 2026). DOI: [10.5281/zenodo.23586955](https://doi.org/10.5281/zenodo.23586955) (concept DOI [10.5281/zenodo.23586954](https://doi.org/10.5281/zenodo.23586954)). Scholarly creator: Anonymous.

**Unrefereed research candidate.** No journal and no named human specialist has reviewed this manuscript. It was checked by internal AI-assisted review in five roles and by an AI-assisted adversarial audit by a different model; the manuscript was then revised, a verification re-review traced the fixes, and a second AI-assisted adversarial audit of the revision led to a final round of local corrections (see [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md)). That is not peer review, it is not independent reproduction, and it is not formal verification.

**Object.** The two-server fluid model of size-aware dispatching of Xie, Hyytiä and Righter, *Size-aware dispatching to fluid queues*, ACM SIGMETRICS Perform. Eval. Rev. 53(4) (2026) 42–48, doi:[10.1145/3797823.3797843](https://doi.org/10.1145/3797823.3797843), preprint arXiv:[2509.21693v1](https://arxiv.org/abs/2509.21693v1) ("XHR"). Fluid of mean-one job sizes arrives at rate ρ < 1; two servers work at rate 1/2 each; a job that joins a queue holding work u waits 2u; the cost is the total waiting of arriving fluid while a backlog drains.

Section, theorem and table numbers below refer to [paper/paper.pdf](paper/paper.pdf).

## Proved in writing

Every proof is in the manuscript. Some steps are exact identities that the code also checks.

* **Theorem 3 (exact optimum), with Lemma 2.** For every nonnegative mean-one size law that is not a point mass, and every 0 < ρ < 1, the explicit function V of eq. (4.4) is the minimum cost over all admissible controls, idling ones included. The threshold policy π* attains it and reaches an axis in finite time.
* **Theorem 4 (the conjecture).** Along every optimal path the relative imbalance z = |u₁ − u₂|/(u₁ + u₂) is nondecreasing, and strictly increasing while both queues are positive and unequal; dz/dx < 0 almost everywhere there. An optimal path never returns to or dwells on the diagonal. This proves XHR's verbal conjecture as posed (sizes with a density) and extends it to all nondegenerate laws. XHR's symbolic form ŷ′ ≥ 0, read literally with ′ = d/dx, is false for every nondegenerate law; the paper reads it as a sign convention or slip (Section 1).
* **Theorem 5 (unique optimal path).** One optimal labelled workload path from unequal starts, two mirror images from equal positive starts, and an explicit formula, eq. (4.5). Remark 6: every closed-loop solution under π* is optimal; from a positive tie the closed-loop system has two solutions even when the diagonal action is fixed, so the tie-break alone does not select one.
* **Section 7 (deterministic sizes).** An exact value, eq. (7.1). Many optimal paths exist and some decrease the imbalance, so the conjecture cannot extend to this case. XHR's Proposition 5 (all size-blind work-conserving policies equally good) needs ρ ≥ 1/2.
* **Section 8 (relation to XHR).** The most-work-left value, eq. (8.1). XHR's printed Proposition 3 has an extra factor 2ρ in its axis term (exponential sizes, ρ = 3/4, start (1/2, 1/2): printed 1.19401, direct 1.10851; running example: 3/2 against 21/16). In the interior, no straight-to-origin segment and no balanced dwelling is optimal for nondegenerate laws; the optimal axis phase is itself a straight-to-origin path.
* **Theorem 10 (heavy traffic).** For 1/2 < ρ < 1 an explicit sandwich holds, and (1 − ρ)V_ρ → P̄x² uniformly, with P̄ < 1/2. For continuous laws P̄ = P(S ≥ m), m the work median; if m is an atom, P̄ splits it (P̄ = P(S > m) + (1 − θ*)P(S = m)), so in the running example P̄ = 1/3 although P(S ≥ 3/2) = 1/2. Most-work-left has the same limit. The ratio 2P̄ equals the ratio of the heavy-traffic constants of CARD and least-work-left in Xie, Grosof and Scully (POMACS 8(1) 2024).
* **Theorem 11 (finite-support controller).** For K-point laws the value is a quadratic form on each of at most K + 1 sectors, with rational coefficients from one O(K) backward pass.
* **Proposition 12 and Corollary 13.** An envelope formula and convex-order monotonicity (a direct proof of XHR's Proposition 4); certified two-sided bounds, eq. (10.3), and a bin policy whose regret is at most the bracket width.
* **Theorem 14 (Wasserstein stability).** |V_X − V_Y| ≤ C_ρ x² W₁(X, Y). The constant is qualitative: it exceeds the true gap by factors 5.4–16.4 in the paper's example.
* **Proposition 15 (noisy size estimates).** Routing on an estimate Ŝ is optimal-equivalent to routing on the law of S̃ = E[S | Ŝ]; the loss is at most 2C_ρ x² E|S − Ŝ|. If S̃ is nondegenerate the rule is π* for S̃; if S̃ ≡ 1 (an uninformative estimate) the deterministic controller of Section 7 is used.

## Exact computation, for the stated finite cases

* The running example (sizes 1/2, 3/2; ρ = 3/4; start (1/2, 1/2)): optimal cost 33/28, switch at z = 3/13, axis fraction θ = 5/9, phase costs 45/196 + 33/49 + 27/98, obtained by integrating the workload segments directly, without quadrature.
* Finite-support Hamiltonian certificate for 16 law–load cases: 544 nonnegative allocation-vertex evaluations, 86 exact zero residuals at the optimal allocation, 19 adjacent value-and-gradient matches.
* Certified brackets for the uniform law on [0, 2] at ρ = 3/4 (4, 16 and 64 bins), exact rationals rounded outwards.
* Exact rational enclosures for Pareto shape 1.5 (Table 5; width 7.0×10⁻⁴ at 1024 cells; a 232-atom bin policy with regret at most 3.9×10⁻⁴) and Pareto shape 1.01 (0.401013 < V(1,0) < 0.402732). The second is a regression test for the floating-point code.
* Deterministic-size costs at ρ = 1/4 (1/6 and 3/16) and the decreasing-imbalance example.
* sympy checks of the gradient identity dV = r(x − k)dx − (y/h)dy and the sector formulas.

## Heuristic only

* The passage from the fluid heavy-traffic constant to the stochastic queue (Section 9, "Reconciliation"). It uses the correspondence E W = E[v(X, 0)] that XHR use, and the CARD constants assume E S² < ∞ (Xie, Grosof and Scully, Section 2.1); the paper does not prove the link.
* Section 3 (how the formula is found) is a heuristic derivation; the proofs begin in Section 5.

## Numerical evidence only

* The six-law quadrature table (Table 3) and the heavy-traffic table (Table 4); the Wasserstein looseness factors.
* The independent dynamic-programming check (Section 10.1): it does not use the value formula, and agrees with it to relative error at most 3.1×10⁻⁵ after Richardson extrapolation.
* **The stochastic simulation (Section 11, Tables 6–7).** Poisson arrivals; exponential, two-point, hyperexponential (SCV 10) and bounded Pareto sizes; loads 0.5, 0.75, 0.9; 20 replications of 10⁶ arrivals; common random numbers. The direct fluid rule beats JSW for the two highly variable laws (ratios 0.31–0.60) but is far worse for exponential and two-point sizes at ρ ≥ 0.75. The stabilised rule FLUID-S is best or tied in six of twelve cells. Tuned Dice is best in five. **No policy dominates in every cell.** Some tuned parameters lie at the edge of their grid.

## Open

More than two servers; heterogeneous rates; a proof that a stabilised fluid rule is stable or asymptotically optimal in the stochastic system; sharp stability constants; whether V is a viscosity solution of the reflected Hamilton–Jacobi–Bellman equation in the classical sense (not needed here).

## Not covered

The stochastic queue (no optimality claim); sizes known only approximately with a miscalibrated rule (only simulated); unknown size law or load; fairness across size classes. The floating-point code's tested domain is narrower than the theorem domain (Section 12). No proof assistant was used. The paper's quotations and its Proposition 3 comparison use arXiv v1, because the publisher's DOI page returned HTTP 403 during revision. A public copy of the published issue, read during review, has the same conjecture wording and the same Proposition 3 formula (see [SOURCES.md](SOURCES.md)). For Pareto shape 1.01 the quadrature code is regression-tested at the balanced state only; some states with larger imbalance raise an error. Novelty statements rest on the bounded searches in [RESEARCH_GATES.json](RESEARCH_GATES.json); they do not establish priority.
