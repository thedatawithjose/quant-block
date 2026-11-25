# Gentle Operational Loop V1

## Purpose

This specification defines the canonical operational loop used by Gentle-AI to govern and orchestrate work. Quant workflow requirements remain mandatory for Quant-classified portions.

Gentle-AI is the primary orchestration harness.

Runtimes such as OpenCode, Cline, Codex, Claude Code, Pi, or others are execution backends reached through adapters.

The runtime does not own:

- project authority;
- specialist authority;
- governance;
- routing semantics;
- invariants;
- evidence requirements;
- human approval.

---

## 1. Human Authority

The user acts as:

`Portfolio Manager / Head of Quant`

Human authority remains final for decisions reserved by project governance, including where applicable:

- project objectives;
- material risk acceptance;
- critical invariant changes;
- production approval;
- live financial side effects;
- governance overrides.

Gentle MUST NOT manufacture human approval.

---

## 2. Canonical Loop

Every authoritative Quant task follows this logical lifecycle:

1. `REQUEST_RECEIVED`
2. `PROJECT_CONTEXT_RESOLVED`
3. `GOVERNANCE_PREFLIGHT`
4. `TASK_CLASSIFIED`
5. `ROUTE_SELECTED`
6. `TASK_PACKET_READY`
7. `SPECIALIST_EXECUTION`
8. `SPECIALIST_RESULT`
9. `HANDOFF_EVALUATION`
10. `VALIDATION`
11. `ENFORCEMENT_EVALUATION`
12. `HUMAN_GATE`
13. `COMPLETED`

Not every task requires every specialist, but required gates MUST NOT be skipped.

---

## 3. Terminal and Blocking States

The loop MUST preserve these non-success states:

- `BLOCKED`
- `CAPABILITY_BLOCKED`
- `INCONCLUSIVE`
- `HUMAN_DECISION_REQUIRED`
- `CANCELLED`

A runtime process exiting successfully does not imply canonical task success.

---

## 4. REQUEST_RECEIVED

Gentle receives the user's objective.

At this stage Gentle MUST determine:

- what outcome the user wants;
- which project or workspace applies;
- whether the request is authoritative project work;
- whether sufficient project identity is known.

Gentle MUST NOT immediately delegate implementation before governance preflight.

---

## 5. PROJECT_CONTEXT_RESOLVED

Gentle resolves the project workspace.

Where available it identifies:

- repository root;
- Git revision;
- project governance;
- source tree;
- tests;
- existing specifications;
- relevant authoritative artifacts.

If the project cannot be identified safely:

`BLOCKED`

or request the minimum human clarification required.

---

## 6. GOVERNANCE_PREFLIGHT

Gentle checks for:

- `.governance/CONTRACT.md`
- `.governance/INVARIANTS.md`
- `.governance/enforcement.yaml`
- `.governance/TEAM.yaml`
- `.governance/ROUTING.yaml`

If governance is absent:

route to `governance-onboard`.

If governance is contradictory or materially incomplete:

`BLOCKED`

unless the active task is governance creation or repair.

Governance preflight occurs before authoritative specialist execution.

---

## 7. TASK_CLASSIFIED

Gentle classifies the work according to canonical routing semantics.

Primary task classes are defined in `GLOBAL-TASK-ROUTING.md` and include:

- `UI_UX`
- `SOFTWARE_ENGINEERING`
- `DATA_ENGINEERING`
- `DATA_SCIENCE`
- `QUANT_RESEARCH`
- `QUANT_IMPLEMENTATION`
- `QUANT_VALIDATION`
- `OPERATIONS`
- `MIXED`

Classification determines required specialists and gates.

The user MUST NOT need to know which specialist to select. Repository type supplies context; it MUST NOT select the specialist.

---

## 8. ROUTE_SELECTED

Gentle selects the smallest sufficient specialist workflow.

Canonical examples:

### Research

`quant-researcher -> quant-validator -> human`

### Product UI

`ui-ux-engineer -> software-engineer` when implementation is required

### Ordinary Application Work

`software-engineer`

### Data Quality

`data-engineer`

### Research to Production

`quant-researcher -> quant-developer -> quant-validator -> human`

### Data to Research

`quant-data-engineer -> quant-validator(data) -> quant-researcher`

### Production Implementation

`quant-developer -> quant-validator -> human`

### Governance Change

`quant-orchestrator -> quant-validator -> human`

Project `.governance/ROUTING.yaml` refines the global result with protected surfaces, invariants, gates, and narrow overrides. It MUST NOT route routine work to Quant solely because the repository is quantitative.

---

## 9. TASK_PACKET_READY

Before specialist execution, Gentle creates or validates a Task Packet conforming to:

`agents/TASK-PACKET-CONTRACT-SPEC.md`

using:

`templates/tasks/TASK-PACKET.template.yaml`

The Task Packet MUST include the required authority package.

A specialist MUST NOT begin authoritative work unless the packet status is:

`READY`

Missing authority produces:

`BLOCKED`

Missing runtime capability produces:

`CAPABILITY_BLOCKED`

---

## 10. SPECIALIST_EXECUTION

Gentle dispatches the Task Packet through the selected runtime adapter.

The adapter MUST preserve:

- assigned role;
- role contract;
- context policy;
- delegation policy;
- governance;
- invariants;
- required skills;
- upstream handoffs;
- verification requirements;
- evidence requirements;
- human authority boundaries.

