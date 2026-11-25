# GQE Task Result — `GQE-PI-CERT-M4-QR-001`

## status
`COMPLETED`

Methodology delivered exactly within the authorized scope (research methodology only). No empirical claim about any market is made, because `dataset-primary` is `UNKNOWN / NOT_PROVIDED` and the packet places data provisioning out of scope. Absence of a dataset is not treated as evidence about markets; it is treated as an unresolvable empirical gap, declared in `unknowns`.

---

## executive_summary

- **specialist_identity:** `quant-researcher` (canonical role `ROLE.md`, subagent contract `SUBAGENT.md`, spec `SUBAGENT-CONTRACT-SPEC.md` @ canonical commit `ff16b6b1e21f34a6df9e72d6121bac93ee8fcd4b`)
- **task_identity:** `task_id=GQE-PI-CERT-M4-QR-001`, `task_version=1.0`, `project=GQE-PI-CERT-M4-001`, `assigned_role=quant-researcher`, packet `status=READY`
- **posture:** `RESEARCH_ONLY`; `trade_authorized = false`; no production implementation, no data pipeline, no code deliverable, no writes performed (read-only tool use).
- **work performed:** a bounded, falsifiable research methodology comparing VaR and Expected Shortfall for fat-tailed, regime-dependent strategy returns; all required mathematical conventions stated; supporting and refuting evidence criteria defined before any data exists.
- **central methodological reduction `[DERIVED]`:** the useful question is not "does ES encode more tail information than VaR?" (analytically, almost trivially, yes) but "**does ES encode information not recoverable from VaR plus a stable fat-tailed tail shape?**" This makes the VaR-only null **non-Gaussian**: the relevant null is a fat-tailed location–scale model with a *fixed* standardized-residual shape, under which `ES_α = d·VaR_α` with `d` constant, so a single calibrated constant carries all the tail information. ES adds decision-relevant information **only if the tail-shape ratio `d` varies over time/regime in a way VaR does not capture**.
- **primary testable quantity `[DERIVED]`:** `d_α := ES_α / VaR_α ∈ [1, ∞)`. Under normality `d_α = c(α) = φ(z_α)/((1−α)z_α)` (a constant); under a Pareto tail `d = 1/(1−ξ)`, α-independent; under a fat-tailed location–scale model `d` is constant over time. `d_α − 1` is exactly the multiplicative understatement of expected tail loss by a VaR-budgeted position.
- **honest cost/benefit `[DERIVED]`:** ES's incremental tail-shape information is paid for with (i) much larger estimation error (`SE(ln d) ≈ 7.9%` vs `2.4%` for Gaussian-like tails at α=0.99, n=10⁴), (ii) a **stronger existence condition** (ES is finite only if the loss's first moment is finite, i.e. tail index `ξ < 1`; VaR is finite regardless), and (iii) non-elicitability of ES alone *(literature-recalled, source-unverified in this session)*, which constrains admissible evaluation machinery.
- **design consequence `[DERIVED]`:** at α=0.99 with daily data, regime-conditional ES is not non-parametrically estimable (~15 stress-day exceedances over 40 years). The design therefore mandates α=0.95 or a weekly horizon as the primary level for the shape comparison, with EVT pooling across a declared tail region, and pre-computed power.
- **handoff:** `READY_FOR_REVIEW` → `quant-validator`. Not `APPROVED_FOR_IMPLEMENTATION` (independent validation and the Human Gate are outstanding; no implementation is authorized in this run).

---

## research_question

> For a trading strategy whose return distribution may be fat-tailed and regime-dependent, does Expected Shortfall (CVaR) provide **decision-relevant** tail-risk information beyond Value-at-Risk — specifically, information that (a) is not recoverable from VaR plus a stable fat-tailed tail shape, (b) is estimable with controlled error at a declared confidence level `α` and horizon `h`, and (c) changes a declared risk decision in a way that reduces a declared realized loss?

Three levels must be answered separately; conflating them is the main failure mode this methodology blocks:

- **Q0 — informational non-redundancy.** Is `ES_α` determined by `VaR_α` alone? `[DERIVED: no — counterexample in `checks_performed` C1]` Necessary, weak, analytically almost tautological; answering Q0 alone cannot justify using ES.
- **Q1 — estimable incremental information.** Given finite samples and a declared estimator class, does ES deliver incremental information beyond the **strongest defensible VaR-only alternative** (VaR + stable fat-tailed shape), with controlled estimation error and multiple-testing discipline?
- **Q2 — decision value.** Does an ES-informed decision rule beat the declared VaR-only rule under a pre-declared loss function on a point-in-time, out-of-time evaluation?

Supporting the general claim "use both metrics" requires **Q1 and Q2**, with Q0 as a prerequisite.

---

## hypothesis

Working hypothesis (falsifiable, stated before any data access):

- **H_pri (primary, alternative):** for the strategy in question, the tail-shape ratio `d_α = ES_α/VaR_α` is *not* time-invariant conditional on observable, point-in-time volatility information; equivalently the fat-tailed location–scale null is rejected out-of-sample, and the ES increment survives multiple-testing control and inclusion of costs. Under H_pri, ES carries tail-shape information beyond VaR and improves at least one declared risk decision.
- **H_0 (primary null, the one that must be defeated):** losses satisfy a fat-tailed location–scale representation `L_t = μ_t + σ_t ε_t` with `(μ_t, σ_t)` point-in-time predictable and `ε_t ~ F_ε` *time-invariant*. Then `VaR_α,t = μ_t + σ_t VaR_α(ε)` and `ES_α,t = μ_t + σ_t ES_α(ε)`, so `d_t` is a deterministic function of `(μ_t/σ_t)` and the single constant `d_ε`. ES adds **no** time-varying tail information beyond VaR. **Note: `F_ε` may be arbitrarily heavy-tailed (e.g. Student-t, Pareto, GPD). This null is deliberately not Gaussian.**
- **H_rescue (ES-as-noise alternative):** `ε_t` shape does vary, but unpredictably, so ES's increment is not estimable above its own error. Then ES adds *noise*, not information → refute (R2 below).
- **H_reject-shape (VaR-dominant alternative):** `d_α` varies but is recoverable from a multi-level VaR curve at matched information budget, or from the volatility state. Then ES is redundant → refute (R1/R5 below).

Falsifiable prediction of H_pri: the ES increment is detectable in the joint-score comparison (I-1/I-2/I-3 in `methodology`) and in the incremental-severity regression (I-4), on a holdout period, net of costs, after Holm correction over a pre-registered family.

---

## mathematical_specification

### S1. Market and time semantics

- `t` indexes a discrete, point-in-time-available observation grid; `h > 0` is the risk horizon in **trading days** (default candidate `h ∈ {1, 5, 10}`; the primary `h` must be declared before analysis).
- Return over `(t, t+h]`: `r_{t,h} = P_{t+h}/P_t − 1` (**simple** returns; the only aggregation-compatible convention). Log returns `ln(P_{t+h}/P_t)` may be used **only** under an explicitly declared log convention and never mixed with simple returns in the same computation.
- `t+h` must be inside the sample: the last `h` observations are unusable for `h`-horizon evaluation. Overlapping `h`-horizon returns induce serial dependence of order `h−1` and reduce effective sample size to `n_eff ≈ n/h`; this must be handled, not ignored.

### S2. Sign convention (definition, not an assumption)

- **Loss** `L_{t,h} := −r_{t,h}`, in units of **fraction of notional per unit exposure**. Positive `L` = loss.
- VaR and ES are defined on the **loss** distribution (upper/loss tail). If reported on returns, `VaR^R := −VaR^L` and `ES^R := −ES^L` (negative numbers for a loss tail). **Choice made here: all internal computation, estimation, testing and comparison uses the loss convention `L = −r` with `VaR^L, ES^L > 0` in the loss tail.** Any reported return-convention figure is a sign flip of this and must be labelled.
- `VaR^L` is only interpretable as a *loss threshold* where `VaR^L > 0`. For a positive-drift strategy at moderate `α`, `VaR^L_α ≤ 0`. The methodology therefore requires a declared **working α range** with `VaR^L_α > 0`, or a shifted-loss convention `L̃ = L + s`, `s ≥ 0`, applied identically to both metrics.

### S3. Confidence-level semantics

- `α ∈ (0,1)` is the **confidence level** (upper-tail level). `p := 1 − α` is the **tail probability**.
- `α` is a *parameter*, not a property: `d_α`, `c(α)`, and every error bound depend on it. Never compare an ES at one `α` to a VaR at a different `α` without an explicit bridge.
- Bridging fact `[DERIVED]`: under normality `ES_{0.975} = 2.3376 ≈ VaR_{0.99} = 2.3263` (ratio 1.0049). Regulatory practice that pairs ES@97.5% with VaR@99% is (under normality) close to a like-for-like comparison; this must be stated, not assumed, and re-derived for the actual estimated shape.

