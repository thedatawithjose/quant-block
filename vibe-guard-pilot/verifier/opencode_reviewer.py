#!/usr/bin/env python3
"""External reviewer adapter: runs an OpenCode model as the adversarial verifier.

Usage:  opencode_reviewer.py <fixture_dir>
Env:    VG_REVIEWER_PROMPT = path to reviewer_prompt.md (set by the harness)
        VG_MODEL           = provider/model to act as the reviewer
        VG_TIMEOUT         = seconds per call (default 300)

The fixture content is inlined into the prompt, so the reviewer needs no tools,
and the reviewer runs against a TEMPORARY COPY so it can never pollute the
original fixture. Binary files (null bytes) and __pycache__ are skipped. It
prints a single clean JSON array of per-criterion verdicts, which is exactly
what verifier/calibrate.py parses.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def read_text(path):
    """Decoded text, or None if the file is missing or binary (has null bytes)."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    return raw.decode("utf-8", errors="replace")


def iter_files(base):
    for p in sorted(glob.glob(os.path.join(base, "**", "*"), recursive=True)):
        if os.path.isfile(p) and "__pycache__" not in p.split(os.sep):
            yield p


def build_prompt(fix, prompt_path):
    chunks = [read_text(prompt_path) or ""]
    criteria = read_text(os.path.join(fix, "criteria.md"))
    chunks.append("\n\n=== criteria.md ===\n" + (criteria if criteria is not None else "<missing>"))
    for base in ("artifact", "evidence"):
        for p in iter_files(os.path.join(fix, base)):
            txt = read_text(p)
            if txt is None:
                continue
            chunks.append("\n\n=== %s ===\n%s" % (os.path.relpath(p, fix), txt))
    chunks.append("\n\nReturn ONLY the JSON verdicts now. One object per criterion in criteria.md.")
    return "".join(chunks)


def extract_json(text):
    t = re.sub(r"```[a-zA-Z]*", "", text).replace("```", "")
    m = re.search(r"\[[\s\S]*\]", t)
    if m:
        try:
            data = json.loads(m.group(0))
            return data if isinstance(data, list) else [data]
        except ValueError:
            pass
    items = []
    for line in t.splitlines():
        line = line.strip().rstrip(",")
        if line.startswith("{") and line.endswith("}"):
            try:
                items.append(json.loads(line))
            except ValueError:
                pass
    if not items:
        for m2 in re.finditer(r"\{[^{}]*\}", t):
            try:
                items.append(json.loads(m2.group(0)))
            except ValueError:
                pass
    return items


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: opencode_reviewer.py <fixture_dir>\n")
        return 2
    src = sys.argv[1]
    prompt_path = os.environ.get("VG_REVIEWER_PROMPT",
                                 os.path.join(HERE, "reviewer_prompt.md"))
    model = os.environ.get("VG_MODEL", "commandcode/deepseek/deepseek-v4-flash")
    timeout = int(os.environ.get("VG_TIMEOUT", "300"))

    work = tempfile.mkdtemp(prefix="vg_review_")
    try:
        dst = os.path.join(work, "fixture")
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        prompt = build_prompt(dst, prompt_path)
        attempts = int(os.environ.get("VG_ATTEMPTS", "3"))
        valid, last = [], ""
        for _ in range(attempts):
            try:
                proc = subprocess.run(
                    ["opencode", "run", "--pure", "-m", model, prompt],
                    capture_output=True, text=True, timeout=timeout, cwd=dst,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                last = "run failed: %s" % exc
                continue
            last = proc.stdout[:800] if proc.stdout.strip() else (proc.stderr[-400:] or "<empty>")
            if proc.returncode == 0:
                valid = [it for it in extract_json(proc.stdout)
                         if isinstance(it, dict) and it.get("verdict") in ("PASS", "FAIL")
                         and "criterion" in it]
                if valid:
                    break
        if not valid:
            sys.stderr.write("opencode_reviewer: no valid verdicts after %d attempts. LAST:\n%s\n"
                             % (attempts, last))
            return 5
        sys.stdout.write(json.dumps(valid))
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
