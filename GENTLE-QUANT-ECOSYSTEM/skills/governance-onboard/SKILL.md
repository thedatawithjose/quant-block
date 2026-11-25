---
name: governance-onboard
description: "Trigger: new project, existing project onboarding, initialize governance. Build the project's governance workspace before development begins."
license: Apache-2.0
metadata:
  author: "datawithjose"
  version: "1.0"
---

## Activation Contract

Load when a new project is created, an existing repository enters the Gentle Quant Ecosystem, or `.governance/` is absent or incomplete.

Do not implement product features during onboarding.

## Hard Rules

- Inspect the repository before asking the user questions.
- Never ask for technical facts that can be reliably discovered from files, configuration, tests, Git, or CI.
- Ask the user only for intent, domain meaning, unacceptable failures, risk boundaries, invariants, priorities, approval rules, and other information requiring human authority.
- Ask at most 3–5 focused questions per round.
- Never invent project rules from assumptions.
- Distinguish context, preference, requirement, invariant, and critical invariant.
- A documented invariant is not considered enforced unless a real verification mechanism exists.
- If enforcement does not exist, mark it explicitly as `NOT_ENFORCED` or require a manual gate.
- Require human approval before the generated governance workspace becomes authoritative.
- Build governance artifacts from the canonical templates under `../../templates/project-governance/`; do not invent alternate schemas without explicit human approval.

## Decision Gates

| Condition | Action |
|---|---|
| Repository can answer the question | Inspect; do not ask user |
| Business/domain intent is required | Ask user |
| Rule can be automatically verified | Map to executable enforcement |
| Rule could be automated but is not yet | Mark `TEST_REQUIRED` |
| Rule cannot currently be automated | Mark `MANUAL_GATE` |
| Critical project information remains unknown | Do not finalize onboarding |

## Execution Steps

1. Inspect repository structure, stack, dependencies, tests, CI, configuration, documentation, Git history, data boundaries, external integrations, and deployment surfaces.
2. Summarize discovered facts separately from assumptions and unknowns.
3. Interview the project owner adaptively in rounds of at most 3–5 questions.
4. Classify each relevant answer as context, preference, requirement, invariant, or critical invariant.
5. Identify protected semantic surfaces, then select required specialist roles through `../../orchestration/GLOBAL-TASK-ROUTING.md`. Repository type is context, not a blanket specialist selector.
6. Map every invariant to an enforcement status and verification mechanism.
7. Load the canonical project-governance templates.
8. Instantiate the project governance workspace from those templates and preserve their required fields. `ROUTING.yaml` inherits the global taxonomy; populate only project context, protected surfaces, human gates, forbidden operations, and narrow overrides.
9. Present unresolved assumptions, unenforced rules, and material risks.
10. Request explicit human approval before activation.

## Output Contract

Prepare:

- `.governance/CONTRACT.md`
- `.governance/INVARIANTS.md`
- `.governance/enforcement.yaml`
- `.governance/TEAM.yaml`
- `.governance/ROUTING.yaml`

Also return:

- discovered facts;
- unanswered questions;
- declared invariants;
- enforcement status for each invariant;
- manual gates;
- specialist roles required;
- explicit statement that governance is either `READY_FOR_APPROVAL` or `NOT_READY`.

## References

- `../../governance/core/START-HERE.md`
- `../../governance/core/AGENT-RULES.md`
- `../../governance/core/ENFORCEMENT-MATRIX-TEMPLATE.md`
- `../../templates/project-governance/CONTRACT.template.md`
- `../../templates/project-governance/INVARIANTS.template.md`
- `../../templates/project-governance/enforcement.template.yaml`
- `../../templates/project-governance/TEAM.template.yaml`
- `../../templates/project-governance/ROUTING.template.yaml`
