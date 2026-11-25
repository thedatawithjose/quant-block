#!/usr/bin/env python3
"""vibe-guard verifier calibration harness.

Runs a reviewer against labelled fixtures and measures whether it can be
trusted as an independent verifier:

  detection_rate       = defect fixtures the reviewer FAILs / defect fixtures
  false_positive_rate  = clean fixtures the reviewer FAILs  / clean fixtures

A fixture counts as FAILed when at least one criterion verdict is FAIL.
Calibration PASSES only if detection_rate >= --min-detection (0.9) AND
false_positive_rate <= --max-false-positive (0.1). Fail-closed: reviewer
errors, malformed output, or a missing defect/clean class fail calibration.

Fixture layout: criteria.md, artifact/, evidence/, label.json
  label.json = {"defect": true|false, "defect_type": "..."}

Reviewer protocol (--reviewer-cmd): the command is run with the fixture
directory appended as its last argument (env VG_REVIEWER_PROMPT points to
reviewer_prompt.md). It prints one JSON object per criterion
{criterion, verdict, reason, proof} as JSON lines or a single JSON array.

Default reviewer: a built-in deterministic MOCK (offline, no network).
Stdlib only. Exit: 0 calibration passed, 1 failed, 2 harness error.
"""

import argparse
import ast
import csv
import datetime
import json
import os
import re
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FIXTURES = os.path.join(HERE, "fixtures")
DEFAULT_REPORT = os.path.join(HERE, "calibration-report.json")
PROMPT_PATH = os.path.join(HERE, "reviewer_prompt.md")
VERDICTS = ("PASS", "FAIL")


class ReviewerError(Exception):
    """Reviewer crashed, timed out, or returned malformed output."""


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

def load_fixtures(root):
    fixtures = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        label_path = os.path.join(path, "label.json")
        if not os.path.isfile(label_path):
            continue
        with open(label_path, encoding="utf-8") as fh:
            label = json.load(fh)
        if not isinstance(label.get("defect"), bool):
            raise ValueError("%s: label.json needs boolean 'defect'" % name)
        fixtures.append({"name": name, "path": path, "defect": label["defect"],
                         "defect_type": label.get("defect_type", "")})
    return fixtures