The specialist MUST NOT receive broader authority than the Task Packet grants.

---

## 11. SPECIALIST_RESULT

Every specialist execution terminates with a canonical state:

- `COMPLETED`
- `BLOCKED`
- `INCONCLUSIVE`

Validator property results use:

- `PASS`
- `FAIL`
- `INCONCLUSIVE`
- `NOT_TESTED`
- `BLOCKED`

Gentle MUST preserve the specialist's failure state.

---

## 12. EVIDENCE

Specialist assertions are not sufficient evidence.

Where applicable, Gentle requires evidence such as:

- command output;
- test reports;
- hashes;
- fingerprints;
- diffs;
- generated artifacts;
- runtime logs;
- numerical oracles;
- validation reports.

Evidence requirements come from:

- governance;
- Task Packet;
- role contract;
- required skill;
- enforcement configuration.

---

## 13. HANDOFF_EVALUATION

When another specialist must continue the work, the source specialist produces a Handoff conforming to:

`agents/HANDOFF-CONTRACT-SPEC.md`

using:

`templates/handoffs/HANDOFF.template.yaml`

Gentle validates:

- source role;
- target role;
- status;
- authoritative inputs;
- outputs;
- verification;
- invariant impact;
- limitations;
- stale state;
- human decisions required.

Conversation summaries MUST NOT replace required Handoffs.

---

## 14. NEXT SPECIALIST

If routing requires another specialist, Gentle creates a new Task Packet.

Authority moves through:

`Task Packet -> Specialist -> Handoff -> New Task Packet`

Specialists MUST NOT silently delegate authority to one another.

Gentle remains responsible for routing.

---

## 15. INDEPENDENT VALIDATION

Where independent validation is required, Gentle dispatches:

`quant-validator`

using:

`context: ISOLATED_REQUIRED`

The validator receives authoritative artifacts and evidence required for validation.

It MUST NOT rely on hidden reasoning from the creator.

If the runtime cannot preserve required isolation:

`CAPABILITY_BLOCKED`

---

## 16. ENFORCEMENT_EVALUATION

Gentle evaluates project:

`.governance/enforcement.yaml`

Required controls MUST be executed where mechanically supported.

Examples include:

- tests;
- commands;
- static analysis;
- runtime assertions;
- manual gates.

Critical invariant failure MUST fail closed.

An agent statement that a control passed is not sufficient when executable evidence is required.

---

## 17. HUMAN_GATE

Gentle escalates to human authority when required by governance.

Possible reasons include:

- production release;
- residual risk acceptance;
- critical invariant change;
- unresolved specialist disagreement;
- governance override;
- live financial side effect;
- material uncertainty.

The system state becomes:

`HUMAN_DECISION_REQUIRED`

until an explicit human decision is supplied.

---

## 18. COMPLETED

A task may enter:

`COMPLETED`

only when all required conditions are satisfied.

Where applicable these include:

- required specialist work completed;
- required Handoffs valid;
- required independent validation complete;
- enforcement controls satisfied;
- blocking findings resolved;
- required human decision supplied;
- authoritative outputs identified;
- evidence retained.

`COMPLETED` does not automatically mean deployed or live.

---

## 19. Stale Authority

If a material authoritative artifact changes during the workflow, Gentle MUST determine downstream impact.

Affected work MUST be stopped or marked stale.

Gentle MUST regenerate or update:

- Task Packets;
- Handoffs;
- verification;
- validation;

where required.

No silent continuation under stale authority.

---

## 20. Runtime Selection

Gentle selects an adapter capable of preserving the required canonical semantics.

Adapter capability is evaluated against its capability manifest.

If a required capability is unavailable:

`CAPABILITY_BLOCKED`

Gentle MUST NOT silently weaken governance to accommodate a runtime.

Changing runtime MUST NOT change canonical project semantics.

---

## 21. Memory

Memory systems such as Engram MAY provide contextual assistance.

Memory is not authoritative project state.

Authority comes from versioned artifacts such as:

- governance;
- Task Packets;
- Handoffs;
- specifications;
- source code;
- tests;
- evidence;
- Git history.

Memory MUST NOT silently override them.

---

## 22. User Experience

The user interacts primarily with Gentle.

The user SHOULD NOT need to manually coordinate:

- Data Engineer;
- Quant Researcher;
- Quant Developer;
- Quant Validator;
- runtime adapters.

Gentle handles internal routing and returns concise decision-relevant information to the user.

The system SHOULD ask the user only for information or decisions requiring human authority.

---

## 23. V1 Success Criterion

Gentle Operational Loop V1 is considered demonstrated when a disposable project can complete the following workflow:

`User request`

→ governance preflight

→ automatic task classification

→ automatic specialist routing

→ Task Packet creation

→ specialist execution

→ evidence production

→ Handoff creation

→ independent Quant Validator execution

→ enforcement evaluation

→ human gate

without requiring the user to manually coordinate specialist agents or runtime internals.

The demonstration MUST preserve fail-closed behavior.

---

## 24. Current Implementation Status

Canonical governance:

`AVAILABLE`

Canonical specialist roles:

`AVAILABLE`

Task Packet contract:

`AVAILABLE`

Handoff contract:

`AVAILABLE`

Runtime adapter specification:

`AVAILABLE`

OpenCode adapter:

`PARTIALLY_VALIDATED`

Automatic Gentle operational loop:

`NOT_IMPLEMENTED`

End-to-end V1 demonstration:

`NOT_TESTED`
