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

PROMPT_MARKERS = (
    "GENERATED OPENCODE SPECIALIST PROMPT",
    "CANONICAL ROLE CONTRACT",
    "CANONICAL SPECIALIST CONTRACT",
    "CANONICAL SUBAGENT CONTRACT SPECIFICATION",
    "CANONICAL TASK PACKET CONTRACT",
    "CANONICAL HANDOFF CONTRACT",
    "CANONICAL USER-INTERACTION POLICY (BY REFERENCE)",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def bundle_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()

    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
    )

    for path in files:
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")

    return digest.hexdigest()


def first_json_object(raw: str) -> dict:
    decoder = json.JSONDecoder()

    for pos, char in enumerate(raw):
        if char != "{":
            continue

        try:
            candidate, _ = decoder.raw_decode(raw[pos:])
        except json.JSONDecodeError:
            continue

        if isinstance(candidate, dict):
            return candidate

    fail("no valid JSON object found in OpenCode output")


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


def main() -> int:
    root = repo_root()

    generator = (
        root
        / "adapters"
        / "opencode"
        / "generate_registration.py"
    )

    if not generator.is_file():
        fail(f"generator missing: {generator}")

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
        fail(f"active OpenCode config missing: {active_config}")

    active_hash_before = sha256(active_config)

    print("===== DETERMINISTIC GENERATION =====")

    with tempfile.TemporaryDirectory(
        prefix="gqe-opencode-validation-"
    ) as temp:

        temp_root = Path(temp)
        bundle_a = temp_root / "bundle-a"
        bundle_b = temp_root / "bundle-b"

        run(
            [
                sys.executable,
                str(generator),
                "--output",
                str(bundle_a),
            ],
            cwd=root,
        )

        run(
            [
                sys.executable,
                str(generator),
                "--output",
                str(bundle_b),
            ],
            cwd=root,
        )

        fingerprint_a = bundle_fingerprint(bundle_a)
        fingerprint_b = bundle_fingerprint(bundle_b)

        if fingerprint_a != fingerprint_b:
            fail(
                "repeated generation is not byte-identical: "
                f"{fingerprint_a} != {fingerprint_b}"
            )

        print(
            "PASS: repeated generation is byte-identical"
        )

        fragment = (
            bundle_a
            / "opencode-agent-fragment.json"
        )

        if not fragment.is_file():
            fail("generated OpenCode fragment missing")

        config_content = fragment.read_text(
            encoding="utf-8"
        )

        env = os.environ.copy()
        env["OPENCODE_CONFIG_CONTENT"] = config_content

        print()
        print("===== EFFECTIVE AGENT VALIDATION =====")

        for specialist in SPECIALISTS:
            completed = run(
                [
                    opencode,
                    "debug",
                    "agent",
                    specialist,
                ],
                cwd=bundle_a,
                env=env,
            )

            data = first_json_object(completed.stdout)

            mode = data.get("mode")
            description = data.get("description")
            tools = data.get("tools") or {}
            prompt = data.get("prompt") or ""

            if mode != "subagent":
                fail(
                    f"{specialist}: mode={mode!r}; "
                    "expected 'subagent'"
                )

            if not description:
                fail(
                    f"{specialist}: description missing"
                )

            if tools.get("task") is not False:
                fail(
                    f"{specialist}: task tool must be false; "
                    f"observed={tools.get('task')!r}"
                )

            missing_markers = [
                marker
                for marker in PROMPT_MARKERS
                if marker not in prompt
            ]

            if missing_markers:
                fail(
                    f"{specialist}: resolved prompt missing "
                    f"{missing_markers}"
                )

            print(
                f"PASS: {specialist} "
                "mode=subagent "
                "task=False "
                "prompt_resolved=yes"
            )

        print()
        print("===== AGENT DISCOVERY =====")

        discovery = run(
            [
                opencode,
                "agent",
                "list",
            ],
            cwd=bundle_a,
            env=env,
        ).stdout

        missing = [
            specialist
            for specialist in SPECIALISTS
            if specialist not in discovery
        ]

        if missing:
            fail(
                "runtime discovery missing specialists: "
                f"{missing}"
            )

        for specialist in SPECIALISTS:
            print(
                f"PASS: runtime discovery contains "
                f"{specialist}"
            )

    print()
    print("===== ACTIVE CONFIG SAFETY =====")

    active_hash_after = sha256(active_config)

    if active_hash_before != active_hash_after:
        fail(
            "active OpenCode configuration changed "
            "during validation"
        )

    print(
        "PASS: active OpenCode configuration is "
        "byte-identical"
    )

    print(
        "PASS: temporary bundle generation did not "
        "mutate active configuration"
    )

    print()
    print("===== RESULT =====")
    print(
        "PASS: OpenCode specialist registration "
        "validation completed successfully"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