### S4. Estimands (definitional core)

Conditional on information available at `t`, let `F_{t,h}(ℓ) = P(L_{t,h} ≤ ℓ | F_t)` with quantile function `F^{-1}_{t,h}`.

```
VaR^L_{α,t,h}  := inf{ ℓ ∈ ℝ : F_{t,h}(ℓ) ≥ α } = F^{-1}_{t,h}(α)
ES^L_{α,t,h}   := (1/p) ∫_{α}^{1} VaR^L_{u,t,h} du                          (Acerbi–Tasche integral form)
                =  min_{c∈ℝ} { c + p^{-1} E[(L_{t,h} − c)^+ | F_t] }        (Rockafellar–Uryasev convex form)
```

**Discrete vs continuous handling (mandatory).** The integral/RV form is the **estimand**. The conditional-expectation form `E[L | L ≥ VaR^L_α]` coincides with it **iff** `F` is continuous at `VaR^L_α`. Under atoms the two disagree, and the conditional-expectation form is not coherent. Worked instance in `checks_performed` C3: for the two-bond portfolio, `ES = 0.516` (correct) vs `E[L | L ≥ VaR] = 0.5102` (incorrect). Empirically: returns are effectively continuous, but *strategy P&L with discrete states, option payoffs, barrier exits, or missing data* can produce atoms at the VaR level — the methodology must test for mass at the empirical VaR and use the RV form in all cases.

**Exact identity (used repeatedly below)** `[DERIVED, C2]`:

```
ES^L_α = VaR^L_α + p^{-1} · E[(L − VaR^L_α)^+] = VaR^L_α + E[L − VaR^L_α | L > VaR^L_α]
```

### S5. Tail-shape ratio and benchmarks

```
d_α        := ES^L_α / VaR^L_α    ∈ [1, ∞)   (defined where VaR^L_α > 0)
c(α)       := ES/VaR of N(0,1) = φ(z_α) / (p · z_α)          (Gaussian benchmark, constant in t)
ξ          := tail index of the loss tail (GPD/Pareto/Hill)
Pareto:      VaR_α = (1−α)^{−ξ} ,  ES_α = (1−α)^{−ξ} / (1−ξ) ,  d = 1/(1−ξ)  for ξ < 1
```

`d_α` is the comparison statistic. `[DERIVED, C5/C6]` it is invariant to positive scale when the loss mean is zero, but **not** invariant when `μ ≠ 0` — hence all shape analysis must be performed on **standardized residuals** `ε = (r − μ̂_t)/σ̂_t` with a declared, point-in-time filter for `(μ̂_t, σ̂_t)`.

### S6. Units and horizon scaling

- Internally: losses in fraction of notional (or in currency per unit exposure if a notional is declared); `α` dimensionless; `h` in trading days; `ξ`, `d`, `c(α)` dimensionless.
- **No `√h` scaling is permitted.** `[DERIVED, C8]` `√h` aggregation requires i.i.d. returns **with finite variance** plus a CLT scaling limit. Fat tails violate this: for i.i.d. `t_ν` with `ν < 2` the `h`-period sum scales as `h^{1/ν}`, not `h^{1/2}`. Every declared `h` must be estimated **directly**, or via an explicitly declared aggregation model whose behavior is verified against a simulation oracle.
- Representative units: if `VaR^L_{0.95,1d} = 0.02`, then a VaR-budgeted position with `C = 0.02` has expected breach loss `C·d_{0.95}` (see `expected_numerical_behavior` E7).

### S7. Estimator choices (declared set; primary must be pre-registered)

Mandatory: **at least two structurally different estimators**, of which at least one is non-parametric and at least one is tail-parametric; disagreement between them is reported as part of the estimand's uncertainty, never hidden.

| ID | Estimator | Assumes | Role |
| --- | --- | --- | --- |
| E-hist | Empirical (order statistics): `VaR̂ = −X_(⌈nα⌉)`; `ÊS = −(1/k)Σ_{i=1}^{k} X_(i)`, `k = ⌈n p⌉`. **Quantile convention declared** (Hyndman–Fan type 7 vs type 1; default: type 7 for quantiles, order-statistic mean for ES). | Continuity near the quantile; no shape assumption | Baseline; mandatory |
| E-fhs | Filtered historical simulation: declared point-in-time volatility filter (EWMA or GARCH-class, parameters fitted on a **train window only**) + bootstrap of standardized residuals, `≥` block length `h` | Correct filter; stationary standardized residual law | Primary conditional estimator |
| E-evt | Peaks-over-threshold GPD on excesses above a declared threshold `u`, with `VaR_α = u + (β/ξ)[(n/N_u·p)^{−ξ} − 1]`, `ES_α = VaR_α/(1−ξ) + (β − ξu)/(1−ξ)`, `ξ < 1` | Regular variation above `u` | Primary tail-shape/`ξ` estimator; also the only route to usable tail estimates at deep `α` |
| E-t | Student-t / skew-t / GED / generalized hyperbolic fitted by MLE; `ES_ν,α = f_ν(q_α)(ν + q_α²)/((ν−1)p)` | Parametric family is correct | Comparator; also the natural instantiation of `H_0` |
| E-qr | Conditional quantile regression / CAViaR-style for `VaR_t`; joint `(VaR, ES)` semiparametric regression (elicitable pair) for `ES_t` | Declared regressor set is point-in-time | Conditional/predictive variant |
| E-hill | Hill estimator `ξ̂ = (1/k)Σ_{i=1}^{k} ln(L_(n−i+1)/L_(n−k)})` with a **pre-declared threshold rule** | Regular variation; `k` chosen before seeing results | `ξ` stability test |
| — | **Excluded as primary:** Cornish–Fisher / Edgeworth expansions (presume near-normality); any `√h`-scaled estimator; any estimator using future information in filters, thresholds or regime labels | — | Robustness only |

Threshold selection for E-evt/E-hill is a **free parameter**: the rule must be pre-declared (fixed `k`, fixed `k/n`, or a declared automated rule) and its sensitivity reported. Post-hoc threshold choice is a multiple-testing violation.

---

## authoritative_inputs

| ID | Type | Classification | Locator | Status |
| --- | --- | --- | --- | --- |
| `acceptance-brief` | user request | `USER_DECLARED` | this task packet objective | `VERIFIED` (as requirement, not as evidence about markets) |
| `TASK-PACKET-QR.yaml` | task packet | `DISCOVERED` | `.../GQE-PI-CERT-M4-001/authoritative-inputs/TASK-PACKET-QR.yaml` | `VERIFIED` (status `READY`, `ready_for_execution: true`) |
| `canonical-researcher-role` | specification | `DISCOVERED` | `GENTLE-QUANT-ECOSYSTEM/agents/quant-researcher/ROLE.md` @ `ff16b6b…` | `VERIFIED` (read in full) |
| `canonical-subagent-contract` | specification | `DISCOVERED` | `.../agents/quant-researcher/SUBAGENT.md`, `.../agents/SUBAGENT-CONTRACT-SPEC.md` @ `ff16b6b…` | `VERIFIED` (read in full) |
| `canonical-agent-rules` | specification | `DISCOVERED` | `GENTLE-QUANT-ECOSYSTEM/governance/core/AGENT-RULES.md` @ `ff16b6b…` | `VERIFIED` (read in full, 614 lines) |
| `governance-contract` | governance | `DISCOVERED` | `.governance/CONTRACT.md` | `VERIFIED` (status `APPROVED`, human approved) |
| `governance-invariants` | governance | `DISCOVERED` | `.governance/INVARIANTS.md` | `VERIFIED` (INV-001…010; applicable INV-001/002/003/008/009 all present) |
| `governance-routing` | governance | `DISCOVERED` | `.governance/ROUTING.yaml` | `VERIFIED` (`quantitative_research` → `quant_researcher` + required reviewer `quant_validator`) |
| `governance-team` | governance | `DISCOVERED` | `.governance/TEAM.yaml` | `VERIFIED` (QR `execution_budget: 1`, `delegation: FORBIDDEN`, `context: ISOLATED_PREFERRED`) |
| `dataset-primary` | dataset | `UNKNOWN` | `path: null` | `NOT_PROVIDED` — no dataset in scope; **not invented** |
| `required_skills` | skills | `DISCOVERED` | packet: `required_skills: []` | `NONE DECLARED`; no substitution made |

Workspace check performed: `authoritative-inputs/` contains only `TASK-PACKET-QR.yaml`; no prior `qr-result.md` exists in this run — no earlier QR output is being reused or paraphrased.

---

## assumptions

`[A]` = assumption adopted for this specification; `[¬A]` = explicitly **not** assumed.

