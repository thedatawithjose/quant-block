# Canonical Specialist Task Packet Contract

## Purpose

This specification defines the runtime-independent work package that the Quant Orchestrator provides to a specialist before delegated execution.

A specialist MUST receive an explicit task packet before performing authoritative project work.

Conversation context, model memory, or inferred intent MUST NOT silently replace required task authority.

---

## 1. Task Identity

Every task packet MUST identify:

- `task_id`
- `task_version`
- `project`
- `assigned_role`
- `created_at`
- `status`

Task identity MUST remain stable during execution.

---

## 2. Allowed Status

A task packet MUST use exactly one:

- `DRAFT`
- `READY`
- `BLOCKED`
- `CANCELLED`
- `SUPERSEDED`

A specialist MUST NOT begin authoritative execution unless status is:

`READY`

---

## 3. Assigned Specialist

The packet MUST identify exactly one primary specialist role.

Canonical specialist roles include:

- `ui-ux-engineer`
- `software-engineer`
- `data-engineer`
- `data-scientist`

- `quant-data-engineer`
- `quant-researcher`
- `quant-developer`
- `quant-validator`

The assigned specialist MUST obey its canonical:

- `ROLE.md`
- `SUBAGENT.md`
- `SUBAGENT-CONTRACT-SPEC.md`

The task packet cannot expand the authority defined by those contracts.

---

## 4. Objective

Every packet MUST state:

- requested outcome;
- reason for the work;
- definition of completion;
- intended downstream consumer.

The objective MUST be specific enough that completion can be evaluated.

---

## 5. Scope

Every packet MUST define:

### In Scope

Work the specialist is authorized to perform.

### Out of Scope

Work explicitly excluded.

### Prohibited Changes

Artifacts, assumptions, formulas, invariants, governance, or decisions the specialist MUST NOT alter.

A specialist MUST NOT silently expand scope.

---

## 6. Authority Package

Every packet MUST identify the authoritative material available to the specialist.

Where applicable:

- project governance;
- upstream handoffs;
- specifications;
- datasets;
- dataset fingerprints;
- source revision;
- configuration;
- tests;
- approved research;
- approved formulas;
- evidence artifacts.

Authoritative artifacts SHOULD use immutable identifiers where available.

Examples:

- Git commit;
- content hash;
- dataset fingerprint;
- artifact version.

### User-Interaction Policy

Every packet MUST carry a `user_interaction_policy` block referencing
`agents/USER-INTERACTION-POLICY.md` and the three canonical DCP sources with
their observed content hashes. The orchestrator resolves these references
before dispatch; the specialist reads the DCP sources completely. DCP shapes
communication only and never expands role authority or overrides governance,
Task Packet scope, or a material validity finding. If the policy file or any
DCP source cannot be resolved, the packet MUST NOT be `READY`; surface
`DCP_CONTEXT_UNAVAILABLE`.

---

## 7. Governance

Every authoritative task MUST reference applicable project governance:

- `.governance/CONTRACT.md`
- `.governance/INVARIANTS.md`
- `.governance/enforcement.yaml`
- `.governance/TEAM.yaml`
- `.governance/ROUTING.yaml`

If required governance is absent, contradictory, or materially incomplete:

`BLOCKED`

unless the task is explicitly governance onboarding or governance repair.

---

## 8. Required Skills

The packet MUST identify any skills required for the task.

Skills MUST be loaded from canonical sources.

A runtime adapter MUST NOT replace required skill content with an undocumented approximation.

If a required skill cannot be supplied reliably:

`CAPABILITY_BLOCKED`

---

## 9. Inputs

Inputs MUST be classified when relevant as:

- `DISCOVERED`
- `USER_DECLARED`
- `UPSTREAM_APPROVED`
- `DERIVED`
- `UNKNOWN`

Unknown information MUST remain unknown until resolved.

An assumption MUST NOT silently become an authoritative input.

---

## 10. Upstream Handoffs

When work depends on a previous specialist, the packet MUST reference the authoritative handoff.

The specialist MUST check:

- handoff identity;
- handoff version;
- handoff status;
- stale state;
- source role;
- intended target role.

A handoff that is:

- `DRAFT`;
- `BLOCKED`;
- `REJECTED`;
- stale;
- intended for another role;

MUST NOT be treated as approved downstream authority.

---

## 11. Invariants

The packet MUST identify applicable invariants where known.

