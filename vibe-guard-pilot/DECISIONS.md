# vibe-guard pilot: frozen decisions

Status: frozen for the pilot. Four are decided (D1, D2, D3-D5 below); **exactly one stays a human decision: D1's remote lock.**

| ID | Decision | Owner |
|----|----------|-------|
| D1 | Local-first now; remote lock deferred | **HUMAN decision (remote part)** |
| D2 | Detection + hashes, not prevention | Decided |
| D3 | Different-family verifier, calibrated, fail-closed | Decided |
| D4 | No new lifecycle; Gentle Operational Loop is authoritative | Decided |
| D5 | Orchestrator is the single entry point; status-line convention only | Decided |

## D1. Enforcement home: local-first now; remote lock deferred (HUMAN DECISION)
- **Decided:** enforcement runs locally (`gate.py`, `report.py`, `verifier/calibrate.py`). Nothing is wired to a remote.
- **Human decision, not made here:** whether and when to add a remote lock (GitHub branch protection, required CI checks, protected evidence storage).
- **Why:** a local gate runs as the same OS user as the agent and can be weakened (see TRADE-OFFS.md). A remote lock is the only place the agent cannot rewrite, but it needs repository ownership, org settings, and a trust/cost choice that belongs to the owner.
- **How to apply:** until the human decides, treat a local PASS as "no tampering detected", not as "tamper-proof". Do not claim remote guarantees.
- **Status (owner, 2026-10-12):** **PARKED** — the owner deferred the remote lock for now. Local-first stands. No further action requested; revisit when convenient.

## D2. Isolation: detection, not prevention
- **Decided:** denying `edit` does NOT block `bash`. An agent with bash can write anything the OS user can write.
- Real prevention needs OS-level separation (different user/container for the verifier, read-only mounts for `.governance/` and `evidence/`, or a remote system).
- **The pilot provides:** detection and evidence hashes (SHA-256 in `verdict.json`, timestamped failures never overwritten). It does not provide prevention.
- The `builder-permissions` fragment is a speed bump for well-behaved runs only.

## D3. Verifier: different model family, calibrated, fail-closed
- **Decided:** the verifier is an OpenCode agent (`vibe-validator`) pinned to a model family different from the builder, read-only (edit deny, bash deny, task false), using `verifier/reviewer_prompt.md` (adversarial, JSON only).
- **Calibration:** `verifier/calibrate.py` runs the reviewer on labelled fixtures. It passes only if detection_rate >= 0.9 AND false_positive_rate <= 0.1 (configurable); otherwise exit non-zero.
- **Fail-closed:** an uncalibrated, failing, erroring, or malformed-output reviewer is not trusted; its PASS verdicts must not be used to release work.
- **Why:** a same-family reviewer shares the builder's blind spots; an unmeasured reviewer is theatre. Default calibration runs offline with a mock; the real reviewer is supplied via `--reviewer-cmd`.
- **Limit:** the mock proves the harness, not the real model. The real reviewer must be calibrated before it is trusted.

## D4. Project lifecycle: reuse, do not rebuild
- **Decided:** no new lifecycle is built. The existing Gentle Operational Loop spec is authoritative.
- The gate and report feed it (verdicts and evidence as inputs); they do not define phases or transitions.

## D5. Single entry point: the orchestrator
- **Decided:** the orchestrator already is the single entry point; no new component is built.
- **Deliverable:** a status-line convention that the orchestrator prints:

  `vibe-guard | gate=<PASS|BLOCK|ERROR> | verifier=<CALIBRATED|UNCALIBRATED|FAILED> | evidence=<n files, hashes ok|MISMATCH> | remote=NONE`

  `remote=NONE` stays until the human decision in D1 is made. Any value other than `gate=PASS` with `verifier=CALIBRATED` means not releasable (fail-closed).

## Calibration result (hard bank) — model chosen (D3 resolved)

Two candidate reviewers were calibrated against a HARD bank of subtle defects that are NOT
enumerated in the reviewer prompt (7 defects + 3 clean-but-suspicious fixtures):
off-by-one, inverted condition, swallowed error, wrong metric formula, a green test that
enforces a wrong value, a sign bug, and an off-by-one window.

| Reviewer (family) | Detection | False alarms | Errors | Result |
|---|---|---|---|---|
| `commandcode/deepseek/deepseek-v4-flash` | 7/7 | 1 (over-flagged a clean fixture) | 1 (plumbing) | FAILED |
| `commandcode/deepseek/deepseek-v4-pro` | 7/7 | 0 | 0 | PASSED |

**Decision:** the verifier is `commandcode/deepseek/deepseek-v4-pro` (a DIFFERENT family from the
Claude builder). Flash has equal detection but over-flags and is flakier, so it is rejected as the
inspector. Re-run this calibration whenever the model or the bank changes: a reviewer must be
re-proven, never assumed.

