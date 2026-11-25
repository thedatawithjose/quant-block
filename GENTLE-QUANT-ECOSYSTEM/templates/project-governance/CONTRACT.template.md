# Project Governance Contract

## Status

- Governance status: `DRAFT`
- Human approved: `NO`
- Contract version: `1`
- Last reviewed: `UNSET`

A project MUST NOT treat this contract as authoritative until the project owner explicitly approves it.

---

## 1. Project Identity

- Project name:
- Repository:
- Project type:
- Primary domain:
- Lifecycle stage:

## 2. Purpose

### Primary objective

Describe what the system is intended to accomplish.

### Primary users / operators

Describe who uses, operates, or relies on the system.

### Decision or business impact

Describe what real-world decisions or actions can depend on this system.

---

## 3. Scope

### In scope

List the capabilities this project is responsible for.

### Out of scope

List capabilities this project explicitly does not own.

### Non-goals

List plausible capabilities that must not be silently introduced.

---

## 4. Operating Modes

Document all relevant modes, for example:

- research;
- simulation;
- backtesting;
- paper trading;
- advisory/signals;
- production/live.

For each mode state:

- whether it exists;
- what side effects are allowed;
- who may activate it;
- what approval is required.

---

## 5. Priority Order

Record the project's explicit priority hierarchy.

Example categories:

1. correctness;
2. safety / capital preservation;
3. causality;
4. reproducibility;
5. auditability;
6. maintainability;
7. performance;
8. development speed.

Do not infer the ordering. It requires owner approval.

---

## 6. Risk Profile

Describe failures that would be materially harmful.

Include where applicable:

- financial loss;
- incorrect research conclusions;
- look-ahead or data leakage;
- corrupted or incomplete data;
- incorrect execution;
- duplicate side effects;
- credential exposure;
- unavailable service;
- unreproducible results.

Classify project risk:

`LOW | MODERATE | HIGH | CRITICAL`

Record the reason for the classification.

---

## 7. Data and External Boundaries

Identify:

- authoritative data sources;
- external APIs;
- databases;
- brokers/exchanges;
- files or datasets;
- infrastructure/services;
- deployment targets;
- secrets or credentials boundaries.

Do not store secrets in this document.

---

## 8. Human Authority

Define decisions that require explicit human approval.

At minimum determine authority for:

- changing project objectives;
- changing critical invariants;
- accepting unresolved risk;
- production deployment;
- enabling live financial side effects;
- overriding failed governance gates.

An AI agent MUST NOT grant itself these approvals.

---

## 9. Agent Authority

Define what agents may:

- investigate;
- propose;
- implement;
- test;
- review;
- refactor;
- deploy.

Define what agents MUST NOT do without human authorization.

---

## 10. Evidence and Completion

Define what evidence is required before work may be declared complete.

Distinguish:

- implementation completed;
- tests executed;
- invariants verified;
- independent review completed;
- governance gates passed;
- human approval received.

Agent statements alone are not evidence.

---

## 11. Source Classification

Every material contract statement should be traceable to one of:

- `DISCOVERED` — verified from repository or infrastructure;
- `USER_DECLARED` — explicitly provided by the project owner;
- `DERIVED` — logically derived from verified facts and identified as such;
- `UNKNOWN` — unresolved.

Do not silently convert assumptions into facts.

---

## 12. Open Questions

List unresolved questions that materially affect governance.

Critical unknowns block status `READY_FOR_APPROVAL`.

---

## 13. Approval

### Agent preparation status

`NOT_READY | READY_FOR_APPROVAL`

### Project owner decision

`PENDING | APPROVED | REJECTED`

Approved by:

Date:

Notes:
