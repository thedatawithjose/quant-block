# GQE Independent Quant Validation Result

## status
`FAIL`

Terminal validation status for candidate `authoritative-inputs/qr-result.md`. `FAIL` means: **the candidate cannot be accepted as independently verified as written** — executed, reproducible computations falsified three material claim groups (the C5 estimator covariance sign/factor, the C11/E4 power table derived from it, and the H₀ ⟺ constant-`d` equivalence that the primary test I-1 operationalises), plus two E1/E3 numeric entries beyond the candidate's own 4th-significant-digit tolerance. `FAIL` does **not** mean the research direction is refuted: the central comparison design (non-Gaussian VaR-only null) survives in weakened form, most analytical oracles PASS, and the defects are bounded and repairable. All failures are enumerated with exact commands in `properties_tested` and `counterexamples`.

---

## executive_summary

- **specialist_identity:** `quant-validator` (canonical `ROLE.md`, `SUBAGENT.md`, `SUBAGENT-CONTRACT-SPEC.md`), invocation `ORCHESTRATOR_ONLY`, context `ISOLATED_REQUIRED`, delegation `FORBIDDEN`, execution status `COMPLETED`.
- **task_identity:** `task_id=GQE-PI-CERT-M4-QV-001`, `task_version=1.0`, `project=GQE-PI-CERT-M4-001`, `assigned_role=quant-validator`, packet `status=READY` (authoritative, frozen).
- **posture:** `RESEARCH_ONLY`; `trade_authorized = false`; no production approval; **no files written** — all computation executed as `python3` stdin heredocs with cwd `/tmp`; read-only inspection of the frozen workspace.
- **authority integrity:** VERIFIED. All 11 frozen artifacts recomputed and matched against `evidence/pre-qv-snapshot.sha256` (`sha256sum -c` → all `OK`), before and again after the validation run. `qr-result.md` = `d27f373f…4bdae`, identical to the hash stated in the QV packet and the handoff.
- **work performed:** adversarial recomputation of the candidate's material analytical and numerical claims by independent routes (exact discrete enumeration, independent numerical quadrature, closed-form integration, exact finite-sample order-statistic algebra, and Monte Carlo), plus a normality audit, a √h audit, analytical oracles, and a falsification attempt on the central methodological null.
- **headline findings:**
  1. **C5 covariance is wrong in sign and magnitude (FAIL).** The candidate states `Cov(ÊS, VaR̂) ≈ −p(ES−q)/(n f(q)) < 0`. The correct asymptotic covariance is `+α(ES−q)/f(q)` (per-observation). Confirmed by three independent routes, including an **exact finite-sample closed form** for the uniform law (`Cov = +4.5027e-6`, `Corr = +0.8540`) and Monte Carlo (`Corr = +0.49…+0.74` for t₃/t₅/N, all positive). The candidate's own `IF_VaR` definition is internally inconsistent with its own reported `σ²_VaR`.
  2. **C11/E4 power table inherits the error (FAIL).** `SE(ln d)` and `MDE(ln d)` are reproduced exactly by the candidate's incorrect covariance; correcting it changes `SE(ln d)` from 7.88% → 5.99% (t₃, α=0.99) and the MDE from 22.1% → 16.8%, and the design margin from 1.57× → 2.06×. The candidate's headline feasibility numbers ("SE(ln d) ≈ 7.9% vs 2.4%") become 5.99% vs 1.22%.
  3. **H₀ ⟺ constant `d` is false (FAIL).** Under the candidate's own H₀ with `μ_t ≠ 0`, `d_t` varies: an executed counterexample with exact H₀ and `μ/σ = ±0.5` gives `d = 1.533` vs `1.821` (|Δ ln d| = 17.2%, above the design's own noise floor). The document is internally contradictory (executive summary/S5 line 17 "`d` is constant over time" vs C6/S5 line 98 "not invariant when μ ≠ 0"), and M1's `V3` restriction `ES = κ·VaR` therefore does not instantiate H₀.
  4. **E1/E3 numeric slips (FAIL, narrow).** Recomputed E1: t₅@0.99 `ES = 4.452429` (candidate 4.4506); t₃@0.99 `ES = 7.003082` (candidate 7.0013) — both differ in the 4th significant digit, triggering the candidate's own T3 falsification criterion and its change-control rule. The `d`-ratio column, the Gaussian rows and all Pareto rows agree to 4 significant digits or exactly. E2's t₃ value "≈5.5" is `5.039583` (9.1% high). E3's t₅/t₃ @0.99 `d−1` entries inherit the ES slip.
  5. **Verifications that PASS:** C1 two-point non-redundancy (identical VaR 0, ES 1 vs 10), C1b curve equivalence, C2 identity (machine-precision), C3 atom case (0.516 vs 0.5102; single bond 0.8 vs 0.04), C4 subadditivity (0.5 > 0+0; 0.516 ≤ 1.6), C5 variance formulas (`Var(VaR)`, `Var(ES)` both confirmed by MC), C6 Student-t ES closed form and location-scale invariance, C7 existence condition (`ξ < 1`), C8 `h^{1/ν}` scaling for ν < 2, C12(c) `d = 1` corner case, E1 Gaussian/Pareto rows, E7, E8 oracles, T2 agreement, T9 normality audit, and the recalled **GPD/POT formulas**, which I verified analytically to machine precision.
  6. **Only 2 of the 6 "LIT-UNVERIFIED" literature premises were addressable at all**, and I verified the one that is mathematics (GPD/POT). The rest required source retrieval, which is unavailable in my context — reported `NOT_TESTED`, not PASS.
- **handoff:** `FAIL` → recommended `return_to_quant_researcher` for a bounded correction under change control.

---

## candidate_identity

| Field | Value |
| --- | --- |
| Path | `/home/datawithjose/Documents/GQE-CERT-RUNS/GQE-PI-CERT-M4-001/authoritative-inputs/qr-result.md` |
| Type | `research_specification` (methodology, no implementation) |
| Version | `1.0` |
| Status in artifact | `COMPLETED` / `handoff_status: READY_FOR_REVIEW` |
| Producer | `quant-researcher`, task `GQE-PI-CERT-M4-QR-001` |
| **Recomputed sha256** | **`d27f373fd0f3c0af7ac1caa6304dbaf044d905dfd6e93ff6a9fc7a1e9d14bdae`** |
| Bytes | 67146 |
| Hash match | ✔ packet `authoritative_inputs[qr-result].hash`, ✔ handoff `outputs[research-spec].hash` and `evidence[0].sha256`, ✔ `evidence/qr-result-hash.txt`, ✔ `evidence/pre-qv-snapshot.sha256` |
| Immutability during QV | ✔ re-verified after all checks; `sha256sum -c` → exit 0 |

Producer audit record (`qr-result.meta.txt`, sha256 `733c241d…1caeb53`): `child_task_id: muitozyl-1-0osb`, `child_session_id: 01a0df55-f2f3-7385-acac-3d22d832a7da`, `model: commandcode/deepseek/deepseek-v4.1-flash`, `tool_names: ['find','read']`, `subagent_tool_invocations: 0`.

