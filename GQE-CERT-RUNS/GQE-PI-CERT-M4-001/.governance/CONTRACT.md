# Project Governance Contract — GQE × Pi M4 Certification

## Status

- Governance status: `APPROVED`
- Human approved: `YES`
- Contract version: `1`
- Last reviewed: `2026-09-26`
- Approval basis: `USER_DECLARED` — the project owner (Portfolio Manager / Head of Quant)
  defined this certification run and its acceptance criteria in the M4 acceptance brief.

---

## 1. Project Identity

- Project name: `GQE-PI-CERT-M4-001`
- Repository: `/home/datawithjose/Documents/GQE-CERT-RUNS/GQE-PI-CERT-M4-001` (disposable, own Git repo)
- Project type: `certification` — runtime acceptance test of Pi as a GQE execution backend
- Primary domain: quantitative risk research (research methodology only)
- Lifecycle stage: `certification`

Canonical ecosystem authority (read-only, MUST NOT be modified):

- `/home/datawithjose/Documents/GENTLE-QUANT-ECOSYSTEM` @ `ff16b6b1e21f34a6df9e72d6121bac93ee8fcd4b`

This workspace has its own governance. It MUST NOT reuse the governance of any other
project (for example `chartpy_copy/.governance/*`).

---

## 2. Purpose

### Primary objective

Prove that the Pi runtime can preserve Gentle Quant Ecosystem authority across one
continuous end-to-end lifecycle: governance preflight, classification, routing, READY
Task Packet, one Quant Researcher execution, persisted result, canonical Handoff,
independent Quant Validator execution in a distinct context, enforcement evaluation,
and the Human Gate — without silent degradation.

### Primary users / operators

- Portfolio Manager / Head of Quant (final human authority)
- Quant Orchestrator (Gentle-AI on Pi; the parent session)

### Decision or business impact

The result decides whether Pi may be declared a `SUPPORTED` GQE runtime. It does not
decide any trading action.

---

## 3. Scope

### In scope

- one research-methodology task (`quantitative_research`);
- one `quant-researcher` execution;
- one canonical `quant-researcher` → `quant-validator` Handoff;
- one `quant-validator` execution in a distinct child context;
- one enforcement evaluation against executable controls;
- one Human Gate record and one production disposition;
- hashes and audit evidence for every authoritative artifact.

### Out of scope

- production implementation of any kind;
- Quant Developer and Quant Data Engineer work;
- redesign of GQE canonical files;
- runtime selection changes mid-run.

### Non-goals

- proving profitability, validating a production model, or authorizing trading;
- reusing prior QR/QV outputs from earlier runs.

---

## 4. Operating Modes

| Mode | Exists | Side effects allowed | Activated by | Approval required |
| --- | --- | --- | --- | --- |
| `RESEARCH_ONLY` | yes | filesystem research artifacts only | orchestrator | contract (this file) |
| `SIMULATION` | no | — | — | — |
| `BACKTESTING` | no | — | — | — |
| `PAPER_TRADING` | no | — | — | — |
| `ADVISORY_SIGNALS` | no | — | — | — |
| `PRODUCTION_LIVE` | no | — | — | PM/HoQ + all applicable gates |

In `RESEARCH_ONLY`, `trade_authorized` MUST remain `false`.

---

## 5. Priority Order

`USER_DECLARED` by the project owner:

1. correctness of evidence;
2. human authority;
3. separation of duties / independence;
4. reproducibility and auditability;
5. fail-closed enforcement;
6. speed of execution.

---

## 6. Risk Profile

Class: `HIGH`

Foreseeable harmful failures:

- a false `SUPPORTED` runtime declaration based on prose instead of executable evidence;
- an unenforced control reported as `ENFORCED`;
- QR and QV collapsing into one context or one regenerated artifact;
- a production or trading authorization inferred from agent output;
- canonical GQE files modified during certification.

---

## 7. Data and External Boundaries

- Authoritative inputs: canonical GQE specs (read-only), the M4 acceptance brief, and the
  artifacts produced inside this workspace.
- External APIs / brokers / exchanges: none.
- Secrets: none stored in this workspace.

---

## 8. Human Authority

Reserved to the Portfolio Manager / Head of Quant:

- changing project objectives;
- changing critical invariants;
- accepting unresolved risk;
- production deployment;
- enabling live financial side effects;
- overriding a failed governance gate;
- deciding the final production disposition.

No agent, specialist, adapter, or memory system may grant these approvals.

---

## 9. Agent Authority

Agents MAY: investigate, research, propose, validate, execute verification commands,
and produce artifacts inside this workspace.

Agents MUST NOT: approve production, modify canonical GQE files, exceed the declared
execution budget, retry a failed specialist automatically, or expand specialist authority
through task wording.

---

## 10. Evidence and Completion

Distinguish explicitly:

- work completed;
- checks executed;
- invariants verified;
- independent review completed;
- governance gates passed;
- human approval received.

Agent statements alone are not evidence. A declared `ENFORCED` control without
executable evidence MUST NOT be treated as satisfied.

Completion of the certification run means: the lifecycle reached the Human Gate and the
enforcement evaluation was executed and reported honestly. It does not mean production
approval.

---

## 11. Source Classification

Every material statement is traceable to `DISCOVERED`, `USER_DECLARED`, `DERIVED`, or
`UNKNOWN`.

---

## 12. Open Questions

- `UNKNOWN`: whether QR and QV share model error modes (same provider/model family).
  Recorded as a control limitation, never as independence evidence.

---

## 13. Approval

### Agent preparation status

`READY_FOR_APPROVAL`

### Project owner decision

`APPROVED`

Approved by: Portfolio Manager / Head of Quant (project owner)

Date: 2026-09-26

Notes: Approval covers the certification workflow only. Production approval is a separate
decision and is NOT granted by this contract.
