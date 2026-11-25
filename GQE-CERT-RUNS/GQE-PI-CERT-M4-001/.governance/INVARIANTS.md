# Project Invariants — GQE × Pi M4 Certification

## Status

- Invariant set version: `1`
- Human approved: `YES` (`USER_DECLARED` via the M4 acceptance brief)
- Last reviewed: `2026-09-26`

An invariant written here is NOT automatically considered enforced. Enforcement status
is justified in `.governance/ENFORCEMENT-MATRIX.md` and exercised by
`evidence/controls/evaluate_enforcement.py`.

---

## 1. Severity Levels

`CRITICAL` — violation invalidates the certification result.
`HIGH` — violation materially compromises correctness or auditability.
`MEDIUM` — degrades an important property but does not invalidate the run immediately.
`LOW` — desirable constraint.

## 2. Enforcement Status

`NOT_ENFORCED` | `TEST_REQUIRED` | `MANUAL_GATE` | `ENFORCED`.
`ENFORCED` requires an executable control that exists, is connected to the behavior,
runs, and can block.

---

## 3. Invariant Register

---

### PROJECT-INV-001 — Final human authority over production

**Status:** `APPROVED`

**Severity:** `CRITICAL`

**Source:** `USER_DECLARED`

**Owner:** `portfolio_manager`

#### Rule

Production approval and any live financial side effect MUST be decided by the Portfolio
Manager / Head of Quant. No agent, specialist, adapter, orchestrator, or memory system
may grant, infer, or manufacture that approval.

#### Why it exists

Prevents an autonomous system from converting research output into an authorized action.

#### Scope

Every transition from research/validation into production or trading.

#### Violation condition

A production disposition of `APPROVED` without an explicit recorded human decision, or
any artifact that sets `trade_authorized = true` in `RESEARCH_ONLY`.

#### Verification

**Enforcement status:** `ENFORCED`

**Verification mechanism:** `evidence/controls/evaluate_enforcement.py` control
`CTRL-CERT-002` requires `gates/HUMAN-GATE.md` with status `HUMAN_DECISION_REQUIRED`,
and `CTRL-CERT-003` requires `trade_authorized: false` in the final disposition.

**Expected evidence:** evaluator JSON output + report; gate record; disposition record.

#### Failure consequence

block task completion; block deployment; block financial side effects; require human decision.

#### Exceptions

`NONE`

#### Traceability

- Related contract section: `CONTRACT.md` §8, §10
- Related tests: `evidence/controls/evaluate_enforcement.py`
- Related enforcement rule: `MATERIAL_HUMAN_REVIEW`, `LLM_CANNOT_EXECUTE_DIRECTLY`
- Related specification: `GENTLE-OPERATIONAL-LOOP-SPEC.md` §1, §17
- Related incident/decision: M4 acceptance brief

---

### PROJECT-INV-002 — Research-only posture

**Status:** `APPROVED`

**Severity:** `CRITICAL`

**Source:** `USER_DECLARED`

**Owner:** `portfolio_manager`

#### Rule

The run performs research methodology only. `trade_authorized` MUST remain `false` for
the whole run.

#### Why it exists

Canonical `LLM_CANNOT_EXECUTE_DIRECTLY` requires `trade_authorized = false` in
`RESEARCH_ONLY`; a high score, positive forecast, or `PASS_RESEARCH` MUST NOT activate
trading credentials.

#### Scope

Every artifact and every terminal state of this run.

#### Violation condition

`trade_authorized` is anything other than `false`, or a specialist enables trading intent.

#### Verification

**Enforcement status:** `ENFORCED`

**Verification mechanism:** control `CTRL-CERT-003` (executable parse of the final
disposition + gate record).

**Expected evidence:** evaluator output; `gates/FINAL-DISPOSITION.md`.

#### Failure consequence

block task completion; block financial side effects; require human decision.

#### Exceptions

`NONE`

#### Traceability

- Related contract section: `CONTRACT.md` §4
- Related enforcement rule: `LLM_CANNOT_EXECUTE_DIRECTLY`

---

### PROJECT-INV-003 — Execution budget: one QR, one QV, zero QD/DE, no retry

**Status:** `APPROVED`

**Severity:** `CRITICAL`

**Source:** `USER_DECLARED`

