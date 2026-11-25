# Control implementation note — enforcement evaluator self-correction

This note records a defect found and corrected **inside the certification's own enforcement
tooling** during this run. It is disclosed here so the evaluation cannot be read as
"the tool always agreed with the declarations".

## Defect 1 — execution-ledger accessor

`evidence/controls/evaluate_enforcement.py` read role identity (`task_id`, `session_id`,
`terminal_state`, `subagent_invocations`) from the top level of each role object in
`evidence/executions.json`, while the ledger stores those fields inside `executions[seq]`.

Observed effect on the first evaluation run: `CTRL-CERT-001` (validator context separation)
and `CTRL-CERT-008` (specialist tool allowlists) were reported `NOT_SATISFIED` even though
the underlying facts were satisfied. Fail-closed direction, but a **false negative** caused
by the control, not by the behavior it protects.

Correction: a `role_record()` accessor now reads both ledger shapes. The uncorrected outputs
are preserved as `evidence/enforcement-evaluation.RUN1-ledger-accessor-defect.json` and
`evidence/ENFORCEMENT-REPORT.RUN1-ledger-accessor-defect.md`.

## Defect 2 — misleading reason text for manual gates

A `manual_gate` mechanism (`CTRL-CERT-012`) was reported with the generic reason
"mechanism check ... could not be resolved". The observed result (`UNKNOWN`, blocking) was
correct; the reason was wrong and could be misread as a broken control.

Correction: manual gates now report that the gate is declared and not yet discharged by a
human decision, and name the observable anchor.

## Why this is disclosed and not hidden

- The correction changed control results from `NOT_SATISFIED` to `SATISFIED` for two
  controls, which is exactly the kind of change that could hide a real failure if undisclosed.
- After correction, all remaining unsatisfied controls are unsatisfied for reasons unrelated
  to the accessor:
  - `CTRL-CERT-005` — the validator really returned `FAIL`.
  - `CTRL-CERT-007` — the deliberate fail-closed probe really has no executable mechanism.
  - `CTRL-CERT-012` — the manual gate is really not yet discharged.
  - `CTRL-CERT-013` — the independence control is really `UNKNOWN`.
- Both pre-correction and post-correction runs are preserved. A third party can re-execute
  either version of the ledger against the current script and reproduce the difference.

## What was NOT changed

- No control was removed, downgraded, or re-declared.
- `.governance/enforcement.yaml` was not modified (it is frozen in
  `evidence/pre-qv-snapshot.sha256`).
- `evidence/executions.json` was not modified after the correction.
- The probe `CTRL-CERT-007` was left as a false `ENFORCED` declaration on purpose.
