# vibe-guard pilot

A deterministic, local, stdlib-only compliance gate for the `.governance/enforcement.yaml`
schema (`schema_version: "1.0"`, see
`GENTLE-QUANT-ECOSYSTEM/templates/project-governance/enforcement.template.yaml`).
It does not add a new governance format; it executes the existing one.

## Files

| File | Purpose |
|------|---------|
| `gate.py` | Runs each invariant's check, stores evidence, writes `verdict.json`, exits non-zero on a CRITICAL non-pass |
| `report.py` | Renders `verdict.json` as a plain-language Markdown acceptance report |
| `test_gate.py` | Seeded fail-closed tests (`unittest`) |
| `TRADE-OFFS.md` | What this lock does and does not guarantee |

Requires Python 3.8+ on Linux/macOS (uses `/bin/sh` and process groups). No third-party packages.

## Usage

```bash
# 1. Run the gate against a project (needs <project>/.governance/enforcement.yaml)
python3 gate.py --project /path/to/project
echo $?        # 0 = all CRITICAL invariants PASS, 1 = BLOCK, 2 = config/gate error

# 2. Render the acceptance report
python3 report.py /path/to/project/.governance/evidence/verdict.json
python3 report.py /path/to/project/.governance/evidence/verdict.json -o ACCEPTANCE.md

# 3. Run the self-tests
python3 test_gate.py
```

Options for `gate.py`: `--project DIR` (default `.`), `--config FILE` (default
`<project>/.governance/enforcement.yaml`), `--verdict FILE` (default
`<evidence dir>/verdict.json`).

## Behaviour

| Invariant situation | Status | Blocks (if CRITICAL) |
|---|---|---|
| `type` in `command`, `test`, `static_analysis`, `runtime_assertion`, exit code == `expected_exit_code` | `PASS` | no |
| same, exit code differs, or timeout | `FAIL` | yes |
| runnable type but `command` empty, bad timeout/exit code, missing `working_directory` | `UNKNOWN` | yes |
| `type` is `none`, `manual_gate`, missing, or unrecognised | `BLOCKED` | yes |

- Severity missing => treated as `CRITICAL`. Non-CRITICAL non-passes are recorded but do not change the exit code.
- `manual_gate` is never auto-passed: the gate cannot verify a human approval, so it stays `BLOCKED`.
- `enforcement_status: ENFORCED`, `evidence.required`, and any agent statement are claims, not evidence.
  Only a command the gate ran itself and whose exit code matched can produce `PASS`.
- Config that weakens the policy (`fail_closed != true`, `agent_claims_are_evidence != false`,
  `unknown_control_state != "BLOCK"`), wrong `schema_version`, or an unreadable file => exit 2, nothing is trusted.
- Per-invariant `working_directory`, `timeout_seconds`, `expected_exit_code` override `defaults`,
  which override built-ins (`.`, 300, 0). `working_directory` is relative to the project root.

## Evidence

Written under `policy.evidence.directory` (default `.governance/evidence`):

- `<INV-ID>-<UTCSTAMP>.json` per invariant per run: command, cwd, exit code, stdout, stderr
  (capped at 64 KiB each), timestamps, status, reason. Written for PASS, FAIL, UNKNOWN and BLOCKED alike.
  Files are timestamped and never overwritten, so failures are preserved.
- `verdict.json` (latest) and `verdict-<UTCSTAMP>.json` (archive).

`verdict.json` per invariant: `id`, `status`, `command`, `exit_code`, `evidence_path`
(plus `title`, `severity`, `reason`, `working_directory`, `expected_exit_code`, `evidence_sha256`).

## Minimal example

```yaml
schema_version: "1.0"
project: { name: "demo" }
policy:
  fail_closed: true
  agent_claims_are_evidence: false
  unknown_control_state: "BLOCK"
  evidence: { directory: ".governance/evidence", preserve_failed_checks: true }
invariants:
  - id: "DEMO-INV-001"
    title: "Unit tests pass"
    severity: "CRITICAL"
    verification:
      type: "test"
      command: "python3 -m unittest discover"
      working_directory: "."
      timeout_seconds: 120
      expected_exit_code: 0
```

The built-in YAML reader supports the subset used by the template (block maps/lists, scalars,
`[]`, `{}`, comments). Anchors, block scalars (`|`, `>`) and multi-line flow collections are
rejected with an error rather than guessed.

Read `TRADE-OFFS.md` before relying on this as a security boundary.