**Structural**
1. `[A]` A probability space and a loss process `L_{t,h}` exist with a well-defined (conditional) quantile at the declared `α`; VaR is finite for every admissible `α ∈ (0,1)`.
2. `[A]` The declared `(α, h)` pair, decision rule and loss function are fixed **before** any evaluation; post-hoc changes require a recorded amendment linking to the superseded spec.
3. `[A]` All inputs, filters, thresholds and regime labels are point-in-time available (`available_at ≤ t`), per `POINT_IN_TIME_ONLY`.
4. `[A]` The evaluation has a genuine out-of-time holdout that is not consulted during design or calibration.
5. `[A]` A finite variance of data available for calibration is available for the estimators that need it (e.g. GARCH-class filter fitting); the **conclusion itself does not assume finite return variance** — that is tested.
6. `[A]` Where a decision rule is compared, a transaction-cost and turnover model is declared; comparisons are net of costs.

**Explicit non-assumptions (`[¬A]`)**
7. `[¬A]` **Normality** of returns. No step, estimator, test or bound in this specification assumes Gaussian returns. The `H_0` null is a **fat-tailed** location–scale model; `c(α)` is used only as a *reference constant for reporting the amount of non-Gaussian tail excess*, never as a distributional assumption, and never as an estimator.
8. `[¬A]` i.i.d. returns. Dependence (volatility clustering, autocorrelation, regime switching, overlapping `h`-horizon windows) is expected and handled by block/stationary bootstrap and by `n_eff` correction.
9. `[¬A]` Stationarity of the return distribution. Weak stationarity of the *shape* is the hypothesis being tested, not an assumption.
10. `[¬A]` Finite variance of returns.
11. `[¬A]` Finiteness of `ES`. ES exists iff `E[L^−] < ∞` (`[DERIVED, C7]`); this is a **tested precondition**, not an assumption. If it fails (tail index `ξ ≥ 1`), the ES-based conclusion is reported as unsubstantiated.
12. `[¬A]` Elicitability of ES alone. *Literature-recalled, source-unverified this session*: ES is not elicitable on its own; `(VaR, ES)` is jointly elicitable. Consequence adopted regardless of source status: standalone ES forecast evaluation may not use a "single-number consistent scoring rule"; it must use joint `(VaR, ES)` scoring or a coverage/exceedance-based ES backtest whose size is verified by simulation.
13. `[¬A]` That a stable tail shape exists, or that any particular `(α, h, estimator, regime definition)` is the right one.
14. `[¬A]` That an ES advantage, if found, persists out-of-time, survives costs, or is robust to estimator choice.
15. `[¬A]` Any dataset, strategy, instrument, or market. None is in scope; none is hypothesized.

**Conventions (definitions, not assumptions)**
16. Sign convention `L = −r`; loss-positive report orientation.
17. `α` = confidence level; `p = 1−α` = tail probability.
18. `ES` = Acerbi–Tasche/Rockafellar–Uryasev integral form as the estimand.

---

## unknowns

1. `[UNKNOWN]` **Dataset identity, provenance, frequency, span, and hash** — `dataset-primary: NOT_PROVIDED`. No empirical claim of any kind can be made; every empirical criterion below is *untestable in this run's current inputs*.
2. `[UNKNOWN]` **The strategy**: instrument set (single vs multi-asset), holding period, turnover, and return-generating process. The task names "a trading strategy" but no strategy is specified.
3. `[UNKNOWN]` **The intended decision use of ES**: reporting/disclosure (D1), limits/sizing (D2), or ranking/selection (D3). The admissible evaluation machinery differs per use (D1 requires joint scoring because ES is not elicitable alone), so this is a **material product decision**, escalated below.
4. `[UNKNOWN]` **`α` and `h`**: not declared by the packet.
5. `[UNKNOWN]` **Risk appetite / tolerance**: the loss magnitude that counts as a material decision error (needed to size the MDE and to declare a practical significance threshold).
6. `[UNKNOWN]` **Cost and turnover model**: required for Q2, not provided.
7. `[UNKNOWN]` **Tail index regime of the strategy**: whether `ξ < 1` (ES finite) or `ξ ≥ 1` (ES undefined). Not knowable without data.
8. `[UNKNOWN]` **Whether the point-in-time volatility filter and regime labels are constructible** from the available data without look-ahead.
9. `[UNKNOWN]` **Independence of QR and QV error modes** — same provider/model family (`PROJECT-INV-010`); not establishable in this runtime. Recorded as a control limitation, never as independence evidence.
10. `[UNKNOWN]` **Prior trials / experiment family** for this question in this project. No ledger exists; per `MULTIPLE_TESTING_CONTROL`, the absence of history is declared and inference is limited — a trial count is **not** invented.
11. `[UNKNOWN]` **Whether market conditions subsequent to any evaluation period behave like the evaluation period** (out-of-time generalization).

Absence of these inputs is **not** evidence that VaR or ES is or is not useful; it is an unresolvable gap requiring data provisioning (escalated to human authority; `quant-data-engineer` has budget 0 in this run).

---

## methodology

### M1. Comparison target and matched information budget

The comparison "ES vs VaR" is only meaningful against a **declared** VaR-only alternative, at a **matched information budget** (number of reported/estimated scalars), because `[DERIVED, C1b]` the VaR curve `{VaR_u : u ≥ α}` and the ES curve `{ES_u : u ≥ α}` are mutually determining: ES as a curve is equivalent to VaR as a curve. Therefore:

- `V1` single `VaR_α` (1 scalar) — a strawman; used only as the trivial reference.
- `V2` VaR curve at `m` declared levels `{α, α₂, …, α_m}` (m scalars) — an increasingly strong competitor; the level set must be declared *and* `m` matched to the number of ES parameters reported.
- `V3` **VaR + stable fat-tailed shape**: `VaR_α` plus a *constant* `d` calibrated on training data (equivalently a fitted constant-shape heavy-tailed law). This is the **primary competitor**, and it is the instantiation of `H_0`. Beating `V3` is the substantive requirement.

The comparison is at **the same `α`, the same `h`, the same estimator class, and the same training/validation split** for both metrics.

### M2. The three-level test sequence (all must hold for "use both")

- **Gate Q0 (analytical prerequisite).** Verify non-redundancy by the counterexample (C1) and confirm it holds in the implemented estimator: two loss distributions with identical `VaR_α` and different `ES_α` must produce different estimates. A pipeline that fails this is not measuring ES.
- **Gate Q1 (estimable incremental information).** Test whether the tail-shape statistic `d_α` is constant (as `H_0` predicts) using:
  - **I-1 Joint-score comparison (primary).** Under a jointly consistent `(VaR, ES)` scoring rule `S(VaR, ES; L)` (Fissler–Ziegel class; *literature-recalled, formula to be source-verified and/or replaced by a simulation-calibrated procedure*), compare out-of-sample mean score of the **free** model vs the **restricted** model `ES = κ·VaR` (`κ` fitted on train only). Test the score difference with a stationary/block bootstrap using HAC-consistent inference (Diebold–Mariano-style). The restricted model *is* `H_0`. ES adds nothing beyond `V3` iff the restricted model is not significantly worse.
  - **I-2 `ξ` (tail-index) stability.** Estimate `ξ` on rolling/expanding windows with a pre-declared Hill/POT rule; test constancy of `ξ` over time and across regimes (HAC / bootstrap; and a change-point scan with pre-registered family size). `ξ` instability is the mechanism by which ES escapes the location–scale null.
  - **I-3 `d_α` vs `c(α)` and vs `V3`.** Report `d̂_α` with bootstrap CI; test `H_0: d_α = d_{V3}` (not `= c(α)` — `c(α)` is only a reporting reference).
  - **I-4 Incremental-severity regression (direct, interpretable).** Regress next-period breach severity on pre-declared, point-in-time predictors:
    - Model A: `E[(L_{t+1} − VaR_{t+1})⁺ | F_t] = g(VaR_{t+1}, σ̂_t)`
    - Model B: `… = g(VaR_{t+1}, ES_{t+1}, σ̂_t)`
    Test out-of-sample incremental explanatory/predictive value of `ES_{t+1}`. Family size pre-registered; HC/HAC errors.
  - **I-5 Coverage / independence for VaR itself.** Kupiec POF, Christoffersen independence/conditional coverage, Engle–Manganelli DQ on `VaR_t`. If `VaR_t` is itself misspecified, the ES-vs-VaR comparison is confounded and must be re-run with a corrected `VaR_t` before any ES conclusion is drawn.
