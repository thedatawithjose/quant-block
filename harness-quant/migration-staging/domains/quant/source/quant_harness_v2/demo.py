"""Offline deterministic demonstration; NOT a CIMA implementation or trading edge."""
from __future__ import annotations
import argparse
import json
import math
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from quant_agent_harness import (Harness, ResearchConfig, RunRequest, RunResult,
                                 Rejected, canonical, digest, iso, utc)


def synthetic_bars(days: int = 1000) -> list[dict]:
    bars, previous = [], 100.0
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    for i in range(days):
        ret = .001 + .009 * math.sin(i / 13) + .004 * math.sin(i / 3)
        close = previous * (1 + ret)
        bars.append({"open_time": (start + timedelta(days=i)).isoformat(),
                     "close_time": (start + timedelta(days=i + 1)).isoformat(),
                     "open": previous, "high": max(previous, close) * 1.001,
                     "low": min(previous, close) * .999, "close": close,
                     "volume": 1000 + i % 30})
        previous = close
    return bars


def signals(bars: list[dict], lookback: int = 12) -> list[int]:
    """Decision at each bar OPEN uses closes strictly before that bar."""
    out = []
    for i in range(len(bars)):
        if i < lookback:
            out.append(0)
        else:
            historical = [b["close"] for b in bars[i - lookback:i]]
            out.append(1 if historical[-1] > sum(historical) / lookback else -1)
    return out


class SyntheticBacktester:
    version = "synthetic-momentum/2.0"

    def __init__(self, bars: list[dict] | None = None):
        self.bars = synthetic_bars() if bars is None else bars
        self.fingerprint = digest(self.bars)

    def list_strategies(self) -> dict:
        return {"synthetic_momentum": {"lookback": {"type": "int", "min": 3, "max": 60, "default": 12}}}

    def run(self, request: RunRequest) -> RunResult:
        if request.dataset_sha256 != digest(self.bars) or request.engine_version != self.version:
            raise Rejected("demo dataset/engine mismatch")
        if not request.closed_bars_only or request.execution != "NEXT_EVENT":
            raise Rejected("unsupported temporal contract")
        a, b = utc(request.start), utc(request.end)
        # Truncate data before computing signals: no future bars enter the engine.
        data = [bar for bar in self.bars if utc(bar["close_time"]) <= b]
        positions = signals(data, request.params["lookback"])
        selected = [(bar, p) for bar, p in zip(data, positions) if a <= utc(bar["open_time"]) < b]
        returns, opens, closes = [], [], []
        previous, trades = 0, 0
        per_side = request.costs.fee_per_side + request.costs.slippage_bps / 10000
        for i, (bar, p) in enumerate(selected):
            # Unit fraction exposure, repriced each open. Toy cost approximation.
            turnover = abs(p - previous)
            if previous != 0 and p != previous:
                trades += 1
            ret = p * (bar["close"] / bar["open"] - 1) - turnover * per_side
            ret -= abs(p) * request.costs.funding_bps_per_day / 10000
            if i == len(selected) - 1 and p:
                ret -= abs(p) * per_side  # specified boundary liquidation
                trades += 1
            returns.append(ret)
            opens.append(bar["open_time"])
            closes.append(bar["close_time"])
            previous = p
        return RunResult(digest(asdict(request)), self.fingerprint, self.version,
                         opens, closes, returns, trades, simulation=True)


def demo_config(bt: SyntheticBacktester) -> ResearchConfig:
    return ResearchConfig(research_start="2020-01-01", holdout_start="2022-01-01",
                          holdout_end="2022-09-01", data_asof="2022-09-27",
                          dataset_sha256=bt.fingerprint, engine_version=bt.version,
                          periods_per_year=365, min_trades_for_selection=2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", default="demo_state.sqlite")
    parser.add_argument("--agent", action="store_true", help="Calls Anthropic; requires HARNESS_MODEL and API key")
    args = parser.parse_args()
    bt = SyntheticBacktester()
    h = Harness(bt, demo_config(bt), args.state)
    try:
        if args.agent:
            print(h.run("Evaluate synthetic_momentum on development data through 2022-01-01. "
                        "Compare lookback 8, 12, 20; stress costs; use walk forward; then final_validate once. "
                        "All data is synthetic. Do not infer live profitability."))
            return
        status = h.call("status")
        if status["phase"] != "RESEARCH":
            print(json.dumps(status, indent=2))
            return
        candidates = [{"lookback": v} for v in (8, 12, 20)]
        comparison = h.call("compare_candidates", {"strategy": "synthetic_momentum", "candidates": candidates,
                                                   "start": "2020-01-01", "end": "2021-01-01"})
        if "error" in comparison or comparison["selected"] is None:
            raise RuntimeError(comparison)
        chosen = comparison["selected"]["params"]
        wf = h.call("walk_forward", {"strategy": "synthetic_momentum", "candidates": candidates,
            "folds": [{"train_start": "2020-01-01", "train_end": "2020-07-01",
                       "test_start": "2020-07-02", "test_end": "2021-01-01"},
                      {"train_start": "2020-01-01", "train_end": "2021-01-01",
                       "test_start": "2021-01-02", "test_end": "2022-01-01"}]})
        stress = h.call("stress_test", {"strategy": "synthetic_momentum", "params": chosen,
                                      "start": "2021-01-01", "end": "2022-01-01", "multipliers": [1, 2, 3]})
        final = h.call("final_validate", {"strategy": "synthetic_momentum", "params": chosen})
        report = {"label": "SYNTHETIC DEMO ONLY — no market-performance evidence", "comparison": comparison,
                  "walk_forward": wf, "stress": stress, "final": final}
        out = Path(args.state).with_suffix(".report.json")
        out.write_text(json.dumps(report, indent=2))
        print(json.dumps({"report": str(out), "final": final}, indent=2))
        h.store.export_audit(str(Path(args.state).with_suffix(".audit.jsonl")))
    finally:
        h.store.close()


if __name__ == "__main__":
    main()
