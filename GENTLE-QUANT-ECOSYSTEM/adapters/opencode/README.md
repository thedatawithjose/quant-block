# OpenCode Runtime Adapter

OpenCode runtime adapter for Gentle and its Quant capability.

## Authority

This adapter implements:

`../RUNTIME-ADAPTER-SPEC.md`

Canonical ecosystem definitions remain under:

- `../../governance/`
- `../../skills/`
- `../../agents/`
- `../../templates/`

OpenCode is a deployment target, not a source of truth.

## Responsibility

This adapter translates canonical Gentle Quant Ecosystem contracts into mechanisms supported by OpenCode.

Conceptually:

Canonical Governance
        +
Canonical Specialist ROLE
        +
Canonical Specialist Execution Contract
        +
Canonical Skills
        +
Project Governance
        |
        v
OpenCode Adapter
        |
        v
OpenCode Runtime
        |
        v
Gentle-controlled specialist execution

## Portability Rule

No OpenCode-specific field, prompt format, tool, permission, or filesystem convention may become authoritative outside this adapter.

If another runtime is used, such as Cline, Codex, Claude Code, or Pi, the canonical ecosystem MUST remain unchanged and only the runtime adapter may differ.

## Fail-Closed Rule

If OpenCode cannot reliably provide a capability required by governance, this adapter MUST report:

`CAPABILITY_BLOCKED`

It MUST NOT silently weaken:

- specialist isolation;
- governance;
- independent validation;
- enforcement;
- human approval gates;
- role boundaries.

## Generated Artifacts

Any files generated under OpenCode configuration directories are deployment artifacts.

They MUST be reproducible from the canonical Gentle Quant Ecosystem and MUST NOT become the maintained source of truth.

## Current Status

Adapter maturity:

`EXPERIMENTAL`

It MUST remain experimental until its capability manifest and validation suite demonstrate compliance with `RUNTIME-ADAPTER-SPEC.md`.
