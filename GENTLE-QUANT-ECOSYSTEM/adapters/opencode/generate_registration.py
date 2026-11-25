#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


SPECIALISTS = {
    "ui-ux-engineer": "ISOLATED_PREFERRED",
    "software-engineer": "ISOLATED_PREFERRED",
    "data-engineer": "ISOLATED_PREFERRED",
    "data-scientist": "ISOLATED_PREFERRED",
    "quant-data-engineer": "ISOLATED_PREFERRED",
    "quant-researcher": "ISOLATED_PREFERRED",
    "quant-developer": "ISOLATED_PREFERRED",
    "quant-validator": "ISOLATED_REQUIRED",
}

REQUIRED_FRONTMATTER = {
    "role_contract": "ROLE.md",
    "contract_spec": "../SUBAGENT-CONTRACT-SPEC.md",
    "contract_version": "1.0",
    "invocation": "ORCHESTRATOR_ONLY",
    "delegation": "FORBIDDEN",
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    if not path.is_file():
        fail(f"required canonical file missing: {path}")
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = read_text(path)

    if not text.startswith("---\n"):
        fail(f"frontmatter missing: {path}")

    end = text.find("\n---", 4)
    if end == -1:
        fail(f"frontmatter terminator missing: {path}")

    block = text[4:end]
    result: dict[str, str] = {}

    for raw in block.splitlines():
        if not raw.strip():
            continue

        # Ignore nested metadata fields.
        if raw.startswith((" ", "\t")):
            continue

        if ":" not in raw:
            continue

        key, value = raw.split(":", 1)
        value = value.strip()

        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {"'", '"'}
        ):
            value = value[1:-1]

        result[key.strip()] = value

    return result


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


def fingerprint(root: Path, paths: list[Path]) -> str:
    digest = hashlib.sha256()

    def label(path: Path) -> str:
        try:
            return path.relative_to(root).as_posix()
        except ValueError:
            return path.resolve().as_posix()

    for path in sorted(paths, key=label):
        relative = label(path)
        data = path.read_bytes()

        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")

    return digest.hexdigest()


def ensure_staging_output(output: Path) -> None:
    output = output.resolve()

    active_config = (
        Path.home() / ".config" / "opencode"
    ).resolve()

    try:
        output.relative_to(active_config)
    except ValueError:
        pass
    else:
        fail(
            "registration generator is staging-only and refuses to write "
            "inside ~/.config/opencode"
        )

    if output.exists() and any(output.iterdir()):
        fail(f"output directory is not empty: {output}")

    output.mkdir(parents=True, exist_ok=True)


def validate_specialist(
    name: str,
    expected_context: str,
    subagent_path: Path,
) -> dict[str, str]:

    fm = parse_frontmatter(subagent_path)

    if fm.get("name") != name:
        fail(
            f"{name}: frontmatter name mismatch: "
            f"{fm.get('name')!r}"
        )

    if not fm.get("description"):
        fail(f"{name}: description missing")

    for key, expected in REQUIRED_FRONTMATTER.items():
        observed = fm.get(key)

        if observed != expected:
            fail(
                f"{name}: {key} expected {expected!r}, "
                f"observed {observed!r}"
            )

    observed_context = fm.get("context")

    if observed_context != expected_context:
        fail(
            f"{name}: context expected {expected_context!r}, "
            f"observed {observed_context!r}"
        )

    return fm


