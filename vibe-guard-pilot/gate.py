#!/usr/bin/env python3
"""vibe-guard gate: deterministic local executor for enforcement.yaml (schema 1.0).

Reads <project>/.governance/enforcement.yaml, runs every executable
invariant check, stores evidence (failed checks included) and writes
verdict.json. Fails closed: anything that is not a verified PASS blocks.

Stdlib only. Exit codes:
  0  every CRITICAL invariant passed
  1  at least one CRITICAL invariant did not pass (BLOCK)
  2  gate/config error (also a BLOCK: nothing could be verified)
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import signal
import subprocess
import sys

SCHEMA_VERSION = "1.0"
CONFIG_RELPATH = os.path.join(".governance", "enforcement.yaml")
RUNNABLE_TYPES = {"command", "test", "static_analysis", "runtime_assertion"}
KNOWN_NON_RUNNABLE = {"none", "manual_gate"}
OUTPUT_CAP = 64 * 1024

PASS, FAIL, UNKNOWN, BLOCKED = "PASS", "FAIL", "UNKNOWN", "BLOCKED"


class GateError(Exception):
    """Configuration or schema problem: the gate cannot judge anything."""


# --------------------------------------------------------------------------
# Minimal YAML subset parser (block maps, block lists, scalars, flow [] / {}).
# Enough for enforcement.template.yaml. Anything unsupported raises GateError
# instead of being silently misread (fail closed).
# --------------------------------------------------------------------------

_KEY_RE = re.compile(r"""^("(?:[^"\\]|\\.)*"|'[^']*'|[^\s:#'"\[\]{}-][^:#]*?|-[^\s:][^:]*?)\s*:(?:\s+(.*))?$""")


def _strip_comment(s):
    out, quote = [], None
    for i, ch in enumerate(s):
        if quote:
            out.append(ch)
            if ch == quote and not (quote == '"' and s[i - 1] == "\\"):
                quote = None
        elif ch in "\"'" and (i == 0 or s[i - 1] in " \t[{,:"):
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or s[i - 1] in " \t"):
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def _split_flow(s):
    parts, buf, quote, depth = [], [], None, 0
    for ch in s:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch in "[{":
            depth += 1
            buf.append(ch)
        elif ch in "]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _scalar(tok):
    tok = tok.strip()
    if tok == "" or tok in ("null", "Null", "NULL", "~"):
        return None
    if tok in ("true", "True", "TRUE"):
        return True
    if tok in ("false", "False", "FALSE"):
        return False
    if tok[0] == '"':
        if len(tok) < 2 or tok[-1] != '"':
            raise GateError("unterminated double-quoted string: %r" % tok)
        try:
            return json.loads(tok)
        except ValueError:
            return tok[1:-1]
    if tok[0] == "'":
        if len(tok) < 2 or tok[-1] != "'":
            raise GateError("unterminated single-quoted string: %r" % tok)
        return tok[1:-1].replace("''", "'")
    if tok[0] == "[":
        if tok[-1] != "]":
            raise GateError("unsupported multi-line flow list: %r" % tok)
        return [_scalar(p) for p in _split_flow(tok[1:-1])]
    if tok[0] == "{":
        if tok != "{}":
            raise GateError("unsupported flow mapping (only {} allowed): %r" % tok)
        return {}
    if tok[0] in "|>&*!":
        raise GateError("unsupported YAML construct: %r" % tok)
    if re.fullmatch(r"[-+]?\d+", tok):
        return int(tok)
    if re.fullmatch(r"[-+]?\d*\.\d+", tok):
        return float(tok)
    return tok


def _tokenize(text):
    lines = []
    for n, raw in enumerate(text.splitlines(), 1):
        body = _strip_comment(raw)
        if not body.strip():
            continue
        indent = len(body) - len(body.lstrip(" "))
        if body[indent:indent + 1] == "\t":
            raise GateError("line %d: tab indentation is not supported" % n)
        lines.append([indent, body[indent:], n])
    return lines


def _parse_block(lines, i, indent):
    if lines[i][1] == "-" or lines[i][1].startswith("- "):
        return _parse_list(lines, i, indent)
    return _parse_map(lines, i, indent)


def _parse_list(lines, i, indent):
    result = []
    while i < len(lines) and lines[i][0] == indent and (
            lines[i][1] == "-" or lines[i][1].startswith("- ")):
        rest = lines[i][1][1:]
        stripped = rest.lstrip(" ")
        if not stripped:
            i += 1
            if i < len(lines) and lines[i][0] > indent:
                value, i = _parse_block(lines, i, lines[i][0])
            else:
                value = None
            result.append(value)
            continue
        # Re-anchor the item content as if it were its own line.
        lines[i] = [indent + 1 + (len(rest) - len(stripped)), stripped, lines[i][2]]
        if _KEY_RE.match(stripped):
            value, i = _parse_map(lines, i, lines[i][0])
        else:
            value = _scalar(stripped)
            i += 1
        result.append(value)
    return result, i


