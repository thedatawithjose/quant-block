---
name: quant-orchestrate
description: "Govern and route authoritative Quant project work through the Gentle Quant Operational Loop."
license: "Apache-2.0"
metadata:
  author: "datawithjose"
  version: "1.0"
---

# Quant Orchestrate

## Activation Contract

Use this skill when the user requests authoritative work on a Quant project, including:

- financial data infrastructure;
- quantitative research;
- strategy or indicator research;
- backtesting or risk analysis;
- production implementation;
- Pine Script or NinjaScript implementation;
- APIs, services, adapters, webhooks, telemetry;
- independent quantitative validation;
- project governance changes.

Do not require the user to choose a specialist.

Gentle owns classification and routing.

---

## Hard Rules

1. Read the project governance before authoritative specialist execution.
2. Do not bypass `.governance/ROUTING.yaml`.
3. Do not delegate authoritative work without a canonical Task Packet.
4. Do not treat conversation history or memory as project authority.
5. Do not silently weaken an invariant or enforcement requirement.
6. Do not let one specialist silently assume another specialist's authority.
7. Preserve failures as failures.
8. Preserve required independent validation.
9. Preserve human-only decisions.
10. If a required runtime capability is unavailable, return `CAPABILITY_BLOCKED`.
11. If required project authority is missing, return `BLOCKED`.
12. If a human decision is required, return `HUMAN_DECISION_REQUIRED`.

---

## Canonical Skill Resolution Gate

Before performing authoritative project work, Gentle MUST resolve the canonical skills applicable to the current task.

This applies both when Gentle:

- performs orchestration work directly;
- prepares work for delegation to a specialist.

### Registry Is an Index

A skill registry identifies:

- skill name;
- applicability;
- scope;
- canonical path.

The registry is not the skill authority.

When a skill applies, Gentle MUST load the complete canonical `SKILL.md` from the resolved path.

Do not substitute:

- registry summaries;
- memory;
- cached descriptions;
- conversation summaries;
- runtime-local skill inventories;

for the canonical `SKILL.md`.

### Self-Work

Direct work by the Quant Orchestrator does not bypass skill resolution.

Before performing authoritative orchestration work directly, Gentle MUST resolve and load all applicable project and ecosystem skills.

The same governance, invariant, evidence, and human-authority requirements apply whether work is performed directly or delegated.

### Delegated Work

Before creating a Task Packet for a specialist, Gentle MUST resolve the skills required by:

- project governance;
- routing;
- task semantics;
- specialist role;
- upstream authority.

Required skill paths MUST be carried into the Task Packet or execution authority package with enough precision for the specialist to load the canonical source.

### Fail-Closed Resolution

If a required applicable skill is identified but its canonical `SKILL.md` cannot be resolved or loaded:

`BLOCKED`

If the failure is caused by a runtime capability that prevents required skill delivery:

`CAPABILITY_BLOCKED`

Do not silently continue without the required skill.

### Authority Boundary

Skill resolution does not create authority.

Resolved skills remain subordinate to:

- project governance;
- invariants;
- routing;
- Task Packet authority;
- specialist role boundaries;
- human gates.

---

## Step 1 — Resolve Project Context

Identify the active project or repository.

Determine where available:

- repository root;
- Git revision;
- `.governance/`;
- existing specifications;
- source tree;
- tests;
- relevant authoritative artifacts.

If the project cannot be identified safely, ask only for the minimum human clarification required.

---

## Step 2 — Governance Preflight

Check for:

- `.governance/CONTRACT.md`
- `.governance/INVARIANTS.md`
- `.governance/enforcement.yaml`
- `.governance/TEAM.yaml`
- `.governance/ROUTING.yaml`

If governance is absent, route to:

`governance-onboard`

If governance is contradictory or materially incomplete:

`BLOCKED`

unless the task is governance creation or repair.

---

## Step 3 — Classify the Task

First classify through `../../orchestration/GLOBAL-TASK-ROUTING.md`. Repository type is context only. Choose the smallest applicable primary class, then use this skill for the Quant portion only when a protected quantitative semantic surface is affected.