**Owner:** `quant_orchestrator`

#### Rule

Exactly one `quant-researcher` execution and exactly one `quant-validator` execution.
Zero `quant-developer` executions. Zero `quant-data-engineer` executions. No automatic
retry after any specialist result. No additional research branches.

#### Why it exists

Bounded, reproducible certification; unbounded retries would allow result-shopping.

#### Scope

The whole run.

#### Violation condition

Any second execution of QR or QV, any QD/DE execution, or a retry triggered without a
new human authorization.

#### Verification

**Enforcement status:** `ENFORCED`

**Verification mechanism:** control `CTRL-CERT-006` reads the orchestrator execution
ledger `evidence/executions.json` and the specialist result records
`authoritative-inputs/*.meta.txt`.

**Expected evidence:** evaluator output; ledger; meta records.

#### Failure consequence

block task completion; invalidate the certification result.

#### Exceptions

`NONE`

#### Traceability

- Related contract section: `CONTRACT.md` §3, §9
- Related enforcement rule: project rule `CERT-BUDGET-001`

---

### PROJECT-INV-004 — Validator context separation

**Status:** `APPROVED`

**Severity:** `CRITICAL`

**Source:** `USER_DECLARED`

**Owner:** `quant_orchestrator`

#### Rule

`quant-researcher` and `quant-validator` MUST execute in distinct child task and session
contexts. The validator MUST NOT share the researcher's conversation context or hidden
reasoning.

#### Why it exists

Canonical `quant-validator` declares `context: ISOLATED_REQUIRED`; if the runtime cannot
preserve isolation it MUST return `CAPABILITY_BLOCKED` rather than silently degrade.

#### Scope

The delegated specialist executions.

#### Violation condition

Identical child task id or identical child session id for QR and QV, or QV receiving QR
conversation/hidden reasoning.

#### Verification

**Enforcement status:** `ENFORCED`

**Verification mechanism:** control `CTRL-CERT-001` compares the recorded QR and QV child
task ids and session ids from `evidence/executions.json` and requires both to differ.

**Expected evidence:** evaluator output; `evidence/executions.json`.

#### Failure consequence

block task completion; invalidate validation independence.

#### Exceptions

`NONE`

#### Traceability

- Related contract section: `CONTRACT.md` §3
- Related enforcement rule: `EFFECTIVE_CHALLENGE`

---

### PROJECT-INV-005 — QV receives persisted authority, not regenerated QR work

**Status:** `APPROVED`

**Severity:** `HIGH`

**Source:** `USER_DECLARED`

**Owner:** `quant_orchestrator`

#### Rule

The validator receives the frozen persisted artifacts (QR result, canonical Handoff,
task packets) with hashes. It MUST NOT receive a regenerated or paraphrased version of
the research, and the researched artifacts MUST NOT change while QV runs.

#### Why it exists

Prevents stale or substituted authority from silently replacing what was produced.

#### Scope

The Handoff and the QV task packet.

#### Violation condition

Hash mismatch between the frozen pre-QV snapshot and the post-QV state. (The packet may
also carry a forbidden-`cd`/`cp` instruction to make regeneration impossible.)

#### Verification

**Enforcement status:** `ENFORCED`

**Verification mechanism:** control `CTRL-CERT-009` compares
`evidence/pre-qv-snapshot.sha256` with a recomputed digest of the same file set after QV.

**Expected evidence:** evaluator output; snapshot files.

#### Failure consequence

block task completion; mark downstream authority stale.

#### Exceptions

`NONE`

#### Traceability

- Related contract section: `CONTRACT.md` §10
- Related enforcement rule: `VERSION_EVERYTHING`

---

### PROJECT-INV-006 — Fail-closed enforcement

**Status:** `APPROVED`

**Severity:** `CRITICAL`

**Source:** `USER_DECLARED`

**Owner:** `quant_orchestrator`

#### Rule

Enforcement MUST evaluate declared controls against real mechanisms. A declared
`ENFORCED` control with no executable evidence MUST NOT be treated as satisfied. An
`UNKNOWN` control state BLOCKS the transition that requires it. A material failure of a
critical invariant fails closed.

#### Why it exists

Canonical `CONTRADICTION_BLOCKS_EXECUTION`: an applicable gate in `UNKNOWN` MUST block.
A written rule is not an implemented control.