For each critical invariant, the specialist MUST preserve its semantics.

The specialist MUST NOT:

- weaken an invariant;
- delete an invariant;
- modify a test merely to make the invariant pass;
- reinterpret a failure as success.

If a critical invariant conflicts with the requested task:

`BLOCKED`

and escalate.

---

## 12. Required Outputs

The packet MUST define required outputs.

Examples:

- data artifact;
- research specification;
- implementation;
- tests;
- validation report;
- evidence bundle;
- specialist handoff.

An output not required by the task does not automatically become authoritative.

---

## 13. Verification Requirements

The packet MUST identify required verification where applicable.

Examples:

- unit tests;
- integration tests;
- numerical oracle;
- causality test;
- truncation invariance;
- mutation test;
- accounting identity;
- dataset fingerprint verification;
- platform parity;
- static analysis;
- reproducibility check.

The specialist MUST distinguish:

- required and executed;
- required but not executed;
- not applicable.

Never claim verification without evidence.

---

## 14. Evidence Requirements

Evidence SHOULD be machine-verifiable whenever practical.

Acceptable evidence may include:

- command output;
- test report;
- hash;
- fingerprint;
- generated artifact;
- diff;
- log;
- validation result.

Model statements alone are not evidence.

---

## 15. Human Decisions

The task packet MUST identify decisions reserved for human authority.

The specialist MUST NOT manufacture or infer human approval.

Examples include:

- changing critical invariants;
- accepting material residual risk;
- changing project objectives;
- production release;
- live financial side effects;
- governance overrides.

If execution reaches a required human decision:

`BLOCKED`

until the decision is supplied.

---

## 16. Execution Result

The specialist MUST terminate with exactly one execution state defined by the canonical subagent contract:

- `COMPLETED`
- `BLOCKED`
- `INCONCLUSIVE`

For validator property results, use:

- `PASS`
- `FAIL`
- `INCONCLUSIVE`
- `NOT_TESTED`
- `BLOCKED`

`COMPLETED` does not automatically mean validated, approved, safe for production, or authorized for live use.

---

## 17. Handoff Requirement

When downstream work is expected, the specialist MUST produce a handoff conforming to:

`HANDOFF-CONTRACT-SPEC.md`

The specialist MUST NOT substitute an informal conversational summary for a required handoff.

---

## 18. Context Isolation

The runtime adapter MUST preserve the context policy from the assigned specialist's canonical `SUBAGENT.md`.

Possible canonical policies include:

- `ISOLATED_REQUIRED`
- `ISOLATED_PREFERRED`
- `SHARED_ALLOWED`

For `ISOLATED_REQUIRED`, execution MUST NOT silently degrade to shared context.

If the runtime cannot provide the required isolation:

`CAPABILITY_BLOCKED`

---

## 19. Delegation

Delegation MUST follow the canonical specialist contract.

If the assigned specialist declares:

`delegation: "FORBIDDEN"`

the specialist MUST NOT delegate its assigned authority to another agent.

Any additional specialist must be routed by the Quant Orchestrator through a separate task packet.

---

## 20. Change Control

If authoritative task inputs materially change during execution:

1. stop affected work;
2. identify the changed authority;
3. determine impacted outputs;
4. mark stale work where necessary;
5. request an updated task packet or authoritative handoff;
6. rerun affected verification.

A specialist MUST NOT continue under materially stale authority.

---

## 21. Runtime Independence

The task packet is canonical.

OpenCode, Cline, Codex, Claude Code, Pi, or another runtime MAY encode or transport it differently.

Adapters MUST preserve:

- task identity;
- role authority;
- scope;
- governance;
- invariants;
- inputs;
- upstream handoffs;
- required outputs;
- verification;
- evidence;
- human gates;
- context policy;
- delegation policy;
- execution state.

A runtime limitation MUST be surfaced explicitly.

It MUST NOT be hidden through silent degradation.

---

## 22. Minimum Valid Task Packet

A valid authoritative task packet contains at minimum:

- identity;
- READY status;
- assigned specialist;
- objective;
- definition of completion;
- scope;
- prohibited changes;
- authoritative inputs;
- governance references;
- required skills;
- upstream handoffs where applicable;
- applicable invariants;
- required outputs;
- verification requirements;
- evidence requirements;
- human decisions;
- context requirement;
- delegation rule;
- intended downstream consumer.

If required material information is missing, the packet MUST NOT be considered ready for execution.
