# Canonical User-Interaction Policy (DCP Inheritance)

This file defines inheritance and enforcement of the user-interaction layer.
It defines no interaction semantics of its own.

```text
USER-INTERACTION-POLICY.md  → inheritance and enforcement
dcp_01.md, dcp_02.md, dcp_03.md → interaction semantics (sole authority)
```

## 1. Purpose and Boundary

Every Gentle specialist, general and Quant alike, inherits the user's three
DCP documents as its interaction contract: how to pace, frame, dose, and
adapt communication to this user. This policy binds that inheritance without
touching specialist competence.

It MUST NOT redefine specialist role authority, technical competence, Quant
methodology, mathematical or data standards, security, safety, governance,
project invariants, evidence requirements, Task Packet or Handoff authority,
enforcement, Human Gates, or runtime permissions.

```text
DCP interaction policy
≠ governance
≠ specialist authority
≠ technical specification
≠ project contract
```

DCP is an interaction model, not a diagnosis. Never infer psychological or
medical characteristics from it.

## 2. Canonical Sources

The DCP documents are canonical at the framework location declared by the
global governance bootstrap. Every specialist MUST read all three completely
before material work. Memory, summaries, conversation paraphrases, or
project-local copies MUST NOT substitute for the canonical files.

| Part | Canonical document |
| --- | --- |
| I — WHO | `/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_01.md` |
| II — HOW | `/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_02.md` |
| III — WHEN | `/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_03.md` |

Paths are absolute so any runtime resolves them regardless of session working
directory.

The Gentle Quant Ecosystem once vendored the same core under
`governance/core/DCP/`. That copy is byte-identical today and is NOT
authority; it is not a source for this policy and MUST NOT be treated as
canonical.

## 3. Precedence

1. System/runtime safety and external hard controls.
2. Project governance, invariants, and enforcement.
3. Specialist role authority, prohibitions, and runtime permissions.
4. Task Packet / Handoff authoritative scope.
5. Explicit current user instruction, insofar as compatible with levels 1–4.
6. This canonical DCP interaction policy.
7. General stylistic defaults.

A lower level never overrides a higher one. Consequences:

- The user controls objectives and choices.
- The user cannot silently expand a specialist's authority.
- A Task Packet cannot grant authority the role does not possess.
- DCP never changes technical authority; it shapes communication only.
- Material validity failures remain reportable and blocking according to
  the specialist contract, regardless of interaction state. A specialist
  that discovers an error capable of invalidating a result MUST interrupt
  clearly.

## 4. Inheritance Requirement

Specialist contracts inherit this policy by reference. No role file, adapter,
or project file may embed a semantic copy of the DCP or maintain a
paraphrase as authority. Brief non-normative illustrations, where they exist,
grant nothing and defer to the DCP sources above.

## 5. Propagation

The orchestrator resolves this file and the DCP sources before dispatch and
carries the reference in the Task Packet's `user_interaction_policy` block.
Runtime adapters deliver the reference deterministically; they MUST NOT
embed semantic copies of the DCP, maintain runtime-specific DCP text, or let
generated files become canonical authority.

## 6. Failure Behavior

If this policy file or any DCP source cannot be resolved, return:

`DCP_CONTEXT_UNAVAILABLE`

Do not run on a guessed, remembered, or stale copy. This state means
user-interaction context is unavailable; it is distinct from technical
`BLOCKED` and is never reported as a validation `FAIL`.

## 7. Provenance

Reference hashes below record the DCP version this policy was written
against. Any specialist MUST be able to answer which interaction source it
received: the resolved policy path, the resolved DCP paths, and their
observed content hashes. A hash mismatch is reported as provenance drift,
never silently ignored. This metadata is for audit and debugging, not for
routine user output.

| Part | Canonical path | sha256 |
| --- | --- | --- |
| I — WHO | `/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_01.md` | `72a9cf07b15d17975789f3b55bf4b24b04068e32ef6cc0a99100b5aee71e4c26` |
| II — HOW | `/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_02.md` | `db0c21480ec66f4a8e6e10555ad3a49b7dd7e3ace298de88c7915922cbfd1966` |
| III — WHEN | `/home/datawithjose/Documents/AI-GOVERNANCE/DCP/dcp_03.md` | `ffc6f2f32ba184a4d02ee8f9f7c1311fb5aa3c3d47f95ffd21c312735f69df2d` |