def generated_prompt(
    *,
    name: str,
    description: str,
    context_policy: str,
    source_commit: str,
    source_fingerprint: str,
    role_text: str,
    subagent_text: str,
    subagent_contract: str,
    task_contract: str,
    handoff_contract: str,
    interaction_policy_abspath: str,
) -> str:

    return f"""# GENERATED OPENCODE SPECIALIST PROMPT

> GENERATED DEPLOYMENT ARTIFACT — DO NOT EDIT MANUALLY.
>
> Canonical source commit: `{source_commit}`
>
> Canonical source fingerprint: `{source_fingerprint}`

## Runtime Identity

- Specialist: `{name}`
- Description: {description}
- Runtime mode: `subagent`
- Context policy: `{context_policy}`
- Delegation: `FORBIDDEN`

## Runtime Authority Boundary

This static registration artifact does **not** authorize project work.

Authoritative project execution requires a current canonical Task Packet
with status:

`READY`

and all governance, upstream handoffs, skills, evidence requirements,
invariants, and human-authority boundaries required by that Task Packet.

If required authority is missing, contradictory, stale, or unavailable,
return:

`BLOCKED`

If the runtime cannot preserve a required canonical capability, return:

`CAPABILITY_BLOCKED`

Do not infer approval from conversation history, memory, runtime success,
or this registration artifact.

Do not delegate this specialist authority to another agent.

Canonical execution states remain:

- `COMPLETED`
- `BLOCKED`
- `INCONCLUSIVE`

Runtime process success does not automatically mean canonical completion.

---

# CANONICAL ROLE CONTRACT

{role_text.rstrip()}

---

# CANONICAL SPECIALIST CONTRACT

{subagent_text.rstrip()}

---

# CANONICAL SUBAGENT CONTRACT SPECIFICATION

{subagent_contract.rstrip()}

---

# CANONICAL TASK PACKET CONTRACT

{task_contract.rstrip()}

---

# CANONICAL HANDOFF CONTRACT

{handoff_contract.rstrip()}

---

# CANONICAL USER-INTERACTION POLICY (BY REFERENCE)

Before material work, read completely and obey as communication contract
only — it never expands role authority or overrides governance:

- `{interaction_policy_abspath}`
- `/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_01.md`
- `/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_02.md`
- `/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_03.md`

These are absolute canonical paths. If any of these cannot be resolved,
return `DCP_CONTEXT_UNAVAILABLE`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a staging-only OpenCode registration bundle "
            "from canonical Gentle Quant specialist contracts."
        )
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Empty staging directory for generated artifacts.",
    )

    args = parser.parse_args()

    root = repo_root()
    output = Path(args.output).expanduser()

    ensure_staging_output(output)

    agents_root = root / "agents"

    interaction_policy = agents_root / "USER-INTERACTION-POLICY.md"
    dcp_paths = [
        Path("/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_01.md"),
        Path("/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_02.md"),
        Path("/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_03.md"),
    ]

    common_paths = [
        agents_root / "SUBAGENT-CONTRACT-SPEC.md",
        agents_root / "TASK-PACKET-CONTRACT-SPEC.md",
        agents_root / "HANDOFF-CONTRACT-SPEC.md",
        interaction_policy,
        *dcp_paths,
    ]

    specialist_paths: list[Path] = []

    frontmatters: dict[str, dict[str, str]] = {}

    for name, expected_context in SPECIALISTS.items():
        role = agents_root / name / "ROLE.md"
        subagent = agents_root / name / "SUBAGENT.md"

        read_text(role)
        read_text(subagent)

        specialist_paths.extend([role, subagent])

        frontmatters[name] = validate_specialist(
            name,
            expected_context,
            subagent,
        )

    source_paths = common_paths + specialist_paths

    for path in common_paths:
        read_text(path)

    source_commit = git_commit(root)
    source_fingerprint = fingerprint(root, source_paths)

    prompt_root = (
        output
        / "gentle-specialists"
        / "prompts"
    )

    prompt_root.mkdir(parents=True)

    subagent_contract = read_text(
        agents_root / "SUBAGENT-CONTRACT-SPEC.md"
    )

    task_contract = read_text(
        agents_root / "TASK-PACKET-CONTRACT-SPEC.md"
    )

    handoff_contract = read_text(
        agents_root / "HANDOFF-CONTRACT-SPEC.md"
    )

    generated_agents: dict[str, dict] = {}
    manifest_agents: dict[str, dict] = {}

    for name, expected_context in SPECIALISTS.items():
        fm = frontmatters[name]

        role_path = agents_root / name / "ROLE.md"
        subagent_path = agents_root / name / "SUBAGENT.md"

        prompt_rel = (
            Path("gentle-specialists")
            / "prompts"
            / f"{name}.md"
        )

        prompt_path = output / prompt_rel

        prompt = generated_prompt(
            name=name,
            description=fm["description"],
            context_policy=expected_context,
            source_commit=source_commit,
            source_fingerprint=source_fingerprint,
            role_text=read_text(role_path),
            subagent_text=read_text(subagent_path),
            subagent_contract=subagent_contract,
            task_contract=task_contract,
            handoff_contract=handoff_contract,
            interaction_policy_abspath=str(interaction_policy.resolve()),
        )

        prompt_path.write_text(
            prompt,
            encoding="utf-8",
            newline="\n",
        )

        generated_agents[name] = {
            "description": fm["description"],
            "mode": "subagent",
            "prompt": f"{{file:./{prompt_rel.as_posix()}}}",
            "tools": {
                "task": False
            },
        }

        manifest_agents[name] = {
            "context": expected_context,
            "delegation": "FORBIDDEN",
            "invocation": "ORCHESTRATOR_ONLY",
            "prompt": prompt_rel.as_posix(),
        }

    config_fragment = {
        "agent": generated_agents
    }

    manifest = {
        "schema_version": "1.0",
        "artifact_class": "REGISTRATION_ONLY",
        "authoritative_for_project_work": False,
        "adapter": "opencode",
        "source_commit": source_commit,
        "source_fingerprint": source_fingerprint,
        "agents": manifest_agents,
    }

    (
        output / "opencode-agent-fragment.json"
    ).write_text(
        json.dumps(
            config_fragment,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    (
        output
        / "gentle-specialists"
        / "bundle-manifest.json"
    ).write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print("PASS: OpenCode registration bundle generated")
    print(f"source_commit={source_commit}")
    print(f"source_fingerprint={source_fingerprint}")
    print(f"output={output.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
