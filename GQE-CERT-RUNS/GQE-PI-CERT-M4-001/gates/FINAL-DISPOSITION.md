# FINAL PRODUCTION DISPOSITION — GQE-PI-CERT-M4-001

run_id: GQE-PI-CERT-M4-001
recorded_at_utc: 2026-09-26T20:32:00Z
recorded_by: quant-orchestrator
authority: none (this file records state; it does not grant authority)

## Disposition

production_status: NOT_APPROVED
production_disposition: REJECTED_FOR_PRODUCTION
trade_authorized: false
deployment_authorized: false
implementation_authorized: false
live_financial_side_effects: NONE
human_gate_status: HUMAN_DECISION_RECORDED
human_gate_decision: REJECT_RESEARCH_CANDIDATE_FOR_PRODUCTION
human_gate_previous_status: HUMAN_DECISION_REQUIRED
human_gate_ratified_at_utc: 2026-09-26T20:48:00Z
research_iterations_started: 1
research_iterations_authorized_additional: 0
retries_performed: 0
automatic_retry: false
run_status: CLOSED
certification_run_disposition: CLOSED
pi_runtime_support_status: SUPPORTED_WITH_LIMITATIONS

## Scope of the rejection

The human decision rejects **only** the quantitative research / methodology candidate
generated inside `GQE-PI-CERT-M4-001` (sha256
`d27f373fd0f3c0af7ac1caa6304dbaf044d905dfd6e93ff6a9fc7a1e9d14bdae`).

It does **NOT** reject the Gentle Quant Ecosystem, Pi, `quant-researcher` as a role,
`quant-validator` as a role, or the GQE architecture. The runtime certification result is
unaffected: `CERTIFICATION-REPORT.md` §1 and `runtime/PI-CAPABILITY-MANIFEST.yaml`
(`SUPPORTED_WITH_LIMITATIONS`) remain authoritative for the runtime question.

## Basis

1. Independent validation terminal state is `FAIL`
   (`authoritative-inputs/qv-result.md`, sha256
   `35b861a305c39c9a8133f6f721ac11ce3e1cba41b1238bee193f8ca1dda6e8d8`).
   Canonical `CONTRADICTION_BLOCKS_EXECUTION` and control `CTRL-CERT-005` block progression
   on a non-`PASS` validator state.
2. Enforcement evaluation reports unsatisfied blocking controls
   (`evidence/enforcement-evaluation.json`), including the deliberate fail-closed probe
   `CTRL-CERT-007` (declared `ENFORCED`, no executable mechanism -> `NOT_SATISFIED`) and the
   `UNKNOWN` control `CTRL-CERT-013`.
3. No production implementation exists and none is authorized (`PROJECT-INV-008`).
4. The run is `RESEARCH_ONLY`; canonical `LLM_CANNOT_EXECUTE_DIRECTLY` requires
   `trade_authorized = false`.
5. Final human authority HAS been exercised: the gate moved from `HUMAN_DECISION_REQUIRED`
   to `HUMAN_DECISION_RECORDED` with decision
   `REJECT_RESEARCH_CANDIDATE_FOR_PRODUCTION`. The human decision confirms and ratifies the
   fail-closed rejection; it does not reopen, soften or re-validate any finding.

## Ratification of this record

This file was intentionally updated by the Human Gate disposition
(`HUMAN_DECISION_RECORDED` / `REJECT_RESEARCH_CANDIDATE_FOR_PRODUCTION`).

- It is a **human-gate ratification**, not a mutation of QR/QV evidence.
- `authoritative-inputs/qr-result.md`, `authoritative-inputs/HANDOFF-QR-to-QV.yaml` and
  `authoritative-inputs/qv-result.md` were NOT modified and remain byte-identical.
- The QV terminal state remains `FAIL` exactly as produced.
- The pre-ratification content and hashes are preserved in
  `evidence/human-gate-ratification/`.

## What would have to change for a different disposition

- The failing claims would have to be corrected under change control and re-validated by a
  separately budgeted independent validation run.
- The unresolved statistical-independence limitation would have to be accepted explicitly by
  human authority or removed by an independence mechanism this runtime does not provide.
- An explicit human decision at the gate would have to approve a specific candidate version
  for a specific, bounded purpose.

None of these conditions is met. The human decision recorded above was to REJECT.
No agent, specialist, adapter, orchestrator, or memory system may change this disposition.
Opening a bounded corrective iteration would require a **new** human decision and a **new**
task packet; it is not authorized by this record.

## Closed state

This certification run is `CLOSED`. No further specialist execution, retry, research branch
or repair is authorized under this run_id.