- **Gate Q2 (decision value).** Instantiate one of D1/D2/D3 (human decision, below) with a declared loss function, and compare rules on the holdout, net of costs:
  - `D1` reporting accuracy: expected absolute/stated tail-loss misstatement under a joint score, restricted vs free.
  - `D2` limits/sizing: fixed risk budget `C`; under a VaR budget the expected breach loss is `C·d_α` (`[DERIVED, C9]`); compare realized tail losses, drawdown, turnover and cost between VaR-budgeted and ES-budgeted rules.
  - `D3` ranking/selection: does the ES-based ranking of strategies/books differ materially from the VaR-based ranking, and does the ES ranking better predict subsequent realized tail loss (out-of-time)? Also test the derived coherence advantage (`C4`): where VaR violates subadditivity, VaR-only ranking can *penalize* diversification and invert a risk ordering; quantify how often and how materially.

### M3. Fat-tail treatment without normality

- Never use `c(α)` as an estimator or as a distribution. Use heavy-tailed families as the neutral working assumption: GPD/Pareto above a declared threshold, Student-t/skew-t as a parametric comparator, and historical/empirical tails as the non-parametric floor.
- Report `d_α` and `ξ` — the two quantities in which all non-Gaussian tail information is concentrated. Under Pareto, `d = 1/(1−ξ)` is **α-independent**; therefore "constant `d` across `α`" is *not* evidence against heavy tails, and the informative test is **constancy of `ξ` (hence `d`) across time/regimes**, not across `α`.
- Test the ES existence precondition explicitly: `ξ̂ < 1` with a CI excluding 1. If `ξ̂ ≥ 1` (or the CI covers 1), ES is not a finite estimand and the ES-based conclusion is reported as **unsubstantiated** — not as a rejection of markets, and not as support.
- Do not use `√h` scaling (`C8`); do not use Cornish–Fisher as a primary path.

### M4. Sampling and estimation-error treatment

- **Asymptotic covariance `[DERIVED, C5]`** for the loss-tail estimators at fixed `α`, `q = VaR^L_α`, density `f`, tail probability `p = 1−α`:
  ```
  Var(VaR̂)   ≈ p·α / (n f(q)²)
  Var(ÊS)    ≈ [ Var(L | L > q) + α·(ES − q)² ] / (n p)
  Cov(ÊS, VaR̂) ≈ −p·(ES − q) / (n f(q))          (negative)
  ```
  Estimated `f(q)` via declared kernel/EVT method. In the studied examples the correlation is small at `α ≥ 0.95`, but it must be computed, not assumed zero.
- **Dependence.** Stationary/block bootstrap with block length `≥ h` (or non-overlapping sampling with `n_eff = n/h`). Overlap correction is mandatory for `h > 1`.
- **Estimator disagreement is uncertainty.** Report the spread across E-hist/E-fhs/E-evt/E-t as part of the estimand's reported uncertainty; a conclusion that holds only for one estimator is not established.
- **Power must be pre-computed** (see E5/MDE): the minimum detectable relative change in `d` at the declared `(α, h, n)` must be computed *before* evaluation and compared against the magnitude that would be decision-relevant. If `MDE` exceeds the decision-relevant magnitude, the honest terminal state for that cell is **INCONCLUSIVE**, not "supported".
- **Minimum-data rule (pre-registered, `ENGINEERING_DEFAULT`).** Require `k = n·p` exceedances per reported cell (`k_min = 100` as an exemplar default, to be calibrated) and at least `N_min = 5` independent regime episodes (`N_min` exemplar). Reporting a cell below these thresholds is a refusal to report; the cell is `NOT_ESTIMABLE`, never zero and never "no effect".
- **No test without a size check.** Any recalled closed-form test (ES/quantile backtests, joint score tests, `ξ` change tests, stable-law asymptotics) must be validated by Monte Carlo **size** simulation under `H_0` with a fat-tailed, dependent generator before its p-value is used. A test whose size is unverified produced no verdict.

### M5. Regime-dependent analysis

- **Regime definition (declared, point-in-time, reproducible).** Admissible: (i) a declared volatility threshold on a point-in-time filter (`σ̂_t`), calibrated on train only; (ii) a two-state Markov-switching model using **filtered** probabilities (never smoothed); (iii) an exogenous calendar state; (iv) an endogenous conditional-quantile (CAViaR) state. Inadmissible: hindsight crisis windows, smoothed-probability labels, ex-post drawdown-defined states, labels chosen after seeing `d`.
- **Regime definitions are free parameters.** The family size counts toward multiple testing; the primary regime definition is pre-registered; alternatives are robustness only.
- **What is tested across regimes.** Under `H_0` (fat-tailed location–scale), `d_ε = ES_α(ε)/VaR_α(ε)` is regime-invariant (`[DERIVED, C6]`), including under arbitrary volatility changes. Therefore a cross-regime difference in `d_ε` that survives estimation error is direct evidence that ES carries shape information no volatility-scaled VaR can carry. Test: (a) equality of `d_ε` across regimes with bootstrap CIs from the joint covariance; (b) equality of `ξ` across regimes; (c) a pre-registered change-point scan on `ξ`.
- **Per-regime estimation reality `[DERIVED, C10]`.** Within-regime ES at deep `α` is usually not estimable. Mitigation: pooled-threshold EVT with a regime indicator on the GPD scale parameter, lower `α` for the within-regime comparison, longer history, or intraday sampling — each declared and power-checked.
- **Regime-dependent `VaR_t` misspecification first (I-5).** Because regime-dependent volatility is exactly where a static VaR fails, part of any observed "ES adds value" may be a mis-specified-`VaR` artifact. Fix `VaR_t` first; only then attribute residual value to ES.

### M6. Multiple testing, stability, holdout

- **Pre-registered finite family:** `{α levels} × {h} × {estimators} × {regime definitions} × {benchmarks V1/V2/V3} × {decision uses}`. The primary cell is singular and pre-declared; everything else is secondary. `experiment_family_id`, `hypotheses_attempted`, `parameter_sets_attempted`, `failed_experiments`, `selected_experiment`, `selection_rule` are recorded.
- **Correction:** Holm step-down (or Romano–Wolf for the score comparisons) at a declared family-wise level; report both raw and adjusted p-values. Threshold choices (`u`, Hill `k`, regime cut, window lengths) must not be tuned on the evaluation data — tuning them consumes family budget.
- **Stability:** sign and magnitude of `d̂_α − 1` and `ξ̂` stable across non-overlapping eras, across declared `α` band, across estimators, and under leave-one-regime-out. Instability beyond sampling error is itself a refutation (R4), not a nuisance.
- **Holdout discipline:** all filters, thresholds, regime cuts, benchmark `κ`, and `(μ,σ)` calibrations fitted on `research`/`train`; a single held-back `out-of-time` period evaluated once. Repeated consultation destroys the test's integrity.
- **No-peeking log:** every evaluation run and its data access is logged; a re-run on the same data is recorded as a new trial, not a correction.
- **Stopping rule (bounded execution).** One pre-declared evaluation pass; no result-shopping; no re-definition of the objective after seeing a score. Terminal states per cell: `SUPPORTED` / `WEAKENED` / `REJECTED` / `NOT_ESTIMABLE` / `INCONCLUSIVE`.

### M7. Supporting evidence criteria (SUPPORT)

All of the following, jointly, are required to conclude "use both VaR and ES":

- **SUPPORT-S1 `[derivable from C1]`** Non-redundancy is demonstrated in the implementation: two loss distributions with identical `VaR_α` and different `ES_α` yield different estimates; the pipeline's `ES` responds to tail depth, not to the quantile alone.
- **SUPPORT-S2** `d̂_α > c(α)` (or equivalently `ξ̂ > 0` with CI excluding 0) at the primary cell: measurable non-Gaussian tail-shape excess exists.
- **SUPPORT-S3** The **fat-tailed location–scale null `H_0` is rejected out-of-sample**: `d_ε` and/or `ξ` are not time-invariant, with the rejection surviving bootstrap inference and Holm correction.
- **SUPPORT-S4** **Incremental out-of-sample information**: the free model beats the `V3`-restricted model (`ES = κ·VaR`) in the joint `(VaR, ES)` score (I-1), *and* `ES` has incremental predictive value for breach severity beyond `VaR` and `σ̂` (I-4), with CIs excluding zero.
- **SUPPORT-S5** **Decision value (Q2)** on the pre-declared holdout: the ES-informed rule reduces the declared realized loss (tail-loss magnitude under a fixed budget, or tail-loss forecast error under D1/D3) relative to the declared VaR-only rule, net of costs and turnover, with a block-bootstrap CI excluding zero, and with `MDE` small enough that the observed effect is not within the design's noise floor.
- **SUPPORT-S6** **Robustness:** S2–S5 hold for at least two structurally different estimators, across ≥ 3 non-overlapping eras, and within the declared `α` band; and they survive selection of the primary regime definition.
- **SUPPORT-S7** **Coherence/diversification materiality (conditional, multi-asset only):** a demonstrated case where the VaR-only rule violates subadditivity (`C4`) and the violation changes a declared decision — i.e. VaR-only reporting penalizes a diversification that ES correctly credits.
- **SUPPORT-S8** **Existence precondition satisfied:** `ξ̂ < 1` with CI excluding 1, so ES is a finite estimand and the incremental information is about a well-defined quantity.