def _parse_map(lines, i, indent):
    result = {}
    while i < len(lines) and lines[i][0] == indent:
        text, n = lines[i][1], lines[i][2]
        m = _KEY_RE.match(text)
        if not m:
            raise GateError("line %d: cannot parse %r" % (n, text))
        key = _scalar(m.group(1)) if m.group(1)[0] in "\"'" else m.group(1).strip()
        key = str(key)
        if key in result:
            raise GateError("line %d: duplicate key %r" % (n, key))
        raw = (m.group(2) or "").strip()
        i += 1
        if raw:
            result[key] = _scalar(raw)
        elif i < len(lines) and lines[i][0] > indent:
            result[key], i = _parse_block(lines, i, lines[i][0])
        elif i < len(lines) and lines[i][0] == indent and (
                lines[i][1] == "-" or lines[i][1].startswith("- ")):
            result[key], i = _parse_list(lines, i, indent)
        else:
            result[key] = None
    if i < len(lines) and lines[i][0] > indent:
        raise GateError("line %d: unexpected indentation" % lines[i][2])
    return result, i


def load_yaml(text):
    lines = _tokenize(text)
    if not lines:
        raise GateError("empty configuration")
    value, i = _parse_block(lines, 0, lines[0][0])
    if i != len(lines):
        raise GateError("line %d: unparsed content" % lines[i][2])
    return value


# --------------------------------------------------------------------------
# Gate logic
# --------------------------------------------------------------------------

def _utc_stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _iso_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _safe_name(s):
    return re.sub(r"[^A-Za-z0-9._-]", "_", str(s)) or "invariant"


def _cap(s):
    if len(s) > OUTPUT_CAP:
        return s[:OUTPUT_CAP], True
    return s, False


def validate_config(cfg):
    if not isinstance(cfg, dict):
        raise GateError("top level must be a mapping")
    if str(cfg.get("schema_version")) != SCHEMA_VERSION:
        raise GateError("schema_version must be %r, got %r"
                        % (SCHEMA_VERSION, cfg.get("schema_version")))
    policy = cfg.get("policy") or {}
    if not isinstance(policy, dict):
        raise GateError("policy must be a mapping")
    if policy.get("fail_closed", True) is not True:
        raise GateError("policy.fail_closed must be true")
    if policy.get("agent_claims_are_evidence", False) is not False:
        raise GateError("policy.agent_claims_are_evidence must be false")
    if policy.get("unknown_control_state", "BLOCK") != "BLOCK":
        raise GateError("policy.unknown_control_state must be \"BLOCK\"")
    invs = cfg.get("invariants")
    if not isinstance(invs, list) or not invs:
        raise GateError("invariants must be a non-empty list")
    seen = set()
    for inv in invs:
        if not isinstance(inv, dict) or not isinstance(inv.get("id"), str) or not inv["id"]:
            raise GateError("every invariant needs a string id")
        if inv["id"] in seen:
            raise GateError("duplicate invariant id %r" % inv["id"])
        seen.add(inv["id"])
    return policy


def _num(value, default):
    return default if value is None else value


def _execute(command, cwd, timeout):
    proc = subprocess.Popen(
        command, shell=True, cwd=cwd, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, errors="replace", start_new_session=True)
    try:
        out, err = proc.communicate(timeout=timeout)
        return proc.returncode, out, err, False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
        out, err = proc.communicate()
        return None, out or "", err or "", True


def evaluate_invariant(inv, defaults, root):
    """Return (status, record) for one invariant. record feeds the evidence file."""
    ver = inv.get("verification")
    ver = ver if isinstance(ver, dict) else {}
    vtype = ver.get("type")
    command = ver.get("command")
    rec = {
        "id": inv["id"], "title": inv.get("title"),
        "severity": str(inv.get("severity") or "CRITICAL").upper(),
        "declared_enforcement_status": inv.get("enforcement_status"),
        "verification_type": vtype, "command": command,
        "working_directory": None, "timeout_seconds": None,
        "expected_exit_code": None, "exit_code": None, "timed_out": False,
        "reason": "", "started_at": _iso_now(),
    }

    def done(status, reason):
        rec["reason"] = reason
        rec["finished_at"] = _iso_now()
        return status, rec

    if vtype in KNOWN_NON_RUNNABLE or vtype is None:
        return done(BLOCKED, "verification.type is %r: no deterministic check exists; "
                    "claims (including enforcement_status=%r) are not evidence"
                    % (vtype, inv.get("enforcement_status")))
    if vtype not in RUNNABLE_TYPES:
        return done(BLOCKED, "unrecognised verification.type %r" % (vtype,))
    if not isinstance(command, str) or not command.strip():
        return done(UNKNOWN, "verification.command is missing or empty")

    wd = ver.get("working_directory") or defaults.get("working_directory") or "."
    timeout = _num(ver.get("timeout_seconds"), _num(defaults.get("timeout_seconds"), 300))
    expected = _num(ver.get("expected_exit_code"), _num(defaults.get("expected_exit_code"), 0))
    rec.update(working_directory=wd, timeout_seconds=timeout, expected_exit_code=expected)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
        return done(UNKNOWN, "timeout_seconds is not a positive number: %r" % (timeout,))
    if isinstance(expected, bool) or not isinstance(expected, int):
        return done(UNKNOWN, "expected_exit_code is not an integer: %r" % (expected,))
    cwd = os.path.normpath(os.path.join(root, wd))
    if not os.path.isdir(cwd):
        return done(UNKNOWN, "working_directory does not exist: %s" % wd)

    try:
        code, out, err, timed_out = _execute(command, cwd, timeout)
    except OSError as exc:
        return done(UNKNOWN, "could not launch command: %s" % exc)
    out, out_cut = _cap(out)
    err, err_cut = _cap(err)
    rec.update(exit_code=code, timed_out=timed_out, stdout=out, stderr=err,
               output_truncated=out_cut or err_cut)
    if timed_out:
        return done(FAIL, "timed out after %s s" % timeout)
    if code == expected:
        return done(PASS, "exit code %d matched expected %d" % (code, expected))
    return done(FAIL, "exit code %d, expected %d" % (code, expected))


