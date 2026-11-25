# Quant Agent Harness v2

A working upgrade of the supplied harness: stronger research tools, durable experiment controls, deterministic order checks, an offline demonstration, and regression tests.

**Start in research mode.** The package works without an API key. It does not include a real-market data feed, a NautilusTrader/Chartpy adapter, or a broker connection. Its demo results are explicitly synthetic.

## Run it

Requires Python 3.11+ on Linux/macOS, or WSL on Windows. No packages are needed for the demo or tests.

```bash
cd quant_harness_v2
python -m unittest discover -s tests -v
python demo.py --state demo_state.sqlite
```

The demo compares three parameter settings, runs two walk-forward folds, stresses costs at 1x/2x/3x, and performs the final holdout once. It writes a JSON report and a JSONL audit export beside its state database. Repeating the command reads the saved final result; it does not reopen research.

Optional LLM interaction:

```bash
python -m pip install anthropic
export ANTHROPIC_API_KEY='your-key'
export HARNESS_MODEL='a-model-ID-available-in-your-account'
python demo.py --agent --state agent_demo.sqlite
```

That last command calls a paid external API. No API calls or broker connections were used to validate this delivery. The provider loop was tested with a stub. The model is deliberately operator-configured instead of hardcoding an unverified model identifier.

## What became stronger

| Area | Supplied version | This version |
|---|---|---|
| Final holdout | Reusable; “once” appears only in text | Persisted commitment before execution; no retries or subsequent research |
| Dates | Lexicographic strings | UTC parsing, exclusive end, closed-bar boundaries |
| Budgets | In-memory backtest counter; holdout bypasses it | Persistent backtest attempts, tool calls and LLM calls |
| Research | One backtest at a time | Candidate comparisons, parameter neighborhoods, walk-forward selection, cost stress |
| Statistics | Accepts arbitrary engine metrics | Computes returns, CAGR, Sharpe, drawdown, duration, VaR and CVaR from net returns |
| Uncertainty | None | Reproducible block-bootstrap interval on holdout mean return |
| Provenance | None | Dataset fingerprint, engine version, canonical request hash, seed, costs |
| Prices | Agent-supplied order price | Trusted fresh account snapshot and instrument valuation |
| Exposure | Position plus proposed order | Positions, broker pending orders and local reservations; gross/leverage caps |
| Order retries | No durable protection | Persistent client IDs; ambiguous responses retain reservations and require reconciliation |
| Concurrency | Check and submit can race | Single-host file lock across check, reservation and submission |
| Audit | Unchained JSONL | Durable SQLite event chain, append-only triggers, JSONL export |
| Demo | Pseudorandom performance numbers | Deterministic synthetic prices, causal decisions and calculated net returns |

## Research workflow

1. The operator fixes the dataset, engine version, research/holdout boundaries, costs and trial budgets in `ResearchConfig`.
2. Use `backtest` for a baseline. `compare_candidates` also serves as parameter sensitivity analysis: explicitly supply nearby configurations and compare the full table, not only the winner.
3. Use `walk_forward` to select on earlier training windows and evaluate later development windows. Training selection uses highest Sharpe among candidates with the minimum completed trade count. Ties retain candidate order.
4. Use `stress_test` to rerun the engine under increased costs. It does not subtract an arbitrary penalty from a precomputed Sharpe.
5. Choose a previously researched candidate and call `final_validate`. Its dates and baseline costs are fixed by the operator; the agent cannot shorten the window or lower the costs.
6. Research is frozen BEFORE the holdout engine call. A crash or failure leaves `HOLDOUT_COMMITTED`, which still blocks reuse. Successful completion leaves `FINALIZED`; `status` returns its saved report.

All actual backtest attempts count, including failed runs, training candidates, validation folds, stress scenarios and final validation. Leave one attempt available for final validation. Batch methods preflight the whole requested batch before starting. A mid-batch failure keeps already consumed attempts and recorded results.

Persisted identity includes configuration, strategy registry, execution mode, account and limits. It cannot silently change on restart. Use one authoritative database per experiment/account deployment. Creating a different database or editing the database is an operator capability, not a legitimate way to obtain a fresh holdout on already-seen data.

Development walk-forward results are visible to the agent and may influence later experiments. They are therefore development evidence, not an untouched final evaluation. The trial count is transparent; this implementation does NOT compute deflated Sharpe, PBO or another multiple-testing correction.

## Costs and statistics

- Default taker fee: **0.05% per filled side** (`0.0005` as a fraction).
- Default slippage: **2 basis points per side**, an explicit placeholder to calibrate to the market.
- Optional funding: basis points per day. The real adapter must model actual signed funding cash flows; the demo applies a simple holding-cost approximation.
- Maker fees may be set to `0.0002` by the operator only when the execution model explicitly simulates maker fills. Lower fees alone do not model fill probability.
- Returns must be fixed-frequency, mark-to-market portfolio simple returns, including every observation and all friction. `periods_per_year` must match that sampling/calendar: the daily synthetic demo uses 365, not the default 252.
- Sharpe uses sample standard deviation and zero risk-free rate. Zero variance gives `null`, not infinite Sharpe.
- CAGR is annualized from observation count, not elapsed wall time. Incorrect frequency or missing expected bars invalidates that interpretation.
- Drawdown is a positive fraction from the running peak, including initial equity. Duration counts consecutive underwater observations; ongoing drawdowns are included.
- VaR95 and CVaR95 are historical **one-period losses**, in return units. CVaR averages the worst 5% probability mass, fractionally weighting the boundary observation. No Gaussian assumption. Both may be negative when the entire empirical distribution represents gains.
- A warning accompanies fewer than 20 equivalent tail observations. This threshold is a diagnostic, not a statistical guarantee.
- The holdout interval is a circular block bootstrap of **mean period return**, with deterministic seed, 400 draws and blocks of up to five observations. It is not a Sharpe interval, a forecast guarantee or a correction for selecting the best strategy. Block length must be reviewed for the series' dependence structure before research use.

## Connect your real backtester

Implement `Backtester.list_strategies()` and `Backtester.run(request)`. This deliberately changes the old `run(strategy, params, start, end)` signature: the old interface cannot carry the necessary temporal, cost and provenance contract.

The registry supports bounded `int`, bounded `float`, and explicit `enum` parameters. Unknown parameters, booleans passed as numbers, nonfinite inputs, and out-of-range values are rejected.

`RunRequest` provides strategy, normalized parameters, `[start,end)`, costs, seed, dataset SHA-256, engine version, `closed_bars_only=True`, and `execution='NEXT_EVENT'`.

Return `RunResult` with:

| Field | Required meaning |
|---|---|
| `request_sha256` | `digest(asdict(request))` for the actual request executed |
| `dataset_sha256` | Hash of the immutable dataset snapshot actually used |
| `engine_version` | Code/build identifier for the engine actually used |
| `bar_opens`, `bar_closes` | Ordered, nonoverlapping timezone-aware times; each bar closes at or before `end` |
| `net_returns` | One finite net portfolio return per bar; include zero-return bars |
| `n_trades` | Completed round trips, not order or fill count |
| `simulation` | `True` for synthetic demonstrations |

The adapter must verify the fingerprint from its underlying data; simply echoing the requested hash proves nothing. The harness validates matching metadata, dimensions, timestamp order, interval boundaries and finite returns, but cannot inspect an external engine's internals.

Responsibilities that remain in your engine/data layer:

- No current-bar OHLCV in decisions or dashboard states; HTF values become available only when their bars close. Warmup data must precede the decision and cannot use later observations.
- No same-bar retroactive bracket fill. A decision after close[T] first executes at the next available event. A timestamp flag alone does not prove this behavior.
- Correct fees, slippage, funding, multipliers, corporate actions, rollover and asset calendar. Validate expected bars against that calendar; the harness does not detect omitted trading sessions.
- Exact accounting, deterministic replay, open/partial-fill state, OCO, IOC/FOK, stop-limit and halt behavior.
- Fit preprocessing/models on training data only. The walk-forward helper selects static parameter sets; it does not transfer a fitted model artifact into validation.
- A train/test time gap is implemented. It is NOT general label-aware purging or CPCV. Overlapping labels need purging in the adapter based on their actual information intervals.
- Each window starts flat, and the engine must use an explicit boundary liquidation policy. Fold results are reported separately rather than inventing a stitched portfolio equity curve.

`causality_checks.assert_closed_bar_causality` tests deterministic decision traces, prefix truncation, current-bar mutation and future-bar mutation. Its decision at index i is the state at that bar's OPEN. The demo passes; deliberately leaky examples fail. Run an equivalent probe on your real strategy and retain the engine's separate fill/accounting tests.

## Paper/live order contract

