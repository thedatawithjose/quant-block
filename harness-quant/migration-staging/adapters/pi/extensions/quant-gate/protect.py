#!/usr/bin/env python3
"""OS-level layer of quant-gate. Stdlib only.

  protect.py protect <project>   chmod a-w every protected file and record its sha256
  protect.py verify  <project>   exit 0 only if every protected file still matches its recorded sha256 and is read-only

Limit: chmod a-w stops accidents and most tool writes, not the file owner. `chattr +i` (root) is stronger.
The manifest is a detection aid: it reveals tampering, it does not prevent it.
"""
import hashlib, json, os, stat, sys
from pathlib import Path

POLICY = ".governance/quant-gate.json"
MANIFEST = ".governance/quant-gate.manifest.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def protected_files(root: Path):
    policy = json.loads((root / POLICY).read_text())
    for entry in policy.get("protected", []):
        p = (root / entry)
        if entry.endswith("/"):
            yield from (f for f in sorted(p.rglob("*")) if f.is_file())
        elif p.is_file():
            yield p
        else:
            print(f"warning: protected entry not found: {entry}", file=sys.stderr)


def main(argv) -> int:
    if len(argv) != 3 or argv[1] not in ("protect", "verify"):
        print(__doc__)
        return 64
    root = Path(argv[2]).resolve()
    if not (root / POLICY).is_file():
        print(f"no policy at {root / POLICY}", file=sys.stderr)
        return 66
    files = list(protected_files(root))
    if argv[1] == "protect":
        manifest = {}
        for f in files:
            manifest[str(f.relative_to(root))] = sha(f)
            f.chmod(f.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
        mf = root / MANIFEST
        if mf.exists():
            mf.chmod(0o644)
        mf.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        print(f"protected {len(files)} file(s); manifest: {MANIFEST}")
        return 0
    mf = root / MANIFEST
    if not mf.is_file():
        print("NO MANIFEST: run `protect` first", file=sys.stderr)
        return 2
    recorded = json.loads(mf.read_text())
    bad = 0
    for rel, digest in sorted(recorded.items()):
        p = root / rel
        if not p.is_file():
            print(f"MISSING  {rel}"); bad += 1; continue
        if sha(p) != digest:
            print(f"CHANGED  {rel}"); bad += 1
        elif os.access(p, os.W_OK):
            print(f"WRITABLE {rel}"); bad += 1
        else:
            print(f"OK       {rel}")
    for f in files:
        if str(f.relative_to(root)) not in recorded:
            print(f"UNRECORDED {f.relative_to(root)}"); bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
