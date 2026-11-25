# Canonical Specialist Subagent Contract

## Purpose

This specification defines the runtime-independent execution contract for specialist agents in the Gentle Quant Ecosystem.

Canonical specialist contracts MUST NOT depend on OpenCode, Cline, Codex, Claude Code, Pi, or any other runtime-specific schema.

Runtime adapters translate this contract into provider-specific configuration.

---

## 1. Canonical Identity

Every specialist subagent MUST declare:

- `name`
- `description`
- `role_contract`
- `contract_version`

The canonical role contract remains the authoritative definition of ownership, boundaries, and escalation.

---

## 2. Invocation Policy

Allowed canonical invocation modes:

- `ORCHESTRATOR_ONLY`
- `HUMAN_OR_ORCHESTRATOR`

Quant specialist agents default to:

`ORCHESTRATOR_ONLY`

Runtime adapters MUST translate this into the closest enforceable runtime mechanism.

---

## 3. Context Policy

Allowed context modes:

- `ISOLATED_REQUIRED`
- `ISOLATED_PREFERRED`
- `SHARED_ALLOWED`

For independent validation:

`ISOLATED_REQUIRED`

For DE, QR, and QD:

`ISOLATED_PREFERRED`

If a runtime cannot satisfy a required isolation level, the adapter MUST report `CAPABILITY_BLOCKED`.

---

## 4. Delegation Policy

Allowed delegation modes:

- `FORBIDDEN`
- `ORCHESTRATOR_AUTHORIZED`
- `ALLOWED`

Quant specialist agents default to:

`FORBIDDEN`

Specialists MUST NOT expand their authority by creating subordinate agents unless the canonical contract explicitly permits it.

---

## 5. Authority Policy

A specialist MUST receive:

- current task;
- project workspace;
- applicable governance;
- authoritative upstream artifacts;
- relevant skills;
- allowed scope;
- required output;
- verification requirements.

A specialist MUST NOT infer additional authority from conversation history or runtime capabilities.

---

## 6. Governance Policy

Applicable project governance MUST be made available before material work:

- `.governance/CONTRACT.md`
- `.governance/INVARIANTS.md`
- `.governance/enforcement.yaml`
- `.governance/TEAM.yaml`
- `.governance/ROUTING.yaml`

Missing required governance MUST be reported.

---

## 7. Skill Policy

Canonical skills remain external authoritative contracts.

The runtime adapter MUST provide exact skill content or exact resolvable references when the task requires them.

Lossy summaries MUST NOT replace critical skill rules.

---

## 8. Execution Status

Every specialist execution MUST use only:

- `COMPLETED`
- `BLOCKED`
- `INCONCLUSIVE`

Validation specialists may additionally report property-level:

- `PASS`
- `FAIL`
- `INCONCLUSIVE`
- `NOT_TESTED`
- `BLOCKED`

Adapters MUST preserve these states exactly.

---

## 9. Structured Result

Every specialist MUST return:

- status;
- specialist identity;
- task identity;
- authoritative inputs;
- assumptions;
- unknowns;
- work performed;
- artifacts produced;
- checks performed;
- evidence;
- limitations;
- unresolved risks;
- handoff status;
- next recommended action;
- required human decisions.

Role-specific contracts MAY add fields but MUST NOT remove these core semantics.

---

## 10. Human Authority

No specialist or runtime adapter may manufacture human approval.

Human-only decisions include where applicable:

- project objective changes;
- critical invariant changes;
- material risk acceptance;
- production release;
- live financial side effects;
- governance overrides.

---

## 11. Runtime Translation Rule

Provider-specific concepts belong only inside adapters.

Examples:

Canonical:

`invocation: ORCHESTRATOR_ONLY`

Possible adapter translations:

- OpenCode: hidden/subagent/task restrictions
- Cline: equivalent orchestration mechanism
- Codex: equivalent delegated-agent mechanism
- Pi: equivalent runtime mechanism

The canonical contract MUST NOT change when switching runtimes.

---

## 12. User-Interaction Inheritance

Every specialist inherits `USER-INTERACTION-POLICY.md` by reference. The
specialist MUST read the canonical DCP sources completely; memory, summaries,
conversation paraphrases, or project-local copies MUST NOT substitute for
them. DCP shapes communication only and never expands role authority,
redefines technical standards, or overrides governance, Task Packet scope, or
a material validity finding. If the policy file or any DCP source cannot be
resolved, return `DCP_CONTEXT_UNAVAILABLE`; this state is distinct from
technical `BLOCKED` and is never reported as a validation `FAIL`.

---

## 13. Failure to Map

If an adapter cannot faithfully translate a canonical requirement, it MUST return:

`CAPABILITY_BLOCKED`

It MUST identify:

- unsupported canonical requirement;
- runtime limitation;
- affected specialist;
- affected workflow;
- safe alternatives if any.

Silent degradation is forbidden.

---

## 14. Portability Test

A canonical specialist contract is portable only if replacing one runtime adapter with another does not require changing:

- ROLE.md;
- specialist semantics;
- governance;
- routing;
- handoff meaning;
- human authority boundaries.

Only deployment representation may change.