### M8. Refuting / weakening evidence criteria (REFUTE)

Any of the following weakens (W) or rejects (R) the conclusion that ES is useful beyond VaR. Note: **absence of evidence for ES is not evidence against ES** — an untestable cell is `INCONCLUSIVE`, never `REJECTED`.

- **REFUTE-R1 (primary rejection).** `H_0` (fat-tailed location–scale, fixed shape) is not rejected: `d_ε` and `ξ` statistically indistinguishable from constants. Then ES is, up to a constant, a deterministic rescaling of VaR and adds no time-varying information. This holds *even with arbitrarily fat tails*.
- **REFUTE-R2 (noise, not information).** The ES increment exists but its estimation error swamps it: `SE(ln d)` exceeds the pre-declared tolerance, or the CI of `d̂_α` covers both `d = 1` and the `V3` benchmark, or `MDE` exceeds the decision-relevant magnitude at the declared `(α, h, n)`. ES then adds noise; the correct action is to report `INCONCLUSIVE` and increase `α`-vs-`h` feasibility, not to claim usefulness.
- **REFUTE-R3 (negative decision value).** The ES-informed rule yields *higher* realized tail loss, or higher net cost/turnover, or worse joint score, than the declared VaR-only rule out-of-sample.
- **REFUTE-R4 (instability).** `d̂_α − 1` or `ξ̂` flips sign or changes magnitude beyond sampling error across non-overlapping eras, or is driven by a single episode/observation (leave-one-out fragility) → not decision-usable.
- **REFUTE-R5 (redundancy to a stronger VaR alternative).** The ES advantage disappears when the competitor is `V2` (a multi-level VaR curve at matched budget) or when `ES` is replaced by `κ·VaR` with `κ` fitted out-of-sample; or the apparent advantage is entirely explained by the sample's non-normality rather than by time-varying shape.
- **REFUTE-R6 (undefined estimand).** `ξ̂ ≥ 1` or its CI covers 1 → ES is infinite/unstable while VaR remains finite. The premise "ES provides bounded tail information" fails; report unsubstantiated.
- **REFUTE-R7 (insufficient data).** Fewer than the pre-declared minimum exceedances or regime episodes in the primary cell, or a holdout too short to contain the relevant tail events → `NOT_ESTIMABLE` / `INCONCLUSIVE`. "We could not detect it" ≠ "it is absent".
- **REFUTE-R8 (integrity failure).** Any look-ahead, non-point-in-time regime labelling, smoothed-state usage, train/test leakage, reused holdout, unreported trials, or post-hoc threshold/objective change → the affected evidence is **invalidated** and cannot be counted as support (or as refutation).
- **REFUTE-R9 (confounded `VaR_t`).** If I-5 shows `VaR_t` is misspecified and the ES "advantage" vanishes after correcting `VaR_t`, the advantage was a VaR-misspecification artifact, not an ES contribution.
- **REFUTE-R10 (synthetic-only evidence).** Support resting only on simulation is not support about markets. Synthetic results validate the *procedure* (size/power), never the *conclusion*.

---

## checks_performed

All checks are **analytical/hand-derived**. Per `DETERMINISTIC_MATH`, no computation was executed in this session (no numerical runtime used; generative arithmetic is not execution evidence), so every decimal below is labelled `DERIVED — hand-arithmetic; machine execution NOT performed; requires independent recomputation by `quant-validator``. Sources for the literature-flavoured claims were not retrievable in this session (documentation and open-web capabilities reported blocked); those claims are marked `LIT-UNVERIFIED`.

**C1 — VaR does NOT determine ES (non-redundancy). `[DERIVED]`**
Let `α = 0.95`, loss `L`. Distribution A: `L = 0` w.p. `0.95`, `L = 1` w.p. `0.05`. Distribution B: `L = 0` w.p. `0.95`, `L = 10` w.p. `0.05`.
`F_A(0) = F_B(0) = 0.95`, so `VaR^L_{0.95}` (integral/RV form) `= 0` for both. `ES^L_A = (1/0.05)(0.05·1) = 1`; `ES^L_B = (1/0.05)(0.05·10) = 10`. Identical VaR, ES differing by 10×. **Conclusion:** `ES_α` does not factor through `VaR_α`; non-redundancy is mathematically real. **C1b `[DERIVED]`:** by the legibility of the ES curve, `{ES_u}_{u≥α}` and `{VaR_u}_{u≥α}` determine each other a.e. (differentiate/integrate), so a "VaR-only" alternative reporting the *entire* VaR curve is informationally equivalent to ES; hence the comparison must declare the number of VaR levels (matched information budget).

**C2 — Exact ES–VaR identity. `[DERIVED]`**
`p^{-1}E[(L−q)⁺] = p^{-1}∫_q^∞ (ℓ−q)dF(ℓ) = p^{-1}∫_α^1 (VaR_u − q)du = ES_α − q`, with `q = VaR_α`. Hence `ES_α = VaR_α + p^{-1}E[(L−VaR_α)⁺] = VaR_α + E[L−VaR_α | L > VaR_α]`.
**Consequence (used later):** `d_α − 1 = E[L−VaR_α | L>VaR_α] / VaR_α` is exactly the relative mean exceedance beyond the VaR threshold.

**C3 — RV vs conditional-expectation form under atoms. `[DERIVED]`**
Two i.i.d. bonds, default prob `0.04` each, `L=1` per bond on default, equal split. Portfolio: `L=0` w.p. `0.9216`, `L=0.5` w.p. `0.0768`, `L=1` w.p. `0.0016`. At `α=0.95`, `F(0)=0.9216<0.95`, `F(0.5)=0.9984≥0.95` ⇒ `VaR^L_{0.95}=0.5`.
- Integral/RV form: `∫_{0.95}^1 VaR_u du = 0.5·(0.9984−0.95) + 1·(1−0.9984) = 0.0242+0.0016 = 0.0258` ⇒ `ES = 0.0258/0.05 = 0.516`.
- Conditional-expectation form: `E[L|L≥0.5] = (0.5·0.0768 + 1·0.0016)/0.0784 = 0.04/0.0784 = 0.5102`.
Discrepancy confirms the atom issue. Single bond at `q=0` is worse: RV gives `ES = 0.8`, whereas `E[L|L≥0] = E[L] = 0.04` — a 20× error. **Mandatory: the estimand is the RV/Acerbi–Tasche form; mass at the empirical VaR must be tested.**

**C4 — Coherence: VaR is not subadditive, ES is. `[DERIVED]`**
Same two bonds. `VaR_{0.95}(bond_a) = VaR_{0.95}(bond_b) = 0`; `VaR_{0.95}(portfolio) = 0.5`. Subadditivity fails: `0.5 > 0 + 0`. ES: `ES(bond) = 0.04·1/0.05 = 0.8`; `ES(portfolio) = 0.516 ≤ 0.8 + 0.8 = 1.6`. **Consequence for the decision layer:** a VaR-only ranking can *penalize* diversification (a concentrated pair of single-name exposures "looks" riskless while the diversified portfolio looks risky), whereas ES ranks it correctly. This is a concrete, checkable decision-relevant difference, and it is VaR-specific (not a normal-tail artifact).

**C5 — Asymptotic variance/covariance of the ES and VaR estimators. `[DERIVED]`**
Functional `T(F) = p^{-1}∫_α^1 F^{-1}(u)du`, `q = F^{-1}(α)`, `g = ∫_q^∞ ℓ dF = p·ES`. Influence-function computation: differentiate `g((1−ε)F + εδ_z)` including the boundary movement `q'(ε) = −(1{z>q} − p)/f(q)`:
`IF_g(z) = z·1{z>q} + q·1{z≤q} − g − qp = (z−q)1{z>q} − p(ES − q)`.
`IF_T = [(z−q)1{z>q} − p(ES−q)]/p`, so `E[IF_T] = 0` and
`σ²_ES = E[IF_T²] = E[(L−q)²1{L>q}]/p² − (ES−q)² = [Var(L|L>q) + α(ES−q)²]/p`.
`IF_VaR(z) = (p − 1{z>q})/f(q)` ⇒ `σ²_VaR = αp/f(q)²`.
`Cov(IF_T, IF_VaR) = −p(ES−q)/f(q) < 0`.
**Note the structure:** `σ²_ES ∝ 1/p` explicitly and grows with the conditional tail variance `Var(L|L>q)` — the estimator cost of ES is governed by *tail dispersion*, which fat tails inflate.
*(Consistency note: an intermediate quantity in this derivation — `E[L²1{L>q}]` for `t_3` — was cross-checked two ways, by direct trigonometric substitution and by conditioning on the `χ²` mixing variable; the two agreed to within ~4%, the residual being quadrature error. The recalled closed form relating `E[L²1{L>q}]` to a `t_{ν−2}` probability was found **incorrect** on this check and is discarded.)*

