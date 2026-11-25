# Enforcement Evaluation Report — GQE-PI-CERT-M4-001

Fail-closed policy: a declaration is not evidence; an unresolved `ENFORCED`.

| Control | Canonical rule | Declared | Observed | Match | Reason |
| --- | --- | --- | --- | --- | --- |
| `CTRL-CERT-001` | `EFFECTIVE_CHALLENGE` | ENFORCED | **UNKNOWN** | NO | evidence/executions.json missing or unreadable |
| `CTRL-CERT-002` | `MATERIAL_HUMAN_REVIEW` | ENFORCED | **NOT_SATISFIED** | NO | gates/HUMAN-GATE.md does not exist: no human gate was reached |
| `CTRL-CERT-003` | `LLM_CANNOT_EXECUTE_DIRECTLY` | ENFORCED | **NOT_SATISFIED** | NO | gates/FINAL-DISPOSITION.md does not exist |
| `CTRL-CERT-004` | `VERSION_EVERYTHING` | ENFORCED | **NOT_SATISFIED** | NO | evidence/artifact-hashes.sha256 missing or empty |
| `CTRL-CERT-005` | `CONTRADICTION_BLOCKS_EXECUTION` | ENFORCED | **UNKNOWN** | NO | no recorded quant-validator execution |
| `CTRL-CERT-006` | `CERT-BUDGET-001` | ENFORCED | **UNKNOWN** | NO | evidence/executions.json missing |
| `CTRL-CERT-007` | `INDEPENDENCE_BEFORE_VOTE` | ENFORCED | **NOT_SATISFIED** | NO | declared ENFORCED but the mechanism declares no executable check; a declaration is not evidence |
| `CTRL-CERT-008` | `CERT-TOOLS-001` | ENFORCED | **NOT_SATISFIED** | NO | quant-researcher subagent_invocations=-1 |
| `CTRL-CERT-009` | `VERSION_EVERYTHING` | ENFORCED | **NOT_SATISFIED** | NO | evidence/pre-qv-snapshot.sha256 missing: authority was never frozen |
| `CTRL-CERT-010` | `CERT-CANON-001` | ENFORCED | **UNKNOWN** | NO | evidence/canon-revision-before.txt missing |
| `CTRL-CERT-011` | `CERT-SCOPE-001` | ENFORCED | **SATISFIED** | yes | no production source tree outside evidence/controls |
| `CTRL-CERT-012` | `EFFECTIVE_CHALLENGE` | MANUAL_ONLY | **UNKNOWN** | yes | mechanism check 'check_human_gate_reached' could not be resolved |
| `CTRL-CERT-013` | `INDEPENDENCE_BEFORE_VOTE` | UNKNOWN | **UNKNOWN** | yes | control state is UNKNOWN; fail-closed policy blocks the transition |

Controls evaluated: 13
Unsatisfied blocking controls: ['CTRL-CERT-001', 'CTRL-CERT-002', 'CTRL-CERT-003', 'CTRL-CERT-004', 'CTRL-CERT-005', 'CTRL-CERT-006', 'CTRL-CERT-007', 'CTRL-CERT-008', 'CTRL-CERT-009', 'CTRL-CERT-010', 'CTRL-CERT-012', 'CTRL-CERT-013']
Production transition allowed: False
Production status under fail-closed policy: NOT_APPROVED
trade_authorized: false
