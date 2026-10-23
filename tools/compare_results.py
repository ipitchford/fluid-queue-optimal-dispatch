#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Anonymous
"""Compare a fresh verify_all.py output directory with the shipped results/.

Usage:
    python -B -I tools/compare_results.py results OUT_DIR [--rel 1e-6] [--bytes]

Rules
  * Every JSON file written by code/verify_all.py must be present in both
    directories (results/simulation*.json are not produced by verify_all.py
    and are ignored).
  * Strings, integers, booleans and null must match exactly. This covers every
    exact field: rationals are written as strings, and outward-rounded
    decimals of exact rationals are strings too.
  * Dictionaries must have identical keys and lists identical lengths.
  * Floating-point fields (8 significant digits in the shipped files) must
    agree to a relative tolerance (default 1e-6) plus an absolute floor of
    1e-12. On the release host the files are byte-identical; the tolerance
    exists only for other platforms and library builds.
  * With --bytes every file must be byte-identical instead.

Exit status 0 if everything matches, 1 otherwise. Read-only.
"""
import argparse
import json
import math
import sys
from pathlib import Path

VERIFY_FILES = (
    "certified_binning.json", "deterministic_checks.json", "dp_cross_check.json",
    "exact_finite_support.json", "heavy_traffic.json", "pareto_101_regression.json",
    "pareto_certificate.json", "quadrature_checks.json", "source_comparison.json",
    "summary.json", "symbolic_identities.json", "two_point_certificate.json",
    "wasserstein_looseness.json",
)


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def compare_values(a, b, path, rel, out):
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            out.append(f"{path}: keys differ: {sorted(set(a) ^ set(b))}")
            return
        for k in sorted(a):
            compare_values(a[k], b[k], f"{path}.{k}", rel, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: list lengths {len(a)} != {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            compare_values(x, y, f"{path}[{i}]", rel, out)
    elif _is_num(a) and _is_num(b) and (isinstance(a, float) or isinstance(b, float)):
        fa, fb = float(a), float(b)
        if not (math.isfinite(fa) and math.isfinite(fb)):
            if not (fa == fb):
                out.append(f"{path}: {a!r} != {b!r}")
        elif abs(fa - fb) > rel * max(abs(fa), abs(fb)) + 1e-12:
            out.append(f"{path}: float {a!r} vs {b!r} (rel tol {rel})")
    else:
        if type(a) is not type(b) or a != b:
            out.append(f"{path}: exact field {a!r} != {b!r}")


def compare_dirs(ref_dir, new_dir, rel=1e-6, byte_identical=False):
    """Return a list of human-readable mismatch descriptions (empty if equal)."""
    ref_dir, new_dir = Path(ref_dir), Path(new_dir)
    problems = []
    for name in VERIFY_FILES:
        ref, new = ref_dir / name, new_dir / name
        if not ref.is_file() or not new.is_file():
            problems.append(f"{name}: missing in {'reference' if not ref.is_file() else 'new output'}")
            continue
        if byte_identical:
            if ref.read_bytes() != new.read_bytes():
                problems.append(f"{name}: bytes differ")
            continue
        try:
            a, b = json.loads(ref.read_text()), json.loads(new.read_text())
        except json.JSONDecodeError as exc:
            problems.append(f"{name}: invalid JSON ({exc})")
            continue
        compare_values(a, b, name, rel, problems)
    extra = sorted(p.name for p in new_dir.glob("*.json") if p.name not in VERIFY_FILES)
    if extra:
        problems.append(f"unexpected output files: {extra}")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("reference", type=Path)
    ap.add_argument("new", type=Path)
    ap.add_argument("--rel", type=float, default=1e-6)
    ap.add_argument("--bytes", action="store_true", help="require byte-identical files")
    args = ap.parse_args(argv)
    problems = compare_dirs(args.reference, args.new, args.rel, args.bytes)
    mode = "byte-identical" if args.bytes else f"exact fields exact, floats rel {args.rel:g}"
    if problems:
        print(f"MISMATCH ({mode}): {len(problems)} problem(s)")
        for p in problems[:50]:
            print("  " + p)
        return 1
    print(f"MATCH ({mode}): {len(VERIFY_FILES)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
