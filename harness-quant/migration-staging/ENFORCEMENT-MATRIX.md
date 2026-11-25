# Enforcement matrix — migration preparation only

Scope: source preservation, cache-only cleanup and accurate evidence reporting. Canonical rules: `/home/datawithjose/Documents/AI-GOVERNANCE/AGENT-RULES.md`. This audit does not certify the legacy trading harness, the external Pi installation or future Hyperion controls. No new behavioral control is implemented here. Evidence: `COPY-MANIFEST.json`, `ACTIVE-BASELINE.json`, `DELETED.json`, `GIT-BASELINE.txt`, `INVENTORY.md`, `verification/RESULTS.md`.

## Applicable P0/P1 controls

Statuses deliberately remain MANUAL_ONLY/PARTIAL: bounded scripts and separate verification were used, but no protected persistent enforcement service prevents this agent/filesystem owner from changing the material later. Integration is outside this task, so integration blocking is NOT_APPLICABLE.

| RULE_ID | CONTROL_ID | QUÉ_PROTEGE | TIPO_DE_CONTROL | CONTROL_CONCRETO | UBICACIÓN_DEL_CONTROL | DEPENDENCIAS | RIESGO_SI_NO_EXISTE | PRIORIDAD_DEL_CONTROL | ESTADO | ACCIÓN_PENDIENTE | QUÉ_PASA_SI_FALLA | EVIDENCIA | QUIÉN_PUEDE_MODIFICAR_EL_CONTROL | BLOQUEA_INTEGRACIÓN | ALCANCE | ÚLTIMA_VERIFICACIÓN | RESPONSABLE_DE_VERIFICACIÓN |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TRUTH_OVER_AGREEMENT | CTRL-MIG-01 | Unsupported cleanup claims | AGENT_POLICY | Retain evidence/demo instead of assuming obsolescence | INVENTORY.md cleanup ledger | Source/reference inspection | Loss of unique behavior/evidence | HIGH | MANUAL_ONLY | Future cleanup must repeat reference inspection | Block unsupported deletion | Reference map; verifier S5–S6 | Filesystem owner/agent | NOT_APPLICABLE | Cleanup classification | This task, RESULTS.md | Parent + separate verifier |
| USER_CLAIM_IS_NOT_EVIDENCE | CTRL-MIG-02 | Assumed source locations/semantics | AGENT_POLICY | Locate original symbols and dependencies | INVENTORY.md extraction map | Read access | Wrong source copied | HIGH | MANUAL_ONLY | Recheck if sources change | Reject unsupported mapping | Symbol line references and 30 hashes | Filesystem owner/agent | NOT_APPLICABLE | Staging provenance | This task, RESULTS.md | Separate verifier |
| PREMISE_AUDIT_FIRST | CTRL-MIG-03 | Mistaking old/demo for obsolete | AGENT_POLICY | Check imports, entrypoints and recorded evidence before cleanup | INVENTORY.md | Local source inspection | Broken tests or lost evidence | HIGH | MANUAL_ONLY | Repeat for any new removal | Preserve source when uncertain | Test imports; clean Git baseline | Filesystem owner/agent | NOT_APPLICABLE | Exact three cache removals | This task, RESULTS.md | Parent + separate verifier |
| ABSTENTION_IS_SUCCESS | CTRL-MIG-04 | Invented archival/runtime proof | AGENT_POLICY | Explicitly report no archive candidates and live runtime unknown | INVENTORY.md verification limits | Honest reporting | False completion claims | HIGH | MANUAL_ONLY | No runtime certification claimed | Withhold dependent claim | RESULTS.md inspected/not-executed section | Filesystem owner/agent | NOT_APPLICABLE | Claims only | This task, RESULTS.md | Separate verifier |
| NO_SOURCE_NO_CRITICAL_FACT | CTRL-MIG-05 | Unsupported provenance | AUDIT_LOG | Record SHA-256 original/destination pairs | COPY-MANIFEST.json | Retained originals | Untraceable copies | HIGH | PARTIAL | No external immutable anchor | Reject hash mismatch | 30 hash comparisons passed | Filesystem owner/agent | NOT_APPLICABLE | Copied bytes | This task, RESULTS.md | Separate verifier |
| PRIMARY_SOURCE_PRIORITY | CTRL-MIG-06 | Substituting memory for source | AGENT_POLICY | Copy directly from local canonical paths | COPY-MANIFEST.json | Original files | Wrong/missing version | HIGH | MANUAL_ONLY | Recheck originals on reuse | Block unsupported source claim | Absolute origins in manifest | Filesystem owner/agent | NOT_APPLICABLE | Local sources | This task, RESULTS.md | Separate verifier |
| RETRIEVED_CONTENT_IS_DATA | CTRL-MIG-07 | Activating copied prompt | AGENT_POLICY | Treat quant-mode prompt as reference, do not run its instructions | INVENTORY.md Pi boundaries | Runtime instruction separation | Unrequested activation/effects | HIGH | MANUAL_ONLY | Future adapter requires independent controls | Do not execute induced commands | No mode/protect/API activation | Filesystem owner/agent | NOT_APPLICABLE | Reference prompt | This task, RESULTS.md | Parent + separate verifier |
| UNCERTAINTY_REQUIRED | CTRL-MIG-08 | Claiming live protection from files | AGENT_POLICY | Separate tested offline behavior from unverified live loading | RESULTS.md | Exact check results | False security assurance | HIGH | MANUAL_ONLY | Live checks belong to future authorized task | Withhold live claim | Explicit unexecuted list | Filesystem owner/agent | NOT_APPLICABLE | Verification claims | This task, RESULTS.md | Separate verifier |
| VERSION_EVERYTHING | CTRL-MIG-09 | Evidence detached from copied bytes | AUDIT_LOG | Hash sources and compare active baseline before/after tests | Manifests and RESULTS.md | Stable sources, SHA-256 | Drift concealed | HIGH | PARTIAL | Hashes lack external signing/anchor | Reject mismatch | 30 copies; 22 active hashes; Git unchanged | Filesystem owner/agent | NOT_APPLICABLE | This snapshot | This task, RESULTS.md | Parent + separate verifier |