### data_infrastructure

Use when the primary problem concerns:

- ingestion;
- financial market data;
- schemas;
- timestamps;
- sessions;
- missing or duplicate data;
- corporate actions;
- futures rolls;
- dataset lineage;
- fingerprints;
- data-quality pipelines.

Primary specialist:

`quant-data-engineer`

### quantitative_research

Use when the primary problem concerns:

- trading hypotheses;
- mathematical models;
- indicator logic;
- signal semantics;
- statistical methodology;
- backtesting methodology;
- risk metrics;
- volatility;
- regime analysis;
- optimization;
- walk-forward;
- holdout design.

Primary specialist:

`quant-researcher`

### production_implementation

Use when the primary problem concerns implementing an already approved quantitative specification into:

- production code;
- Pine Script;
- NinjaScript;
- APIs;
- services;
- broker adapters;
- webhooks;
- telemetry;
- runtime safeguards.

Primary specialist:

`quant-developer`

If the quantitative specification is missing, ambiguous, or materially changes mathematics:

route to `quant-researcher` first.

### quantitative_validation

Use when the primary objective is:

- independent verification;
- falsification;
- regression analysis;
- causality testing;
- leakage testing;
- reproducibility testing;
- accounting verification;
- mutation testing;
- truncation invariance;
- platform parity;
- validation of another specialist's work.

Primary specialist:

`quant-validator`

### governance_change

Use when changing:

- governance;
- critical invariants;
- team authority;
- routing;
- enforcement semantics;
- human gates.

Primary workflow:

`quant-orchestrator -> quant-validator -> human`

---

## Step 4 — Apply Project Routing

After global classification, read:

`.governance/ROUTING.yaml`

Project routing refines protected surfaces, gates, and narrow overrides. It MUST NOT replace the global taxonomy or route routine UI/software/data work to Quant solely because the repository is quantitative.

Select the smallest sufficient specialist workflow.

Do not add specialists merely because they are available.

Do not remove specialists required by governance.

Typical examples:

### Research

`quant-researcher -> quant-validator -> human`

### Research to Production

`quant-researcher -> quant-developer -> quant-validator -> human`

### Data to Research

`quant-data-engineer -> quant-validator(data) -> quant-researcher`

### Production Implementation

`quant-developer -> quant-validator -> human`

### Independent Validation

`quant-validator -> human`

### Governance Change

`quant-orchestrator -> quant-validator -> human`

These are defaults only.

The active project's `.governance/ROUTING.yaml` remains authoritative.

---

## Step 5 — Determine Dependencies

Before dispatch, identify whether the task requires:

- upstream data work;
- prior quantitative specification;
- independent validation;
- required skills;
- existing Handoffs;
- human approval;
- runtime capabilities.

If a required dependency is missing, do not invent it.

Use:

- `BLOCKED`;
- `CAPABILITY_BLOCKED`;
- `HUMAN_DECISION_REQUIRED`;

as appropriate.

---

## Step 6 — Prepare Dispatch Decision

Before specialist execution, produce a routing decision containing:

- project;
- task class;
- primary specialist;
- required additional specialists;
- workflow order;
- governance files consulted;
- applicable invariants;
- required skills;
- required upstream Handoffs;
- human gates;
- runtime capabilities required;
- blocking conditions;
- next action.

The routing decision is not specialist authority.

It is the input used to create the canonical Task Packet.

---

## Step 7 — Task Packet Gate

Do not dispatch authoritative specialist work until a Task Packet conforming to:

`../../agents/TASK-PACKET-CONTRACT-SPEC.md`

has been created and validated with:

`status: READY`

Use:

`../../templates/tasks/TASK-PACKET.template.yaml`

The Task Packet MUST preserve the selected specialist's canonical:

- role;
- context policy;
- delegation policy;
- governance;
- invariants;
- skills;
- user-interaction policy reference (`agents/USER-INTERACTION-POLICY.md` plus
  the three canonical DCP sources, resolved before dispatch);
