# Validation record

Environment: Python 3.12.14, Linux. Core/demo/tests use the standard library only.

Command: `python -m unittest discover -s tests -v`

Result: **49 tests passed.** Exact output is in `TEST_RESULTS.txt`.

Verified:

- UTC/exclusive-end research boundaries; rejected nonfinite, boolean and out-of-range parameters.
- Persistent budgets, failed-attempt accounting, immutable experiment identity and batch preflight.
- Holdout reuse blocked after success, failure and harness restart; research frozen after commitment.
- Concurrent holdout attempts across separate harness/SQLite connections expose it only once.
- Provenance mismatch, unordered/overlapping bars and invalid returns rejected.
- Walk-forward training selection, chronology, gap and overlapping test rejection.
- Cost stress sends new costs to the engine and recomputes results.
- No execution tool in research mode; exact mode checking and deny-all empty allowlist.
- Order deduplication across restart, conflicting IDs and agent-supplied prices rejected.
- Freshness, finite valuation, contract multipliers, FX, quantity steps and exclusive limits.
- Pending buy/sell exposure, concurrent local reservations, gross and leverage caps.
- Unknown submissions remain reserved and are not automatically retried.
- Stale reconciliation cannot release reservations; valid reconciliation counts filled positions.
- Persistent hourly limits, daily-loss latch, operator latch and live approval checks.
- Audit append-only triggers, hash verification and fail-closed behavior on audit failure.
- Stubbed provider loop: matched tool IDs, error flags, multiple results, persistent LLM budget.
- Numerical oracles for wealth, CAGR, drawdown, duration and fractional-tail CVaR.
- Undefined Sharpe handling and deterministic block bootstrap.
- Decision invariance on synthetic data, plus deliberate current/future leak detection.
- Dataset fingerprint stability in a fresh Python process.
- End-to-end offline demo and saved final result on restart.

Limits of this evidence:

- Concurrency tests use threads with separate harness instances/connections; the OS file-lock implementation is intended for cooperating single-host processes. Distributed execution is not supported.
- Restart tests reopen persistent state; they do not inject a power failure into every SQLite/broker instruction boundary.
- No real broker, paid model endpoint, market feed, Chartpy or NautilusTrader integration was exercised.
- No real strategy performance or economic advantage has been established. Synthetic results are not evidence of profitability.
- The temporal probe covers decision traces only. Exact execution, accounting, HTF alignment, label purging and calendar completeness still require adapter-specific tests.
- No claim of multiple-testing correction, production certification, tamper-proof storage or guaranteed market-order execution price is made.

The package is an implemented and tested foundation for research and adapter integration, not a completed production trading deployment.
