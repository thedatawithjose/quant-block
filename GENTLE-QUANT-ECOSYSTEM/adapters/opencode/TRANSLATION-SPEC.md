# OpenCode Adapter Translation Specification

## Purpose

This document defines how Gentle canonical general and Quant specialist contracts are translated into OpenCode runtime agents.

OpenCode is a deployment target.

It is not the source of truth for:

- specialist roles;
- governance;
- task authority;
- handoffs;
- invariants;
- human authority.

Canonical artifacts remain authoritative.

---

## 1. Canonical Sources

The adapter MUST derive OpenCode specialist agents from:

- `agents/SUBAGENT-CONTRACT-SPEC.md`
- `agents/TASK-PACKET-CONTRACT-SPEC.md`
- `agents/HANDOFF-CONTRACT-SPEC.md`
- `agents/<specialist>/ROLE.md`
- `agents/<specialist>/SUBAGENT.md`
- project `.governance/` artifacts
- required canonical skills
- authoritative Task Packet

The adapter MUST NOT maintain an independent copy of role semantics.

---

## 2. OpenCode Representation

Each canonical specialist is represented as an OpenCode agent entry. General specialists are generated through the same adapter process as Quant specialists; no OpenCode file defines their canonical authority.

Canonical mapping:

| Canonical field | OpenCode representation |
|---|---|
| `name` | agent key |
| `description` | `description` |
| specialist execution | `mode: "subagent"` |
| canonical authority package | generated prompt artifact |
| tool restrictions | `tools` and/or `permission` |
| context policy | adapter execution behavior |
| delegation policy | prompt + tool/runtime restrictions |
| role contract | generated prompt reference |
| Task Packet | generated execution authority |
| governance | generated execution authority |
| skills | injected/referenced canonical skill content |

The OpenCode configuration is generated runtime state.

It MUST NOT become canonical governance.

---

## 3. Supported OpenCode Agent Fields

The installed OpenCode SDK exposes the following relevant `AgentConfig` fields:

- `model`
- `variant`
- `temperature`
- `top_p`
- `prompt`
- `tools`
- `disable`
- `description`
- `mode`
- `hidden`
- `options`
- `color`
- `steps`
- `maxSteps`
- `permission`

Supported `mode` values include:

- `subagent`
- `primary`
- `all`

Quant specialists MUST be generated as:

`mode: "subagent"`

unless a future canonical architecture change explicitly states otherwise.

---

## 4. Specialist Mapping

The adapter MUST support these canonical identities:

- `ui-ux-engineer`
- `software-engineer`
- `data-engineer`
- `data-scientist`
- `quant-data-engineer`
- `quant-researcher`
- `quant-developer`
- `quant-validator`

Their semantic authority comes exclusively from their canonical contracts. The adapter receives the global routing decision; it MUST NOT route by repository type.

OpenCode-specific configuration MUST NOT change their responsibilities.

---

## 5. Prompt Generation

The adapter SHOULD generate a runtime prompt artifact for each specialist.

The prompt artifact MUST include or reference, without semantic loss:

1. specialist identity;
2. canonical `ROLE.md`;
3. canonical `SUBAGENT.md`;
4. canonical subagent contract;
5. authoritative Task Packet;
6. applicable project governance;
7. required skills;
8. upstream Handoff where applicable;
9. output requirements;
10. verification requirements;
11. human authority boundaries.

The generated prompt MUST distinguish canonical authority from contextual information.

Conversation history or model memory MUST NOT replace missing canonical authority.

---

## 6. Task-Specific Authority

Static agent registration does not grant project authority.

A registered specialist becomes authoritative for a specific project task only when supplied with a valid Task Packet whose status is:

`READY`

Therefore:

`registered agent != authorized task`

The adapter MUST preserve this distinction.

---

## 7. Context Policy Mapping

Canonical context values:

- `ISOLATED_REQUIRED`
- `ISOLATED_PREFERRED`
- `SHARED_ALLOWED`

For OpenCode:

### ISOLATED_REQUIRED

The specialist MUST execute through a separate subagent context.

If this cannot be demonstrated:

`CAPABILITY_BLOCKED`

This applies to `quant-validator`.

### ISOLATED_PREFERRED

The adapter SHOULD use a separate subagent context.

If isolation cannot be provided, the limitation MUST be surfaced and evaluated against governance before execution.

No silent degradation is allowed.

---

## 8. Delegation Mapping

Canonical Quant specialists currently declare:

`delegation: "FORBIDDEN"`

The generated specialist MUST NOT receive authority to delegate its assigned specialist responsibility.

If OpenCode exposes delegation tools to the specialist, the adapter SHOULD disable them where technically possible.

If technical prevention is unavailable, the adapter MUST enforce the prohibition through runtime instructions and report the limitation in the capability manifest.

Additional specialists MUST be dispatched by the Quant Orchestrator through separate Task Packets.

---

## 9. Tool and Permission Mapping

