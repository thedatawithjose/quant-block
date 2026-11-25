#!/usr/bin/env python3
"""Install canonical Gentle specialists into an OpenCode config layer.

Deterministic, idempotent, reversible deployment of the registration bundle
produced by generate_registration.py into a user-owned OpenCode config layer.

This is a deployment action, not canonical authority. Canonical authority
remains agents/*/ROLE.md, agents/*/SUBAGENT.md and the contract specs.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
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

TASK_ALLOW = SPECIALISTS

PROMPTS_SUBDIR = "gentle-specialists"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_config() -> Path:
    return Path.home() / ".config" / "opencode" / "opencode.jsonc"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"config is not valid JSON: {path}: {exc}")


def generate_bundle(root: Path, dest: Path) -> Path:
    generator = root / "adapters" / "opencode" / "generate_registration.py"
    if not generator.is_file():
        fail(f"generator missing: {generator}")
    subprocess.run(
        [sys.executable, str(generator), "--output", str(dest)],
        check=True,
        cwd=root,
    )
    fragment = dest / "opencode-agent-fragment.json"
    if not fragment.is_file():
        fail("generator did not produce opencode-agent-fragment.json")
    return fragment


def planned_prompt_rel(name: str) -> str:
    return f"./{PROMPTS_SUBDIR}/prompts/{name}.md"


def apply_agents(config: dict) -> list[str]:
    changed: list[str] = []
    agents = config.setdefault("agent", {})
    for name in SPECIALISTS:
        entry = {
            "description": f"Gentle specialist: {name}",
            "mode": "subagent",
            "prompt": "{file:" + planned_prompt_rel(name) + "}",
            "tools": {"task": False},
        }
        if agents.get(name) != entry:
            agents[name] = entry
            changed.append(f"agent.{name}")
    return changed


def apply_task_permissions(config: dict) -> list[str]:
    changed: list[str] = []
    agents = config.setdefault("agent", {})
    go = agents.setdefault("gentle-orchestrator", {})
    perm = go.setdefault("permission", {})
    task = perm.setdefault("task", {})
    for name in TASK_ALLOW:
        if task.get(name) != "allow":
            task[name] = "allow"
            changed.append(f"agent.gentle-orchestrator.permission.task.{name}")
    return changed


def remove_install(config: dict) -> list[str]:
    changed: list[str] = []
    agents = config.get("agent") or {}
    for name in SPECIALISTS:
        if name in agents:
            del agents[name]
            changed.append(f"agent.{name}")
    go = agents.get("gentle-orchestrator") or {}
    task = ((go.get("permission") or {}).get("task")) or {}
    for name in TASK_ALLOW:
        if name in task:
            del task[name]
            changed.append(f"agent.gentle-orchestrator.permission.task.{name}")
    return changed


def backup(path: Path) -> Path:
    stamp = time.strftime("%Y%m%dT%H%M%S")
    dst = path.with_name(path.name + f".bak-{stamp}")
    shutil.copy2(path, dst)
    return dst


def install_prompts(bundle: Path, prompts_dir: Path) -> None:
    src = bundle / PROMPTS_SUBDIR
    if not src.is_dir():
        fail("bundle is missing gentle-specialists/")
    if prompts_dir.exists():
        shutil.rmtree(prompts_dir)
    prompts_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, prompts_dir)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(default_config()))
    ap.add_argument("--prompts-dir", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    args = ap.parse_args()

    root = repo_root()
    config_path = Path(args.config).expanduser().resolve()
    if not config_path.is_file():
        fail(f"config not found: {config_path}")

    prompts_dir = (
        Path(args.prompts_dir).expanduser().resolve()
        if args.prompts_dir
        else config_path.parent / PROMPTS_SUBDIR
    )

    active = (Path.home() / ".config" / "opencode").resolve()
    try:
        prompts_dir.relative_to(active)
    except ValueError:
        fail(f"prompts dir must live under {active}: {prompts_dir}")

    config = read_json(config_path)

    if args.uninstall:
        changed = remove_install(config)
        if args.dry_run:
            print("DRY-RUN uninstall changes:", changed or "none")
            return 0
        if not changed:
            print("PASS: nothing installed; no change")
            return 0
        b = backup(config_path)
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        if prompts_dir.exists():
            shutil.rmtree(prompts_dir)
        print("PASS: uninstalled", changed)
        print(f"backup={b}")
        return 0

    with tempfile.TemporaryDirectory(prefix="gqe-install-") as tmp:
        bundle = Path(tmp) / "bundle"
        generate_bundle(root, bundle)

        agents_changed = apply_agents(config)
        task_changed = apply_task_permissions(config)

        if args.dry_run:
            print("DRY-RUN agent changes:", agents_changed or "none")
            print("DRY-RUN permission changes:", task_changed or "none")
            print("DRY-RUN prompts dir:", prompts_dir)
            return 0

        b = backup(config_path)
        install_prompts(bundle, prompts_dir)
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    print("PASS: installed Gentle specialists")
    print("agent changes:", agents_changed or "none")
    print("permission changes:", task_changed or "none")
    print(f"prompts: {prompts_dir}")
    print(f"backup: {b}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