**C6 — ES closed form for Student-t (derived, not recalled). `[DERIVED]`**
`X ~ t_ν`, density `f_ν(x) = c_ν(1+x²/ν)^{−(ν+1)/2}`. For `q = q_α > 0`, with `u = 1+x²/ν`:
`∫_q^∞ x f_ν dx = c_ν(ν/(ν−1))·u_q^{−(ν−1)/2}` and `f_ν(q) = c_ν u_q^{−(ν+1)/2}`, giving `u_q^{−(ν−1)/2} = u_q f_ν(q)/c_ν` and therefore
```
ES_α(t_ν) = f_ν(q_α) · (ν + q_α²) / [ (ν − 1) p ]        (ν > 1)
```
**Location–scale invariance `[DERIVED]`:** if `L = σ ε` with `σ > 0` and `F_ε` fixed, then `VaR_α(L) = σVaR_α(ε)`, `ES_α(L) = σES_α(ε)`, hence `d` is invariant. If `L = μ + σε` with `μ ≠ 0`, `d = (μ + σES_ε)/(μ + σVaR_ε)` is **not** invariant — so shape analysis must use standardized residuals (or include `μ` in the null).

**C7 — ES existence condition. `[DERIVED]`**
`ES_α = p^{-1}∫_α^1 VaR_u du`. If `E[L^−] = ∞` then `∫_0^1 VaR_u du` diverges and `ES_α = ∞` for every `α ∈ (0,1)`. `VaR_α ∈ ℝ` whenever the quantile exists. **Conclusion: ES requires a strictly stronger moment condition than VaR (finite first moment; in the regular-variation case `ξ < 1`). This is a real *cost* of ES's extra information and must be tested before ES is used.**

**C8 — `√h` scaling is invalid under fat tails. `[DERIVED]`**
`√h` aggregation follows from i.i.d. + finite variance + CLT. For i.i.d. `t_ν` with `ν < 2` the variance is infinite and the `h`-period sum converges to a stable law with index `ν`, giving scaling `h^{1/ν} ≠ h^{1/2}`. **Consequence:** horizon semantics must be *estimated*, not scaled; `h` must be declared and computed directly at each value.

**C9 — Decision-relevant meaning of `d`. `[DERIVED]`**
Under a VaR **budget**: choose exposure `w` so that `w·VaR_α = C`. Then the expected loss conditional on breach is `w·ES_α = C·(ES_α/VaR_α) = C·d_α`, so the expected breach loss exceeds the budget by the factor `d_α − 1`. By `C2`, `d_α − 1 = E[L−VaR_α|L>VaR_α]/VaR_α`. **This is the economic reading of the entire research question:** `d_α − 1` is the multiplicative understatement of expected tail loss by VaR-only budgeting, and it is *irreducible from VaR alone*.

**C10 — Tail-count arithmetic. `[DERIVED]`**
`k = n·p` expected exceedances. With n = 10,000 daily observations (≈ 39.7 years at 252 days/year): `k = 100` at `α = 0.99`, `k = 500` at `α = 0.95`. If 15% of days are stress days (`n_stress = 1512`), the stress-regime draw at `α=0.99` is `1512 × 0.01 ≈ 15` exceedances — far below any minimum. **Regime-conditional ES at α=0.99 daily is not non-parametrically estimable; EVT pooling, a lower α, a longer/intraday history, or an explicit `NOT_ESTIMABLE` verdict is required.**

**C11 — Power / minimum detectable effect for `d`. `[DERIVED]`**
`Var(ln d̂) ≈ σ²_ES/ES² + σ²_VaR/VaR² − 2Cov/(ES·VaR)`; `MDE(ln d) = (z_{0.975} + z_{0.80})·SE(ln d) = 2.8016·SE` (5% two-sided, 80% power), `n = 10⁴`. Values in `expected_numerical_behavior` E5. This is the check that converts "we tested" into "the test could have detected the effect".

**C12 — Boundary/edge-case enumeration. `[DERIVED]`**
(a) `VaR^L_α ≤ 0` (positive-drift strategy) makes `d` undefined → restrict the reporting `α` range or use the shifted-loss convention. (b) Atoms at the VaR level → RV form mandatory (`C3`). (c) `ES = VaR` iff the tail beyond `VaR_α` has probability `p` concentrated exactly at `VaR_α` → `d = 1`, the minimum; this can occur with capped/limited-liability payoffs and must not be read as "no risk". (d) `p·n < 1` ⇒ `ÊS` undefined under the order-statistic estimator. (e) Ties in order statistics. (f) Missing data inside an `h`-window. (g) `ξ ≥ 1` (`C7`).

---

## expected_numerical_behavior

All values `DERIVED — hand-arithmetic; NOT machine-executed; MUST be independently recomputed before downstream use`. Student-t rows are on the **raw** `t_ν` scale (variance `ν/(ν−2)`), so absolute values are not comparable across laws; `d` **is** comparable because it is invariant to positive scale when the loss mean is zero (`C6`).

**E1 — VaR, ES and `d_α` by tail law.** `[DERIVED, hand-computed]`

| law | `VaR^L_{0.95}` | `ES^L_{0.95}` | `d_{0.95}` | `VaR^L_{0.99}` | `ES^L_{0.99}` | `d_{0.99}` |
| --- | --- | --- | --- | --- | --- | --- |
| `N(0,1)` | 1.6449 | 2.0627 | **1.2541** | 2.3263 | 2.6651 | **1.1457** |
| `t_5` | 2.0150 | 2.8903 | **1.4343** | 3.3649 | 4.4506 | **1.3226** |
| `t_3` | 2.3534 | 3.8741 | **1.6462** | 4.5407 | 7.0013 | **1.5419** |
| Pareto, `ξ=0.25` | — | — | **1.3333** | — | — | **1.3333** |
| Pareto, `ξ=0.50` | — | — | **2.0000** | — | — | **2.0000** |
| Pareto, `ξ=0.75` | — | — | **4.0000** | — | — | **4.0000** |

Gaussian benchmark constants: `c(0.95)=1.2541`, `c(0.975)=1.1927`, `c(0.99)=1.1457`. Order-of-magnitude reading: the incremental information ES carries **is** `d − c(α)`; it is zero under normality and grows with tail index. Note that Pareto `d` is `α`-independent while Gaussian `d` is not, so the *pattern of `d` across `α`* is itself diagnostic of the tail family.

**E2 — Confidence-level bridge.** `[DERIVED]` `ES_{0.975}(N) = 2.3376` vs `VaR_{0.99}(N) = 2.3263` → ratio `1.0049`. An ES@97.5% vs VaR@99% pairing is near like-for-like *under normality only*; under `t_3` it is not (`ES_{0.975}(t_3)` ≈ 5.5 vs `VaR_{0.99}(t_3) = 4.54`). Any `α`-bridge must be re-derived from the estimated shape, never assumed.

**E3 — `ES − VaR` and the relative understatement `d − 1`.** `[DERIVED]` At `α=0.99`, `N`: `d−1 = 0.1457`; `t_5`: `0.3226`; `t_3`: `0.5419`; `ξ=0.5`: `1.0000`. Interpreted via `C9`: a VaR-budgeted position whose threshold is hit has an expected breach loss `15%` above the budget under Gaussian-like tails, `32%` under `t_5`, `54%` under `t_3`, and `100%` under `ξ=0.5`.

**E4 — Estimation error and feasibility.** `[DERIVED]` `α=0.99`, `n=10⁴`:

| law | exceedances `k` | `SD(VaR̂)/VaR` | `SD(ÊS)/ES` | `SE(ln d̂)` | `MDE(ln d)` | Gaussian-excess `d/c(α) − 1` | margin (`excess/MDE`) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `N(0,1)` | 100 | 1.60% | 1.72% | 2.35% | 6.6% | 0% (by construction) | — (size check: must not reject ≈5%) |
| `t_3` | 100 | 3.70% | 6.96% | **7.88%** | **22.1%** | **34.6%** | 1.57× |
| `t_3` @ `α=0.95` | 500 | 2.04% | 3.35% | **3.93%** | **11.0%** | **31.3%** | 2.85× |

Order-of-magnitude conclusions: (i) fat tails inflate ES's relative estimation error ~4× versus ~2.3× for VaR; (ii) at `α=0.99` daily with 40 years of data, only `d`-shifts ≳22% are detectable, giving a thin margin against the `t_3` signal; (iii) moving the primary comparison to `α=0.95` improves the margin to ~2.9× and is therefore the recommended primary cell pending a declared decision-relevance target. **These are feasibility facts the design must live with, not arguments for a preferred answer.**