There is no broker adapter in this package. `Executor` is a protocol, and tests use an in-memory executor.

The `propose_order` tool accepts `symbol`, signed `qty` as a decimal string, `client_order_id`, and `rationale`. There is no agent-supplied price. Research mode does not even expose execution tools. Paper/live must match the executor's declared mode and stable account ID. Live also requires a human callback returning literal `True`; its input is a copy. A new snapshot is checked after approval, and changed reviewed valuation/exposure requires a new approval attempt.

`Snapshot` must be an atomic account view. Its timestamp certifies freshness of ALL marks, FX, positions, remaining broker orders, equity and net daily P&L. Never attach a current timestamp to stale component values. Daily P&L must use the broker's documented day boundary and include unrealized P&L and fees.

Supported valuation is `abs(quantity × mark × contract multiplier × FX-to-account)`: linear spot, stocks, futures and appropriate FX instruments. Options, inverse contracts, negative prices and nonlinear risk require an extended valuation/risk model. This is a notional gate, not a margin, liquidation or portfolio-VaR engine.

Limits on order notional, position notional, gross notional and leverage are **exclusive**: reaching a limit rejects the order. Quantity minimums are inclusive. Empty allowlist denies all. Pending buys and sells are evaluated separately because either side can fill first. Reservations remain until a trusted snapshot accounts for them. This conservative method can also reject risk-reducing orders when an account already breaches a limit; use a separately controlled emergency broker workflow.

Broker submission must deduplicate the supplied client order ID. Timeouts, malformed receipts and unknown execution outcomes never trigger automatic resubmission. `RESERVED`, `ACCEPTED` and `UNKNOWN` orders all reserve exposure. `accounted_order_ids` may release a reservation only when that snapshot includes all its fills and its remaining open quantity, or confirms a terminal rejection/cancellation. The adapter must reconcile against the broker; it must not guess. A process crash after broker submission but before receipt persistence retains `RESERVED` and blocks a duplicate submit.

The daily-loss and operator kill switches latch. No reset tool is available to the agent. They block new submissions; they do not cancel open broker orders or liquidate existing positions. Operator kill-switch updates use the same lock, so a hung adapter or approval callback can delay them. Production emergency controls must exist outside this process.

Market orders can fill beyond the snapshot mark and price buffer. The gate controls pretrade estimates, not a guaranteed realized notional ceiling. Broker-enforced price collars, account-wide execution coordination and independent risk controls are necessary for a production deployment. Other terminals/accounts do not share this database lock automatically.

## Persistence, audit and process boundaries

SQLite uses WAL, FULL synchronous writes, and explicit transactions for research attempts and order reservations. A process lock serializes tool calls across cooperating processes on one host. Do not put the database on a network filesystem or run separate databases against the same account and expect shared limits.

The audit stores requests, results, usage, commits and order outcomes. JSON is canonical and rejects nonfinite values. Audit-write failures propagate before side effects. `Store.export_audit(path)` emits JSONL and returns the chain head. The chain and SQLite triggers detect/prevent ordinary edits, but are not an external signature: a privileged filesystem owner can rebuild the chain or remove its tail. For stronger auditability, anchor the returned head in an independently controlled append-only system.

The tool caller must not have Python execution, shell access, database editing, direct engine access or broker credentials. Python private methods are conventions, not a security sandbox. A tool allowlist is meaningful only when these process/credential boundaries are real.

The local backtester executes synchronously. There is no hard worker timeout or memory sandbox. Run untrusted or potentially hanging engines in a separately supervised process/container. LLM usage is logged and call counts are limited; this is not a token-dollar spending cap. Provider retries are disabled and its timeout is 60 seconds.

## Files

- `quant_agent_harness.py`: core, metrics, persistence, risk gate and optional Anthropic loop.
- `demo.py`: synthetic dataset, causal toy strategy and complete offline workflow.
- `causality_checks.py`: operator-side temporal invariance probe.
- `tests/test_harness.py`: regression and numerical oracle tests.
- `TEST_RESULTS.txt`: captured validation output for this delivery.
- `examples/synthetic_demo_report.json`: actual output from the offline demo.
- `VALIDATION.md`: what was checked and what remains unverified.

## Primary references checked

- Anthropic tool-call/result format: https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls
- Python SQLite transaction behavior: https://docs.python.org/3/library/sqlite3.html

These references inform the integration; they do not certify this harness or its external adapters.
