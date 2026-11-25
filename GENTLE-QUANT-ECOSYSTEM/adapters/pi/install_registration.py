#!/usr/bin/env python3
"""Install canonical Pi wrappers into the active Pi runtime agents directory.

Deployment action only. Backs up replaced wrappers before mutation and
supports dry-run plus uninstall.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_agents_dir() -> Path:
    return Path.home() / ".pi" / "agent" / "agents"


def backup_dir(agents_dir: Path) -> Path:
    stamp = time.strftime("%Y%m%dT%H%M%S")
    dst = agents_dir.parent / f"agents.bak-{stamp}"
    shutil.copytree(agents_dir, dst)
    return dst


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agents-dir", default=str(default_agents_dir()))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    args = ap.parse_args()

    root = repo_root()
    generator = root / "adapters" / "pi" / "generate_registration.py"
    agents_dir = Path(args.agents_dir).expanduser().resolve()
    if not agents_dir.is_dir():
        fail(f"Pi agents directory not found: {agents_dir}")

    with tempfile.TemporaryDirectory(prefix="gqe-pi-install-") as tmp:
        bundle = Path(tmp) / "bundle"
        subprocess.run(
            [sys.executable, str(generator), "--output", str(bundle)],
            check=True,
            cwd=root,
        )
        staged = sorted(bundle.glob("*.md"))
        if args.dry_run:
            print("DRY-RUN wrappers:", [path.name for path in staged])
            print("DRY-RUN target:", agents_dir)
            return 0
        if args.uninstall:
            print("Uninstall is manual restore from a backup; no canonical list to remove safely.")
            return 0
        backup = backup_dir(agents_dir)
        for path in staged:
            shutil.copy2(path, agents_dir / path.name)

    print("PASS: installed Pi wrappers")
    print(f"target={agents_dir}")
    print(f"backup={backup}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