**E5 — Atom subtlety (worked).** `[DERIVED]` Two-bond portfolio: correct `ES = 0.516` vs the conditional-expectation form `0.5102`; single bond: `0.8` vs `0.04`.

**E6 — Subadditivity (worked).** `[DERIVED]` `VaR: 0.5 > 0 + 0` (violation); `ES: 0.516 ≤ 1.6` (satisfied).

**E7 — Decision illustration.** `[DERIVED]` Budget `C = 0.02` of notional. VaR-budgeted expected breach loss: Gaussian-like `0.0229`; `t_5` `0.0265`; `t_3` `0.0308`; `ξ=0.5` `0.0400`. The differences are the whole economic case for reporting both metrics — and they are *only* as large as the estimated `d` allows, which is why E4 is binding.

**E8 — Sanity oracles (must hold exactly for any estimator).** `[DERIVED]` `ES_α ≥ VaR_α` (equality iff the beyond-`VaR` mass is concentrated at `VaR_α`); `ES_α` non-decreasing in `α` since `dES_α/dα = (ES_α − VaR_α)/p ≥ 0`; `ES^L_α = VaR^L_α + p^{-1}E[(L−VaR^L_α)^+]`; `d = 1/(1−ξ)` under Pareto; `d` invariant to positive scale when `μ=0`.

---

## required_tests

What an independent validator must **execute** to falsify the claims above. Each is a fully specified, executable check; none is satisfied by reading this document.

| ID | Test | Target claim | Falsifies if |
| --- | --- | --- | --- |
| `T1` | Construct the two-point counterexample (C1) and the atom example (C3) and check numeric output of the implemented estimand against `ES=1` vs `ES=10`, and `ES=0.516` (not `0.5102`) | Non-redundancy (C1); RV-form mandate (C3) | Output matches the quantile alone, or matches the conditional-expectation form under atoms |
| `T2` | Numerically integrate `p^{-1}∫_α^1 VaR_u du` and `min_c{c + p^{-1}E[(L−c)^+]}` on a large sample from `t_3` and from the two-point law; confirm agreement to ≤ 1e-6 and equality with `f_ν(q)(ν+q²)/((ν−1)p)` | C2, C3, C6 | Any disagreement beyond tolerance |
| `T3` | Recompute the E1 table independently (two methods: closed form and numerical integration/quantile average) | E1 values | Any entry deviating in the 4th significant digit |
| `T4` | Monte Carlo: simulate `t_3`, `n=10⁴`, `R ≥ 10⁴` replications; compare empirical `SD(ÊS)`, `SD(VaR̂)`, `Corr` to `C5` | C5 asymptotic formulas, including the negative covariance | Empirical/analytic mismatch beyond Monte Carlo error |
| `T5` | Simulate `L_t = μ_t + σ_t ε_t` with fixed `ε` law (including `t_3`) and strong volatility clustering; run the `H_0` test at nominal 5%; verify empirical rejection ≈ 5% (size), and that `d̂_ε` is flat across volatility regimes | C6 location–scale invariance; validity of the primary null test | Size materially above nominal (design invalid), or `d̂_ε` trending with `σ_t` under `H_0` |
| `T6` | Simulate an alternative with genuinely time-varying shape (mixing `t_3` and normal residuals; a regime-switching tail index); reproduce the E4 MDE table and its power; verify `margin` accounting | C11 power claims, E4 | Observed power materially below the claimed MDE |
| `T7` | Verify `ξ̂ < 1` handling: simulate `ξ = 1.2`; confirm the pipeline returns "ES unsubstantiated" rather than an ES number presented as usable | C7, REFUTE-R6 | A finite ES reported with a conclusion attached |
| `T8` | Verify the `√h` prohibition: simulate i.i.d. `t_2`; compare the empirical `h`-period ES scaling against both `h^{1/2}` and `h^{1/ν}`; confirm the estimator does not silently apply `√h` | C8 | The implementation rescales across horizons |
| `T9` | **Normality audit.** Line-by-line/grep-level inspection of every estimator, test and bound for a Gaussian assumption; confirm the only use of `c(α)` is as a reporting reference; confirm the `H_0` generator in T5 is fat-tailed | Requirement "no step assumes normal returns" | Any estimator, test, or variance formula that presumes normality |
| `T10` | **Point-in-time audit.** Inject future information into the filter/threshold/regime-labelling path and confirm the causal invariant rejects it; verify regime labels reproduce exactly under replay as-of `t` | `POINT_IN_TIME_ONLY`; REFUTE-R8 | Any injected future value changes a label or estimate at `t` |
| `T11` | **Test-size validation.** For every recalled/inherited test statistic (joint `(VaR,ES)` score test, `ξ` change test, ES backtest), run a size simulation under a fat-tailed, serially dependent generator; require empirical size within tolerance before accepting its p-values | "No test without a size check" | A test used with unvalidated size, or size materially off nominal |
| `T12` | **Multiple-testing audit.** Verify the family is finite, pre-registered, and that all trials including failures are logged; recompute Holm-adjusted p-values from the raw log | `MULTIPLE_TESTING_CONTROL`; REFUTE-R8 | Family undercounted, or corrected values unreproducible from the log |
| `T13` | **Holdout integrity.** Verify all tuning constants (`κ`, `u`, Hill `k`, regime cut, filter parameters) were fitted on train only and that the holdout was accessed once | REFUTE-R8 | Any holdout-derived constant |
| `T14` | **Exceedance-count audit.** Recompute `k = n·p` per reported cell; verify cells below the pre-declared minimum are reported `NOT_ESTIMABLE`, never `0`, never "no effect" | REFUTE-R7; absence-of-evidence rule | A sub-threshold cell reported as evidence |
| `T15` | **Reproducibility.** Seeded simulation and fixed estimator code reproduce E1/E4 within declared tolerance on re-execution | `VERSION_EVERYTHING` | Non-reproducible outputs |
| `T16` | **Analytical sanity oracles.** Verify `ES ≥ VaR`, monotonicity in `α` (`C12`/E8), `d = 1/(1−ξ)` under Pareto, scale invariance with `μ=0` | E8 | Any violation |

`T3`, `T4`, `T5`, `T6` re-check **every number in this document**. Any claim here failing them must be withdrawn and corrected, and this document must be revised under change control before downstream use.

---

## evidence

**Explicit statement of what is and is not evidence here.**

- **No data was inspected. No code was run. No market fact is asserted.** Consequently this result contains **no empirical evidence** about VaR, ES, or any strategy, and **claims nothing empirical**. All empirical criteria (SUPPORT-S2…S8, REFUTE-R1…R7) are **untested** in this run. `[UNKNOWN]`
- **Analytical derivations (the only positive content).** `[DERIVED]` C1, C1b, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, E1–E8. These are hand derivations of *mathematical* properties of the definitions. They are checkable by `T1–T4, T7–T9, T16`, and they are **not** claims about markets. Their decimal values are **hand arithmetic, not executed** (`DETERMINISTIC_MATH` failure behaviour: formulation may be delivered, but the numbers must not be used as validated results until recomputed).
- **Definitional/conventional content.** `[DERIVED, definitional]` The sign convention (`L = −r`), `α` = confidence level, `h` in trading days, the RV/Acerbi–Tasche estimand, the units. These are choices made explicit, not findings.
- **Assumptions.** `[A]` items 1–6 in `assumptions`; all consequential ones (data availability, point-in-time discipline, existence of a holdout, presence of a cost model, a pre-declared decision rule) are **unverified** in this run.
- **Literature-recalled claims, NOT source-verified in this session.** `[LIT-UNVERIFIED]` (i) ES is not elicitable alone while `(VaR, ES)` is jointly elicitable; (ii) a jointly consistent `(VaR, ES)` scoring family exists (Fissler–Ziegel class); (iii) canonical ES backtests of the coverage/conditional-expectation type exist (Acerbi–Székely family); (iv) the GPD/POT `VaR`/`ES` formulas; (v) the Hill estimator and its bias–variance threshold problem; (vi) the `H_0`-relevant literature on the non-elicitability/coherence debate. **Source status: I had no working retrieval capability this session (`documentation` and `open-web` capabilities reported blocked; no web/fetch tools in this context), so these are recorded as `SUPPORTED by domain knowledge but UNVERIFIED`, and every one of them must be independently source-verified and, where possible, replaced with a simulation-calibrated procedure (`T11`) before being used as a critical premise. They are not presented as verified external facts.**
- **Not evidence:** this document's prose, its internal consistency, the fact that it was produced by a specialist, and any agreement between this document and a future validator from the same model family. Per `PROJECT-INV-010`, sharing provider/model family is a **possible dependency**, never independence evidence.
- **Absence-of-evidence handling.** No failure to detect an effect is reported as evidence of absence. Cells without sufficient data are `NOT_ESTIMABLE`; criteria that cannot be tested are `UNKNOWN`.
- **Synthetic/simulation results.** Any future simulation (T4–T6, T11) validates the *procedure* only. Per the `ROLE.md` hard rule, synthetic or in-sample results will never be reported as proof about markets.
- **Artifacts produced by this execution:** this structured result only (returned, not written — no write tool exists in this context; the orchestrator persists it verbatim). The packet's second required output, `authoritative-inputs/HANDOFF-QR-to-QV.yaml`, is a separate orchestrator-persisted artifact per `.governance/ROUTING.yaml → handoff_contract`; the handoff-relevant content is carried by `authoritative_inputs`, `assumptions`, `unknowns`, `required_tests`, `limitations`, `unresolved_risks`, `handoff_status` and `required_human_decisions` in this result. No file under `/home/datawithjose/Documents/GENTLE-QUANT-ECOSYSTEM` or the certification workspace was modified.

