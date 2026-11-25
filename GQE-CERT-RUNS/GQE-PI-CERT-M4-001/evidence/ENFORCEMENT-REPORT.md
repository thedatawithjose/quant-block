# Enforcement Evaluation Report — GQE-PI-CERT-M4-001

Fail-closed policy: a declaration is not evidence; an unresolved `ENFORCED`.

| Control | Canonical rule | Declared | Observed | Match | Reason |
| --- | --- | --- | --- | --- | --- |
| `CTRL-CERT-001` | `EFFECTIVE_CHALLENGE` | ENFORCED | **SATISFIED** | yes | distinct task ids (muitozyl-1-0osb vs muitwelp-2-pqha) and session ids (01a0df55-f2f3-7385-acac-3d22d832a7da vs 01a0df5b-38f4-73f0-80b5-0b02f8708933) |
| `CTRL-CERT-002` | `MATERIAL_HUMAN_REVIEW` | ENFORCED | **SATISFIED** | yes | human gate recorded with HUMAN_DECISION_REQUIRED and an explicit decision request |
| `CTRL-CERT-003` | `LLM_CANNOT_EXECUTE_DIRECTLY` | ENFORCED | **SATISFIED** | yes | trade_authorized=false and production_status=NOT_APPROVED |
| `CTRL-CERT-004` | `VERSION_EVERYTHING` | ENFORCED | **SATISFIED** | yes | manifest covers 15 governance/packet/gate artifacts |
| `CTRL-CERT-005` | `CONTRADICTION_BLOCKS_EXECUTION` | ENFORCED | **NOT_SATISFIED** | NO | validator terminal state FAIL blocks the transition |
| `CTRL-CERT-006` | `CERT-BUDGET-001` | ENFORCED | **SATISFIED** | yes | 1 QR, 1 QV, 0 QD, 0 DE, 0 retries |
| `CTRL-CERT-007` | `INDEPENDENCE_BEFORE_VOTE` | ENFORCED | **NOT_SATISFIED** | NO | declared ENFORCED but the mechanism declares no executable check; a declaration is not evidence |
| `CTRL-CERT-008` | `CERT-TOOLS-001` | ENFORCED | **SATISFIED** | yes | no subagent_* tool in any specialist allowlist; 0 observed invocations |
| `CTRL-CERT-009` | `VERSION_EVERYTHING` | ENFORCED | **SATISFIED** | yes | 11 frozen artifacts byte-identical after validation |
| `CTRL-CERT-010` | `CERT-CANON-001` | ENFORCED | **SATISFIED** | yes | canonical GQE clean at revision ff16b6b1e21f34a6df9e72d6121bac93ee8fcd4b |
| `CTRL-CERT-011` | `CERT-SCOPE-001` | ENFORCED | **SATISFIED** | yes | no production source tree outside evidence/controls |
| `CTRL-CERT-012` | `EFFECTIVE_CHALLENGE` | MANUAL_ONLY | **UNKNOWN** | yes | manual gate declared and not yet discharged by a human decision; fail-closed policy blocks the transition that requires it (underlying observable anchor: check_human_gate_reached) |
| `CTRL-CERT-013` | `INDEPENDENCE_BEFORE_VOTE` | UNKNOWN | **UNKNOWN** | yes | control state is UNKNOWN; fail-closed policy blocks the transition |

Controls evaluated: 13
Unsatisfied blocking controls: ['CTRL-CERT-005', 'CTRL-CERT-007', 'CTRL-CERT-012', 'CTRL-CERT-013']
Production transition allowed: False
Production status under fail-closed policy: NOT_APPROVED
trade_authorized: false
