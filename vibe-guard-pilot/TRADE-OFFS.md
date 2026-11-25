# Trade-offs of the local lock ("blindaje")

vibe-guard turns declared rules into commands that run deterministically and leave evidence.
It closes the gap "every rule is only prompt text". It does **not** make cheating impossible.
This document states what the lock does not give you.

## 1. Detectable, not preventable

The gate runs on the same machine, as the same user, as the agent it is meant to check.
Anything that user can write, the agent can write. Concretely:

- The agent can edit `.governance/enforcement.yaml` (change `command` to `true`, lower severity,
  set `type` to something weaker). The gate then reports a clean PASS for a weakened rule.
- The agent can edit or delete `gate.py`, `report.py`, `verdict.json`, or the evidence files,
  or hand-write a fake `verdict.json`.
- The checked commands themselves (tests, linters) live in the repo and can be edited to pass trivially.

What the gate does give: runs are reproducible, failures are preserved in timestamped
files (never overwritten), `verdict.json` records a SHA-256 of each evidence file, and
the config schema rejects policy-weakening flags. Tampering therefore tends to leave a trail
(diffs, mismatched hashes, missing evidence) that a human or a remote system can detect
after the fact. Detection depends on someone looking at the right artefact, with an
unmodified copy to compare against.

## 2. Denying "edit" does not block bash

Agent tool permissions that deny a file-edit tool do not stop a shell tool from running
`sed -i`, `echo > file`, `python -c`, `git checkout`, and so on. If the agent has bash,
it can write any file the OS user can write. Permission rules are a speed bump on the
well-behaved path, not a sandbox. Real prevention needs OS-level separation: a different
user owning the governance files (read-only to the agent), a container or VM with
read-only mounts, or a gate running somewhere the agent has no shell.

The gate also executes `verification.command` through `/bin/sh` with the caller's
privileges. Whoever controls the YAML controls what runs. Treat the config as code.

## 3. A verifier from the same model has correlated biases

This pilot's checks are deterministic commands, which sidesteps most of that problem: the
status comes from an exit code, not from a model's opinion, and `report.py` maps status to
wording with a fixed table. But the weak spot moves rather than vanishes:

- If the same model that wrote the code also writes the tests and the `command`, it can write
  tests that share its own blind spots (wrong spec reading, missing edge cases). A green gate
  then means "consistent with the author's understanding", not "correct".
- A model reviewing the evidence, or proposing which invariants matter, inherits those same
  biases. Errors it cannot see in its own output it will also not see in a second pass.
- Exit code 0 proves the command exited 0. It does not prove the command tests anything meaningful.

## 4. Explicitly out of scope

- **Remote lock** (GitHub branch protection, required status checks, CI running the gate on a
  clean checkout with secrets and config the agent cannot edit). This is the step that turns
  detection into prevention for merge and deploy. Not implemented here; no network or git is used.
- **A verifier from a different model family** (or a human reviewer) to break correlated bias
  and to review whether the invariants and tests are the right ones.
- OS-level isolation, signed or append-only evidence, trusted timestamps, and tamper-proof storage.
- Automatic verification of `manual_gate` approvals. They stay `BLOCKED`.
- Semantic checks of evidence content (the declared `evidence.path`/`evidence.type` fields are not
  validated beyond what the gate itself produces).
- Enforcement of `failure_policy` side effects (blocking merge, deploy, financial actions). The gate
  only reports and returns a non-zero exit code; wiring that into hooks or pipelines is up to the caller.
- A full YAML implementation. The parser covers the template's subset and errors on the rest.

## Summary

| Claim | Holds? |
|---|---|
| Rules become executable and repeatable | Yes |
| Unknown or unverifiable controls block (fail closed) | Yes |
| Failed checks leave evidence | Yes |
| An agent with shell access cannot bypass the gate | **No** |
| Passing the gate proves the software is correct | **No** |
| Independent verification | **No** (needs remote lock + different-family verifier) |