#### Scope

Every declared control in `.governance/enforcement.yaml`.

#### Violation condition

A control declared `ENFORCED` whose mechanism cannot be resolved to an executable check,
or a control whose check returns `UNKNOWN`/`NOT_SATISFIED`, is reported as satisfied.

#### Verification

**Enforcement status:** `ENFORCED`

**Verification mechanism:** `evidence/controls/evaluate_enforcement.py` resolves each
declared control to a named executable check; unresolvable `ENFORCED` declarations are
reported `NOT_SATISFIED`; indeterminate results are reported `UNKNOWN`; both are
blocking. Exit code 1 on any unsatisfied blocking control.

**Expected evidence:** `evidence/enforcement-evaluation.json` + evaluator stdout + the
planted probe `CTRL-CERT-007`.

#### Failure consequence

block task completion; block production; require human decision.

#### Exceptions

`NONE`

#### Traceability

- Related contract section: `CONTRACT.md` §10
- Related enforcement rule: `CONTRADICTION_BLOCKS_EXECUTION`
- Related specification: `GENTLE-OPERATIONAL-LOOP-SPEC.md` §16

---

### PROJECT-INV-007 — Agent claims are not evidence

**Status:** `APPROVED`

**Severity:** `HIGH`

**Source:** `USER_DECLARED`

**Owner:** `quant_orchestrator`

#### Rule

Specialist prose, model confidence, and persuasive narrative MUST NOT be accepted as
verification evidence. A check counts as executed only with recorded command output,
hash, or artifact.

#### Why it exists

Canonical `EFFECTIVE_CHALLENGE` / `INDEPENDENCE_BEFORE_VOTE` require observable evidence
and adversarial verification, not agreement.

#### Scope

Every check reported in packets, handoffs, results, and the final report.

#### Violation condition

An `executed_checks` entry with no evidence path or observable output.

#### Verification

**Enforcement status:** `MANUAL_GATE`

**Verification mechanism:** No reliable automation proves that a human-readable evidence
path truly corresponds to the claimed observation; the Human Gate reviewer must inspect
`evidence/` and the QV-reported evidence. Partial automatic support: control
`CTRL-CERT-004` requires the artifact hash manifest to exist and cover all artifacts.

**Expected evidence:** evaluator output for `CTRL-CERT-004`; human gate record.

#### Failure consequence

block review; require human decision.

#### Exceptions

`NONE`

#### Traceability

- Related contract section: `CONTRACT.md` §10
- Related enforcement rule: `EFFECTIVE_CHALLENGE`

---

### PROJECT-INV-008 — No production implementation, no QD/DE

**Status:** `APPROVED`

**Severity:** `CRITICAL`

**Source:** `USER_DECLARED`

**Owner:** `quant_orchestrator`

#### Rule

No production implementation is produced or requested. `quant-developer` and
`quant-data-engineer` MUST NOT execute.

#### Why it exists

The acceptance brief scopes the run to research methodology.

#### Scope

The whole run.

#### Violation condition

A QD/DE execution, or a produced production artifact.

#### Verification

**Enforcement status:** `ENFORCED`

**Verification mechanism:** control `CTRL-CERT-006` (execution ledger) plus
`CTRL-CERT-011` (workspace contains no production source tree).

**Expected evidence:** evaluator output.

#### Failure consequence

block task completion.

#### Exceptions

`NONE`

#### Traceability

- Related contract section: `CONTRACT.md` §3
- Related enforcement rule: project rule `CERT-SCOPE-001`

---

### PROJECT-INV-009 — Canonical GQE remains unchanged

**Status:** `APPROVED`

**Severity:** `HIGH`

**Source:** `USER_DECLARED`

**Owner:** `quant_orchestrator`

#### Rule

Every file under `/home/datawithjose/Documents/GENTLE-QUANT-ECOSYSTEM` MUST remain
byte-identical for the duration of the run.

#### Why it exists

A runtime adapter MUST NOT silently modify canonical semantics.

#### Scope

The canonical ecosystem repository.

#### Violation condition

A non-empty `git status --porcelain` or a changed canonical revision in GQE.

#### Verification

**Enforcement status:** `ENFORCED`

