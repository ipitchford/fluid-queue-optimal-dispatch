# Corrections

Errata to release 1.0.0-candidate (DOI 10.5281/zenodo.23586955). The archived PDF, the manuscript source on this
branch, the checksum manifests, the Zenodo deposit and the tag `v1.0.0-candidate` are unchanged.

## 2026-10-26 — §10.4, illustrative certificate size for Pareto shape 1.5

Source location: `paper/paper.tex` line 473.

Corrected an illustrative estimate in §10.4. The archived text says that for a Pareto law of shape 1.5 at $\rho=3/4$ a 1% certificate needs $R\approx4\times10^5$ and mesh $\Delta\approx2\times10^{-3}$, “about $10^9$ bins”. With the paper's own bound $V_{S^-}-C_\rho x^2(\Delta+2\mathbb E[S;S>R])$, $C_\rho=9/2$, those values give a gap of about 2% of $V\approx0.854$ from about $R/\Delta=2\times10^8$ bins. A 1% certificate needs, for example, $R\approx2\times10^6$ and $\Delta\approx9\times10^{-4}$, about $2\times10^9$ bins.

The conclusion that this route is impractical is unchanged, and no theorem, certificate or table uses the estimate. The archived PDF, version DOI and repository tag are unchanged; the erratum is recorded here and at <https://evidencepress.org/releases/fluid-queue-optimal-dispatch/>.