def parse_criteria(fixture_dir):
    """Lines '- [C1] text (evidence: path) (must-contain: path :: text)'."""
    out = []
    with open(os.path.join(fixture_dir, "criteria.md"), encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^\s*-\s*\[(\w+)\]\s*(.*?)\s*$", line)
            if m:
                out.append({"id": m.group(1), "text": m.group(2)})
    return out


# --------------------------------------------------------------------------
# Built-in MOCK reviewer: deterministic, adversarial heuristics
# --------------------------------------------------------------------------

def _read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _py_files(directory, prefix=""):
    if not os.path.isdir(directory):
        return []
    return sorted(os.path.join(directory, f) for f in os.listdir(directory)
                  if f.endswith(".py") and f.startswith(prefix))


def _empty_tests(test_file):
    """Names of test functions that contain no assertion."""
    tree = ast.parse(_read(test_file))
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
            asserts = any(
                isinstance(n, ast.Assert)
                or (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr.startswith(("assert", "fail")))
                for n in ast.walk(node))
            if not asserts:
                bad.append(node.name)
    return bad


LOOKAHEAD = re.compile(r"shift\(\s*-\s*\d|\.iloc\[[^\]]*\+\s*\d|\[\s*i\s*\+\s*\d+\s*\]|\bfuture\b")


def mock_review_criterion(fixture_dir, crit):
    text, low = crit["text"], crit["text"].lower()

    def fail(reason, proof):
        return {"criterion": crit["id"], "verdict": "FAIL", "reason": reason, "proof": proof}

    ev = re.search(r"\(evidence:\s*([^)]+)\)", text)
    if not ev:
        return fail("Claim has no evidence reference.", "criteria.md: no '(evidence: ...)'")
    ev_rel = ev.group(1).strip()
    ev_path = os.path.join(fixture_dir, ev_rel)
    if not os.path.isfile(ev_path) or os.path.getsize(ev_path) == 0:
        return fail("Referenced evidence file is missing or empty.", ev_rel)

    mc = re.search(r"\(must-contain:\s*(.+?)\s*::\s*(.+?)\)", text)
    if mc:
        target = os.path.join(fixture_dir, mc.group(1).strip())
        needle = mc.group(2).strip().lower()
        if not os.path.isfile(target) or needle not in _read(target).lower():
            return fail("Criterion not met although claimed done.",
                        "%r not found in %s" % (needle, mc.group(1).strip()))

    art = os.path.join(fixture_dir, "artifact")
    if "test" in low:
        for tf in _py_files(art, "test"):
            bad = _empty_tests(tf)
            if bad:
                return fail("Tests assert nothing: %s." % ", ".join(bad),
                            "%s: no assert in %s" % (os.path.basename(tf), ", ".join(bad)))

    if "accuracy" in low or "metric" in low:
        rows_path = os.path.join(art, "results.csv")
        try:
            claimed = float(json.loads(_read(ev_path))["accuracy"])
            with open(rows_path, newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            actual = sum(r["pred"] == r["label"] for r in rows) / len(rows)
        except (OSError, ValueError, KeyError, ZeroDivisionError):
            return fail("Metric cannot be recomputed from the artifact.", "results.csv/metrics.json")
        if abs(claimed - actual) > 0.01:
            return fail("Claimed metric does not match recomputation.",
                        "claimed=%.3f recomputed=%.3f" % (claimed, actual))

    if "backtest" in low or "look-ahead" in low or "lookahead" in low:
        for pf in _py_files(art):
            for no, line in enumerate(_read(pf).splitlines(), 1):
                if LOOKAHEAD.search(line):
                    return fail("Look-ahead: future data used for a signal.",
                                "%s:%d: %s" % (os.path.basename(pf), no, line.strip()))

    return {"criterion": crit["id"], "verdict": "PASS",
            "reason": "Tried to falsify; no defect found.", "proof": ev_rel}


def mock_reviewer(fixture_dir):
    return [mock_review_criterion(fixture_dir, c) for c in parse_criteria(fixture_dir)]


# --------------------------------------------------------------------------
# External reviewer
# --------------------------------------------------------------------------

def parse_reviewer_output(stdout):
    stdout = stdout.strip()
    try:
        data = json.loads(stdout)
        items = data if isinstance(data, list) else [data]
    except ValueError:
        try:
            items = [json.loads(l) for l in stdout.splitlines() if l.strip()]
        except ValueError as exc:
            raise ReviewerError("output is not JSON: %s" % exc)
    if not items:
        raise ReviewerError("empty output")
    for it in items:
        if not isinstance(it, dict) or it.get("verdict") not in VERDICTS or "criterion" not in it:
            raise ReviewerError("invalid verdict object: %r" % (it,))
    return items


def external_reviewer(cmd, timeout=120):
    argv = shlex.split(cmd)
    env = dict(os.environ, VG_REVIEWER_PROMPT=PROMPT_PATH)

    def run(fixture_dir):
        try:
            proc = subprocess.run(argv + [fixture_dir], capture_output=True, text=True,
                                  timeout=timeout, env=env)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ReviewerError("reviewer failed to run: %s" % exc)
        if proc.returncode != 0:
            raise ReviewerError("reviewer exit %d: %s" % (proc.returncode, proc.stderr[-300:]))
        return parse_reviewer_output(proc.stdout)
    return run


# --------------------------------------------------------------------------
# Calibration
# --------------------------------------------------------------------------

def calibrate(fixtures, reviewer, min_detection=0.9, max_fp=0.1, reviewer_name="mock"):
    results, errors = [], 0
    for fx in fixtures:
        entry = {"fixture": fx["name"], "defect": fx["defect"], "defect_type": fx["defect_type"]}
        try:
            verdicts = reviewer(fx["path"])
            entry["verdicts"] = verdicts
            entry["reviewer_failed"] = any(v["verdict"] == "FAIL" for v in verdicts)
            entry["correct"] = entry["reviewer_failed"] == fx["defect"]
        except ReviewerError as exc:
            errors += 1
            entry.update(error=str(exc), reviewer_failed=None, correct=False)
        results.append(entry)

    defects = [r for r in results if r["defect"]]
    cleans = [r for r in results if not r["defect"]]
    detected = sum(1 for r in defects if r["reviewer_failed"] is True)
    false_pos = sum(1 for r in cleans if r["reviewer_failed"] is True)
    detection = detected / len(defects) if defects else None
    fpr = false_pos / len(cleans) if cleans else None

    reasons = []
    if not defects or not cleans:
        reasons.append("need at least one defect and one clean fixture")
    if errors:
        reasons.append("%d reviewer error(s)" % errors)
    if detection is not None and detection < min_detection:
        reasons.append("detection_rate %.3f < %.3f" % (detection, min_detection))
    if fpr is not None and fpr > max_fp:
        reasons.append("false_positive_rate %.3f > %.3f" % (fpr, max_fp))

    return {
        "schema_version": "1.0",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "reviewer": reviewer_name,
        "thresholds": {"min_detection_rate": min_detection, "max_false_positive_rate": max_fp},
        "counts": {"defect_fixtures": len(defects), "detected": detected,
                   "clean_fixtures": len(cleans), "false_positives": false_pos,
                   "reviewer_errors": errors},
        "detection_rate": detection,
        "false_positive_rate": fpr,
        "calibration_passed": not reasons,
        "failure_reasons": reasons,
        "results": results,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fixtures", default=DEFAULT_FIXTURES)
    ap.add_argument("--reviewer-cmd", default=None,
                    help="command run with the fixture dir appended; default: built-in mock")
    ap.add_argument("--min-detection", type=float, default=0.9)
    ap.add_argument("--max-false-positive", type=float, default=0.1)
    ap.add_argument("--reviewer-timeout", type=int, default=120,
                    help="seconds allowed per reviewer call (external reviewer)")
    ap.add_argument("--report", default=DEFAULT_REPORT)
    args = ap.parse_args(argv)

    try:
        fixtures = load_fixtures(args.fixtures)
    except (OSError, ValueError) as exc:
        print("harness error: %s" % exc, file=sys.stderr)
        return 2
    if args.reviewer_cmd:
        reviewer = external_reviewer(args.reviewer_cmd, timeout=args.reviewer_timeout)
        name = args.reviewer_cmd
    else:
        reviewer, name = mock_reviewer, "builtin-mock"

    report = calibrate(fixtures, reviewer, args.min_detection, args.max_false_positive, name)
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")

    fmt = lambda v: "n/a" if v is None else "%.3f" % v
    print("reviewer=%s detection_rate=%s false_positive_rate=%s -> %s" % (
        name, fmt(report["detection_rate"]), fmt(report["false_positive_rate"]),
        "CALIBRATION PASSED" if report["calibration_passed"] else
        "CALIBRATION FAILED (%s)" % "; ".join(report["failure_reasons"])))
    print("report: %s" % args.report)
    return 0 if report["calibration_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