def run_gate(project_dir, config_path=None, verdict_path=None):
    """Run the gate. Returns (verdict_dict, exit_code). Raises GateError on bad config."""
    root = os.path.abspath(project_dir)
    config_path = config_path or os.path.join(root, CONFIG_RELPATH)
    try:
        with open(config_path, encoding="utf-8") as fh:
            cfg = load_yaml(fh.read())
    except OSError as exc:
        raise GateError("cannot read %s: %s" % (config_path, exc))
    policy = validate_config(cfg)
    defaults = cfg.get("defaults") or {}
    ev_cfg = policy.get("evidence") or {}
    ev_dir = ev_cfg.get("directory") or ".governance/evidence"
    ev_abs = os.path.normpath(os.path.join(root, ev_dir))
    os.makedirs(ev_abs, exist_ok=True)
    stamp = _utc_stamp()

    results = []
    for inv in cfg["invariants"]:
        status, rec = evaluate_invariant(inv, defaults, root)
        rec["status"] = status
        # Failed/unknown/blocked checks are preserved on purpose: they are the
        # most valuable evidence. Files are timestamped, never overwritten.
        ev_file = os.path.join(ev_abs, "%s-%s.json" % (_safe_name(inv["id"]), stamp))
        rec["checked_at_stamp"] = stamp
        with open(ev_file, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=2, sort_keys=True)
        with open(ev_file, "rb") as fh:
            body = fh.read()
        results.append({
            "id": inv["id"],
            "title": inv.get("title"),
            "severity": rec["severity"],
            "status": status,
            "command": rec["command"],
            "working_directory": rec["working_directory"],
            "exit_code": rec["exit_code"],
            "expected_exit_code": rec["expected_exit_code"],
            "reason": rec["reason"],
            "contract_section": (inv.get("traceability") or {}).get("contract_section")
            if isinstance(inv.get("traceability"), dict) else None,
            "evidence_path": os.path.relpath(ev_file, root).replace(os.sep, "/"),
            "evidence_sha256": hashlib.sha256(body).hexdigest(),
        })

    critical_bad = [r["id"] for r in results if r["severity"] == "CRITICAL" and r["status"] != PASS]
    verdict = {
        "schema_version": SCHEMA_VERSION,
        "project": (cfg.get("project") or {}).get("name"),
        "generated_at": _iso_now(),
        "project_root": root,
        "overall": "BLOCK" if critical_bad else "PASS",
        "blocking_invariants": critical_bad,
        "invariants": results,
    }
    out_path = verdict_path or os.path.join(ev_abs, "verdict.json")
    for target in (out_path, os.path.join(ev_abs, "verdict-%s.json" % stamp)):
        os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
        with open(target, "w", encoding="utf-8") as fh:
            json.dump(verdict, fh, indent=2)
    verdict["verdict_path"] = out_path
    return verdict, (1 if critical_bad else 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description="vibe-guard compliance gate (enforcement schema 1.0)")
    ap.add_argument("--project", default=".", help="project root (default: cwd)")
    ap.add_argument("--config", help="path to enforcement.yaml (default: <project>/.governance/enforcement.yaml)")
    ap.add_argument("--verdict", help="where to write verdict.json (default: <evidence dir>/verdict.json)")
    args = ap.parse_args(argv)
    try:
        verdict, code = run_gate(args.project, args.config, args.verdict)
    except GateError as exc:
        print("vibe-guard: BLOCK (gate error): %s" % exc, file=sys.stderr)
        return 2
    for r in verdict["invariants"]:
        print("%-8s %-10s %s  (%s)" % (r["status"], r["severity"], r["id"], r["reason"]))
    print("vibe-guard: %s  verdict=%s" % (verdict["overall"], verdict["verdict_path"]))
    return code


if __name__ == "__main__":
    sys.exit(main())
