# Human-Gate Ratification Record — GQE-PI-CERT-M4-001

ratified_at_utc: `2026-09-26T20:48:00Z`
ratified_by: Portfolio Manager / Head of Quant (project owner, human authority)
recorded_by: quant-orchestrator
nature: **human-gate ratification, not a mutation of QR/QV evidence**

## Decision

```text
human_gate_status: HUMAN_DECISION_RECORDED
previous_status:   HUMAN_DECISION_REQUIRED
decision:          REJECT_RESEARCH_CANDIDATE_FOR_PRODUCTION
run_status:        CLOSED
```

## Intentionally updated disposition artifacts (old -> new)

| Artifact | Previous sha256 | New sha256 |
| --- | --- | --- |
| `gates/HUMAN-GATE.md` | `92d536aaf92eadc1e4f3ea38b8ef450edd0acfe8adf017a853a8d20d4d4ffb97` | see `POST-RATIFICATION-HASHES.txt` |
| `gates/FINAL-DISPOSITION.md` | `b9e3867a3656f9038add2d35d58cf62e68c11440565c99a457f496c27e8f063d` | see `POST-RATIFICATION-HASHES.txt` |
| `gates/CERTIFICATION-CLOSURE.md` | (new artifact) | see `POST-RATIFICATION-HASHES.txt` |

Exact new digests are in `POST-RATIFICATION-HASHES.txt` (written after the edits, not
hand-transcribed, so they cannot drift).

## Preserved pre-ratification evidence

- `HUMAN-GATE.md.pre-ratification` — verbatim pre-edit content
- `FINAL-DISPOSITION.md.pre-ratification` — verbatim pre-edit content
- `PRE-RATIFICATION-HASHES.txt` — pre-edit digests of the gate artifacts and of the frozen
  QR / handoff / QV artifacts
- `artifact-hashes.sha256.pre-ratification` and `artifact-hashes-full.sha256.pre-ratification`
  — the complete manifests as they stood before ratification
- `CHARTPY-BASELINE-FINGERPRINT.txt`, `CANON-BASELINE.txt` — external baselines

## Artifacts deliberately NOT modified

| Artifact | sha256 (unchanged) |
| --- | --- |
| `authoritative-inputs/qr-result.md` | `d27f373fd0f3c0af7ac1caa6304dbaf044d905dfd6e93ff6a9fc7a1e9d14bdae` |
| `authoritative-inputs/HANDOFF-QR-to-QV.yaml` | `275402b1ee901e8c372494707246599f13f350e66b8b02ddebe0539a1fd7880e` |
| `authoritative-inputs/qv-result.md` | `35b861a305c39c9a8133f6f721ac11ce3e1cba41b1238bee193f8ca1dda6e8d8` |
| `authoritative-inputs/TASK-PACKET-QR.yaml` | `d27b0a7e8c08081be7943813496af357d63f17b48a82dcdd5795365ff40ee3c2` |
| `authoritative-inputs/TASK-PACKET-QV.yaml` | `8cf44a6bf8dad98aa680f66bba3bc2df92683dd847f8657209450774b0e2af51` |
| `.governance/*` | unchanged (see `artifact-hashes.sha256.pre-ratification`) |
| `evidence/enforcement-evaluation.json` | unchanged; the evaluator was NOT re-run, because re-running would overwrite prior evidence |

The QV terminal state remains `FAIL` exactly as produced. No finding was repaired, softened or
re-classified.

## Why the enforcement evaluation was not re-run

Re-running `evidence/controls/evaluate_enforcement.py` would rewrite
`evidence/enforcement-evaluation.json` and `evidence/ENFORCEMENT-REPORT.md`, which are prior
persisted evidence. The frozen evaluation therefore stands as the pre-decision record
(`production_transition_allowed: false`). The human decision recorded afterwards is captured
here, in `gates/HUMAN-GATE.md`, `gates/FINAL-DISPOSITION.md` and
`gates/CERTIFICATION-CLOSURE.md`.

Consequence to keep visible: control `CTRL-CERT-012` (`MANUAL_ONLY`) is recorded in the frozen
evaluation as `UNKNOWN` (gate not yet discharged), because the evaluation ran before the human
decision. It is not restated as satisfied by retroactively editing frozen output.
