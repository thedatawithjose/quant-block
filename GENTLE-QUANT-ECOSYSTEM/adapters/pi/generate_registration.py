#!/usr/bin/env python3
"""Generate staging-only Pi runtime wrappers from canonical GQE contracts.

Deployment action only. Canonical authority remains agents/*/ROLE.md,
agents/*/SUBAGENT.md, agents/SUBAGENT-CONTRACT-SPEC.md, and
agents/USER-INTERACTION-POLICY.md with the canonical DCP sources.

Provenance is fail-closed. Generation aborts unless the canonical inputs are
committed at Git HEAD and the DCP sources match the hashes recorded in
USER-INTERACTION-POLICY.md, so the emitted stamp always describes the content
it was generated from.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path


SPECIALISTS = {
    "ui-ux-engineer": ("GQE general UI/UX specialist.", "medium"),
    "software-engineer": ("GQE general software engineering specialist.", "medium"),
    "data-engineer": ("GQE general data engineering specialist.", "medium"),
    "data-scientist": ("GQE general data-science specialist.", "medium"),
    "quant-data-engineer": ("GQE financial data engineering specialist.", "medium"),
    "quant-researcher": ("GQE quantitative research specialist.", "medium"),
    "quant-developer": ("GQE quantitative implementation specialist.", "medium"),
    "quant-validator": ("GQE independent quantitative validation specialist.", "medium"),
}

CANONICAL_ROOT = "/home/datawithjose/Documents/GENTLE-QUANT-ECOSYSTEM"
DCP_ROOT = "/home/datawithjose/Documents/AI-GOVERNANCE/DCP"
DCP_PARTS = ("dcp_01.md", "dcp_02.md", "dcp_03.md")

WRAPPER_TOOLS = {
    "quant-validator": ("read", "grep", "find", "bash"),
}

# Runtime-specific model mapping. Canonical role contracts stay
# runtime-independent, so model selection lives in the adapter.
#
# CODE_MODEL      roles that write code.
# RESEARCH_MODEL  roles whose work is investigation and analysis.
# AUDITOR_MODEL   the independent validator. It is meant to run on a different
#                 vendor from the roles it reviews, so verification is not the
#                 same model family checking itself. That separation is
#                 currently waived (see DECORRELATION_WAIVER).
CODE_MODEL = "claude-bridge/claude-sonnet-5-5"
RESEARCH_MODEL = "claude-bridge/claude-haiku-5-5"
AUDITOR_MODEL = "claude-bridge/claude-sonnet-5-5"

# TEMPORARY waiver of the validator vendor-decorrelation check. While it is a
# non-empty string the validator reports WAIVED (never PASS) with this reason.
# Set it to None to restore the enforced check.
DECORRELATION_WAIVER: str | None = (
    "commandcode subscription lapsed (2026-10-31); every role runs on Claude "
    "through claude-bridge until a second provider is available."
)

WRAPPER_MODELS = {
    "quant-validator": AUDITOR_MODEL,
    "quant-researcher": RESEARCH_MODEL,
    "data-scientist": RESEARCH_MODEL,
}

DEFAULT_MODEL = CODE_MODEL

DEFAULT_TOOLS = ("read", "grep", "find", "edit", "write", "bash")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    if not path.is_file():
        fail(f"required canonical file missing: {path}")
    return path.read_text(encoding="utf-8")


def git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        fail("unable to resolve canonical Git commit")


def canonical_inputs(root: Path) -> list[Path]:
    """Canonical files whose committed revision the wrapper stamp claims."""
    paths = [
        root / "agents" / "SUBAGENT-CONTRACT-SPEC.md",
        root / "agents" / "USER-INTERACTION-POLICY.md",
    ]
    for name in SPECIALISTS:
        paths.append(root / "agents" / name / "ROLE.md")
        paths.append(root / "agents" / name / "SUBAGENT.md")
    return paths


def assert_canonical_inputs_committed(root: Path) -> None:
    """Fail closed when HEAD does not describe the content being generated."""
    relative = sorted(str(path.relative_to(root)) for path in canonical_inputs(root))
    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain", "--", *relative],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        fail("unable to inspect canonical input status")
    dirty = [line for line in status.splitlines() if line.strip()]
    if dirty:
        fail(
            "canonical inputs are not committed at HEAD; refusing to stamp a "
            "revision that does not describe the generated content:\n  "
            + "\n  ".join(dirty)
        )


def recorded_dcp_hash(policy: str, part: str) -> str | None:
    for line in policy.splitlines():
        if part in line:
            match = re.search(r"`([0-9a-f]{64})`", line)
            if match:
                return match.group(1)
    return None


def assert_dcp_provenance(policy: str) -> None:
    """Fail closed when the DCP sources drift from their recorded hashes."""
    for part in DCP_PARTS:
        expected = recorded_dcp_hash(policy, part)
        if expected is None:
            fail(f"no recorded provenance hash for {part} in USER-INTERACTION-POLICY.md")
        actual = hashlib.sha256((Path(DCP_ROOT) / part).read_bytes()).hexdigest()
        if actual != expected:
            fail(f"DCP provenance drift for {part}: recorded {expected}, observed {actual}")


def wrapper(name: str, description: str, thinking: str, commit: str) -> str:
    tools = WRAPPER_TOOLS.get(name, DEFAULT_TOOLS)
    tools_block = "\n".join(f"  - {tool}" for tool in tools)
    model = WRAPPER_MODELS.get(name, DEFAULT_MODEL)
    return f"""---
name: {name}
description: {description}
model: {model}
thinking: {thinking}
tools:
{tools_block}
---

<!-- GENERATED PI WRAPPER — DO NOT EDIT MANUALLY. Canonical commit: `{commit}` -->

You are a Pi runtime wrapper, not the source of GQE role semantics.

Before acting, read these canonical files completely and obey them exactly:
- `{CANONICAL_ROOT}/agents/{name}/ROLE.md`
- `{CANONICAL_ROOT}/agents/{name}/SUBAGENT.md`
- `{CANONICAL_ROOT}/agents/SUBAGENT-CONTRACT-SPEC.md`
- `{CANONICAL_ROOT}/agents/USER-INTERACTION-POLICY.md`
- `{DCP_ROOT}/dcp_01.md`
- `{DCP_ROOT}/dcp_02.md`
- `{DCP_ROOT}/dcp_03.md`

The DCP documents govern communication only; they never expand role
authority or override governance, Task Packet scope, or a material validity
finding. If any canonical file above cannot be resolved, return
`DCP_CONTEXT_UNAVAILABLE` for interaction context or the canonical blocked
status for task authority. Do not delegate.
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate staging-only Pi wrappers from canonical contracts."
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = repo_root()
    output = Path(args.output).expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        fail(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    agents_root = root / "agents"
    for name in SPECIALISTS:
        read_text(agents_root / name / "ROLE.md")
        read_text(agents_root / name / "SUBAGENT.md")
    read_text(agents_root / "SUBAGENT-CONTRACT-SPEC.md")
    policy = read_text(agents_root / "USER-INTERACTION-POLICY.md")
    for part in DCP_PARTS:
        read_text(Path(DCP_ROOT) / part)

    assert_dcp_provenance(policy)
    assert_canonical_inputs_committed(root)

    commit = git_commit(root)
    for name, (description, thinking) in SPECIALISTS.items():
        (output / f"{name}.md").write_text(
            wrapper(name, description, thinking, commit),
            encoding="utf-8",
            newline="\n",
        )

    print("PASS: Pi wrapper bundle generated")
    print("dcp_provenance=VERIFIED")
    print(f"source_commit={commit}")
    print(f"output={output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