**Verification mechanism:** control `CTRL-CERT-010` runs
`git -C /home/datawithjose/Documents/GENTLE-QUANT-ECOSYSTEM status --porcelain` and
compares `rev-parse HEAD` with the pre-run revision.

**Expected evidence:** evaluator output; `evidence/canon-revision-before.txt` /
`evidence/canon-revision-after.txt`.

#### Failure consequence

block task completion; invalidate the certification.

#### Exceptions

`NONE`

#### Traceability

- Related contract section: `CONTRACT.md` §1
- Related enforcement rule: `VERSION_EVERYTHING`

---

### PROJECT-INV-010 — Statistical independence of QR and QV error modes

**Status:** `APPROVED`

**Severity:** `HIGH`

**Source:** `DERIVED` — derived from the fact that all GQE Pi specialist wrappers pin the
same provider/model family (`commandcode/deepseek/deepseek-v4.1-flash`), so shared
training/decoding error modes cannot be excluded.

**Owner:** `quant_orchestrator`

#### Rule

Shared model or provider MUST be recorded as a possible dependency and MUST NOT be
presented as proof of error independence. Where genuine statistical independence cannot
be demonstrated, the property MUST be reported as not established.

#### Why it exists

Canonical `EFFECTIVE_CHALLENGE` states that sharing a model or provider MUST be recorded
as a possible dependency, not as evidence of independence. Canonical
`INDEPENDENCE_BEFORE_VOTE` requires independence before treating agreement as
confirmation.

#### Scope

The QR→QV independence claim.

#### Violation condition

A report claims statistical independence of QR and QV error modes solely because the
child contexts/sessions differ.

#### Verification

**Enforcement status:** `NOT_ENFORCED`

**Verification mechanism:** No executable mechanism in this runtime can establish
independence of shared-model error modes. `.governance/enforcement.yaml` additionally
declares `CTRL-CERT-007` as `ENFORCED` as a deliberate fail-closed probe: the evaluator
MUST detect that no executable check backs that declaration and MUST report
`NOT_SATISFIED` (PROJECT-INV-006).

**Expected evidence:** evaluator output showing `CTRL-CERT-007 = NOT_SATISFIED`.

#### Failure consequence

block task completion; require human decision; record as residual risk.

#### Exceptions

`NONE` — the limitation must remain visible.

#### Traceability

- Related contract section: `CONTRACT.md` §12
- Related enforcement rule: `EFFECTIVE_CHALLENGE`, `INDEPENDENCE_BEFORE_VOTE`

---

## 4. Critical Invariant Summary

| ID | Invariant | Severity | Enforcement | Owner |
| --- | --- | --- | --- | --- |
| PROJECT-INV-001 | Final human authority over production | CRITICAL | ENFORCED | portfolio_manager |
| PROJECT-INV-002 | Research-only posture (`trade_authorized=false`) | CRITICAL | ENFORCED | portfolio_manager |
| PROJECT-INV-003 | One QR, one QV, zero QD/DE, no retry | CRITICAL | ENFORCED | quant_orchestrator |
| PROJECT-INV-004 | Validator context separation | CRITICAL | ENFORCED | quant_orchestrator |
| PROJECT-INV-005 | QV receives persisted authority | HIGH | ENFORCED | quant_orchestrator |
| PROJECT-INV-006 | Fail-closed enforcement | CRITICAL | ENFORCED | quant_orchestrator |
| PROJECT-INV-007 | Agent claims are not evidence | HIGH | MANUAL_GATE | quant_orchestrator |
| PROJECT-INV-008 | No production implementation, no QD/DE | CRITICAL | ENFORCED | quant_orchestrator |
| PROJECT-INV-009 | Canonical GQE unchanged | HIGH | ENFORCED | quant_orchestrator |
| PROJECT-INV-010 | QR/QV statistical independence | HIGH | NOT_ENFORCED | quant_orchestrator |

---

## 5. Unenforced Invariants

- `PROJECT-INV-007` — `MANUAL_GATE`: requires Human Gate review.
- `PROJECT-INV-010` — `NOT_ENFORCED`: shared-model error modes cannot be excluded; the
  limitation stays visible and is escalated to the Human Gate.

## 6. Change Control

Changing or deleting a `CRITICAL` invariant requires explicit human approval. Agents MUST
NOT weaken an invariant to make a failing implementation pass.
