# Project Invariants

## Status

- Invariant set version: `1`
- Human approved: `NO`
- Last reviewed: `UNSET`

This file defines properties that project changes MUST preserve.

An invariant written here is NOT automatically considered enforced.

---

## 1. Severity Levels

Use only:

- `CRITICAL` — violation can invalidate results, create unacceptable risk, corrupt state, or cause dangerous side effects.
- `HIGH` — violation materially compromises correctness, reliability, security, or reproducibility.
- `MEDIUM` — violation degrades an important project property but does not invalidate the system immediately.
- `LOW` — desirable constraint with limited operational impact.

Severity MUST reflect consequence, not implementation difficulty.

---

## 2. Enforcement Status

Every invariant MUST have exactly one current enforcement status:

- `NOT_ENFORCED` — declared rule with no reliable verification mechanism.
- `TEST_REQUIRED` — an automated check is feasible but does not yet exist.
- `MANUAL_GATE` — requires explicit human review because reliable automation is unavailable.
- `ENFORCED` — an executable control exists and can block failure.

Do not label an invariant `ENFORCED` merely because an agent was instructed to respect it.

---

## 3. Source Classification

Every invariant MUST identify its authority source:

- `USER_DECLARED`
- `DISCOVERED`
- `DERIVED`

`DERIVED` invariants MUST state the facts from which they were derived and require human confirmation before becoming authoritative.

Agents MUST NOT invent invariants from assumptions.

---

## 4. Invariant Register

Use one block per invariant.

---

### PROJECT-INV-001 — <Short invariant name>

**Status:** `DRAFT`

**Severity:** `CRITICAL | HIGH | MEDIUM | LOW`

**Source:** `USER_DECLARED | DISCOVERED | DERIVED`

**Owner:** `<human or responsible role>`

#### Rule

State the property that MUST remain true.

Use precise language that can be evaluated.

#### Why it exists

Explain the failure or risk this invariant prevents.

#### Scope

Identify the components, workflows, data, or operating modes to which the invariant applies.

#### Violation condition

Describe observable conditions that constitute a violation.

Avoid vague language such as "works correctly".

#### Verification

**Enforcement status:** `NOT_ENFORCED | TEST_REQUIRED | MANUAL_GATE | ENFORCED`

**Verification mechanism:**

Describe the test, static check, runtime assertion, CI gate, audit procedure, or human review that verifies the invariant.

**Expected evidence:**

Describe the artifact proving that verification actually occurred.

Examples:

- test result;
- CI job;
- signed report;
- deterministic comparison;
- audit record;
- manual approval record.

#### Failure consequence

Define what MUST happen if verification fails.

Choose explicitly where applicable:

- block task completion;
- block review;
- block merge;
- block deployment;
- block financial side effects;
- require human decision.

#### Exceptions

State approved exceptions.

Use `NONE` when no exception exists.

An agent MUST NOT create an exception for itself.

#### Traceability

- Related contract section:
- Related tests:
- Related enforcement rule:
- Related specification:
- Related incident/decision:

---

## 5. Critical Invariant Summary

Maintain a compact index after invariants are defined.

| ID | Invariant | Severity | Enforcement | Owner |
|---|---|---|---|---|
| PROJECT-INV-001 | UNSET | UNSET | NOT_ENFORCED | UNSET |

---

## 6. Unenforced Invariants

List every invariant whose enforcement status is:

- `NOT_ENFORCED`;
- `TEST_REQUIRED`;
- `MANUAL_GATE`.

The project MUST NOT hide these limitations when reporting governance status.

---

## 7. Change Control

Changing or deleting a `CRITICAL` invariant requires explicit human approval.

When an invariant changes:

1. record why;
2. identify affected tests and enforcement;
3. update traceability;
4. rerun applicable verification;
5. preserve the change in version control.

Agents MUST NOT weaken an invariant simply to make a failing implementation pass.

---

## 8. Approval

### Agent preparation status

`NOT_READY | READY_FOR_APPROVAL`

### Project owner decision

`PENDING | APPROVED | REJECTED`

Approved by:

Date:

Notes:
