# Replay receipt

## Commands

From the root of a fresh extraction, using Python 3.13 with the pins in [requirements.txt](requirements.txt):

```sh
sha256sum -c SHA256SUMS                                     # macOS: shasum -a 256 -c SHA256SUMS
python -B -O -I code/verify_all.py OUT                      # every computational check, about 1 minute
python -B -I tools/compare_results.py results OUT --bytes   # byte identity (release host)
python -B -I tools/compare_results.py results OUT           # exact fields exactly, floats to relative 1e-6
python -B -O negative_controls.py                           # semantic negative controls
python -B -I code/simulate.py OUT --quick                   # simulation smoke test (not compared)
```

`verify_all.py` and `simulate.py` write only into `OUT`. `negative_controls.py` works only in temporary directories.

## Runs before freezing

| Run | Command | Result |
|---|---|---|
| Revision and final-pass records, 23 October 2026 | `verify_all.py` with `-B -O -I` and `-B -I` | Byte-identical to each other and to `results/`, according to the revision record; the final pass records two further byte-identical runs, with only `results/pareto_101_regression.json` changed. The editor's record says the full simulation was replayed byte-identically, and `simulate.py` was unchanged in the final pass. Two `simulate.py --quick` runs (one with `-O` and a different process count) identical. |
| Verification re-review, 23 October 2026, on a copy | `verify_all.py` with `-B -I` and `-B -O -I` | All 12 sections PASS; both trees byte-identical to `results/` (13 files); no `__pycache__` written. `simulate.py --quick` ran cleanly. |
| Release preparation, final source (after the final pass), 2026-10-23T06:51Z, CPython 3.13.5, macOS 27.0.1 arm64 | `python -B -O -I code/verify_all.py OUT` on the read-only final snapshot (about 44 s) | Exit 0. All 12 sections PASS. All 13 JSON files byte-identical to `results/` (`tools/compare_results.py --bytes`). |
| Negative controls on the assembled final tree | `python -B -O negative_controls.py` (about 52 s) | ALL NEGATIVE CONTROLS BEHAVED: 32 checks (same set as below). |
| Release preparation, pre-freeze replay of the source before the final pass, 2026-10-23T05:23Z, CPython 3.13.5, macOS 27.0.1 arm64, packages as in [ENVIRONMENT.txt](ENVIRONMENT.txt) | `python -B -O -I code/verify_all.py OUT` run on the read-only final package from a new scratch directory (about 67 s wall time) | Exit 0. All 12 sections PASS. All 13 JSON files byte-identical to `results/` (checked with `cmp` and with `tools/compare_results.py --bytes`). |
| Same (pre-final-pass source), assertions enabled, 2026-10-23T05:36Z | `python -B -I code/verify_all.py OUT` | Exit 0. All 13 files byte-identical to `results/`. |
| Negative controls, release preparation (pre-final-pass source) | `python -B -O negative_controls.py` (about 1 minute) | ALL NEGATIVE CONTROLS BEHAVED: 32 checks. Two baselines passed (full replay with comparison; SHA256SUMS). Rejected: five tampered result values and a missing section; six inadmissible inputs; fourteen code or claim mutations; three tampered files or hash entries. A 1e-9 float change was accepted, as it should be. |
| Simulation smoke test, release preparation | `python -B -I code/simulate.py OUT --quick --processes 2` (about 11 s) | Exit 0; `simulation_quick.json` written (116 cells). Not compared with `results/simulation.json`, which comes from the full run. |

The full simulation (`code/simulate.py OUT`, about 50 CPU-minutes) is outside this receipt's runs. Whether it was replayed for this release, and its outcome, is recorded by the publisher with the frozen-archive replay.

## Frozen-archive replay

This file cannot record a hash of the archive that contains it. The final replay from a fresh extraction of the frozen archive (`-B -O`, comparison with `results/`, negative controls) is recorded by the publisher in its own gate record. The repository's CI workflow repeats the SHA-256 check, the replay with comparison, the negative controls and the simulation smoke test on GitHub for the tagged commit.

## What this establishes

Byte-identical replay shows that the shipped outputs are exactly what the shipped programs produce on the stated environment. It does not show that the programs implement the manuscript's definitions correctly. That rests on the written proofs, the independent dynamic-programming check, the negative controls, and the independent recomputations in the internal reviews. None of these runs is an independent reproduction by an unaffiliated party. On other platforms the 8-significant-digit floating-point fields may differ in the last digit; the comparator then applies a relative tolerance of 1e-6 to floats and still requires every exact field to match exactly.
