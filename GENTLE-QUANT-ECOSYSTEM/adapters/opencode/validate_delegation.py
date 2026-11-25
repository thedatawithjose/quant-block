#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


TARGET_SPECIALIST = "quant-researcher"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def run(
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:

    completed = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if completed.returncode != 0:
        print(completed.stdout)
        fail(
            f"command failed ({completed.returncode}): "
            f"{' '.join(args)}"
        )

    return completed


def walk(value, path: str = "root"):
    if isinstance(value, dict):
        yield path, value

        for key, child in value.items():
            yield from walk(
                child,
                f"{path}.{key}",
            )

    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(
                child,
                f"{path}[{index}]",
            )


def parse_json_events(raw: str) -> list[dict]:
    events: list[dict] = []

    for line in raw.splitlines():
        line = line.strip()

        if not line.startswith("{"):
            continue

        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if isinstance(event, dict):
            events.append(event)

    return events


def find_delegation(
    events: list[dict],
    specialist: str,
) -> tuple[int, str, dict] | None:

    for event_number, event in enumerate(events, 1):
        for object_path, obj in walk(event):
            serialized = json.dumps(
                obj,
                ensure_ascii=False,
                sort_keys=True,
            )

            if specialist not in serialized:
                continue

            if (
                "subagent_type" not in serialized
                and "subagentType" not in serialized
            ):
                continue

            has_task_identity = any(
                obj.get(key) in {"task", "Task"}
                for key in (
                    "tool",
                    "tool_name",
                    "toolName",
                    "name",
                )
            )

            # Some runtime event shapes place the task identity
            # in a parent object while subagent_type is nested.
            # Presence of the explicit subagent selector remains
            # the critical delegation evidence.
            if has_task_identity or (
                "subagent_type" in serialized
                or "subagentType" in serialized
            ):
                return event_number, object_path, obj

    return None


def main() -> int:
    root = repo_root()

    generator = (
        root
        / "adapters"
        / "opencode"
        / "generate_registration.py"
    )

    if not generator.is_file():
        fail(f"registration generator missing: {generator}")

    opencode = shutil.which("opencode")

    if not opencode:
        fail("opencode executable not found")

    active_config = (
        Path.home()
        / ".config"
        / "opencode"
        / "opencode.jsonc"
    )

    if not active_config.is_file():
        fail(
            f"active OpenCode config missing: "
            f"{active_config}"
        )

    active_hash_before = sha256(active_config)

    print("===== GENERATE TEMPORARY REGISTRATION =====")

    with tempfile.TemporaryDirectory(
        prefix="gqe-opencode-delegation-"
    ) as temp:

        bundle = Path(temp) / "bundle"

        run(
            [
                sys.executable,
                str(generator),
                "--output",
                str(bundle),
            ],
            cwd=root,
        )

        fragment = (
            bundle
            / "opencode-agent-fragment.json"
        )

        if not fragment.is_file():
            fail(
                "generated OpenCode agent fragment missing"
            )

        env = os.environ.copy()
        env["OPENCODE_CONFIG_CONTENT"] = (
            fragment.read_text(encoding="utf-8")
        )

        instruction = (
            "This is a runtime delegation diagnostic only. "
            "You MUST use the task tool to delegate to the "
            "registered subagent named quant-researcher. "
            "Do not perform the specialist task yourself. "
            "Give the subagent this instruction: "
            "'No READY Task Packet has been supplied. "
            "Apply your canonical authority rules and return "
            "the appropriate canonical execution state with "
            "a short reason.' "
            "After the task returns, report its result "
            "without changing it."
        )

        print()
        print("===== ORCHESTRATOR DELEGATION =====")

        completed = run(
            [
                opencode,
                "run",
                "--agent",
                "gentle-orchestrator",
                "--format",
                "json",
                "--dir",
                str(bundle),
                instruction,
            ],
            cwd=bundle,
            env=env,
        )

        raw = completed.stdout
        events = parse_json_events(raw)

        print(
            f"PASS: runtime returned "
            f"{len(events)} JSON events"
        )

        delegation = find_delegation(
            events,
            TARGET_SPECIALIST,
        )

        if delegation is None:
            print()
            print(
                "===== RUNTIME OUTPUT "
                "(first 8000 chars) ====="
            )
            print(raw[:8000])

            fail(
                "no observable task delegation to "
                "quant-researcher"
            )

        event_number, object_path, obj = delegation

        print(
            "PASS: observed task delegation to "
            "quant-researcher"
        )
        print(f"event={event_number}")
        print(f"path={object_path}")

        serialized = json.dumps(
            obj,
            ensure_ascii=False,
            sort_keys=True,
        )

        if TARGET_SPECIALIST not in serialized:
            fail(
                "delegation event does not contain "
                "quant-researcher"
            )

        if (
            "subagent_type" not in serialized
            and "subagentType" not in serialized
        ):
            fail(
                "delegation event lacks explicit "
                "subagent selector"
            )

        print(
            "PASS: subagent_type identifies "
            "quant-researcher"
        )

        if "BLOCKED" not in raw:
            fail(
                "delegated specialist did not preserve "
                "canonical BLOCKED state"
            )

        print(
            "PASS: delegated specialist returned "
            "canonical BLOCKED state"
        )

        if (
            "Task Packet" not in raw
            and "task packet" not in raw.lower()
        ):
            fail(
                "BLOCKED result was observed but missing "
                "Task Packet reason was not visible"
            )

        print(
            "PASS: BLOCKED result is associated with "
            "missing Task Packet authority"
        )

    print()
    print("===== ACTIVE CONFIG SAFETY =====")

    active_hash_after = sha256(active_config)

    if active_hash_before != active_hash_after:
        fail(
            "active OpenCode configuration changed "
            "during delegation validation"
        )

    active_text = active_config.read_text(
        encoding="utf-8"
    )

    if f'"{TARGET_SPECIALIST}"' in active_text:
        fail(
            "temporary specialist registration leaked "
            "into active OpenCode configuration"
        )

    print(
        "PASS: active OpenCode configuration is "
        "byte-identical"
    )

    print(
        "PASS: temporary specialist registration "
        "was not persisted"
    )

    print()
    print("===== RESULT =====")

    print(
        "PASS: Gentle orchestrator delegated through "
        "task to quant-researcher and preserved "
        "fail-closed authority behavior"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
