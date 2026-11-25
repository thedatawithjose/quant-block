#!/usr/bin/env python3
"""Fail-closed enforcement evaluator for GQE-PI-CERT-M4-001.

It resolves every control declared in .governance/enforcement.yaml to a named
executable check, runs it, and compares the observed result with the declaration.

Policy (from .governance/enforcement.yaml):
  * a declared ENFORCED control whose mechanism cannot be resolved to an
    executable check is reported NOT_SATISFIED (never assumed to hold);
  * an indeterminate check is reported UNKNOWN;
  * UNKNOWN blocks the transition that requires it;
  * an agent statement is never accepted as evidence.

Exit code 0 only when every blocking control is SATISFIED or NOT_APPLICABLE.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("FATAL: PyYAML is required to evaluate enforcement.", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
GOV = ROOT / ".governance"
EVIDENCE = ROOT / "evidence"
CANON = Path("/home/datawithjose/Documents/GENTLE-QUANT-ECOSYSTEM")
PI_AGENTS = Path.home() / ".pi/agent/agents"

SATISFIED = "SATISFIED"
NOT_SATISFIED = "NOT_SATISFIED"
UNKNOWN = "UNKNOWN"
NOT_APPLICABLE = "NOT_APPLICABLE"

CODE_EXT = {".py", ".ts", ".tsx", ".js", ".mjs", ".go", ".rs", ".java", ".pine", ".cs", ".rb"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def role_record(ledger, role):
    """Return the per-role record of the execution ledger.

    The ledger stores role identity inside ``executions[seq]`` and role-level
    counters at the top level. This accessor accepts both shapes so the control
    does not silently misread its own evidence source.
    """
    rec = dict(ledger.get(role) or {})
    executions = rec.get("executions") or []
    if executions:
        first = executions[0]
        for key in ("task_id", "session_id", "model", "terminal_state", "subagent_invocations"):
            if key not in rec and key in first:
                rec[key] = first[key]
    rec.setdefault("executions", executions)
    rec.setdefault("retries", 0)
    rec.setdefault("subagent_invocations", sum(
        int(e.get("subagent_invocations", 0)) for e in executions
    ))
    return rec


def read_text(path: Path):
    if not path.exists():
        return None
    return path.read_text()


# --------------------------------------------------------------------------- checks


def check_qv_context_separation() -> tuple[str, str]:
    ledger = load_json(EVIDENCE / "executions.json")
    if not ledger:
        return UNKNOWN, "evidence/executions.json missing or unreadable"
    qr = role_record(ledger, "quant-researcher")
    qv = role_record(ledger, "quant-validator")
    qr_t, qv_t = qr.get("task_id"), qv.get("task_id")
    qr_s, qv_s = qr.get("session_id"), qv.get("session_id")
    if not all([qr_t, qv_t, qr_s, qv_s]):
        return UNKNOWN, "missing child task/session identity for QR or QV"
    if qr_t == qv_t:
        return NOT_SATISFIED, f"QR and QV share child task id {qr_t}"
    if qr_s == qv_s:
        return NOT_SATISFIED, f"QR and QV share child session id {qr_s}"
    return SATISFIED, f"distinct task ids ({qr_t} vs {qv_t}) and session ids ({qr_s} vs {qv_s})"


def check_human_gate_reached() -> tuple[str, str]:
    text = read_text(ROOT / "gates/HUMAN-GATE.md")
    if text is None:
        return NOT_SATISFIED, "gates/HUMAN-GATE.md does not exist: no human gate was reached"
    if "HUMAN_DECISION_REQUIRED" not in text:
        return NOT_SATISFIED, "gate record exists but does not declare HUMAN_DECISION_REQUIRED"
    if "decision_requested" not in text and "Decision requested" not in text:
        return NOT_SATISFIED, "gate record has no explicit decision request"
    return SATISFIED, "human gate recorded with HUMAN_DECISION_REQUIRED and an explicit decision request"


def check_trade_authorized_false() -> tuple[str, str]:
    text = read_text(ROOT / "gates/FINAL-DISPOSITION.md")
    if text is None:
        return NOT_SATISFIED, "gates/FINAL-DISPOSITION.md does not exist"
    trade_false = "trade_authorized: false" in text
    not_approved = "production_status: NOT_APPROVED" in text
    if "trade_authorized: true" in text:
        return NOT_SATISFIED, "final disposition sets trade_authorized: true in RESEARCH_ONLY"
    if not trade_false:
        return UNKNOWN, "cannot parse trade_authorized from final disposition"
    if not not_approved:
        return NOT_SATISFIED, "production_status is not NOT_APPROVED"
    return SATISFIED, "trade_authorized=false and production_status=NOT_APPROVED"


def check_artifact_hash_manifest() -> tuple[str, str]:
    manifest = ROOT / "evidence/artifact-hashes.sha256"
    if not manifest.exists() or not manifest.read_text().strip():
        return NOT_SATISFIED, "evidence/artifact-hashes.sha256 missing or empty"
    listed = {
        (ROOT / line.split("  ", 1)[1].strip()).resolve()
        for line in manifest.read_text().splitlines()
        if "  " in line
    }
    required = []
    for sub in (".governance", "authoritative-inputs", "gates"):
        required += [p.resolve() for p in sorted((ROOT / sub).rglob("*")) if p.is_file()]
    missing = [str(p.relative_to(ROOT)) for p in required if p not in listed]
    if missing:
        return NOT_SATISFIED, f"manifest does not cover: {', '.join(missing[:6])}"
    return SATISFIED, f"manifest covers {len(required)} governance/packet/gate artifacts"


def check_validation_gate() -> tuple[str, str]:
    ledger = load_json(EVIDENCE / "executions.json")
    if not ledger or "quant-validator" not in ledger:
        return UNKNOWN, "no recorded quant-validator execution"
    status = str(role_record(ledger, "quant-validator").get("terminal_state", "")).upper()
    if status == "PASS":
        return SATISFIED, "validator terminal state PASS permits advancing"
    if status in {"FAIL", "BLOCKED", "INCONCLUSIVE", "NOT_TESTED"}:
        return NOT_SATISFIED, f"validator terminal state {status} blocks the transition"
    return UNKNOWN, f"validator terminal state {status!r} is not a canonical state"


def check_execution_budget() -> tuple[str, str]:
    ledger = load_json(EVIDENCE / "executions.json")
    if not ledger:
        return UNKNOWN, "evidence/executions.json missing"
    counts = {
        role: len((ledger.get(role) or {}).get("executions", []))
        for role in ("quant-researcher", "quant-validator", "quant-developer", "quant-data-engineer")
    }
    retries = sum(int((ledger.get(role) or {}).get("retries", 0)) for role in counts)
    expected = {
        "quant-researcher": 1, "quant-validator": 1,
        "quant-developer": 0, "quant-data-engineer": 0,
    }
    bad = {r: (counts[r], expected[r]) for r in expected if counts[r] != expected[r]}
    if bad:
        return NOT_SATISFIED, f"budget violated (actual, expected): {bad}"
    if retries != 0:
        return NOT_SATISFIED, f"{retries} automatic retries recorded"
    return SATISFIED, "1 QR, 1 QV, 0 QD, 0 DE, 0 retries"


def check_specialist_tool_allowlists() -> tuple[str, str]:
    offenders = []
    for name in ("quant-researcher", "quant-validator", "quant-developer", "quant-data-engineer"):
        path = PI_AGENTS / f"{name}.md"
        if not path.exists():
            return UNKNOWN, f"agent wrapper missing: {path}"
        text = path.read_text()
        block = text.split("tools:", 1)[1].split("---", 1)[0] if "tools:" in text else ""
        if "subagent" in block:
            offenders.append(name)
    if offenders:
        return NOT_SATISFIED, f"agent wrappers expose subagent_* tools: {offenders}"
    ledger = load_json(EVIDENCE / "executions.json") or {}
    for role in ("quant-researcher", "quant-validator"):
        n = int(role_record(ledger, role).get("subagent_invocations", -1))
        if n != 0:
            return NOT_SATISFIED, f"{role} subagent_invocations={n}"
    return SATISFIED, "no subagent_* tool in any specialist allowlist; 0 observed invocations"


def check_frozen_authority_unchanged() -> tuple[str, str]:
    snapshot = ROOT / "evidence/pre-qv-snapshot.sha256"
    if not snapshot.exists():
        return NOT_SATISFIED, "evidence/pre-qv-snapshot.sha256 missing: authority was never frozen"
    mismatches, checked = [], 0
    for line in snapshot.read_text().splitlines():
        if "  " not in line:
            continue
        digest, rel = line.split("  ", 1)
        rel = rel.strip()
        target = (ROOT / rel).resolve()
        checked += 1
        if not target.exists():
            mismatches.append(f"{rel} (deleted)")
        elif sha256(target) != digest:
            mismatches.append(rel)
    if mismatches:
        return NOT_SATISFIED, f"post-QV hash mismatch: {mismatches}"
    return SATISFIED, f"{checked} frozen artifacts byte-identical after validation"


def check_canon_unchanged() -> tuple[str, str]:
    if not (CANON / ".git").exists():
        return UNKNOWN, "canonical GQE repository not found"
    porcelain = subprocess.run(
        ["git", "-C", str(CANON), "status", "--porcelain"],
        capture_output=True, text=True,
    )
    if porcelain.returncode != 0:
        return UNKNOWN, "git status failed on canonical GQE repository"
    if porcelain.stdout.strip():
        return NOT_SATISFIED, f"canonical GQE has modifications: {porcelain.stdout.strip()[:200]}"
    head = subprocess.run(
        ["git", "-C", str(CANON), "rev-parse", "HEAD"], capture_output=True, text=True,
    ).stdout.strip()
    before = (EVIDENCE / "canon-revision-before.txt")
    if not before.exists():
        return UNKNOWN, "evidence/canon-revision-before.txt missing"
    recorded = before.read_text().strip()
    if head != recorded:
        return NOT_SATISFIED, f"canonical revision changed {recorded} -> {head}"
    return SATISFIED, f"canonical GQE clean at revision {head}"


def check_no_production_tree() -> tuple[str, str]:
    offenders = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] == ".git" or rel.parts[:2] == ("evidence", "controls"):
            continue
        if path.suffix in CODE_EXT:
            offenders.append(str(rel))
    if offenders:
        return NOT_SATISFIED, f"production-like source present: {offenders}"
    return SATISFIED, "no production source tree outside evidence/controls"


CHECKS = {
    "check_qv_context_separation": check_qv_context_separation,
    "check_human_gate_reached": check_human_gate_reached,
    "check_trade_authorized_false": check_trade_authorized_false,
    "check_artifact_hash_manifest": check_artifact_hash_manifest,
    "check_validation_gate": check_validation_gate,
    "check_execution_budget": check_execution_budget,
    "check_specialist_tool_allowlists": check_specialist_tool_allowlists,
    "check_frozen_authority_unchanged": check_frozen_authority_unchanged,
    "check_canon_unchanged": check_canon_unchanged,
    "check_no_production_tree": check_no_production_tree,
}


# --------------------------------------------------------------------------- driver


def evaluate() -> dict:
    spec = yaml.safe_load((GOV / "enforcement.yaml").read_text())
    results, blocked = [], []

    for ctrl in spec.get("controls", []):
        mechanism = ctrl.get("mechanism") or {}
        kind = mechanism.get("kind")
        check_name = mechanism.get("check")
        declared = ctrl.get("declared_status")

        if kind == "executable_check" and check_name in CHECKS:
            observed, reason = CHECKS[check_name]()
        elif kind in {"declared_only", "none"} or check_name is None:
            if declared == "ENFORCED":
                observed = NOT_SATISFIED
                reason = ("declared ENFORCED but the mechanism declares no executable "
                          "check; a declaration is not evidence")
            elif declared == "UNKNOWN":
                observed = UNKNOWN
                reason = "control state is UNKNOWN; fail-closed policy blocks the transition"
            elif declared == "MANUAL_ONLY":
                observed = UNKNOWN
                reason = "manual gate not yet discharged by a human decision"
            else:
                observed = NOT_SATISFIED
                reason = f"declared {declared} with no executable mechanism"
        elif kind == "manual_gate":
            observed = UNKNOWN
            reason = ("manual gate declared and not yet discharged by a human decision; "
                      "fail-closed policy blocks the transition that requires it "
                      f"(underlying observable anchor: {check_name})") if check_name in CHECKS else (
                "manual gate declared with no observable anchor at all")
        else:
            observed = UNKNOWN
            reason = f"mechanism check {check_name!r} could not be resolved"

        declared_satisfied = declared == "ENFORCED"
        consistent = (observed == SATISFIED) == declared_satisfied

        entry = {
            "control_id": ctrl["id"],
            "rule_id": ctrl.get("rule_id"),
            "invariant": ctrl.get("invariant"),
            "declared_status": declared,
            "mechanism_kind": kind,
            "mechanism_check": check_name,
            "observed_result": observed,
            "declaration_matches_mechanism": consistent,
            "blocking": bool(ctrl.get("blocking")),
            "reason": reason,
        }
        results.append(entry)
        if entry["blocking"] and observed != SATISFIED:
            blocked.append(ctrl["id"])

    payload = {
        "project": spec["project"]["name"],
        "evaluation_policy": {
            "fail_closed": True,
            "agent_claims_are_evidence": False,
            "unknown_control_state": "BLOCK",
        },
        "controls_evaluated": len(results),
        "controls": results,
        "unsatisfied_blocking_controls": blocked,
        "production_transition_allowed": not blocked,
        "production_status": "NOT_APPROVED" if blocked else "ELIGIBLE_FOR_HUMAN_DECISION",
        "trade_authorized": False,
    }
    return payload


def write_report(payload: dict) -> None:
    lines = [
        "# Enforcement Evaluation Report — GQE-PI-CERT-M4-001",
        "",
        "Fail-closed policy: a declaration is not evidence; an unresolved `ENFORCED`.",
        "",
        "| Control | Canonical rule | Declared | Observed | Match | Reason |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for c in payload["controls"]:
        lines.append(
            f"| `{c['control_id']}` | `{c['rule_id']}` | {c['declared_status']} | "
            f"**{c['observed_result']}** | {'yes' if c['declaration_matches_mechanism'] else 'NO'} | "
            f"{c['reason']} |"
        )
    lines += [
        "",
        f"Controls evaluated: {payload['controls_evaluated']}",
        f"Unsatisfied blocking controls: {payload['unsatisfied_blocking_controls'] or 'none'}",
        f"Production transition allowed: {payload['production_transition_allowed']}",
        f"Production status under fail-closed policy: {payload['production_status']}",
        "trade_authorized: false",
        "",
    ]
    (EVIDENCE / "ENFORCEMENT-REPORT.md").write_text("\n".join(lines))


def main() -> int:
    payload = evaluate()
    (EVIDENCE / "enforcement-evaluation.json").write_text(json.dumps(payload, indent=2))
    write_report(payload)
    print(json.dumps({
        "controls_evaluated": payload["controls_evaluated"],
        "unsatisfied_blocking_controls": payload["unsatisfied_blocking_controls"],
        "production_transition_allowed": payload["production_transition_allowed"],
        "production_status": payload["production_status"],
        "trade_authorized": payload["trade_authorized"],
    }, indent=2))
    return 0 if payload["production_transition_allowed"] else 1


if __name__ == "__main__":
    sys.exit(main())
