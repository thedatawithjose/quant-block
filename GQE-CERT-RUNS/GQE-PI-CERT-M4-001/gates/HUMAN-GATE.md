# HUMAN GATE — GQE-PI-CERT-M4-001

## status

`HUMAN_DECISION_RECORDED`

previous_status: `HUMAN_DECISION_REQUIRED`
ratified_at_utc: `2026-09-26T20:48:00Z`
ratified_by: Portfolio Manager / Head of Quant (project owner, human authority)

## gate_identity

| Field | Value |
| --- | --- |
| run_id | `GQE-PI-CERT-M4-001` |
| gate_id | `GQE-PI-CERT-M4-GATE-001` |
| reached_at_utc | `2026-09-26T20:31:00Z` |
| required_by | `.governance/CONTRACT.md` §8; `PROJECT-INV-001`; canonical `MATERIAL_HUMAN_REVIEW` |
| approver_role | Portfolio Manager / Head of Quant |
| approval_record | `NONE YET` |

## decision_requested

The Portfolio Manager / Head of Quant is asked to decide the **final production
disposition** for `GQE-PI-CERT-M4-001` after reading the validation result and the
enforcement evaluation.

Explicitly: this gate does **not** ask whether Pi may be declared a supported runtime for
research work. That is the certification question and is answered by the acceptance report.
This gate asks whether anything produced by this run may move toward production.

## what_is_being_presented

| Item | Identity |
| --- | --- |
| Research candidate | `authoritative-inputs/qr-result.md` — sha256 `d27f373fd0f3c0af7ac1caa6304dbaf044d905dfd6e93ff6a9fc7a1e9d14bdae` |
| Canonical handoff | `authoritative-inputs/HANDOFF-QR-to-QV.yaml` — status `APPROVED_FOR_HANDOFF`, `GQE-PI-CERT-M4-HO-001` |
| Independent validation | `authoritative-inputs/qv-result.md` — sha256 `35b861a305c39c9a8133f6f721ac11ce3e1cba41b1238bee193f8ca1dda6e8d8`, terminal status **`FAIL`** |
| Enforcement evaluation | `evidence/enforcement-evaluation.json`, `evidence/ENFORCEMENT-REPORT.md` |
| Execution ledger | `evidence/executions.json` |
| Capability manifest | `runtime/PI-CAPABILITY-MANIFEST.yaml` |

## evidence summary

1. **The validator falsified material claims.** Terminal status `FAIL` with executed,
   reproducible evidence:
   - `F-1`: the estimator covariance `Cov(ES_hat, VaR_hat)` is stated as negative; an exact
     finite-sample computation plus Monte Carlo plus numeric influence functions show it is
     positive (uniform `rho = +0.8540`; t-3 `rho = +0.4907`).
   - `F-2`: the mandatory power table (`C11`/`E4`) is built on that covariance and is wrong
     (`SE(ln d)` 7.88% -> 5.99%; `MDE` 22.1% -> 16.8% at alpha=0.99, t-3, n=10^4).
   - `F-3`: the equivalence "fat-tailed location-scale null <=> constant d" is false when
     `mu_t != 0`; an exact counterexample gives `|delta ln d| = 17.19%`, above the design's
     own detectable effect. The `V3` restriction is therefore not an instantiation of the null.
   - `F-4` to `F-6`: numeric slips in `E1`/`E2`/`E3` beyond the candidate's own tolerance.
   - `F-7`: trivial arithmetic slip in `C10`.
2. **Most analytical claims survived.** `C1`, `C1b`, `C2`, `C3`, `C4`, `C5` variances,
   `C6`, `C7`, `C8`, `C12c`, `E7`, `E8` and the normality audit passed with executed evidence.
3. **Enforcement is fail-closed.** A declared `ENFORCED` control with no executable
   mechanism (`CTRL-CERT-007`, a deliberate probe) was reported `NOT_SATISFIED`; an
   `UNKNOWN` control (`CTRL-CERT-013`) blocks. See `evidence/ENFORCEMENT-REPORT.md`.
4. **Independence is procedural, not statistical.** QR and QV ran in distinct child task and
   session contexts, but both use `commandcode/deepseek/deepseek-v4.1-flash`. Shared error
   modes cannot be excluded (`PROJECT-INV-010`, `NOT_ENFORCED`).
5. **No dataset exists.** Every empirical criterion is `NOT_TESTED`. No empirical claim is
   supported by this run.

## options presented to human authority

1. **Reject** the candidate for any production use and close the certification as
   "runtime certified, research candidate not accepted as written".
2. **Authorize one bounded corrective research iteration** — a new task packet and a new,
   separately budgeted QR execution under change control, strictly limited to the five
   enumerated repairs. This is **not** started automatically and is **not** started by the
   orchestrator.
3. **Archive as inconclusive/failed** and take no further action.

## what the gate does NOT do

- It does not grant production approval.
- It does not authorize implementation, deployment, trading, or live side effects.
- It does not authorize a retry. No retry has occurred and none will occur without an
  explicit human decision.

## pre-declared certification constraint

The project owner's acceptance brief for this certification (`USER_DECLARED`) requires that
production remain **NOT APPROVED** and `trade_authorized` remain **false**. The gate record
therefore leaves the production disposition at `NOT_APPROVED` and marks the human decision
as pending ratification rather than manufacturing an approval.

## decision

```text
decision: REJECT_RESEARCH_CANDIDATE_FOR_PRODUCTION
human_gate_status: HUMAN_DECISION_RECORDED
scope: the quantitative research / methodology candidate produced inside this certification run
production_status: NOT_APPROVED
production_disposition: REJECTED_FOR_PRODUCTION
trade_authorized: false
automatic_retry: false
additional_qr_iteration_authorized: false
run_status: CLOSED
```

Approved by: Portfolio Manager / Head of Quant (project owner)
Date: 2026-09-26
Notes: Human Gate disposition only. No specialist was rerun, no retry occurred, no additional
research iteration was authorized, and the QV `FAIL` is preserved exactly as evidence and is
not softened to `PASS`, `INCONCLUSIVE` or any other status.

## scope of this decision

This decision rejects **only** the quantitative research / methodology candidate produced
inside `GQE-PI-CERT-M4-001`.

It does **NOT** reject:

- Gentle Quant Ecosystem;
- Pi;
- `quant-researcher` as a role;
- `quant-validator` as a role;
- the GQE architecture.

See `gates/CERTIFICATION-CLOSURE.md` for the explicit two-track disposition:

```text
Pi certification PASS (SUPPORTED_WITH_LIMITATIONS)  !=  Quant research candidate PASS (REJECTED)
```
