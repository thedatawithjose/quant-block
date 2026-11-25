# Canonical Specialist Handoff Contract

## Purpose

This specification defines the runtime-independent contract for transferring work between specialist agents in the Gentle Quant Ecosystem.

A handoff is an authoritative workflow artifact.

Conversation summaries, model memory, or informal prose MUST NOT replace a required handoff.

---

## 1. Handoff Identity

Every handoff MUST identify:

- `handoff_id`
- `handoff_version`
- `task_id`
- `source_role`
- `target_role`
- `project`
- `created_at`
- `status`

The handoff identity MUST remain stable once downstream work begins.

---

## 2. Allowed Status

A handoff MUST use exactly one:

- `DRAFT`
- `READY_FOR_REVIEW`
- `APPROVED_FOR_HANDOFF`
- `BLOCKED`
- `REJECTED`

Downstream implementation MUST NOT treat `DRAFT`, `BLOCKED`, or `REJECTED` as approved authority.

---

## 3. Authoritative Inputs

Every handoff MUST identify the authoritative inputs used by the source specialist.

Where applicable include:

- governance artifacts;
- specifications;
- datasets;
- dataset fingerprints;
- source-code revision;
- configuration;
- upstream handoffs;
- research reports;
- evidence artifacts.

References SHOULD include immutable identity where available, such as:

- Git commit;
- content hash;
- dataset fingerprint;
- artifact version.

Do not silently substitute another input.

---

## 4. Scope

Every handoff MUST define:

- work requested;
- work completed;
- work explicitly excluded;
- allowed downstream interpretation;
- prohibited downstream reinterpretation.

The target specialist MUST NOT silently expand scope.

---

## 5. Facts, Assumptions, and Unknowns

Keep these categories separate:

### Discovered Facts

Verified from authoritative sources.

### User-Declared Requirements

Explicitly provided by human authority.

### Derived Conclusions

Reasoned from identified facts and assumptions.

### Assumptions

Required assumptions not independently established.

### Unknowns

Information still unresolved.

An assumption MUST NOT be promoted to fact during handoff.

---

## 6. Decisions

Record:

### Decisions Made

Decisions the source role was authorized to make.

### Decisions Not Authorized

Decisions explicitly reserved to:

- another specialist;
- governance;
- Quant Orchestrator;
- Portfolio Manager / Head of Quant.

A specialist MUST NOT create authority by writing a decision into the handoff.

---

## 7. Outputs

List every authoritative output produced.

For each output identify where applicable:

- artifact path;
- artifact type;
- version;
- hash or fingerprint;
- status;
- intended consumer.

Downstream specialists MUST use authoritative artifacts rather than reconstructed summaries when available.

---

## 8. Verification

Record:

- checks required;
- checks actually executed;
- commands or methods used;
- expected results;
- observed results;
- evidence paths;
- checks not executed;
- reasons for missing verification.

Never report a check as executed without evidence.

---

## 9. Invariant Impact

Every material handoff MUST identify:

- applicable invariants;
- invariants checked;
- invariants not checked;
- invariant failures;
- enforcement status.

A failed critical invariant forces:

`BLOCKED`

unless governance explicitly defines a different human-controlled procedure.

---

## 10. Limitations and Risks

Record:

- known limitations;
- unresolved defects;
- uncertainty;
- residual risk;
- unsupported claims;
- unverified behavior.

Do not hide limitations merely because downstream work can continue.

---

## 11. Required Downstream Work

Define exactly what the target specialist is expected to do.

Include:

- required outputs;
- required tests;
- required skills;
- required governance;
- required independent verification;
- prohibited changes.

---

## 12. Change Protection

After a handoff reaches:

`APPROVED_FOR_HANDOFF`

the source artifacts referenced by that handoff MUST NOT be silently changed.

If an authoritative upstream artifact changes materially:

1. mark the existing handoff stale;
2. identify affected downstream work;
3. issue a new handoff version;
4. rerun required verification.

Downstream work MUST NOT continue under stale authority without explicit resolution.

---

## 13. Specialist Boundaries

Typical authoritative transitions:

- Data Engineer → Quant Validator
- Quant Validator(data) → Quant Researcher
- Quant Researcher → Quant Developer
- Quant Developer → Quant Validator
- Quant Validator → Portfolio Manager / Head of Quant

Global task routing selects work-nature specialists; project `ROUTING.yaml` refines the actual workflow with project-specific protected surfaces, gates, and narrow overrides.

---

## 14. Human Authority

A handoff MUST NOT manufacture human approval.

The following remain human-controlled where governance declares them so:

- critical invariant changes;
- material risk acceptance;
- project objective changes;
- production approval;
- live financial side effects;
- governance overrides.

---

## 15. Runtime Independence

The handoff contract is canonical.

OpenCode, Cline, Codex, Claude Code, Pi, or another runtime MAY transport or render handoffs differently.

They MUST preserve the same semantics.

Runtime adapters MUST NOT:

- remove required fields;
- convert failure into success;
- replace authoritative artifacts with lossy summaries;
- manufacture approvals;
- discard unresolved risks.

---

## 16. Minimum Handoff Result

A valid handoff contains at minimum:

- identity;
- source and target roles;
- status;
- task;
- authoritative inputs;
- scope;
- facts;
- assumptions;
- unknowns;
- decisions made;
- decisions not authorized;
- outputs;
- verification;
- invariant impact;
- limitations;
- required downstream work;
- evidence;
- human decisions required.

If required material information is missing, the handoff is not ready for `APPROVED_FOR_HANDOFF`.
