# ENFORCEMENT-MATRIX.md — GQE-PI-CERT-M4-001

Records, for each applicable canonical rule, which real control exists, where it lives,
what evidence exists, and what happens on failure.

`AGENT-RULES.md` (canonical GQE) defines **what must hold**.
This matrix records **how it is controlled** and **what evidence exists**.
Executable results: `evidence/enforcement-evaluation.json` and
`evidence/ENFORCEMENT-REPORT.md`.

Canonical rules source: `/home/datawithjose/Documents/GENTLE-QUANT-ECOSYSTEM/governance/core/AGENT-RULES.md`
@ `ff16b6b1e21f34a6df9e72d6121bac93ee8fcd4b`.

---

## Matrix

| RULE_ID | CONTROL_ID | QUÉ_PROTEGE | TIPO_DE_CONTROL | CONTROL_CONCRETO | UBICACIÓN | DEPENDENCIAS | RIESGO_SI_NO_EXISTE | PRIORIDAD | ESTADO_DECLARADO | QUÉ_PASA_SI_FALLA | EVIDENCIA | PUEDE_AUTOEVADIRSE | BLOQUEA_INTEGRACIÓN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `EFFECTIVE_CHALLENGE` | `CTRL-CERT-001` | Researcher and validator collapsing into one context | `DETERMINISTIC_GATE`, `AUDIT_LOG` | Compare recorded QR vs QV child task id and session id; both must differ | `.governance/enforcement.yaml`, `evidence/controls/evaluate_enforcement.py` | `evidence/executions.json` populated with real child ids | Self-review masquerading as independent validation | `CRITICAL` | `ENFORCED` | `BLOCK`, `INVALIDATE_VALIDATION` | evaluator JSON + `evidence/executions.json` | No — ids come from the runtime, not from the agent | `YES` |
| `MATERIAL_HUMAN_REVIEW` | `CTRL-CERT-002` | Production transition without a human gate | `HUMAN_REVIEW`, `DETERMINISTIC_GATE` | `gates/HUMAN-GATE.md` must exist, declare `HUMAN_DECISION_REQUIRED`, and contain an explicit decision request | `.governance/enforcement.yaml`, `gates/HUMAN-GATE.md` | gate record authored by orchestrator, decided by human | Agent self-approval | `CRITICAL` | `ENFORCED` | `BLOCK`, `HITL` | evaluator JSON + gate record | Partially — orchestrator writes the file; the human decides its content | `YES` |
| `LLM_CANNOT_EXECUTE_DIRECTLY` | `CTRL-CERT-003` | Free text becoming trading authorization | `SOFTWARE_INVARIANT`, `DETERMINISTIC_GATE` | Parse `gates/FINAL-DISPOSITION.md`: `trade_authorized: false` and `production_status: NOT_APPROVED` | `.governance/enforcement.yaml`, `gates/FINAL-DISPOSITION.md` | disposition record | Unauthorized trading intent | `CRITICAL` | `ENFORCED` | `BLOCK`, `DENY_ORDERS` | evaluator JSON | No — the check reads the artifact, not an agent claim | `YES` |
| `VERSION_EVERYTHING` | `CTRL-CERT-004` | Unauditable artifacts | `AUDIT_LOG`, `SOFTWARE_INVARIANT` | `evidence/artifact-hashes.sha256` must exist and cover every file under `.governance/`, `authoritative-inputs/`, `gates/` | `evidence/controls/evaluate_enforcement.py` | hash manifest regenerated at the end of the run | Silent artifact mutation | `HIGH` | `ENFORCED` | `BLOCK_REVIEW` | evaluator JSON + manifest | No — manifest is recomputed from disk | `YES` |
| `CONTRADICTION_BLOCKS_EXECUTION` | `CTRL-CERT-005` | Promoting FAIL/INCONCLUSIVE to approval | `DETERMINISTIC_GATE`, `INDEPENDENT_VERIFIER` | Validator terminal state must be `PASS`; `FAIL`/`BLOCKED`/`INCONCLUSIVE`/`NOT_TESTED` block; non-canonical state → `UNKNOWN` → block | `evidence/controls/evaluate_enforcement.py` | recorded QV terminal state | Failure converted into success | `CRITICAL` | `ENFORCED` | `BLOCK`, `NEEDS_REMEDIATION` | evaluator JSON | No — state comes from the child result record | `YES` |
| `CERT-BUDGET-001` (project) | `CTRL-CERT-006` | Retries, extra branches, QD/DE | `DETERMINISTIC_GATE`, `AUDIT_LOG` | `evidence/executions.json`: exactly 1 QR, exactly 1 QV, 0 QD, 0 DE, 0 retries | `.governance/enforcement.yaml` | orchestrator ledger | Result shopping / unbounded research | `CRITICAL` | `ENFORCED` | `BLOCK`, `INVALIDATE_RUN` | evaluator JSON + ledger | Partially — orchestrator authors the ledger; runtime task records must agree | `YES` |
| `INDEPENDENCE_BEFORE_VOTE` | `CTRL-CERT-007` | Treating QR/QV agreement as independent confirmation | `INDEPENDENT_VERIFIER` | **Declared `ENFORCED` with no executable mechanism** — intentional fail-closed probe | `.governance/enforcement.yaml` | none | False independence claim | `HIGH` | `ENFORCED` (declared) | `BLOCK` | evaluator must report `NOT_SATISFIED` — see `evidence/ENFORCEMENT-REPORT.md` | n/a | `YES` |
| `CERT-TOOLS-001` (project) | `CTRL-CERT-008` | Specialist self-delegation | `DETERMINISTIC_GATE`, `SCHEMA_VALIDATION` | No `subagent_*` tool in any specialist allowlist; 0 observed `subagent_*` invocations | `~/.pi/agent/agents/quant-*.md`, evaluator | Pi agent wrappers on disk | Authority expansion through delegation | `CRITICAL` | `ENFORCED` | `BLOCK` | evaluator JSON | No — allowlists are read from disk | `YES` |
| `VERSION_EVERYTHING` | `CTRL-CERT-009` | Authority changing while validation runs | `SOFTWARE_INVARIANT`, `DETERMINISTIC_GATE` | `evidence/pre-qv-snapshot.sha256` must match a post-QV recomputation | `evidence/controls/evaluate_enforcement.py` | frozen snapshot taken before QV launch | Stale/substituted authority | `HIGH` | `ENFORCED` | `BLOCK`, `MARK_STALE` | evaluator JSON + snapshot | No — snapshot is written before the child starts | `YES` |
| `CERT-CANON-001` (project) | `CTRL-CERT-010` | Runtime adapter modifying canonical semantics | `DETERMINISTIC_GATE`, `AUDIT_LOG` | Canonical GQE `git status --porcelain` empty and `HEAD` equals the recorded revision | evaluator, `evidence/canon-revision-before.txt` | clean canonical working tree | Silent canonical drift | `HIGH` | `ENFORCED` | `BLOCK`, `INVALIDATE_RUN` | evaluator JSON + revision files | No — Digests come from Git | `YES` |
| `CERT-SCOPE-001` (project) | `CTRL-CERT-011` | Producing production implementation | `DETERMINISTIC_GATE` | No code-extension file outside `evidence/controls/` | evaluator | — | Scope creep into production | `CRITICAL` | `ENFORCED` | `BLOCK` | evaluator JSON | No | `YES` |
| `EFFECTIVE_CHALLENGE` | `CTRL-CERT-012` | Evidence paths asserted but never inspected | `HUMAN_REVIEW`, `INDEPENDENT_VERIFIER` | Human gate reviewer inspects the evidence set; no automation can confirm the correspondence | `gates/HUMAN-GATE.md` | human review | Unsupported claims passing as evidence | `HIGH` | `MANUAL_ONLY` | `BLOCK_REVIEW`, `HITL` | gate record | n/a | `CONDITIONAL` |
| `INDEPENDENCE_BEFORE_VOTE` | `CTRL-CERT-013` | Statistical independence of QR/QV error modes | `INDEPENDENT_VERIFIER` | No mechanism available; state declared `UNKNOWN` so fail-closed policy blocks the transition | `.governance/enforcement.yaml`, `INVARIANTS.md` PROJECT-INV-010 | none | Overstated independence | `HIGH` | `UNKNOWN` | `BLOCK`, `HITL` | evaluator JSON | n/a | `YES` |

---

## Manual-only and unenforced controls

- `CTRL-CERT-012` — `MANUAL_ONLY`: the Human Gate reviewer must inspect the evidence set.
- `CTRL-CERT-013` and `PROJECT-INV-010` — `UNKNOWN`/`NOT_ENFORCED`: shared provider/model
  error modes cannot be excluded in this runtime. The limitation is escalated to the
  Human Gate and never presented as independence evidence.

## Self-approval risk

`CTRL-CERT-002`, `CTRL-CERT-006` and `CTRL-CERT-012` depend on artifacts the orchestrator
authors or on human review. That dependency is recorded rather than hidden:
`CTRL-CERT-012` is `MANUAL_ONLY`, and `CTRL-CERT-007` demonstrates that a declared
`ENFORCED` control without an executable mechanism is reported `NOT_SATISFIED` instead of
being trusted.