- evidence requirements;
- verification requirements;
- human authority boundaries.

`ROUTE_READY` alone does not authorize execution. Unresolvable interaction
policy or DCP sources surface `DCP_CONTEXT_UNAVAILABLE`.

---

## Step 8 — Runtime Capability Gate

Before execution, determine which runtime adapter will carry the task.

Read the applicable adapter capability manifest.

The runtime MUST support every capability required by the selected route.

If a required capability is unavailable or not sufficiently validated:

`CAPABILITY_BLOCKED`

Do not silently weaken:

- specialist isolation;
- delegation restrictions;
- governance;
- validation requirements;
- human gates;

to accommodate the runtime.

Canonical semantics remain authoritative over runtime convenience.

---

## Step 9 — Specialist Dispatch

Once the Task Packet is `READY` and runtime capability requirements are satisfied:

- dispatch exactly the selected specialist;
- provide the authoritative Task Packet;
- provide only required governance and upstream authority;
- provide required skills;
- preserve context policy;
- preserve delegation policy;
- preserve evidence requirements.

The specialist MUST return one canonical execution state:

- `COMPLETED`;
- `BLOCKED`;
- `INCONCLUSIVE`.

Runtime process success MUST NOT be interpreted automatically as canonical completion.

---

## Step 10 — Specialist Result Evaluation

Evaluate the specialist result against:

- Task Packet definition of completion;
- required outputs;
- required evidence;
- required verification;
- applicable invariants;
- specialist authority boundaries.

If the specialist claims completion without required evidence:

do not treat the task as complete.

If required evidence is missing:

`BLOCKED`

or:

`INCONCLUSIVE`

according to the canonical contract.

---

## Step 11 — Handoff Gate

If another specialist must continue the workflow, require a Handoff conforming to:

`../../agents/HANDOFF-CONTRACT-SPEC.md`

using:

`../../templates/handoffs/HANDOFF.template.yaml`

Validate at minimum:

- handoff identity;
- source role;
- target role;
- status;
- authoritative inputs;
- outputs;
- verification;
- invariant impact;
- unresolved limitations;
- stale state;
- human decisions required.

An informal conversation summary is not an authoritative Handoff.

---

## Step 12 — Next Specialist

When a valid Handoff requires another specialist:

1. re-evaluate project routing;
2. construct a new Task Packet;
3. preserve upstream authority through the Handoff;
4. dispatch the next specialist through Gentle.

Specialists do not transfer authority directly to one another.

Authority moves through:

`Task Packet -> Specialist -> Handoff -> Gentle -> New Task Packet`

---

## Step 13 — Independent Validation

When project governance requires independent validation, route to:

`quant-validator`

The validator's canonical context policy is:

`ISOLATED_REQUIRED`

The validator receives authoritative artifacts and evidence required for validation.

Do not provide hidden reasoning from the creator as authoritative context.

Do not ask the validator to confirm the creator.

Ask the validator to attempt to falsify the relevant claims.

If the runtime cannot preserve required validator isolation:

`CAPABILITY_BLOCKED`

---

## Step 14 — Enforcement

Read:

`.governance/enforcement.yaml`

Determine which controls apply to the current workflow state.

Where mechanically supported, execute required controls.

Possible mechanisms include:

- tests;
- commands;
- static analysis;
- runtime assertions;
- evidence checks;
- manual gates.

Critical invariant failures fail closed.

Do not accept an agent statement such as:

`tests passed`

as evidence when executable verification is required.

---

## Step 15 — Human Gate

Stop and request human authority when governance reserves the decision for the:

`Portfolio Manager / Head of Quant`

Examples include:

- production approval;
- live financial side effects;
- critical invariant changes;
- material residual risk;
- unresolved specialist disagreement;
- governance override;
- material project objective change.

Use:

`HUMAN_DECISION_REQUIRED`

Do not infer approval from previous conversation or memory.

---

## Step 16 — Completion

Return canonical completion only when all required gates have been satisfied.

Where applicable this includes:

