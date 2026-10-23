#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Anonymous
"""Semantic negative controls for the fluid-queue dispatching package.

Run from the repository root:

    python -B -O negative_controls.py

First an unmodified baseline must pass: a full run of code/verify_all.py on a
temporary copy of the code, compared with results/ by tools/compare_results.py,
and the SHA256SUMS check. Then each control below injects one plausible error
(a tampered result, a code bug, a flipped claim, an inadmissible input or a
tampered file) and must be REJECTED. The script exits nonzero if the baseline
fails or if any control is accepted.

The repository is never modified: all work happens in temporary copies.
Every check is explicit, so python -O disables nothing. Runtime is about two to
three minutes, dominated by the baseline and by two quadrature sections.
"""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CODE = ROOT / "code"
RESULTS = ROOT / "results"

# Exception classes that count as a deliberate rejection by the package's own
# checks. CheckFailed comes from verify_all.check; ArithmeticError and
# ValueError from the explicit _require/argument checks of the solvers.
REJECTIONS = {"CheckFailed", "ArithmeticError", "ValueError", "ZeroDivisionError"}


def load_comparator():
    spec = importlib.util.spec_from_file_location("compare_results", ROOT / "tools" / "compare_results.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def copy_code(dest):
    shutil.copytree(CODE, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return dest


def run_python(snippet, timeout=600):
    """Run a snippet in a fresh isolated interpreter; return (rc, exception name, tail)."""
    proc = subprocess.run([sys.executable, "-B", "-O", "-I", "-c", snippet],
                          capture_output=True, text=True, timeout=timeout)
    exc = ""
    for line in reversed(proc.stderr.strip().splitlines()):
        head = line.split(":", 1)[0].strip()
        if head and " " not in head and (head.endswith("Error") or head.endswith("Failed") or "." in head):
            exc = head.rsplit(".", 1)[-1]
            break
    tail = (proc.stderr.strip().splitlines() or [""])[-1][:160]
    return proc.returncode, exc, tail


def run_section(code_dir, section):
    snippet = (f"import sys; sys.path.insert(0, {str(code_dir)!r}); "
               f"import verify_all; verify_all.{section}()")
    return run_python(snippet)


def sha_problems(sums_text, base, overrides=None):
    overrides = overrides or {}
    bad = []
    for line in sums_text.splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        name = name.lstrip("*")
        data = overrides[name] if name in overrides else (base / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            bad.append(name)
    return bad


RECORD = []


def record(name, ok, detail):
    RECORD.append((name, ok, detail))
    print(f"[{'ok' if ok else 'FAILED'}] {name}: {detail}", flush=True)


# Code mutations: (label, file, old text, new text, verify_all section).
MUTATIONS = [
    ("fluid_exact: wrong sign in the affine form of D(h)", "fluid_exact.py",
     "affine[a] = (2*cum_f-1, 1-2*cum_m)", "affine[a] = (2*cum_f-1, 1+2*cum_m)", "exact_finite_support"),
    ("fluid_exact: wrong terminal cutoff H (work target 1/(3 rho))", "fluid_exact.py",
     "target = 1/(2*rho)", "target = 1/(3*rho)", "exact_finite_support"),
    ("fluid_exact: wrong r = rho/(1+rho)", "fluid_exact.py",
     "self.rho, self.r = rho, rho/(1-rho)", "self.rho, self.r = rho, rho/(1+rho)", "exact_finite_support"),
    ("fluid_exact: wrong axis job fraction F_H", "fluid_exact.py",
     "self.FH = cum_f+self.theta*p", "self.FH = cum_f+self.theta*p/2", "exact_finite_support"),
    ("verify_all: running-example cost integral uses duration^2/3", "verify_all.py",
     "(wi - F(1, 2)) * duration ** 2 / 2)", "(wi - F(1, 2)) * duration ** 2 / 3)", "two_point_certificate"),
    ("verify_all: claimed running-example optimum 34/28 instead of 33/28", "verify_all.py",
     'check(opt == F(33, 28), "optimum 33/28")', 'check(opt == F(34, 28), "optimum 33/28")',
     "two_point_certificate"),
    ("verify_all: wrong load (rho = 4/5) in the running example", "verify_all.py",
     '"""Direct physical integration of the running example; no quadrature."""\n    rho = F(3, 4)',
     '"""Direct physical integration of the running example; no quadrature."""\n    rho = F(4, 5)',
     "two_point_certificate"),
    ("verify_all: flipped conjecture check (claim imbalance decreasing along optimal paths)", "verify_all.py",
     "np.all(np.diff(ratios) >= -2e-9)", "np.all(np.diff(ratios) <= 2e-9)", "quadrature_checks"),
    ("verify_all: flipped deterministic counterexample (claim imbalance increases)", "verify_all.py",
     'check(zdot < 0, "imbalance decreases")', 'check(zdot > 0, "imbalance decreases")',
     "deterministic_checks"),
    ("fluid_quadrature: wrong D(h) for exponential sizes", "fluid_quadrature.py",
     "return h-1.0+2.0*exp(-h)", "return h-1.0+2.0*exp(-1.05*h)", "quadrature_checks"),
    ("fluid_quadrature: log-variable integration disabled (the audited heavy-tail defect)", "fluid_quadrature.py",
     "SCALE = 4.0", "SCALE = 1e300", "pareto_101_regression"),
    ("dp_check: DP value biased by 1% (independent cross-check must notice)", "dp_check.py",
     "return np.linspace(0.0, 1.0, base_pts), 2 * v3 - v2, v3",
     "return np.linspace(0.0, 1.0, base_pts), 1.01 * (2 * v3 - v2), v3", "dp_cross_check"),
    ("verify_all: DP agreement tolerance tightened below what the DP achieves", "verify_all.py",
     "check(rel_ext < 2e-3,", "check(rel_ext < 1e-7,", "dp_cross_check"),
    ("verify_all: wrong sign in the symbolic sector formula (F7)", "verify_all.py",
     "F7 = (r * (om - be) * xs ** 2 - 2 * xs * ys", "F7 = (r * (om - be) * xs ** 2 + 2 * xs * ys",
     "symbolic_identities"),
]

# Inadmissible inputs that the solvers must reject (exception name expected).
DOMAIN_CASES = [
    ("deterministic (degenerate) size law given to the exact solver",
     "from fluid_exact import FiniteFluidSolver as S; from fractions import Fraction as F; "
     "S([F(1)], [F(1)], F(3, 4))"),
    ("size law with mean 5/4 instead of 1",
     "from fluid_exact import FiniteFluidSolver as S; from fractions import Fraction as F; "
     "S([F(1, 2), F(2)], [F(1, 2), F(1, 2)], F(3, 4))"),
    ("probabilities summing to 9/10",
     "from fluid_exact import FiniteFluidSolver as S; from fractions import Fraction as F; "
     "S([F(1, 2), F(3, 2)], [F(1, 2), F(2, 5)], F(3, 4))"),
    ("load rho = 1 (exact solver)",
     "from fluid_exact import FiniteFluidSolver as S; from fractions import Fraction as F; "
     "S([F(1, 2), F(3, 2)], [F(1, 2), F(1, 2)], F(1))"),
    ("load rho = 1.0 (quadrature solver)",
     "from fluid_quadrature import Law, FluidSolution; FluidSolution(Law('exponential'), 1.0)"),
    ("Pareto shape 1.001 at rho = 0.9 (terminal cutoff beyond floating-point range)",
     "from fluid_quadrature import Law, FluidSolution; FluidSolution(Law('pareto', 1.001), 0.9)"),
]


def main():
    t0 = time.time()
    for needed in (CODE / "verify_all.py", RESULTS, ROOT / "tools" / "compare_results.py"):
        if not needed.exists():
            print(f"missing {needed}; run from the repository root")
            return 2
    cmp = load_comparator()
    tmp = Path(tempfile.mkdtemp(prefix="fq-negctl-"))
    try:
        # ---------------- baseline 1: full replay + comparison
        clean = copy_code(tmp / "clean_code")
        out = tmp / "baseline_out"
        proc = subprocess.run([sys.executable, "-B", "-O", "-I", str(clean / "verify_all.py"), str(out)],
                              capture_output=True, text=True, timeout=1200)
        problems = cmp.compare_dirs(RESULTS, out) if proc.returncode == 0 else ["verify_all failed"]
        if proc.returncode != 0 or problems:
            record("BASELINE verify_all + comparison", False, (proc.stderr[-300:] or "; ".join(problems[:5])))
            return 1
        record("BASELINE verify_all + comparison", True, "all 12 sections PASS; 13 files match results/")

        # ---------------- baseline 2: SHA256SUMS
        sums_path = ROOT / "SHA256SUMS"
        if not sums_path.is_file():
            record("BASELINE SHA256SUMS", False, "SHA256SUMS missing at repository root")
            return 1
        sums = sums_path.read_text()
        bad = sha_problems(sums, ROOT)
        if bad:
            record("BASELINE SHA256SUMS", False, f"mismatched: {bad[:5]}")
            return 1
        record("BASELINE SHA256SUMS", True, f"{len(sums.splitlines())} entries verified")

        # ---------------- comparator controls (tampered outputs)
        def tampered(label, fname, mutate, expect_reject=True):
            d = tmp / f"tamper_{len(RECORD)}"
            shutil.copytree(out, d)
            data = json.loads((d / fname).read_text())
            mutate(data)
            (d / fname).write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
            probs = cmp.compare_dirs(RESULTS, d)
            rejected = bool(probs)
            ok = rejected if expect_reject else not rejected
            verdict = ("rejected: " + probs[0]) if rejected else "accepted"
            record(label, ok, verdict[:160])

        tampered("tampered running-example optimum 33/28 -> 34/28 in two_point_certificate.json",
                 "two_point_certificate.json", lambda d: d.__setitem__("optimal", "34/28"))
        tampered("tampered exact value V(1,0) 33/28 -> 33/29 in exact_finite_support.json",
                 "exact_finite_support.json",
                 lambda d: d["two_point_rho_3_4"].__setitem__("value_at_x1_y0", "33/29"))
        tampered("tampered switching ratio 3/13 -> 3/14", "exact_finite_support.json",
                 lambda d: d["two_point_rho_3_4"].__setitem__("switch_z", "3/14"))
        tampered("tampered Pareto 1.01 enclosure lower bound", "pareto_101_regression.json",
                 lambda d: d.__setitem__("enclosure_lower_rounded_down", "0.401014000000"))

        def bump(d):
            row = d["continuous_laws"][0]
            row["limit_constant_P_S_ge_m"] *= 1.0001
        tampered("heavy-traffic constant perturbed by 1e-4 relative (beyond float tolerance)",
                 "heavy_traffic.json", bump)

        def tiny(d):
            row = d["continuous_laws"][0]
            row["limit_constant_P_S_ge_m"] *= 1 + 1e-9
        tampered("POSITIVE CONTROL: float perturbed by 1e-9 relative is accepted",
                 "heavy_traffic.json", tiny, expect_reject=False)
        tampered("summary.json reports a section missing", "summary.json",
                 lambda d: d.pop("dp_cross_check"))

        # ---------------- inadmissible inputs
        for label, snippet in DOMAIN_CASES:
            rc, exc, tail = run_python(f"import sys; sys.path.insert(0, {str(clean)!r}); " + snippet)
            ok = rc != 0 and exc == "ValueError"
            record("input rejected: " + label, ok, f"rc={rc} {tail}")

        # ---------------- code mutations
        for i, (label, fname, old, new, section) in enumerate(MUTATIONS):
            mdir = copy_code(tmp / f"mut_{i}")
            text = (mdir / fname).read_text()
            if text.count(old) != 1:
                record("mutation: " + label, False, f"anchor found {text.count(old)} times in {fname}")
                continue
            (mdir / fname).write_text(text.replace(old, new))
            rc, exc, tail = run_section(mdir, section)
            ok = rc != 0 and exc in REJECTIONS
            record("mutation: " + label, ok, f"{section}: rc={rc} {tail}")

        # ---------------- tampered files against SHA256SUMS
        names = [ln.split(None, 1)[1].lstrip("*") for ln in sums.splitlines() if ln.strip()]
        target = "code/fluid_exact.py" if "code/fluid_exact.py" in names else names[0]
        mod = (ROOT / target).read_bytes() + b"# tampered\n"
        bad = sha_problems(sums, ROOT, {target: mod})
        record(f"tampered file {target} detected by SHA256SUMS", bad == [target], f"mismatched: {bad}")
        res = "results/two_point_certificate.json"
        if res in names:
            data = (ROOT / res).read_bytes().replace(b'"33/28"', b'"34/28"', 1)
            bad = sha_problems(sums, ROOT, {res: data})
            record(f"tampered {res} detected by SHA256SUMS", bad == [res], f"mismatched: {bad}")
        lines = sums.splitlines()
        first = lines[0]
        flipped = ("0" if first[0] != "0" else "1") + first[1:]
        bad = sha_problems("\n".join([flipped] + lines[1:]), ROOT)
        record("tampered SHA256SUMS entry (one hex digit) detected", len(bad) == 1, f"mismatched: {bad}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [n for n, ok, _ in RECORD if not ok]
    print(f"\n{len(RECORD)} checks, {len(failed)} failed, {time.time() - t0:.0f} s")
    if failed:
        print("NEGATIVE CONTROLS FAILED: " + "; ".join(failed))
        return 1
    print("ALL NEGATIVE CONTROLS BEHAVED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
