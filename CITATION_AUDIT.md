# Citation audit

All checks were made inside the Evidence Press workflow by AI agents. They are bibliographic checks, not a judgement of the cited works.

## Identifier resolution

**Date:** 23 October 2026 (release preparation). **Method:** each DOI was read from the manuscript's bibliography (`paper/paper.tex`) and looked up read-only. Crossref REST API `api.crossref.org/works/{doi}` for 23 DOIs; the one DataCite DOI (LIPIcs) through the doi.org handle API and the DataCite REST API. The returned title, year and first author were compared with the bibliography entry.

| Key | DOI | Registry | Result |
|---|---|---|---|
| ABR1995 | 10.1007/978-1-4757-2418-9_11 | Crossref | Avram et al., *Fluid models of sequencing problems in open queueing networks…*, 1995. Match. |
| AKLL2018 | 10.1017/jpr.2018.59 | Crossref | Adan et al., *Optimal routeing in two-queue polling systems*, J. Appl. Probab., 2018. Match. |
| BCD1997 | 10.1007/978-0-8176-4755-1 | Crossref | Bardi & Capuzzo-Dolcetta, 1997. Match. |
| Bauerle2000 | 10.1214/aoap/1019487606 | Crossref | Bäuerle, Ann. Appl. Probab., 2000. Match. |
| BMDP2002 | 10.1016/S0005-1098(01)00174-1 | Crossref | Bemporad et al., Automatica, 2002. Match. |
| FMR2005 | 10.1016/j.peva.2005.07.031 | Crossref | Feng, Misra & Rubenstein, Perform. Eval., 2005. Match. |
| FS2006 | 10.1007/0-387-31071-1 | Crossref | *Controlled Markov Processes and Viscosity Solutions*, 2006. Match (Crossref lists no author for the book record). |
| HB2013 | 10.1017/CBO9781139226424 | Crossref | Harchol-Balter, 2013. Match. |
| HCM1999 | 10.1006/jpdc.1999.1577 | Crossref | Harchol-Balter, Crovella & Murta, 1999. Match. |
| HPA2012 | 10.1016/j.ejor.2011.09.029 | Crossref | Hyytiä, Penttinen & Aalto, EJOR, 2012. Match. |
| HR2022 | 10.1109/ITNAC55475.2022.9998339 | Crossref | Hyytiä & Righter, *On sequential dispatching policies*, 2022. Match. |
| HR2024 | 10.1016/j.peva.2024.102396 | Crossref | Hyytiä & Righter, Perform. Eval., 2024. Match. |
| Maglaras2000 | 10.1214/aoap/1019487513 | Crossref | Maglaras, Ann. Appl. Probab., 2000. Match. |
| Meyn2008 | 10.1017/CBO9780511804410 | Crossref | Meyn, *Control Techniques for Complex Networks*. Crossref's issued year is 2007 (online); the bibliography gives the 2008 print year. |
| MV2022 | 10.1145/3528087 | Crossref | Mitzenmacher & Vassilvitskii, Commun. ACM, 2022. Match. |
| SGM2022 | 10.4230/LIPIcs.ITCS.2022.114 | DataCite | Scully, Grosof & Mitzenmacher, *Uniform bounds for scheduling with job size estimates*, 2022; resolves to drops.dagstuhl.de. Match. |
| SS2007 | 10.1007/978-0-387-34675-5 | Crossref | *Stochastic Orders*, 2007. Match. |
| Soner1986 | 10.1137/0324032 | Crossref | Soner, SIAM J. Control Optim., 1986. Match. |
| vEHvL2022 | 10.1287/ijoc.2021.1130 | Crossref | van Eekelen et al., INFORMS J. Comput., 2022. Match. |
| Villani2009 | 10.1007/978-3-540-71050-9 | Crossref | Villani, *Optimal Transport*, 2009. Match. |
| Weiss2008 | 10.1007/s10107-008-0217-x | Crossref | Weiss, Math. Program., 2008. Match. |
| Winston1977 | 10.2307/3213271 | Crossref | Winston, *Optimality of the shortest line discipline*, 1977. Match. |
| XGS2024 | 10.1145/3639035 | Crossref | Xie, Grosof & Scully, *Heavy-traffic optimal size- and state-aware dispatching*, 2024. Match. |
| XHR2026 | 10.1145/3797823.3797843 | Crossref | Xie, Hyytiä & Righter, *Size-Aware Dispatching to Fluid Queues*, ACM SIGMETRICS PER 53(4), 42–48, issued 31 March 2026. Match. |

All 24 DOIs resolve, and every record matches the bibliography's title, year and authors, with the one year note above. The revision record states that the added references were checked against Crossref or doi.org during revision on 23 October 2026; this audit repeats that check independently of it. arXiv:2509.21693v1 resolves on arxiv.org (title and v1 date 25 September 2025 confirmed by the arXiv API on 23 October 2026).

## Source-to-claim checks

* The conjecture is quoted from XHR arXiv v1, Section 5 (symbolic form) and Section 6.1 (verbal form). The domain review asked for both quotations and the sign reconciliation; the paper's Section 1 now has both.
* Model normalisation (rate-1/2 servers, mean-one sizes, cost 2Σaᵢuᵢ) was checked against XHR Section 3 by the domain review and the adversarial audit. XHR's random-split formula (Remark 1) gives 3/2 in the paper's normalisation, which confirms the constants are aligned.
* XHR Proposition 3: the paper compares with the arXiv v1 formula and states that the published version prints the same one. The verification re-review (23 October) found the same formula and most-work-left definition in a public copy of the published PER issue, and the 19 October novelty report recorded the same discrepancy (see [SOURCES.md](SOURCES.md)).
* The verification re-review separately resolved all 24 DOIs through Crossref and DataCite on 23 October 2026 and spot-checked the claims attributed to Winston, Feng–Misra–Rubenstein, Hyytiä–Righter (Dice), Xie–Grosof–Scully (constants K_CARD = 2P(S ≥ m) and K_LWL = 1), Weiss, Soner and van Eekelen et al.
* Xie–Grosof–Scully: the CARD heavy-traffic constant K = 2P(S ≥ m) is used as stated there; the reconciliation in Section 9 is labelled heuristic for the stochastic link.

## Not done

There was no systematic citation export from MathSciNet, zbMATH, Scopus or Web of Science, no exhaustive search in languages other than English, and no enquiry to the source authors.