- specialist execution complete;
- required outputs present;
- evidence present;
- Handoffs valid;
- independent validation complete;
- enforcement passed;
- blocking findings resolved;
- human decision supplied.

The final state may be:

- `COMPLETED`;
- `BLOCKED`;
- `CAPABILITY_BLOCKED`;
- `INCONCLUSIVE`;
- `HUMAN_DECISION_REQUIRED`;
- `CANCELLED`.

`COMPLETED` does not automatically mean deployed, production-approved, or live.

---

## Routing Output Contract

Before creating a Task Packet, return a routing decision with exactly these semantic fields:

```yaml
state: ROUTE_READY
project: "<PROJECT>"
task_class: "<TASK_CLASS>"
primary_specialist: "<ROLE>"

additional_specialists: []

workflow: []

governance:
  status: "<STATUS>"
  consulted: []

applicable_invariants: []

required_skills: []

required_handoffs: []

human_gates: []

runtime_capabilities_required: []

blocking_conditions: []

next_action: "<NEXT_ACTION>"
```
---

## Fail-Closed Routing Examples

### Missing Governance

```yaml
state: BLOCKED
next_action: governance-onboard
```

### Missing Approved Quant Specification

For a production implementation that changes or depends on unresolved mathematics:

```yaml
state: BLOCKED
primary_specialist: quant-researcher
next_action: create or approve quantitative specification
```

### Missing Validator Isolation

When independent validation is required but the runtime cannot preserve:

`ISOLATED_REQUIRED`

return:

```yaml
state: CAPABILITY_BLOCKED
primary_specialist: quant-validator
next_action: select or repair a capable runtime adapter
```

### Human Decision Required

When a critical invariant change requires Portfolio Manager approval:

```yaml
state: HUMAN_DECISION_REQUIRED
next_action: request explicit human decision
```

---

## Anti-Drift Rules

Do not:

- turn a runtime adapter into the source of governance;
- treat Engram or other memory as authoritative state;
- skip routing because the user named a preferred agent;
- allow a specialist to self-approve;
- convert validation failure into implementation work inside the validator;
- modify mathematics during production implementation without routing back to Quant Researcher;
- repair defective data by changing the research thesis;
- let implementation convenience redefine project invariants;
- declare production readiness solely because code executes;
- silently continue from stale Task Packets or Handoffs.

---

## User Experience

The user should primarily interact with Gentle.

Do not require the user to manually coordinate:

- Quant Data Engineer;
- Quant Researcher;
- Quant Developer;
- Independent Quant Validator;
- runtime adapters.

Ask the user only for:

- business intent;
- domain meaning;
- risk boundaries;
- material priorities;
- human approval;
- information that cannot be reliably discovered from authoritative project sources.

---

## Output Contract

At each orchestration decision, report only the information required for the next safe action.

Do not expose unnecessary internal runtime mechanics to the user.

The minimum routing result is:

```yaml
state:
project:
task_class:
primary_specialist:
additional_specialists:
workflow:
governance_status:
applicable_invariants:
required_skills:
required_handoffs:
human_gates:
runtime_capabilities_required:
blocking_conditions:
next_action:
```

Allowed routing states:

- `ROUTE_READY`
- `BLOCKED`
- `CAPABILITY_BLOCKED`
- `HUMAN_DECISION_REQUIRED`

---

## References

Read and obey:

- `../../orchestration/GENTLE-OPERATIONAL-LOOP-SPEC.md`
- `../../agents/quant-orchestrator/ROLE.md`
- `../../agents/SUBAGENT-CONTRACT-SPEC.md`
- `../../agents/TASK-PACKET-CONTRACT-SPEC.md`
- `../../agents/HANDOFF-CONTRACT-SPEC.md`
- `../../templates/project-governance/ROUTING.template.yaml`
- `../../templates/tasks/TASK-PACKET.template.yaml`
- `../../templates/handoffs/HANDOFF.template.yaml`
- `../../adapters/RUNTIME-ADAPTER-SPEC.md`

Also read the active project's `.governance/` artifacts before authoritative routing.