## Other P0/P1 applicability

| RULE_ID | Status for this task | Reason / boundary |
|---|---|---|
| INDEPENDENT_FIRST_PASS | NOT_APPLICABLE | Preservation task, not validation of a desired scientific thesis; separate verifier was not claimed blind. |
| MULTI_TURN_STANCE_STABILITY | MANUAL_ONLY | No factual conclusion changed under pressure; preserve evidence-based classifications. |
| DISCONFIRMING_EVIDENCE_REQUIRED | NOT_APPLICABLE | No trading thesis evaluated; searched references that would refute safe removal. |
| INDEPENDENCE_BEFORE_VOTE | NOT_APPLICABLE | No source/model vote used as proof; separate verifier is another agent execution, not proof of independent model errors. |
| DETERMINISTIC_MATH | NOT_APPLICABLE | No new financial/statistical calculation; preserved existing numerical tests ran offline. Byte totals and hashes are computed programmatically. |
| POINT_IN_TIME_ONLY | NOT_APPLICABLE | No historical market decision/result produced; preserved temporal behavior is tested only as legacy code. |
| CALIBRATION_SEPARATE_FROM_TEST | NOT_APPLICABLE | No model fitting, calibration or dataset selection. |
| BACKTEST_VALIDITY | NOT_APPLICABLE | No strategy/backtest claim promoted; synthetic suite is software evidence only. |
| MULTIPLE_TESTING_CONTROL | NOT_APPLICABLE | No strategy/parameter search performed. |
| EFFECTIVE_CHALLENGE | NOT_APPLICABLE | No promotion to validated research/execution; separate migration verifier checked S1–S8 anyway. |
| CONTRADICTION_BLOCKS_EXECUTION | NOT_APPLICABLE | No trading execution; contract/template discrepancies preserved and disclosed, not reconciled by assertion. |
| SEPARATE_EPISTEMIC_AND_TRADING_MONITORING | NOT_APPLICABLE | No system deployment or trading performance monitoring. |
| MATERIAL_HUMAN_REVIEW | NOT_APPLICABLE | No production/capital/control change. Human explicitly authorized cache-only cleanup; external installations unchanged. |
| LLM_CANNOT_EXECUTE_DIRECTLY | NOT_APPLICABLE | No broker or order capability invoked; copied protocols are inert reference material. |

Residual limitation: the same filesystem owner can modify copies, manifests and tests. Nothing here grants approval, implements final task closure, or establishes a tamper-proof audit.
