# Agent Runtime Adapter Specification

## Purpose

This specification defines the contract that any AI coding runtime must satisfy to operate under Gentle and its Quant capability.

Gentle-AI is the primary orchestration harness.

OpenCode, Cline, Codex, Claude Code, Pi, or any future runtime are execution targets only.

Canonical governance, general and Quant specialist roles, routing, skills, handoffs, and enforcement MUST remain runtime-independent.

---

## 1. Canonical Authority

The adapter MUST treat these ecosystem artifacts as authoritative:

- `governance/`
- `skills/`
- `agents/`
- `templates/`

Runtime-specific generated files are deployment artifacts, not sources of truth.

An adapter MUST NOT silently modify canonical semantics.

---

## 2. Required Runtime Capabilities

A runtime adapter MUST declare whether the target runtime supports:

- primary orchestrator context;
- isolated specialist context;
- delegated task execution;
- role-specific prompts/instructions;
- contextual skill loading;
- project governance loading;
- tool restrictions;
- filesystem scope restrictions;
- execution of verification commands;
- structured result return;
- independent validator context;
- human approval gates.

The adapter MUST carry the global task-classification decision and must not use repository type as a substitute for specialist selection.

Each capability MUST be classified as:

- `NATIVE`
- `EMULATED`
- `UNAVAILABLE`

---

## 3. Fail-Closed Capability Rule

If project governance requires a capability that the runtime cannot provide reliably, the adapter MUST NOT silently weaken the requirement.

It MUST return:

`CAPABILITY_BLOCKED`

and identify:

- missing capability;
- affected governance rule;
- affected workflow;
- possible safe alternatives.

Example:

If independent validation is required but the runtime cannot create an isolated validator context, the adapter MUST NOT substitute self-review without explicit authorization.

---

## 4. Canonical Agent Semantics

Canonical specialist semantics include:

- orchestrator-controlled invocation;
- isolated specialist context where required;
- explicit role boundary;
- explicit allowed scope;
- explicit prohibited actions;
- no implicit human authority;
- structured handoff;
- structured result;
- no silent delegation expansion.

Runtime-specific configuration MAY express these differently.

The meaning MUST remain equivalent.

---

## 5. Canonical Invocation Model

Conceptually, every specialist execution receives:

- specialist role contract;
- specialist execution contract;
- project governance;
- relevant canonical skills;
- authoritative upstream artifacts;
- current task;
- allowed scope;
- required output;
- verification requirements.

The adapter translates this package into the target runtime's supported mechanism.

---

## 6. Context Isolation

When governance or routing requires independent reasoning, the adapter MUST provide an isolated context if the runtime supports it.

The adapter MUST disclose when:

- context is shared;
- conversation history leaks across roles;
- memory is inherited;
- tools or filesystem authority are broader than requested.

Such limitations MUST NOT be hidden.

---

## 7. Skills

Canonical skills live in the Gentle Quant Ecosystem.

Adapters MAY:

- expose them through native runtime skills;
- inject their exact paths;
- load their contents into isolated contexts;
- translate them into an equivalent runtime mechanism.

Adapters MUST NOT replace canonical skill content with lossy summaries when exact rules are required.

---

## 8. Governance

Before material work, the adapter MUST make applicable governance available to the executing context.

Project governance includes:

- `.governance/CONTRACT.md`
- `.governance/INVARIANTS.md`
- `.governance/enforcement.yaml`
- `.governance/TEAM.yaml`
- `.governance/ROUTING.yaml`

Missing required governance MUST be reported.

---

## 9. Enforcement

Runtime adapters may execute enforcement mechanisms but MUST NOT redefine them.

The source of truth for project enforcement remains:

`.governance/enforcement.yaml`

Adapters MUST preserve:

- command identity;
- expected result;
- blocking semantics;
- evidence requirements;
- manual gates.

---

## 10. Structured Results

Every specialist execution MUST return enough information for Gentle-AI to determine:

- execution status;
- specialist used;
- artifacts produced;
- evidence produced;
- failed checks;
- unresolved assumptions;
- unresolved risks;
- handoff status;
- next authorized action;
- whether human authority is required.

Adapters MUST NOT translate failure states into success states.

---

## 11. Human Authority

Adapters MUST preserve human-only decisions.

They MUST NOT manufacture approval for:

- critical invariant changes;
- risk acceptance;
- production release;
- live financial side effects;
- governance overrides.

---

## 12. Runtime Capability Manifest

Every adapter MUST provide a machine-readable capability manifest.

Minimum fields:

- adapter name;
- adapter version;
- runtime name;
- runtime version;
- capability matrix;
- known limitations;
- supported specialist execution model;
- supported skill-loading model;
- supported governance-loading model;
- supported enforcement model.

---

## 13. Portability Requirement

Changing runtime MUST NOT require modification of canonical:

- specialist ROLE files;
- governance rules;
- project invariants;
- project routing;
- enforcement semantics;
- handoff contracts.

Only the adapter implementation may change.

---

## 14. Validation Requirement

Before an adapter is considered usable, it MUST demonstrate:

1. canonical role preservation;
2. governance loading;
3. specialist isolation behavior;
4. skill delivery;
5. structured result return;
6. failure-state preservation;
7. human-gate preservation;
8. deterministic regeneration of deployment artifacts where applicable.

---

## 15. Adapter Status

Allowed adapter maturity:

- `EXPERIMENTAL`
- `VALIDATING`
- `SUPPORTED`
- `BLOCKED`

An adapter MUST NOT claim `SUPPORTED` without passing its validation suite.