---

## specification_identity

| ID | Type | Path | Identity |
| --- | --- | --- | --- |
| `task-packet-qv` | authoritative task | `authoritative-inputs/TASK-PACKET-QV.yaml` | sha256 `8cf44a6bf8dad98aa680f66bba3bc2df92683dd847f8657209450774b0e2af51`, `status: READY`, `completion_gate.ready_for_execution: true` |
| `task-packet-qr` | upstream task | `authoritative-inputs/TASK-PACKET-QR.yaml` | sha256 `d27b0a7e8c08081be7943813496af357d63f17b48a82dcdd5795365ff40ee3c2` |
| `handoff-qr-to-qv` | canonical handoff | `authoritative-inputs/HANDOFF-QR-to-QV.yaml` | sha256 `275402b1ee901e8c372494707246599f13f350e66b8b02ddebe0539a1fd7880e`; `handoff_id GQE-PI-CERT-M4-HO-001`; source `quant-researcher` → target `quant-validator`; `status: APPROVED_FOR_HANDOFF`; `stale: false` |
| governance | contract + invariants + enforcement + team + routing | `.governance/…` | CONTRACT `fd045e79…`, INVARIANTS `8b683cad…`, enforcement `866a558f…`, TEAM `4d7c8ac5…`, ROUTING `d59762c9…`; governance status `VALID`, contract `APPROVED` |
| canonical role contracts | specifications | `GENTLE-QUANT-ECOSYSTEM/agents/…` | read in full; canonical repo at `ff16b6b1e21f34a6df9e72d6121bac93ee8fcd4b` (matches the run's declared authority commit) |

Specification-level semantics validated as **declared, not assumed**: loss sign convention `L = −r` (loss-positive), `α` = confidence level, `p = 1−α`, `h` in trading days, RV/Acerbi–Tasche estimand, English technical artifacts. No conflict found between the candidate's declared conventions and the packet's requirements.

---

## dataset_identity

**`NOT_PROVIDED`** (matches `TASK-PACKET-QV.authoritative_inputs[dataset-primary].status: NOT_PROVIDED` and the QR packet's identical declaration).

- `path: null`; no dataset, no strategy definition, no cost/turnover model exists in this run.
- Consequence for this validation: **all empirical claims are untestable here by construction**. Every empirical criterion in the candidate (S1–S8, R1–R10, gates Q1/Q2, T5–T7, T10–T15) is `NOT_TESTED`, never PASS. No synthetic result is treated as evidence about markets.
- Absence of a dataset is **not** evidence for or against VaR/ES usefulness; it is an unresolvable gap requiring human authorisation and a new task packet.

---

## authority_integrity_check

Executed: `sha256sum` over each frozen path, then `sha256sum -c evidence/pre-qv-snapshot.sha256`.

| Artifact | Recomputed sha256 | vs snapshot | vs handoff/packet claim |
| --- | --- | --- | --- |
| `.governance/CONTRACT.md` | `fd045e79facb63111ff6999e58e920a21704848817be8489832dff37e4bd7600` | MATCH | — |
| `.governance/ENFORCEMENT-MATRIX.md` | `b6668f6d3690e223d512f1ea10174533c7053024c588f5c5567dd852f4fc4500` | MATCH | — |
| `.governance/enforcement.yaml` | `866a558f1fdaeb43389eee316322029b21975b2aea34a1b05cf30f195959bb47` | MATCH | — |
| `.governance/INVARIANTS.md` | `8b683cad1e562302ea93452fae6819f577914600c2cf47bb4f481f3fe00874dc` | MATCH | — |
| `.governance/ROUTING.yaml` | `d59762c9572143b87d8f3bf690b19bcdbdf6a7a5e9c3d11a7b0ffc056fa0a9a5` | MATCH | — |
| `.governance/TEAM.yaml` | `4d7c8ac5eb9c490194b1ef745fe1beea6ec5cbabaaf0e587b6f7689c8e1428c0` | MATCH | — |
| `authoritative-inputs/TASK-PACKET-QR.yaml` | `d27b0a7e8c08081be7943813496af357d63f17b48a82dcdd5795365ff40ee3c2` | MATCH | MATCH (handoff `status_history` + `authoritative_inputs`) |
| **`authoritative-inputs/qr-result.md`** | **`d27f373fd0f3c0af7ac1caa6304dbaf044d905dfd6e93ff6a9fc7a1e9d14bdae`** | MATCH | MATCH (QV packet + handoff + `evidence/qr-result-hash.txt`) |
| `authoritative-inputs/qr-result.meta.txt` | `733c241d28fb6e0d507407c3a889205c0a991c3d3f0b72d1d27d36bcb1caeb53` | MATCH | — |
| `authoritative-inputs/HANDOFF-QR-to-QV.yaml` | `275402b1ee901e8c372494707246599f13f350e66b8b02ddebe0539a1fd7880e` | MATCH | — |
| `authoritative-inputs/TASK-PACKET-QV.yaml` | `8cf44a6bf8dad98aa680f66bba3bc2df92683dd847f8657209450774b0e2af51` | MATCH | MATCH (`evidence/packet-qv-hash.txt`) |

- `sha256sum -c evidence/pre-qv-snapshot.sha256` → **11/11 `OK`, exit code 0**, run **twice** (before and after the validation work) — no frozen artifact changed during QV (`PROJECT-INV-005` satisfied on the observable evidence).
- No dataset, no implementation, no evidence of prior `qr-result.md` reuse; the candidate is answered from persisted bytes, not a regenerated version.
- Canonical GQE read-only check: `git -C … rev-parse HEAD` = `ff16b6b1e21f34a6df9e72d6121bac93ee8fcd4b`; `git status --porcelain` empty (`PROJECT-INV-009` holds on the observable check).

---

## invariants_checked

| Invariant | How checked | Result | Limitation |
| --- | --- | --- | --- |
| `PROJECT-INV-005` — QV receives persisted authority, not regenerated work | `sha256sum -c evidence/pre-qv-snapshot.sha256`, twice | **PASS** | proves non-substitution, not authorship |
| `PROJECT-INV-004` — validator context separation | `PI_SESSION_ID=01a0df5b-38f4-73f0-80b5-0b02f8708933` vs QR `child_session_id 01a0df55-f2f3-7385-acac-3d22d832a7da`; distinct child tasks | **PASS** (observable part) | non-sharing of hidden reasoning is not machine-verifiable from inside the child; session distinctness ≠ statistical independence |
| `PROJECT-INV-010` — QR/QV error-mode independence | provider/model read from environment and meta | **NOT_ENFORCED / NOT ESTABLISHED** | both are `commandcode/deepseek/deepseek-v4.1-flash`; recorded as dependency, never as independence |
| `PROJECT-INV-002` — research-only posture | no artifact sets `trade_authorized=true`; candidate declares `RESEARCH_ONLY` | **PASS** (within QV scope) | final disposition not yet materialised (empty `gates/`) |
| `PROJECT-INV-001` — final human authority over production | this report grants no approval; `production_approval` = NOT APPROVED | **PASS** (within QV scope) | Human Gate outstanding |
| `PROJECT-INV-007` — agent claims are not evidence | every PASS below names a command and its observed output; candidate prose treated as hypothesis only | **PASS** (QV practice) | `MANUAL_GATE`: human must confirm evidence-path correspondence |
| `PROJECT-INV-009` — canonical GQE unchanged | `git rev-parse HEAD` + `git status --porcelain` | **PASS** (read-only check) | — |
| `PROJECT-INV-006` — fail-closed enforcement | not QV-owned; `evidence/enforcement-evaluation.PRE-RUN.json` exists but I did not execute the evaluator | **NOT_TESTED** | outside validation scope; enforcement evaluation is the orchestrator's gate |
| `PROJECT-INV-003` / `PROJECT-INV-008` — budgets, no QD/DE | ledger not authored or evaluated by me; no production source tree present in `runtime/`, `gates/` empty | **NOT_TESTED** | orchestrator-owned ledger |

No invariant was weakened, reinterpreted, or modified to obtain a result.

---

## properties_tested

Status vocabulary is exactly `PASS | FAIL | INCONCLUSIVE | NOT_TESTED | BLOCKED`; each row names the executed route. All Python was executed via `python3 - <<'PY' … PY` heredocs (cwd `/tmp`, no files written). Primary routes are **stdlib** (`math`, `statistics.NormalDist`, `fractions`); `numpy 2.5.2` / `scipy 1.18.1` were used as **additional independent oracles** (Monte Carlo, quadrature, `ppf`) and are disclosed in `limitations`.

### A. Authority and integrity

| claim_id | method | command | expected | observed | status | evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `AUTH-1` | hash recomputation vs frozen snapshot | `sha256sum … ; sha256sum -c evidence/pre-qv-snapshot.sha256` | all match, `qr-result.md = d27f373f…` | 11/11 `OK`, exit 0, twice | **PASS** | inline output above |
| `AUTH-2` | canonical repo read-only check | `git -C … rev-parse HEAD; git status --porcelain` | `ff16b6b1…`, clean | `ff16b6b1…`, clean | **PASS** | inline output above |

### B. Analytical claims

| claim_id | claim (candidate) | method / independent route | command | expected | observed | status |
| --- | --- | --- | --- | --- | --- | --- |
| `C1` | VaR does not determine ES | exact enumeration of the two-point laws + RV integral + convex form | `python3` heredoc: `es_rv`/`quantile` on `[0,1]/[.95,.05]` and `[0,10]/[.95,.05]` | VaR 0 for both; ES 1 vs 10 | `quantile 0.95 = 0` both; `ES_RV = 1.000000` vs `10.000000`; convex form agrees | **PASS** |
| `C1b` | ES curve ⟺ VaR curve | numeric differentiation `VaR_u = ES_u − (1−u)ES'_u` | `python3` heredoc over u ∈ {0.90,0.95,0.975,0.99,0.995} | reconstruction error ≈ 0 | N: worst 3.67e-09; t₃: worst 6.31e-08 | **PASS** |
| `C2` | `ES = VaR + p⁻¹E[(L−VaR)⁺]` | exact discrete RV vs right-hand side | `python3` heredoc, three laws | identity exact | diffs +4.4e-16, +7.8e-16, +8.9e-15 | **PASS** |
| `C3` | atom example: ES 0.516 (RV) vs 0.5102 (cond-exp); single bond 0.8 vs 0.04 | exact enumeration of the two-bond pmf `[0.9216, 0.0768, 0.0016]` | `python3` heredoc `es_rv`, `es_cond_expect` | 0.516 / 0.5102 / 0.8 / 0.04 | `0.516000` / `0.510204` / `0.800000` / `0.040000`; `VaR_0.95 = 0.5` | **PASS** |
| `C4` | VaR not subadditive, ES subadditive | same enumeration | `python3` heredoc | `0.5 > 0+0`; `0.516 ≤ 1.6` | violation confirmed; `0.5160 ≤ 1.6` confirmed | **PASS** |
| `C5a` | `Var(VaR̂) ≈ αp/(n f(q)²)` | MC (t₃, N; R=2000–3000, n=10⁴) + exact order-statistic variance | `python3` heredoc MC | analytic 3.695% (t₃, 0.99); MC within noise | analytic 3.695%, MC 3.712% (N: 1.605% vs 1.604%) | **PASS** |
| `C5b` | `Var(ÊS) ≈ [Var(L|L>q)+α(ES−q)²]/(np)` | MC + exact finite-sample sum | `python3` heredoc MC | analytic 6.931% (t₃, 0.99) | analytic 6.931%, MC 7.221% (≈2.6σ, within finite-sample bias) | **PASS** |
| **`C5c`** | **`Cov(ÊS,VaR̂) ≈ −p(ES−q)/(n f(q))`, "negative"** | (i) hand derivation, (ii) **exact finite-sample uniform order-statistic algebra** (`fractions`), (iii) MC, (iv) numerical differentiation of the estimator functionals | `python3` heredoc; uniform n=10⁴ α=0.9 exact | candidate: `−5.0e-7`, `Corr < 0` | **exact: `Cov = +4.5027e-06`, `Corr = +0.8540`**; my asymptotic `+α(ES−q)/(n f) = +4.5e-6` (ratio 1.0006); MC `+4.446e-6`, `ρ = +0.8513`; α=0.99 t₃ MC `ρ = +0.4907`, N MC `ρ = +0.7360` | **FAIL** |
| `C5-note` | "the correlation is small at α ≥ 0.95" | same | same | small / ≈ 0 | `ρ = +0.49 … +0.85` | **FAIL** |
| `C5-internal` | internal consistency of `IF_VaR` | symbolically+evaluated `E[IF_VaR²]` under the candidate's own definition | `python3` heredoc p=0.05 | candidate's IF should reproduce `αp` | candidate's IF gives `p³+α³ = 0.857500` vs reported `αp = 0.047500` → reported `σ²_VaR` belongs to the **opposite-sign** IF | **FAIL** |
| `C6` | Student-t ES closed form `f_ν(q)(ν+q²)/((ν−1)p)` | substitution quadrature + direct Simpson + scipy `quad` + MC | `python3` heredoc, nu∈{3,5}, α∈{0.95,0.99} | agreement ≤ 1e-6 | 3 independent routes agree to ≥6 digits (e.g. t₃@0.99 `7.003082`, scipy `7.0030804`); MC 7.00612 ± 0.00927 | **PASS** |
| `C6b` | location–scale invariance at μ=0; non-invariance at μ≠0 | exact ratio construction | `python3` heredoc | invariance at μ=0 | `d = 1.646268` identical for σ ∈ {0.5,1,2,4}; varies for μ≠0 | **PASS** |
| `C7` | ES finite iff `E[L⁻] < ∞`; `ξ < 1` under regular variation | `ES = p⁻¹∫₀ᵖ w^{−ξ}dw` with shrinking lower cut-off | `python3` heredoc | convergence iff ξ<1 | ξ=0.5, 0.9 stable; ξ=1.0, 1.2, 1.5 grow without bound as cut-off → 0 | **PASS** |
| `C8` | for i.i.d. `t_ν`, `ν<2`: `h`-period scale `h^{1/ν} ≠ h^{1/2}` | MC h ∈ {1…1024}, |S_h| 95% quantile log-log slope | slope ≈ 1/ν, not 0.5 | ν=1: 0.9992; ν=1.5: 0.6811; (ν=3: 0.5079; ν=5: 0.4974) | **PASS** (ν<2) with scope caveat |
| `C9` | VaR-budgeted breach loss = `C·d` | arithmetic `C·d` | `python3` heredoc | 0.02·d | 0.02291 / 0.02646 / 0.03085 / 0.04 | **PASS** |
| `C10` | tail-count arithmetic | arithmetic | `python3` heredoc | k=100 @0.99, 500 @0.95; 39.7 yr; ≈15 stress exceedances | k=100 / 500 ✔; 39.68 yr ✔; 15% of 10000 = **1500**, not 1512 → 15.00 exceedances | **PASS** (with a 0.8% arithmetic slip in `n_stress`) |
| **`C11`/`E4`** | `SE(ln d)` and `MDE` table | full recomputation from `C5`, both covariance signs | `python3` heredoc (scipy moments + exact formulas) | internally consistent power table | reproduced **exactly** with the candidate's wrong covariance: t₃@0.99 `7.871%`/`22.05%` vs reported `7.88%`/`22.1%`; with the correct covariance `5.986%`/`16.77%`; margin 1.57× → 2.06× (and 2.85× → 3.85× @0.95) | **FAIL** |
| `C12c` | `d = 1` iff mass ≥ p sits exactly at VaR with nothing above | exact enumeration `[0,1]/[0.85,0.15]`, α=0.9 | `python3` heredoc | `VaR = ES = 1`, `d = 1` | `VaR = 1`, `ES_RV = 1`, `d = 1` | **PASS** |
| `E8` | `ES ≥ VaR`; monotone non-decreasing in α; `dES/dα = (ES−VaR)/p`; `d = 1/(1−ξ)`; scale invariance | exact enumeration + analytic derivative + numeric derivative; direct integration of the declared Pareto law | `python3` heredoc, α grid 0.50→0.99 step 0.01 | all hold exactly | ES≥VaR: True; monotone: True; numeric `dES/dα` = analytic to 6 dp (N 8.357184 = 8.357184; t₃ 30.418082; t₅ 17.501611); Pareto `d = 1.333333 / 2.000000 / 4.000000` exact; scale invariance rel. diff 0.000% | **PASS** |

### C. Required tests T1–T16 (packet §verification)

| test | target | executed? | observed | status |
| --- | --- | --- | --- | --- |
| `T1` | C1 non-redundancy + C3 atoms | mathematical part **executed**; "numeric output of the *implemented* estimand" | VaR 0/ES 1 vs 10; RV 0.516 vs cond-exp 0.5102; single bond 0.8 vs 0.04 | **PASS** (math) / **NOT_TESTED** (implementation — none exists) |
| `T2` | integral vs closed form ≤ 1e-6 | yes | agreement ≥ 6 digits via 3 routes; MC consistent | **PASS** |
| `T3` | E1 table recomputation | yes | d column: 4 s.f. match; Pareto exact; **ES@α=0.99 for t₅ and t₃ differ in the 4th s.f.**; t₅/t₃ α=0.95 same at 4 s.f. | **FAIL** (2 entries, narrow) |
| `T4` | MC size/consistency of C5 | yes (MC + exact finite-sample) | variance formulas match; **covariance sign falsified** (`ρ = +0.85` exact, vs claimed negative) | **FAIL** (covariance component) |
| `T5` | H₀ test size under fixed `t₃` shape | **no** — requires an implemented test statistic | — | **NOT_TESTED** |
| `T6` | power/MDE reproduction | partially: I reproduced the MDE table analytically (it is wrong); the *power* simulation is not possible | — | **NOT_TESTED** (power) |
| `T7` | `ξ̂ ≥ 1` handling returns "ES unsubstantiated" | mathematical part verified (C7); pipeline not implemented | C7 divergence confirmed | **NOT_TESTED** (implementation) |
| `T8` | √h prohibition in the estimator | mathematical part verified (C8); **the specified t₂ comparison set is degenerate** (`h^{1/2} ≡ h^{1/ν}` at ν=2; measured slope 0.5630, consistent with `√(h log h)`) | — | **NOT_TESTED** (implementation) + **test-design defect recorded** |
| `T9` | normality audit | yes (grep/line inspection of every estimator, test, bound) | no estimator/test/variance formula presumes normality; `c(α)` used as comparison constant/benchmark; Cornish–Fisher excluded; H₀ generator specified fat-tailed (`t₃`) | **PASS** (with nuance) |
| `T10` | point-in-time audit w/ future-injection | no implementation/filter exists | — | **NOT_TESTED** |
| `T11` | test-size validation of recalled statistics | the statistics are not concretely specified (LIT-UNVERIFIED, "formula to be source-verified") | — | **NOT_TESTED** — cannot validate an unspecified statistic |
| `T12` | multiple-testing audit | no trial log exists (human-declared gap) | only the *requirement* is stated | **NOT_TESTED** |
| `T13` | holdout integrity | no data, no code, no tuning constants materialised | — | **NOT_TESTED** |
| `T14` | exceedance-count audit | partially: the `k = n·p` arithmetic is executable (PASS, `C10`); no reported cell exists | — | **NOT_TESTED** (reported cells) |
| `T15` | reproducibility of E1/E4 | E1 reproducible (with the 2 noted corrections); E4 **not** reproducible as stated | — | **FAIL** (E4) / **PASS** (E1 after correction) |
| `T16` | analytical sanity oracles | yes | all hold (`E8` row) | **PASS** |

### D. Recalled premises (LIT-UNVERIFIED) and boundary compliance

| claim_id | premise | what I could do | observed | status |
| --- | --- | --- | --- | --- |
| `LIT-iv` | GPD/POT `VaR`/`ES` formulas | verified **as mathematics** by independent closed-form integration, not by source retrieval | ξ=0.3/0.5/0.2/0.75: candidate formula == my independent route to ≤3.6e-15 | **PASS** (formula verified; source attribution NOT_TESTED) |
| `LIT-v` | Hill estimator and its convention | arithmetic convention verified by MC on the declared Pareto law | ξ_true 0.25 → `ξ̂ = 0.2499`; 0.50 → `0.4983`; matches the candidate's formula convention | **PASS** (convention) |
| `LIT-i,ii,iii,vi` | non-elicitability of ES; Fissler–Ziegel joint scoring family; Acerbi–Székely backtests; coherence/non-elicitability debate | **cannot retrieve sources** (documentation/open-web capabilities blocked in my context too) | — | **NOT_TESTED** |
| `ROLE-BOUNDARY` | QR role compliance of the candidate | inspection against `quant-researcher/ROLE.md` | methodology-only; no data ingestion, no implementation, no deployment, no live execution, no self-certification ("Not independently validated"); assumption 7 pre-declared non-normality; holdout/causality requirements stated; handoff status `READY_FOR_REVIEW` is an allowed value; no silent change of an approved spec | **PASS** (no violation found) |
| `CENTRAL-NULL` | "the fat-tailed location-scale model is the correct primary null" | (a) argument audit, (b) executed counterexample | (a) preferring a non-Gaussian VaR-only benchmark over a Gaussian one is a sound, non-falsifiable design choice; (b) the *operational equivalence* "H₀ ⟺ constant `d`" and M1's `V3` restriction are **false** | **FAIL** (operational form) / preference itself not falsifiable |

---

## counterexamples

**CE-1 (decisive) — the C5 covariance has the wrong sign and the wrong factor.**
Exact finite-sample computation for i.i.d. `Uniform(0,1)`, `n = 10⁴`, `α = 0.9`, `VaR̂ = X_(9000)`, `ÊS =` mean of `X_(9001..10000)` (using exact order-statistic moments `Var(X_(i)) = i(n+1−i)/((n+1)²(n+2))`, `Cov(X_(i),X_(j)) = i(n+1−j)/((n+1)²(n+2))`, `i ≤ j`, computed in exact rational arithmetic):

```
EXACT finite-sample: Var(VaR)=9.005397e-06  Var(ES)=3.086934e-06  Cov=4.502699e-06  Corr=+0.8540
asymptotic QV route : Cov=+4.500000e-06     (α(ES−q)/(n f(q)), ratio exact/analytic = 1.000600)
candidate C5        : Cov=−5.000000e-07     (ratio exact/candidate = −9.005)
MC (R=4000)         : Cov=+4.446e-06  Corr=+0.8513
```

Additional confirmations: `t₃` α=0.99, `n=10⁴`, `R=2000`: `Cov = +4.18e-2`, `ρ = +0.4907 ± 0.0170` (analytic `+0.5048`); `N(0,1)` α=0.99: `ρ = +0.7360 ± 0.0084` (analytic `+0.7348`); independent numerical differentiation of the estimator functionals + quadrature: `Cov = +4.0921e2` per-n (analytic `+4.1107e2`) at α=0.99. The candidate's stated value is `−p(ES−q)/(nf)`; the correct value is `+α(ES−q)/f` per observation. **Four independent routes (hand derivation, exact algebra, MC, numeric-IF) agree on the sign; the candidate is alone on the other side.**

**CE-2 — "constant `d` ⟺ H₀" is false when `μ_t ≠ 0`.**
Under the candidate's H₀ with `ε ~ t₃` fixed (no shape variation whatsoever):
```
α=0.95: μ=+0.5,σ=1 → VaR=2.853363 ES=4.374268 d=1.533022
        μ=−0.5,σ=1 → VaR=1.853363 ES=3.374268 d=1.820618      |Δ ln d| = 17.19%
        (candidate's own noise floor at this cell: MDE(ln d) = 11.0% (as claimed) / 8.12% (corrected))
α=0.99: |Δ ln d| = 7.81%
```
So `d`-constancy tests, and M1's `V3` restriction `ES = κ·VaR` with a single calibrated `κ`, reject a **true** H₀ — with power above the design's own MDE at α=0.95. `d` is constant only with `μ_t = 0` (verified: `d = 1.646268` for all σ at μ=0). The candidate's own C6/S5 acknowledge the non-invariance; the executive summary's flat claim "under a fat-tailed location–scale model `d` is constant over time" and M1's "`V3` … is the instantiation of `H_0`" contradict that. Consequence: I-1/I-3 as specified are not valid tests of H₀, and I-4 can report "ES adds incremental value" driven purely by mean drift rather than tail shape.

**CE-3 — E1/E3 numeric entries outside the candidate's own tolerance.**
```
E1 ES t_5 a=0.99  cand=4.4506  true=4.452429   4 s.f.: 4.451 vs 4.452  DIFFER  rel=4.1e-04
E1 ES t_3 a=0.99  cand=7.0013  true=7.003082   4 s.f.: 7.001 vs 7.003  DIFFER  rel=2.5e-04
E3 d-1 t_5 a=0.99 cand=0.3226  true=0.323186   4 s.f.: 0.3226 vs 0.3232 DIFFER rel=1.8e-03
E3 d-1 t_3 a=0.99 cand=0.5419  true=0.542290   4 s.f.: 0.5419 vs 0.5423 DIFFER rel=7.2e-04
E2 ES.975 t_3     cand≈5.5     true=5.039583   rel=9.1e-02
```
Confirmed independently by stdlib quadrature, substitution quadrature, direct Simpson, `scipy.stats`/`scipy.integrate.quad`, and Monte Carlo (t₃@0.99 MC `7.00612 ± 0.00927`; t₅@0.99 MC `4.44687 ± 0.00299`). The `d`-ratio entries themselves agree at 4 significant figures. `T3`'s stated criterion ("any entry deviating in the 4th significant digit") is therefore triggered, and with it the candidate's change-control clause.

**CE-4 — `T8`'s specified comparison is degenerate.** The candidate's C8 claim is verified for ν<2 (slopes 0.9992 at ν=1, 0.6811 at ν=1.5). But `T8` prescribes `t₂`, for which `1/ν = 0.5`, so the two reference scalings the test asks the estimator to discriminate (`h^{1/2}` vs `h^{1/ν}`) are **identical**; the correct norming at ν=2 is `√(h log h)`. Measured slope 0.5630, closer to `√(h log h)` than to the candidate's asserted alternative at that ν. `T8` is not a discriminative test as written.

**CE-5 — `C10` arithmetic slip.** `0.15 × 10000 = 1500`, not `1512` (impact: 15.00 vs 15.12 expected exceedances — immaterial).

**CE-6 — mandated estimator converges slowly at atoms.** The candidate's E-hist estimator `ÊS = (1/k)Σ_{i=1}^{k}X_(i)`, `k = ⌈np⌉`, on the two-bond atom law: `n=2 000 → 0.51000`; `n=20 000 → 0.51200`; `n=200 000 → 0.51545` (RV estimand 0.516000, conditional-expectation form 0.510204). The asymptotic target is correctly 0.516, but a *sample-based* `T1` cannot cleanly separate 0.516 from 0.5102 at realistic `n`; `T1` is only decisive with an exact discrete evaluator. Observation, not a failure — reported so it is not mistaken for PASS evidence.

---

## failures

| # | Failing claim | Evidence | Severity | Repair |
| --- | --- | --- | --- | --- |
| F-1 | `C5`: `Cov(ÊS,VaR̂) ≈ −p(ES−q)/(n f(q)) < 0` | CE-1 (exact finite-sample, MC, numeric-IF, algebra) | **HIGH** — the covariance is a derived building block of the design's *mandatory pre-computed power* | replace with `+α(ES−q)/f(q)`; state the correlation is ~0.5–0.85, not small; fix the sign-inconsistent `IF_VaR` (`CE-1`, `C5-internal`) |
| F-2 | `C11`/`E4`: `SE(ln d)` and `MDE` table | recomputation: t₃@0.99 `7.88% → 5.986%`, `22.1% → 16.77%`; N@0.99 `2.35% → 1.216%`; margin 1.57× → 2.06× | **HIGH** — power feasibility and the "ES is expensive" argument | rebuild E4/E11 from the corrected covariance; the α=0.95 recommendation survives and strengthens (2.85× → 3.85×) |
| F-3 | `H₀ ⟺ constant d`; M1 `V3` as "the instantiation of H_0"; I-1/I-3 as tests of H₀ | CE-2 (exact H₀, `μ/σ = ±0.5`, `|Δ ln d| = 17.19% > MDE`) + internal contradiction with C6/S5 | **HIGH** — attacks the *primary* test's validity; risk of rejecting a true null and attributing it to tail shape | restate H₀ on standardized residuals (or add `μ_t` to the restricted model); make `V3` `ES_t = κ·VaR_t` on residuals with a declared filter; add a filter-correctness precondition before attributing any residual value to ES |
| F-4 | `E1` ES entries, t₅@0.99 and t₃@0.99 | CE-3 (5 independent routes) | **LOW-MATERIAL / process-significant** — ≤4e-4 relative, triggers T3 and change control | correct the two entries; version the document with a link to the superseded revision |
| F-5 | `E3` `d−1` entries, t₅/t₃ @0.99 | CE-3 | **LOW** | inherits F-4 |
| F-6 | `E2` t₃ value "≈5.5" | CE-3 (true 5.039583; the qualitative conclusion survives) | **LOW** | correct to ≈5.04 |
| F-7 | `C10` `n_stress = 1512` | CE-5 | **TRIVIAL** | correct to 1500 |
| F-8 | `T15` reproducibility of E4 | E4 as stated is not reproducible on independent recomputation | **MEDIUM** | resolved by F-1/F-2 |

Nothing was smoothed: the failures are preserved verbatim, and no invariant, criterion, or tolerance was weakened to obtain a passing result.

---

## inconclusive_areas

1. **Whether the C5 error changes any conclusion of the methodology.** Direction of the α=0.95 recommendation is unchanged and its margin *improves*; but the "ES is expensive" argument softens (5.99% vs 1.22% instead of 7.9% vs 2.4%). Whether the *decision-relevant* effect size would be detectable is unknowable without the human-declared effect size and a dataset → `INCONCLUSIVE`.
2. **Whether the `μ_t`-driven `d` variation is material for this strategy.** My counterexample uses `μ/σ = ±0.5`; the actual magnitude depends on the unspecified strategy and horizon → `INCONCLUSIVE`. The *existence* of the defect is established (CE-2); its practical size is not.
3. **Whether the fat-tailed location–scale model is the "correct" primary null.** As a design preference it is sound and not falsifiable without data; whether it is the right competitor for this strategy's tail structure → `NOT_TESTED`/`INCONCLUSIVE`. Its operational form is falsified (F-3).
4. **Whether the recalled (VaR, ES) scoring/backtest machinery is admissible** (`LIT-i..iii`): I could not retrieve sources and the candidate did not specify the statistics concretely, so `T11` cannot even be set up → `INCONCLUSIVE`.
5. **The definition of the `E-hist` ES level for the atom case in an implementation** (CE-6): asymptotically correct, finite-sample ambiguous → `INCONCLUSIVE` pending an implementation.

---

## untested_areas

Stated precisely, per the packet's requirement that untested ≠ PASS:

| Area | Why untested |
| --- | --- |
| **Every empirical criterion** — `SUPPORT-S2…S8`, `REFUTE-R1…R10`, gates Q1 and Q2, Q0 in an estimator | no dataset, no strategy, no cost/turnover model, no decision use (`dataset_identity = NOT_PROVIDED`); packet places empirical evaluation out of scope |
| `T5`, `T6` (power), `T7`, `T10`, `T11`, `T12`, `T13`, `T14` (reported cells), `T15` (implementation) | require an implementation, a fitted filter, a trial log, a holdout, or reported cells — none exists |
| `T8` (estimator behaviour), `T3`/`T4` against an implementation | same; only the mathematical claims were testable |
| `LIT-i` non-elicitability of ES alone | no documentation/open-web retrieval available in my context (`documentation: blocked; tools=[]`); refusing rather than asserting |
| `LIT-ii` Fissler–Ziegel jointly consistent scoring family | same |
| `LIT-iii` Acerbi–Székely canonical ES backtests | same |
| `LIT-vi` coherence/non-elicitability debate | same |
| Look-ahead/leakage/current-bar contamination, survivorship, futures-roll, fills, fees, slippage, partial fills, order-state | no data pipeline, no execution model, no code — nothing to mutate or truncate |
| `PROJECT-INV-006` enforcement evaluation, `PROJECT-INV-003`/`008` ledger controls | orchestrator-owned; QV has no write/eval authority here |
| Independence of QR/QV error modes | not establishable in this runtime (`PROJECT-INV-010 NOT_ENFORCED`) — recorded, not claimed |

---

## limitations

1. **No dataset and no implementation.** The packet authorises methodology-only scope, but the consequence is binding: most of `T1–T16` are untestable, and this report can only falsify *analytical and numerical* claims.
2. **Shared provider/model family.** QR and QV are both `commandcode/deepseek/deepseek-v4.1-flash` (verified from `qr-result.meta.txt` and `PI_PROVIDER`/`PI_MODEL`). Every PASS where I agree with the candidate may reflect a *shared error mode*, not independent confirmation. This is the single largest limitation of this report.
3. **No source retrieval.** `documentation` and `open-web` capabilities are blocked in my context. Four literature premises are therefore `NOT_TESTED`; I verified only their mathematical content where it is verifiable (GPD/POT, Hill convention).
4. **Tooling disclosure.** Primary recomputation used stdlib only (`math`, `statistics.NormalDist`, `fractions`, custom Simpson/trapezoid quadrature). `scipy 1.18.1` (`ppf`, `pdf`, `quad`) and `numpy 2.5.2` (Monte Carlo) were used as **additional** independent oracles; a bug in my own first atom-handling and two `scipy.quad` power-tail failures were caught and corrected before reporting (results are from corrected code only).
5. **Monte Carlo precision.** MC standard errors are reported with each MC figure; no PASS rests on MC alone where a deterministic oracle was available (the covariance FAIL rests on an exact closed form).
6. **Scope of my authority.** I did not verify authorship, only integrity; I did not evaluate governance enforcement, budgets, or the human gate; I did not repair anything.
7. **"4th significant digit" tolerance is a proxy.** For F-4/F-5 the deviations are 2.5e-4–1.8e-3 relative. I report the raw numbers and the 4-s.f. comparison so the human can judge materiality rather than trusting a threshold I chose.

---

## unresolved_risks

| ID | Risk | Severity | Owner |
| --- | --- | --- | --- |
| `QV-UR-1` | The primary test I-1/I-3 can reject a **true** H₀ when `μ_t ≠ 0` (CE-2), producing a false "ES adds information" verdict once data exists | **HIGH** | `quant-researcher` (spec repair) → Human Gate |
| `QV-UR-2` | The mandatory pre-computed power is derived from a wrong covariance (F-1/F-2); any design sized on the old MDE is mis-sized (conservatively so, but the stated feasibility is wrong) | **HIGH** | `quant-researcher` |
| `QV-UR-3` | `PROJECT-INV-010`: QR/QV error-mode independence not established; all agreements in this report are conditional on that | **HIGH** | human authority (accept/record) |
| `QV-UR-4` | Four `LIT-UNVERIFIED` premises remain source-unverified (elicitability, joint scoring family, backtests, coherence debate) and are load-bearing for the evaluation machinery | **HIGH** | human authority + future role with retrieval capability |
| `QV-UR-5` | Hand-derived numerics are now **demonstrably** error-prone (UR-7 materialised): 2 entry-level deviations + 1 formula-level sign error | **MEDIUM** | `quant-researcher`; change control |
| `QV-UR-6` | `E4` shows the design may still be underpowered at deep α (MDE ≥ 16.8%); pressure to convert `INCONCLUSIVE` into a conclusion remains the main epistemic hazard | **MEDIUM** | Human Gate policy |
| `QV-UR-7` | Free-parameter surface (α, h, estimator, threshold, regime definition, benchmark complexity, decision rule) remains a selection-risk surface (`T12` untested, no trial ledger) | **MEDIUM** | `quant-researcher` / orchestrator |
| `QV-UR-8` | No dataset ⇒ the entire empirical layer is untestable; any downstream claim of empirical support would be fabricated | **HIGH** | human authority |
| `QV-UR-9` | `PROJECT-INV-007` is `MANUAL_GATE`: the correspondence between this report's inline evidence and a human-readable evidence path must be confirmed by the Human Gate. **This report is returned, not persisted** — the orchestrator persists it; there is currently no `authoritative-inputs/qv-result.md` on disk | **MEDIUM** | orchestrator + Human Gate |

---

## evidence

All commands executed read-only, from `/tmp`, via stdin heredocs; **no file was created or modified anywhere**. Workspace immutability re-verified after all work (`sha256sum -c evidence/pre-qv-snapshot.sha256` → 11/11 OK, exit 0).

| # | Purpose | Exact command (heredoc body abbreviated) | Observed output (key values) |
| --- | --- | --- | --- |
| E-01 | authority hashes | `sha256sum .governance/* authoritative-inputs/*` ; `sha256sum -c evidence/pre-qv-snapshot.sha256` | 11/11 `OK`, exit 0; `qr-result.md d27f373f…4bdae` |
| E-02 | canonical repo check | `git -C …/GENTLE-QUANT-ECOSYSTEM rev-parse HEAD ; git status --porcelain` | `ff16b6b1…`, clean |
| E-03 | E1 recomputation (stdlib + 3 quadrature routes) | `python3 - <<'PY'` NormalDist inv_cdf loop; Simpson CDF/inverse; substitution integral; direct Simpson; Pareto direct integration | N `1.254040/1.145665`; t₅ `1.434273/1.323186`; t₃ `1.646268/1.542290`; Pareto `1.333333/2.0/4.0` |
| E-04 | E1 arbitration of the two suspect entries | `python3 - <<'PY'` scipy `st.t.ppf/pdf` + `quad`; numpy MC 2e7 | t₅@0.99 ES `4.452429` (scipy) / MC `4.44687 ± 0.00299`; t₃@0.99 ES `7.0030804` / MC `7.00612 ± 0.00927` |
| E-05 | C1, C2, C3, C4 (exact enumeration) | `python3 - <<'PY'` `quantile`,`es_rv`,`es_cond_expect` | VaR 0/ES 1 vs 10; `0.516000` vs `0.510204`; single bond `0.800000` vs `0.040000`; `0.5 > 0+0`; `0.5160 ≤ 1.6`; C2 diff ≤9e-15 |
| E-06 | C1b curve equivalence | `python3 - <<'PY'` numeric `ES'_u` | worst error N `3.67e-09`, t₃ `6.31e-08` |
| E-07 | E2 bridge | `python3 - <<'PY'` | `ES_0.975(N)=2.337803`, ratio `1.004924`; `ES_0.975(t₃)=5.039583` vs claimed `≈5.5` |
| E-08 | E8 oracles | `python3 - <<'PY'` α-grid + numeric derivative + Pareto integration + scale invariance | ES≥VaR True; monotone True; `dES/dα` = `(ES−VaR)/p` to 6 dp; Pareto exact; scale rel. diff 0 |
| E-09 | C7 existence | `python3 - <<'PY'` `(1/p)∫_lo^p w^-ξ dw` | ξ=0.5,0.9 stable; ξ=1.0,1.2,1.5 grow without bound |
| E-10 | C5 variance/covariance + E4 table | `python3 - <<'PY'` scipy moments + both covariance signs | `SD(VaR)/VaR` and `SD(ES)/ES` match candidate; `SE(ln d)` reproduced with candidate's covariance; corrected `5.986%`/`16.77%` |
| E-11 | **C5 covariance sign — MC** | `python3 - <<'PY'` numpy `standard_t`/`standard_normal`, R=2000–3000, n=10⁴ | N: `ρ=+0.7360±0.0084`; t₃ 0.99: `ρ=+0.4907±0.0170`; t₃ 0.95: `ρ=+0.4796±0.0172` |
| E-12 | **C5 covariance sign — exact finite sample** | `python3 - <<'PY'` `fractions` exact order-statistic moments, uniform n=10⁴ α=0.9 | `Cov=+4.502699e-06`, `Corr=+0.8540`; my asymptotic `+4.5e-6`; candidate `−5.0e-7` |
| E-13 | **C5 covariance sign — numeric differentiation** | `python3 - <<'PY'` `F_3` closed form, finite-difference influence functions, quadrature | α=0.99 `Cov=+4.0921e2` (analytic `+4.1107e2`); α=0.95 `+3.1805e2` (`+3.1843e2`) |
| E-14 | `C5-internal` inconsistency | `python3 - <<'PY'` | candidate IF gives `p³+α³ = 0.857500` vs reported `αp = 0.047500` |
| E-15 | C8/T8 √h scaling | `python3 - <<'PY'` numpy MC, h∈{1…1024} | slopes ν=1: `0.9992`; ν=1.5: `0.6811`; ν=2: `0.5630`; ν=3: `0.5079`; ν=5: `0.4974` |
| E-16 | **central-null falsification (CE-2)** | `python3 - <<'PY'` exact `μ_t+σ_t ε` with `ε~t₃` | `d=1.533022` vs `1.820618`, `|Δln d|=17.19%` > MDE |
| E-17 | GPD/POT formulas | `python3 - <<'PY'` independent closed-form `VaR + ζ_uβA^{1−1/ξ}/((1−ξ)p)` | 4 parameter sets, diff ≤ `3.6e-15` |
| E-18 | Hill convention | `python3 - <<'PY'` MC Pareto | `ξ̂ = 0.2499 / 0.4983` for `ξ = 0.25 / 0.50` |
| E-19 | atom-case estimator convergence (CE-6) | `python3 - <<'PY'` numpy | `0.51000 / 0.51200 / 0.51545` at n = 2e3/2e4/2e5 |
| E-20 | normality audit (T9) | `grep -n -i 'norm\|Gauss\|c(α)\|φ(z\|√h\|Cornish\|Edgeworth' authoritative-inputs/qr-result.md` | 10 `c(α)` uses: definition, reporting constants, benchmark threshold in S2, explicit "reporting reference" in I-3; no estimator/test/variance formula assumes Gaussianity |
| E-21 | identity/context | `env \| grep ^PI_` ; `grep … qr-result.meta.txt` | `PI_SESSION_ID=01a0df5b-38f4-73f0-80b5-0b02f8708933` ≠ QR `01a0df55…`; both `commandcode/deepseek/deepseek-v4.1-flash` |
| E-22 | post-run immutability | `sha256sum -c evidence/pre-qv-snapshot.sha256` (2nd run) | 11/11 `OK` |

Reported evidence is inline; there is no persistence path for QV in this run (no write authority), so `E-01…E-22` are reproducible by re-executing the same heredocs against the frozen artifacts.

---

## next_recommended
`return_to_quant_researcher`

Rationale: the candidate is a **research specification**, and the defects found are specification/mathematical defects, not implementation defects and not data defects. Repairs are bounded and enumerable: (1) correct the C5 covariance and its derivation; (2) rebuild C11/E4 from it; (3) restate H₀/I-1/V3 on standardized residuals (or add `μ_t` to the restricted model) and add a filter-correctness precondition; (4) correct the E1/E3/E2/C10 numerics; (5) make `T8` discriminative (use ν<2, e.g. `t_1.5`, not `t_2`). Not `return_to_quant_developer` (no implementation exists or is authorised). Not `return_to_data_engineer` (no lineage/timestamp defect — there is no data). Not `ready_for_human_review` (material claim failures outstanding; the Human Gate should receive a corrected revision, not this one).

---

## required_human_decisions

1. **Disposition of this FAIL.** Decide whether the candidate must be corrected (recommended) or accepted with the enumerated defects recorded as known limitations. The E1/E3 numeric slips and F-3 (H₀ equivalence) are safe to repair; F-1/F-2 change a mandatory design input.
2. **Authorise a bounded correction under change control.** `T3`/`T4` failures trigger the candidate's own rule that the document must be revised and versioned with a link to the superseded revision before downstream use. Versioning language and the permitted edit surface are human choices.
3. **Decide the decision use of ES** — D1 reporting, D2 limits/sizing, D3 ranking/selection. This fixes the admissible evaluation machinery.
4. **Fix the comparison parameters** — α, h, primary estimator, primary regime definition, benchmark complexity `m`.
5. **Declare the decision-relevant effect size**, which fixes the required MDE and therefore whether the design is feasible at any given `n`. Note the corrected MDE (16.8% at α=0.99 vs 8.1% at α=0.95 for t₃, n=10⁴) makes the feasibility question *less* binding than the candidate claimed.
6. **Declare the cost/turnover model** for gate Q2.
7. **Accept and record the residual risk of `PROJECT-INV-010`** (shared provider/model family; independence not established) and confirm that agreement between QR and QV is not treated as confirmation.
8. **Decide on dataset/strategy provisioning** for any empirical run — a scope change requiring a new task packet (`quant-data-engineer` budget is 0 in this run).
9. **Confirm the RESEARCH_ONLY posture and that no implementation is authorised** (`PROJECT-INV-008`), and that no production approval is granted or implied by anything in this report (`PROJECT-INV-001`).
10. **Confirm the final production disposition** at the Human Gate, with `trade_authorized: false` (`PROJECT-INV-002`).
11. **Decide how the four source-unverified literature premises (`LIT-i..iii`, `LIT-vi`) are to be resolved**, given that neither the QR session nor this QV session had retrieval capability; a role/tool with documentation access is required, or the premises must be explicitly accepted as unverified.

---

## independence_statement

**QR/QV error-mode independence is NOT established, and no such claim is made.**

- The two executions ran in **distinct child contexts** — observed: QR `child_session_id 01a0df55-f2f3-7385-acac-3d22d832a7da`, `child_task_id muitozyl-1-0osb`; QV `PI_SESSION_ID 01a0df5b-38f4-73f0-80b5-0b02f8708933`, distinct child task, and this transport carried only the task packet (no QR hidden reasoning). That satisfies the *reported* separation of `PROJECT-INV-004`, which is a procedural requirement.
- It does **not** establish statistical independence. Both specialists are pinned to the same provider/model family — `commandcode/deepseek/deepseek-v4.1-flash` (read from `qr-result.meta.txt` and from `PI_PROVIDER`/`PI_MODEL`). Shared training and decoding error modes cannot be excluded. Per `PROJECT-INV-010` (status `NOT_ENFORCED`) and canonical `EFFECTIVE_CHALLENGE` / `INDEPENDENCE_BEFORE_VOTE`, this is recorded as a **possible dependency, never as evidence of independence**.
- Practical consequence for the reader: **every PASS in this report where I agree with the candidate is weaker evidence than it appears**, because the agreement may be a shared blind spot. By contrast, the **FAILs are stronger**: they rest on deterministic computations (exact rational order-statistic algebra, machine-precision closed-form identities, exact discrete enumeration) that are verifiable by any third party and do not depend on either model's judgment. Treat the FAILs as robust and the PASSes as provisional.

---

## production_approval

**I am NOT approving production.** `trade_authorized` remains **`false`**. This report grants no production, deployment, implementation, trading, or release authority, and it does not constitute human approval under `PROJECT-INV-001` or `PROJECT-INV-002`. It is an independent adversarial validation result for `authoritative-inputs/qr-result.md` (sha256 `d27f373fd0f3c0af7ac1caa6304dbaf044d905dfd6e93ff6a9fc7a1e9d14bdae`) with terminal status `FAIL`, intended for the orchestrator and, downstream, the Human Gate. No file in `/home/datawithjose/Documents/GQE-CERT-RUNS/GQE-PI-CERT-M4-001` or `/home/datawithjose/Documents/GENTLE-QUANT-ECOSYSTEM` was created or modified by this validation.