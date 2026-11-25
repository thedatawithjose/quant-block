#!/usr/bin/env python3
"""Canonical inheritance and boundary checks for the DCP interaction layer.

Verifies that all eight specialists inherit the same canonical interaction
policy, that no role embeds a DCP semantic copy, and that role boundaries are
unchanged. Read-only.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


SPECIALISTS = (
    "ui-ux-engineer",
    "software-engineer",
    "data-engineer",
    "data-scientist",
    "quant-data-engineer",
    "quant-researcher",
    "quant-developer",
    "quant-validator",
)

DCP_EXPECTED = {
    "dcp_01.md": "72a9cf07b15d17975789f3b55bf4b24b04068e32ef6cc0a99100b5aee71e4c26",
    "dcp_02.md": "db0c21480ec66f4a8e6e10555ad3a49b7dd7e3ace298de88c7915922cbfd1966",
    "dcp_03.md": "ffc6f2f32ba184a4d02ee8f9f7c1311fb5aa3c3d47f95ffd21c312735f69df2d",
}

EXPECTED_CONTEXT = {
    "quant-validator": "ISOLATED_REQUIRED",
}

BOUNDARY_TERMS = ("## Owns", "## Does Not Own", "## Hard Rules")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_dcp_sources(root: Path) -> None:
    canonical_root = Path("/home/datawithjose/Documents/AI-GOVERNANCE/DCP")
    for name, expected in DCP_EXPECTED.items():
        path = canonical_root / name
        if not path.is_file():
            fail(f"canonical DCP source missing: {path}")
        observed = sha256(path)
        if observed != expected:
            fail(f"{name}: provenance drift {observed} != {expected}")
    print("PASS: 3/3 canonical DCP sources present at canonical location with expected hashes")


def check_policy(root: Path) -> None:
    policy = root / "agents" / "USER-INTERACTION-POLICY.md"
    if not policy.is_file():
        fail(f"interaction policy missing: {policy}")
    text = policy.read_text(encoding="utf-8")
    required = ("dcp_01.md", "dcp_02.md", "dcp_03.md", "DCP_CONTEXT_UNAVAILABLE")
    missing = [item for item in required if item not in text]
    if missing:
        fail(f"interaction policy missing references: {missing}")
    # Anti-duplication: the policy must not restate DCP state semantics.
    duplicated = [
        marker
        for marker in ("EXPLORATION", "OVERLOAD", "OVERENGINEERING", "DEEPENING")
        if marker in text
    ]
    if duplicated:
        fail(f"interaction policy duplicates DCP semantics: {duplicated}")
    if "| State | Action |" in text:
        fail("interaction policy restates the DCP WHEN state table")
    print("PASS: interaction policy is inheritance-only and references all DCP parts")


def check_contract_and_packet(root: Path) -> None:
    contract = (root / "agents" / "SUBAGENT-CONTRACT-SPEC.md").read_text(encoding="utf-8")
    if "USER-INTERACTION-POLICY.md" not in contract:
        fail("SUBAGENT-CONTRACT-SPEC does not inherit interaction policy")
    packet = (root / "agents" / "TASK-PACKET-CONTRACT-SPEC.md").read_text(encoding="utf-8")
    if "user_interaction_policy" not in packet:
        fail("TASK-PACKET-CONTRACT-SPEC lacks user_interaction_policy block")
    template = (root / "templates" / "tasks" / "TASK-PACKET.template.yaml").read_text(encoding="utf-8")
    if "user_interaction_policy" not in template or "dcp_sources" not in template:
        fail("TASK-PACKET template lacks user_interaction_policy propagation")
    print("PASS: subagent contract and Task Packet propagate the interaction policy")


def check_specialists(root: Path) -> None:
    agents_root = root / "agents"
    for name in SPECIALISTS:
        role = agents_root / name / "ROLE.md"
        subagent = agents_root / name / "SUBAGENT.md"
        if not role.is_file() or not subagent.is_file():
            fail(f"{name}: canonical role files missing")
        text = role.read_text(encoding="utf-8")
        missing = [term for term in BOUNDARY_TERMS if term not in text]
        if missing:
            fail(f"{name}: role boundaries missing {missing}")
        frontmatter = subagent.read_text(encoding="utf-8")
        if "delegation: \"FORBIDDEN\"" not in frontmatter:
            fail(f"{name}: delegation policy changed")
        expected = EXPECTED_CONTEXT.get(name, "ISOLATED_PREFERRED")
        if f"context: \"{expected}\"" not in frontmatter:
            fail(f"{name}: context policy changed (expected {expected})")
        if "DCP" in role.read_text(encoding="utf-8") and "dcp_0" in role.read_text(encoding="utf-8"):
            fail(f"{name}: role embeds DCP semantics")
    print(f"PASS: {len(SPECIALISTS)}/{len(SPECIALISTS)} specialists inherit policy with boundaries unchanged")


def main() -> int:
    root = repo_root()
    check_dcp_sources(root)
    check_policy(root)
    check_contract_and_packet(root)
    check_specialists(root)
    print("PASS: canonical DCP inheritance validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
