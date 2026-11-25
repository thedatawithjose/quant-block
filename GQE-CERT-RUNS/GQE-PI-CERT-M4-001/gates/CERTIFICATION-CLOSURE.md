# CERTIFICATION CLOSURE — GQE × Pi M4

run_id: `GQE-PI-CERT-M4-001`
closed_at_utc: `2026-09-26T20:49:00Z`
closed_by: Portfolio Manager / Head of Quant (human authority), recorded by the quant-orchestrator
canonical GQE revision: `ff16b6b1e21f34a6df9e72d6121bac93ee8fcd4b` (unchanged)

---

## The distinction this closure records

```text
Pi certification PASS  !=  Quant research candidate PASS
```

The runtime successfully demonstrated that it can **detect, preserve, enforce and escalate**
a failed quantitative result. That is the certification success. The candidate that was
processed during the demonstration failed independent validation, and human authority
rejected it. Both statements are true at the same time and are recorded separately.

---

## Track A — GQE × Pi runtime certification

| Field | Value |
| --- | --- |
| M4 acceptance workflow | `PASS` |
| Pi runtime support status | `SUPPORTED_WITH_LIMITATIONS` |
| GQE operational on Pi | `YES` |
| Runtime portability versus OpenCode | `VERIFIED` |
| Certification run | `CLOSED` |
| Governance requirements | 13/13 `PASS` |
| Mechanical requirements | 21/21 `PASS` |

Basis:

- The full canonical operational loop executed once, end to end, with no stage skipped:
  governance preflight, classification, routing, READY packet, one QR execution, persisted
  result, canonical handoff, one QV execution in a distinct child context, independent
  validation, enforcement evaluation, Human Gate.
- Canonical GQE semantics were preserved without modification; only the deployment
  representation (Pi agent wrappers) was used, and the canonical tree is byte-identical at
  revision `ff16b6b1e21f34a6df9e72d6121bac93ee8fcd4b`.
- Fail-closed enforcement worked: a declared `ENFORCED` control with no executable mechanism
  was reported `NOT_SATISFIED`, an `UNKNOWN` control blocked, and the production transition
  was denied (evaluator exit code `1`).
- Portability versus OpenCode is satisfied at the contract level required by
  `adapters/RUNTIME-ADAPTER-SPEC.md` §13: no canonical artifact — `ROLE.md`,
  `SUBAGENT.md`, governance, invariants, routing, enforcement semantics, handoff contract —
  needed to change to move from the OpenCode adapter to the Pi adapter. Only the adapter
  representation differs. This is a contract-level portability verification; the OpenCode
  adapter itself is separately `PARTIALLY_VALIDATED` and was not re-run here.
- The validator genuinely falsified material candidate claims, which is direct evidence that
  the validation stage is independent-at-the-process-level and not ceremonial.

Support status is `SUPPORTED_WITH_LIMITATIONS` rather than `SUPPORTED` because of the
declared runtime limitations in Track C below.

---

## Track B — Quantitative research candidate used during M4

| Field | Value |
| --- | --- |
| QR terminal state | `COMPLETED` |
| QV terminal state | **`FAIL`** (preserved exactly; not softened) |
| production disposition | `REJECTED_FOR_PRODUCTION` |
| production_status (safety/enforcement state) | `NOT_APPROVED` |
| `trade_authorized` | `false` |
| automatic retry | `false` |
| additional QR iteration authorized | `false` |
| candidate artifact | `authoritative-inputs/qr-result.md` sha256 `d27f373fd0f3c0af7ac1caa6304dbaf044d905dfd6e93ff6a9fc7a1e9d14bdae` |
| validation artifact | `authoritative-inputs/qv-result.md` sha256 `35b861a305c39c9a8133f6f721ac11ce3e1cba41b1238bee193f8ca1dda6e8d8` |

Human decision: `REJECT_RESEARCH_CANDIDATE_FOR_PRODUCTION`.

Scope: this rejects **only** the quantitative research / methodology candidate produced inside
this certification run. It does **not** reject the Gentle Quant Ecosystem, Pi,
`quant-researcher` as a role, `quant-validator` as a role, or the GQE architecture.

The QV `FAIL` remains preserved byte-identical as evidence. It is not converted to `PASS`,
`INCONCLUSIVE` or any softer status, and no finding was repaired.

---

## Track C — Declared limitations carried forward (backlog)

These are recorded, not repaired, and they do not reopen this M4 certification.

1. **QR/QV statistical independence not established** — both specialists ran
   `commandcode/deepseek/deepseek-v4.1-flash`. Shared model error modes cannot be excluded
   (`PROJECT-INV-010` `NOT_ENFORCED`, `CTRL-CERT-013` `UNKNOWN`).
2. **No per-child filesystem confinement** — Pi exposes no child sandbox
   (`filesystem_scope_restrictions: UNAVAILABLE`).
3. **No native runtime interlock for human approval** — the gate is a convention plus a
   fail-closed evaluator (`human_approval_gates: EMULATED`).
4. **Specialist outputs persisted verbatim by the orchestrator** where specialists lack write
   access (contract-faithful: canonical `ROLE.md` says "Return:").
5. **Retrieval limitations** — documentation/open-web unavailable in the specialist contexts;
   four literature premises remain `NOT_TESTED`.
6. **Empirical / data-dependent claims remain `NOT_TESTED`** — no dataset exists in this run.
7. **Known enforcement implementation notes** — the ledger accessor defect in
   `evidence/controls/evaluate_enforcement.py`, disclosed and corrected mid-run, with both
   pre-correction and post-correction outputs preserved
   (`evidence/CONTROL-IMPLEMENTATION-NOTE.md`).
8. **Manual gate anchor** `CTRL-CERT-012` records the pre-decision evaluation state; the human
   decision recorded after that evaluation is captured in this closure and in
   `gates/HUMAN-GATE.md`. The frozen evaluation output was intentionally **not** re-run or
   rewritten.

---

## Integrity statement

- The Human Gate updated exactly two disposition artifacts: `gates/HUMAN-GATE.md` and
  `gates/FINAL-DISPOSITION.md`. Their pre-ratification content and hashes are preserved under
  `evidence/human-gate-ratification/`.
- `authoritative-inputs/qr-result.md`, `authoritative-inputs/HANDOFF-QR-to-QV.yaml` and
  `authoritative-inputs/qv-result.md` were **not** modified: byte-identical to their frozen
  hashes.
- Task packets, governance files and the frozen pre-QV snapshot were **not** modified.
- No specialist was executed after the original single QR and single QV runs. No retry
  occurred. No new research iteration was authorized.
- Canonical GQE remained untouched.

Verification evidence: `evidence/human-gate-ratification/CLOSURE-VERIFICATION.txt`