OpenCode supports agent-level:

- `tools`
- `permission`

The adapter MUST apply least-authority configuration appropriate to each specialist.

Permissions MUST be derived from the task and canonical role.

They MUST NOT be expanded merely because the runtime supports additional tools.

Runtime permission configuration MUST NOT override canonical prohibitions.

Where canonical restrictions cannot be mechanically enforced, the limitation MUST be recorded.

---

## 10. Quant Validator

`quant-validator` requires:

`context: "ISOLATED_REQUIRED"`

The OpenCode adapter MUST NOT mark Quant Validator support as operational until independent subagent context has been empirically demonstrated.

The validator MUST NOT receive hidden reasoning or informal creator conclusions as authority.

It MAY receive:

- authoritative artifacts;
- specifications;
- code;
- datasets;
- Task Packet;
- Handoffs;
- governance;
- required evidence.

---

## 11. Generated Runtime Artifacts

Generated OpenCode artifacts MUST be reproducible from canonical inputs.

Generated files are deployment artifacts.

They MUST NOT become the source of truth.

A generated artifact SHOULD identify:

- adapter version;
- canonical source revision;
- project revision where applicable;
- generation timestamp;
- specialist identity.

Manual edits to generated runtime artifacts SHOULD be treated as drift.

---

## 12. Runtime Configuration Mutation

The adapter MUST NOT silently modify global OpenCode configuration.

Any mutation of:

`~/.config/opencode/opencode.jsonc`

or equivalent runtime configuration requires:

1. deterministic generation;
2. backup or recoverable previous state;
3. validation before activation;
4. explicit evidence of resulting agent registration;
5. rollback capability.

Where possible, generated configuration SHOULD minimize unrelated changes.

---

## 13. Registration Validation

A generated specialist is not considered registered merely because configuration was written.

Registration MUST be validated against the runtime.

Minimum validation:

- agent appears in runtime agent discovery;
- runtime resolves `mode: "subagent"`;
- description matches generated identity;
- prompt resolves successfully;
- required permissions are present;
- prohibited permissions are absent where mechanically enforceable.

Failure produces:

`CAPABILITY_BLOCKED`

or a more specific adapter failure.

---

## 14. Invocation Validation

Registration does not prove invocation.

Before OpenCode adapter maturity can advance beyond experimental status, the adapter MUST demonstrate that the Gentle orchestrator can invoke each required specialist through the runtime's supported delegation mechanism.

Evidence MUST distinguish:

- registration;
- invocation;
- context isolation;
- result return.

These are separate properties.

---

## 15. Result Mapping

Specialist runtime results MUST preserve canonical execution states:

- `COMPLETED`
- `BLOCKED`
- `INCONCLUSIVE`

Validator results MUST preserve:

- `PASS`
- `FAIL`
- `INCONCLUSIVE`
- `NOT_TESTED`
- `BLOCKED`

OpenCode runtime success MUST NOT automatically map to canonical `COMPLETED`.

Process execution success and task semantic completion are different properties.

---

## 16. Handoff Mapping

When a canonical workflow requires downstream work, the OpenCode specialist MUST produce a Handoff conforming to:

`agents/HANDOFF-CONTRACT-SPEC.md`

The adapter MUST NOT substitute:

- chat text;
- task-tool summaries;
- memory;
- hidden reasoning;

for a required canonical Handoff.

---

## 17. Failure Preservation

The adapter MUST preserve failures.

It MUST NOT translate:

- runtime error;
- missing governance;
- invalid Task Packet;
- failed invariant;
- missing skill;
- missing isolation;
- stale Handoff;
- required human decision;

into successful specialist completion.

Fail closed where canonical contracts require it.

---

## 18. Capability Manifest

Observed and validated behavior MUST be reflected in:

`adapters/opencode/capability-manifest.yaml`

Capabilities MUST advance only when supported by evidence.

Examples:

`NOT_TESTED -> PASS`

or:

`NOT_TESTED -> FAIL`

must be evidence-driven.

The adapter MUST NOT infer support solely from schema availability.

---

## 19. Portability Boundary

Nothing in this OpenCode adapter may require changing:

- canonical ROLE files;
- canonical SUBAGENT files;
- Task Packet contract;
- Handoff contract;
- project governance semantics;
- Quant workflow semantics.

Changing from OpenCode to another runtime should require replacing the adapter, not redesigning the Quant organization.

---

## 20. Current Status

OpenCode schema capability has been observed for:

- custom agent entries;
- `mode: "subagent"`;
- prompt configuration;
- descriptions;
- tools;
- permissions.

The following remain unvalidated:

- generated Quant specialist registration;
- Gentle-to-specialist invocation;
- specialist context isolation;
- Quant Validator independent context;
- role-specific tool restrictions;
- canonical structured result return;
- deterministic adapter regeneration.

Therefore the OpenCode adapter remains:

`EXPERIMENTAL`