---

## limitations

1. **No empirical content.** With no dataset in scope, nothing here is validated against reality; the packet explicitly authorizes this (methodology-only), but it means the deliverable cannot answer Q1 or Q2 for any actual strategy.
2. **Level-1 (informational) vs level-2 (decision) irreducible gap.** Non-redundancy (`C1`) is near-tautological and is **not** evidence that ES is worth using. The methodology deliberately refuses to treat Q0 as support.
3. **`d` is not a sufficient statistic for risk.** `d` captures tail *shape* only at the declared `(α, h)`; it is silent about the loss magnitude scale, the body of the distribution, drawdown path, liquidity, and capacity. A "use both" conclusion concerns tail-shape reporting, not the whole risk model.
4. **Non-elicitability of ES** *(LIT-UNVERIFIED)* constrains evaluation: standalone ES evaluation is not straightforward and requires joint scoring or size-validated backtests. This is a permanent methodological tax on ES, not an implementation gap.
5. **Estimation cost is binding.** `C10`/`C11`/E4: deep-`α`, short-`h`, regime-conditional ES is frequently unestimable. The design may be forced to `α = 0.95`-class levels, which changes what "beyond VaR" can mean and reduces the practical bite of the conclusion.
6. **ES existence is conditional.** If the strategy's loss tail has `ξ ≥ 1`, the ES conclusion is unsubstantiated (`C7`) — and this is a property of the strategy, not of the methodology.
7. **Free-parameter surface.** `α`, `h`, estimator, threshold `u`/`k`, regime definition, benchmark complexity `m`, decision rule and loss function each constitute a degree of freedom. No amount of pre-registration removes them; it only makes the multiplicity visible and controlled.
8. **Regime labels are choices.** Even point-in-time-compliant regime definitions are analyst-chosen constructions; conclusions may be definition-sensitive, and the design must report that sensitivity rather than select a favourable definition.
9. **Cost/turnover realism** is unaddressed in detail and is a stated dependency for Q2.
10. **Multiple-testing control is partial.** Holm/Romano–Wolf control the declared family, not the unknown family of prior implicit trials (none is recorded). Per `MULTIPLE_TESTING_CONTROL`, a trial count is not invented.
11. **Independence limitation (`PROJECT-INV-010`).** Same provider/model family for QR and QV ⇒ error-mode independence **not established**. Any apparent agreement between this document and the validator's result is not confirmation.
12. **This includes recalled literature.** Per item (v) in `evidence`, several critical premises are remembered rather than retrieved. That is a real, material limitation and is the first thing the validator should attack.
13. **Not independently validated.** By role definition, this research cannot certify itself; `READY_FOR_REVIEW` is the maximum honest handoff status.

---

## unresolved_risks

| ID | Risk | Severity | Owner / escalation |
| --- | --- | --- | --- |
| `UR-1` | No dataset ⇒ the entire empirical layer (Q1, Q2) is untestable in this run; any downstream claim of empirical support would be fabricated | HIGH | human authority (data provisioning is `quant-data_engineer`, budget 0; packet routes this to `BLOCKED` if requested) |
| `UR-2` | Strategy and decision use unspecified ⇒ the "useful beyond VaR" criterion is not yet instantiated; a different decision use could change the verdict | HIGH | human authority (D1/D2/D3 selection) |
| `UR-3` | Critical literature premises are `LIT-UNVERIFIED` in this session (elicitability, scoring families, backtests, GPD formulas) | HIGH | `quant-validator` must source-verify or replace with simulation-calibrated procedures (`T11`) |
| `UR-4` | Statistical independence of QR and QV error modes not established (`PROJECT-INV-010`, `NOT_ENFORCED`) | HIGH | human authority; record as residual risk |
| `UR-5` | Design may be underpowered at deep `α`/short `h` (`C10`, `C11`) ⇒ `INCONCLUSIVE` is a likely legitimate terminal state; pressure to convert it into a conclusion is the main epistemic hazard | HIGH | `quant-validator` + human gate; policy must accept `INCONCLUSIVE` |
| `UR-6` | Free-parameter surface (α, h, estimator, threshold, regime definition, benchmark `m`) creates selection risk even with pre-registration | MEDIUM | `quant-validator` (`T12`) |
| `UR-7` | Hand-derived numerics (E1–E8) may contain arithmetic errors — they are unexecuted | MEDIUM | `quant-validator` (`T3`, `T4`); any error must return here under change control |
| `UR-8` | `PROJECT-INV-007` is `MANUAL_GATE`: this evidence section is prose and requires human inspection to be trusted | MEDIUM | Human Gate |
| `UR-9` | Scope pressure: "research methodology only" could drift toward implementation or toward an empirical claim | HIGH | orchestrator; `PROJECT-INV-008` (ENFORCED) |

---

## handoff_status
`READY_FOR_REVIEW`

Justification: the methodology is complete, internally consistent, self-consistent on sign conventions, and contains no normality assumption in any step (packet verification checks). It is **not** `APPROVED_FOR_IMPLEMENTATION`: independent validation (`quant-validator`) is outstanding, the Human Gate is outstanding, and no implementation is authorized in `GQE-PI-CERT-M4-001` (`PROJECT-INV-008`). Not `BLOCKED`: the missing dataset was declared out of scope by the packet and `completion_gate.ready_for_execution: true`, so it does not block a methodology-only deliverable. Not `DRAFT`: the specification is complete for review.

---

## next_recommended

1. **`quant-validator` (independent, isolated context)**: execute `T1–T16`, prioritizing `T3`/`T4` (recompute every number), `T9` (normality audit), `T11` (test-size validation), and source verification of the `LIT-UNVERIFIED` premises. The validator must be given the frozen persisted artifacts with hashes (`PROJECT-INV-005`), not a regenerated version of this text.
2. **Human authority (Portfolio Manager / Head of Quant)**: decide the instantiation inputs before any empirical run — the decision use (D1/D2/D3), `α`, `h`, the declared loss function and cost/turnover model, and the minimum decision-relevant effect size (which fixes the required `MDE` and hence the required sample). Until these are fixed, no empirical test can be run without contaminating the design.
3. **Data provisioning decision (human)**: if an empirical answer is wanted, a dataset and a strategy definition must be authorized; the packet currently routes data work to `BLOCKED` with `quant-data-engineer` budget 0, so this requires explicit human authorization and a new task packet (never a silent retry or scope expansion).
4. **No implementation, no trading**: nothing here authorizes code, deployment, or orders. `trade_authorized` remains `false` (`PROJECT-INV-002`).
5. **Change control**: any modification of this specification after review (including corrections from `T3`/`T4`) must be versioned with a link to the superseded revision; this specification must not be silently changed after approval.

---

## required_human_decisions

1. **Decide the decision use of ES** — `D1` reporting/disclosure accuracy, `D2` limits/sizing, or `D3` ranking/selection. Material: it determines the admissible evaluation machinery (D1 requires joint `(VaR, ES)` scoring because ES is not elicitable alone) and the admissible loss function.
2. **Fix the comparison parameters** — confidence level `α`, horizon `h`, primary estimator, primary regime definition, and the benchmark complexity `m`. Material: these define the family and the power.
3. **Declare the decision-relevant effect size** — the `d`-shift (or breach-loss magnitude) that would actually change a risk decision. Material: it sets the required `MDE` and therefore whether the design is feasible at the available `n`, or must be declared `INCONCLUSIVE` by construction.
4. **Declare the cost/turnover model** for Q2.
5. **Authorize (or decline) dataset and strategy provision** for an empirical run, and record that this is a scope change requiring a new task packet.
6. **Accept and record the residual risk** of `PROJECT-INV-010` (QR/QV shared model family; independence not established) and accept that `INCONCLUSIVE` is an admissible terminal outcome.
7. **Confirm posture** — the run remains `RESEARCH_ONLY` with `trade_authorized = false`, and no implementation is authorized (`PROJECT-INV-008`).
8. **Approve the Human Gate disposition** — no production approval is granted or implied by this result (`PROJECT-INV-001`).