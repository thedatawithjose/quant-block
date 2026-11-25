import concurrent.futures
import copy
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace
from quant_agent_harness import (Harness, ResearchConfig, RiskGate, RiskLimits, RunResult,
    Snapshot, Instrument, Rejected, block_bootstrap, digest, iso, metrics, utc)
from demo import SyntheticBacktester, signals, synthetic_bars
from causality_checks import assert_closed_bar_causality

NOW = 1_700_000_000.0

class Engine:
    def __init__(self):
        self.requests, self.fail, self.mutate = [], False, None
    def list_strategies(self):
        return {"trend": {"length": {"type": "int", "min": 2, "max": 30, "default": 5}}}
    def run(self, req):
        self.requests.append(req)
        if self.fail:
            raise RuntimeError("simulated engine failure")
        start = utc(req.start)
        r = RunResult(digest(asdict(req)), req.dataset_sha256, req.engine_version,
            [iso(start + i * 86400) for i in range(4)],
            [iso(start + (i + 1) * 86400) for i in range(4)],
            [x - 2 * req.costs.fee_per_side for x in [-.01, .02, -.005, .007]], 20, True)
        if self.mutate:
            self.mutate(r)
        return r

class PaperExecutor:
    mode, account_id = "paper", "test-account"
    def __init__(self):
        self.state = Snapshot(NOW, "10000", "0", {}, {"ABC": "10"}, {"ABC": Instrument()})
        self.sent, self.fail = [], False
    def snapshot(self):
        return copy.deepcopy(self.state)
    def submit(self, order):
        self.sent.append(order)
        if self.fail:
            raise TimeoutError("broker reply lost")
        return {"status": "accepted", "client_order_id": order["client_order_id"]}

class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "state.sqlite")
        self.bt = Engine()
        self.cfg = ResearchConfig("2020-01-01", "2022-01-01", "2023-01-01", "2023-01-01",
                                  "a" * 64, "test/1", min_trades_for_selection=2)
        self.handles = []
    def tearDown(self):
        for h in self.handles:
            h.store.close()
        self.tmp.cleanup()
    def harness(self, **kwargs):
        cfg = kwargs.pop("config", self.cfg)
        h = Harness(self.bt, cfg, self.path, clock=lambda: NOW, **kwargs)
        self.handles.append(h)
        return h
    def research(self, h, **extra):
        return h.call("backtest", {"strategy": "trend", "params": {},
                                  "start": "2020-01-01", "end": "2021-01-01", **extra})
    def final(self, h):
        return h.call("final_validate", {"strategy": "trend", "params": {}})
    def order(self, h, oid="order1", qty="10", **extra):
        return h.call("propose_order", {"symbol": "ABC", "qty": qty,
                    "client_order_id": oid, "rationale": "test", **extra})
    def paper(self, limits=None):
        ex = PaperExecutor()
        return self.harness(mode="paper", executor=ex, limits=limits or RiskLimits(allowed_symbols=("ABC",))), ex
    def test_temporal_boundaries(self):
        h = self.harness()
        self.assertNotIn("error", self.research(h, end="2022-01-01"))
        for a, b in [("2022-01-01", "2022-01-02"), ("2019-12-31", "2020-01-05"),
                     ("2020-01-05", "2020-01-01"), ("2020-01-01", "2022-01-01T00:00:01Z")]:
            with self.subTest(a=a, b=b):
                self.assertIn("error", self.research(h, start=a, end=b))
        self.assertEqual(len(self.bt.requests), 1)
    def test_timezone_normalization(self):
        self.assertEqual(utc("2022-01-01T02:00:00+02:00"), utc("2022-01-01"))
        with self.assertRaises(Rejected):
            utc("2022-01-01T00:00:00")
    def test_parameter_validation(self):
        h = self.harness()
        for p in [{"length": True}, {"length": 2.5}, {"length": 31}, {"other": 1}, {"length": float("nan")}]:
            with self.subTest(params=p):
                self.assertIn("error", self.research(h, params=p))
        self.assertEqual(len(self.bt.requests), 0)
    def test_failed_attempt_consumes_persistent_budget(self):
        cfg = replace(self.cfg, max_backtests=1)
        h = self.harness(config=cfg)
        self.bt.fail = True
        self.assertIn("error", self.research(h))
        h2 = self.harness(config=cfg)
        self.bt.fail = False
        self.assertIn("budget", self.research(h2)["message"])
        self.assertEqual(len(self.bt.requests), 1)
    def test_holdout_once_and_freeze_after_restart(self):
        h = self.harness()
        self.research(h)
        self.assertNotIn("error", self.final(h))
        h2 = self.harness()
        self.assertIn("error", self.final(h2))
        self.assertIn("error", self.research(h2))
        self.assertEqual(h2.call("status")["phase"], "FINALIZED")
        self.assertIsNotNone(h2.call("status")["final_report"])
    def test_failed_holdout_consumed(self):
        h = self.harness()
        self.research(h)
        self.bt.fail = True
        self.assertIn("error", self.final(h))
        self.bt.fail = False
        self.assertIn("error", self.final(h))
        self.assertEqual(h.call("status")["phase"], "HOLDOUT_COMMITTED")
        self.assertEqual(len(self.bt.requests), 2)
    def test_holdout_requires_researched_candidate(self):
        h = self.harness()
        self.assertIn("error", self.final(h))
        self.assertEqual(h.call("status")["phase"], "RESEARCH")
    def test_cannot_choose_holdout_window_or_costs(self):
        h = self.harness()
        self.research(h)
        self.assertIn("error", h.call("final_validate", {"strategy": "trend", "params": {}, "end": "2022-02-01"}))
        self.assertIn("error", self.research(h, costs={"fee_per_side": 0}))
    def test_configuration_change_rejected(self):
        self.harness()
        for cfg in [replace(self.cfg, seed=18), replace(self.cfg, dataset_sha256="b" * 64), replace(self.cfg, max_backtests=101)]:
            with self.subTest(config=cfg), self.assertRaises(Rejected):
                self.harness(config=cfg)
    def test_concurrent_holdout(self):
        h1, h2 = self.harness(), self.harness()
        self.research(h1)
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            outputs = list(pool.map(self.final, [h1, h2]))
        self.assertEqual(sum("error" not in x for x in outputs), 1)
        self.assertEqual(len(self.bt.requests), 2)
    def test_provenance_bar_and_metric_validation(self):
        h = self.harness()
        for mutation in [lambda r: setattr(r, "dataset_sha256", "b" * 64),
            lambda r: setattr(r, "request_sha256", "bad"), lambda r: setattr(r, "engine_version", "other"),
            lambda r: r.net_returns.__setitem__(0, float("inf")), lambda r: r.net_returns.__setitem__(0, -1),
            lambda r: r.bar_closes.__setitem__(-1, "2022-01-01"),
            lambda r: r.bar_opens.__setitem__(1, r.bar_opens[0]), lambda r: setattr(r, "n_trades", True)]:
            self.bt.mutate = mutation
            with self.subTest(mutation=mutation):
                self.assertIn("error", self.research(h))
    def test_walk_forward_selection_and_gap(self):
        h = self.harness()
        f = {"train_start": "2020-01-01", "train_end": "2020-07-01", "test_start": "2020-07-02", "test_end": "2021-01-01"}
        args = {"strategy": "trend", "candidates": [{"length": 5}, {"length": 10}], "folds": [f]}
        result = h.call("walk_forward", args)
        self.assertNotIn("error", result)
        self.assertEqual(len(self.bt.requests), 3)
        self.assertEqual(self.bt.requests[-1].params, result["folds"][0]["train_selection"]["params"])
        f["test_start"] = "2020-07-01"
        self.assertIn("error", h.call("walk_forward", args))
        self.assertEqual(len(self.bt.requests), 3)
    def test_overlapping_folds_rejected(self):
        h = self.harness()
        f = {"train_start": "2020-01-01", "train_end": "2020-07-01", "test_start": "2020-07-02", "test_end": "2021-01-01"}
        self.assertIn("error", h.call("walk_forward", {"strategy": "trend", "candidates": [{}], "folds": [f, f]}))
        self.assertEqual(len(self.bt.requests), 0)
    def test_batch_budget_preflight(self):
        h = self.harness(config=replace(self.cfg, max_backtests=1))
        self.assertIn("error", h.call("compare_candidates", {"strategy": "trend", "candidates": [{}, {"length": 10}],
                                                            "start": "2020-01-01", "end": "2021-01-01"}))
        self.assertEqual(len(self.bt.requests), 0)
    def test_cost_stress_reruns_engine(self):
        h = self.harness()
        out = h.call("stress_test", {"strategy": "trend", "params": {}, "start": "2020-01-01", "end": "2021-01-01", "multipliers": [1, 2, 3]})
        self.assertNotIn("error", out)
        self.assertEqual([r.costs.fee_per_side for r in self.bt.requests], [.0005, .001, .0015])
        rs = [x["run"]["metrics"]["total_return"] for x in out["scenarios"]]
        self.assertEqual(rs, sorted(rs, reverse=True))
    def test_research_cannot_execute(self):
        h = self.harness()
        self.assertNotIn("propose_order", h._tools)
        self.assertIn("error", self.order(h))
    def test_invalid_modes(self):
        for mode in ["LIVE", "unknown", "paper", "live"]:
            with self.subTest(mode=mode), self.assertRaises(Rejected):
                self.harness(mode=mode)
        with self.assertRaises(Rejected):
            self.harness(mode="live", executor=PaperExecutor(), human_approve=lambda _: True)
    def test_empty_allowlist_denies(self):
        h, ex = self.paper(RiskLimits())
        self.assertIn("error", self.order(h))
        self.assertEqual(ex.sent, [])
    def test_idempotency_restart_conflict(self):
        h, ex = self.paper()
        self.assertEqual(self.order(h)["status"], "ACCEPTED")
        self.assertTrue(self.order(h)["duplicate"])
        h2 = self.harness(mode="paper", executor=ex, limits=RiskLimits(allowed_symbols=("ABC",)))
        self.assertTrue(self.order(h2)["duplicate"])
        self.assertIn("error", self.order(h2, qty="11"))
        self.assertEqual(len(ex.sent), 1)
    def test_agent_price_rejected(self):
        h, ex = self.paper()
        self.assertIn("error", self.order(h, price=.01))
        self.assertEqual(len(ex.sent), 0)
    def test_bad_snapshots(self):
        h, ex = self.paper()
        original = ex.state
        for s in [replace(original, asof=NOW-6), replace(original, asof=NOW+1),
                  replace(original, marks={"ABC": "NaN"}), replace(original, equity="Infinity")]:
            ex.state = s
            with self.subTest(snapshot=s):
                self.assertIn("error", self.order(h))
        self.assertEqual(ex.sent, [])
    def test_exclusive_limits_and_quantity(self):
        h, ex = self.paper(RiskLimits(allowed_symbols=("ABC",), price_buffer_bps=0))
        for q in ["100", "101", "0", "0.5", "NaN", "Infinity", "-100"]:
            with self.subTest(q=q):
                self.assertIn("error", self.order(h, qty=q))
        self.assertEqual(ex.sent, [])
        self.assertEqual(self.order(h, qty="99")["status"], "ACCEPTED")
    def test_opposite_pending_orders_do_not_net(self):
        h, ex = self.paper(RiskLimits(allowed_symbols=("ABC",), max_position_notional=750, price_buffer_bps=0))
        ex.state = replace(ex.state, pending=(("ABC", "70"), ("ABC", "-70")))
        self.assertIn("error", self.order(h, qty="10"))
    def test_concurrent_reservations(self):
        limits = RiskLimits(allowed_symbols=("ABC",), max_position_notional=750)
        h1, ex = self.paper(limits)
        h2 = self.harness(mode="paper", executor=ex, limits=limits)
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            outputs = list(pool.map(lambda x: self.order(x[0], x[1], "40"), [(h1, "a"), (h2, "b")]))
        self.assertEqual(sum(o.get("status") == "ACCEPTED" for o in outputs), 1)
        self.assertEqual(len(ex.sent), 1)
    def test_unknown_no_retry_and_keeps_reservation(self):
        h, ex = self.paper(RiskLimits(allowed_symbols=("ABC",), max_position_notional=750))
        ex.fail = True
        self.assertEqual(self.order(h, "a", "40")["status"], "UNKNOWN")
        ex.fail = False
        self.assertTrue(self.order(h, "a", "40")["duplicate"])
        self.assertIn("error", self.order(h, "b", "40"))
        self.assertEqual(len(ex.sent), 1)
    def test_stale_reconciliation_cannot_release(self):
        h, ex = self.paper(RiskLimits(allowed_symbols=("ABC",), max_position_notional=750))
        self.order(h, "a", "40")
        ex.state = replace(ex.state, asof=NOW-20, accounted_order_ids=("a",))
        self.assertIn("error", self.order(h, "b", "40"))
        ex.state = replace(ex.state, asof=NOW, accounted_order_ids=())
        self.assertIn("error", self.order(h, "c", "40"))
    def test_valid_reconciliation_counts_fills(self):
        h, ex = self.paper(RiskLimits(allowed_symbols=("ABC",), max_position_notional=750))
        self.order(h, "a", "40")
        ex.state = replace(ex.state, positions={"ABC": "40"}, accounted_order_ids=("a",))
        self.assertEqual(self.order(h, "b", "10")["status"], "ACCEPTED")
        self.assertIn("error", self.order(h, "c", "30"))
    def test_persistent_hourly_limit(self):
        limits = RiskLimits(allowed_symbols=("ABC",), max_orders_per_hour=1)
        h, ex = self.paper(limits)
        self.order(h)
        h2 = self.harness(mode="paper", executor=ex, limits=limits)
        self.assertIn("hourly", self.order(h2, "order2")["message"])
    def test_daily_loss_latches(self):
        h, ex = self.paper()
        ex.state = replace(ex.state, daily_pnl="-200")
        self.assertIn("error", self.order(h))
        ex.state = replace(ex.state, daily_pnl="0")
        self.assertIn("error", self.order(h))
        self.assertTrue(h.call("status")["kill_switch"])
    def test_operator_kill_switch(self):
        h, ex = self.paper()
        h.set_kill_switch("operator stop")
        self.assertIn("error", self.order(h))
        self.assertEqual(ex.sent, [])
    def test_live_approval_copy(self):
        ex = PaperExecutor()
        ex.mode = "live"
        def approve(order):
            order["qty"] = "9999"
            return True
        h = self.harness(mode="live", executor=ex, limits=RiskLimits(allowed_symbols=("ABC",)), human_approve=approve)
        self.assertEqual(self.order(h)["status"], "ACCEPTED")
        self.assertEqual(float(ex.sent[0]["qty"]), 10)
    def test_live_approval_literal_true(self):
        ex = PaperExecutor()
        ex.mode = "live"
        h = self.harness(mode="live", executor=ex, limits=RiskLimits(allowed_symbols=("ABC",)), human_approve=lambda _: "yes")
        self.assertIn("error", self.order(h))
        self.assertEqual(ex.sent, [])
    def test_live_price_rechecked(self):
        ex = PaperExecutor()
        ex.mode = "live"
        def approve(_):
            ex.state = replace(ex.state, marks={"ABC": "11"})
            return True
        h = self.harness(mode="live", executor=ex, limits=RiskLimits(allowed_symbols=("ABC",)), human_approve=approve)
        self.assertIn("error", self.order(h))
        self.assertEqual(ex.sent, [])
    def test_audit_append_only_and_tamper_detection(self):
        h = self.harness()
        self.research(h)
        with h.store.guard():
            self.assertEqual(len(h.store.verify()), 64)
            with self.assertRaises(sqlite3.IntegrityError):
                h.store.db.execute("UPDATE events SET hash='broken' WHERE seq=1")
            h.store.db.execute("DROP TRIGGER events_no_update")
            h.store.db.execute("UPDATE events SET hash='broken' WHERE seq=1")
            with self.assertRaises(Rejected):
                h.store.verify()
    def test_audit_failure_blocks_execution(self):
        h, ex = self.paper()
        def fail(*args, **kwargs):
            raise OSError("disk unavailable")
        h.store.event = fail
        with self.assertRaises(OSError):
            self.order(h)
        self.assertEqual(ex.sent, [])
    def test_tool_call_budget(self):
        cfg = replace(self.cfg, max_tool_calls=1)
        self.harness(config=cfg).call("list_strategies")
        self.assertIn("budget", self.harness(config=cfg).call("list_strategies")["message"])
    def test_agent_protocol_offline(self):
        h = self.harness()
        responses = [SimpleNamespace(stop_reason="tool_use", usage={}, content=[
            {"type": "tool_use", "id": "a", "name": "no_such_tool", "input": {}},
            {"type": "tool_use", "id": "b", "name": "list_strategies", "input": {}}]),
            SimpleNamespace(stop_reason="end_turn", usage={}, content=[{"type": "text", "text": "done"}])]
        requests = []
        def create(**kwargs):
            requests.append(copy.deepcopy(kwargs))
            return responses.pop(0)
        client = SimpleNamespace(messages=SimpleNamespace(create=create))
        self.assertEqual(h.run("test", model="operator-model", client=client), "done")
        results = requests[1]["messages"][-1]["content"]
        self.assertEqual([r["tool_use_id"] for r in results], ["a", "b"])
        self.assertTrue(results[0]["is_error"])
        self.assertFalse(results[1]["is_error"])
    def test_llm_budget_persists(self):
        h = self.harness(config=replace(self.cfg, max_llm_calls=1))
        create = lambda **_: SimpleNamespace(stop_reason="end_turn", usage={}, content=[{"type": "text", "text": "ok"}])
        client = SimpleNamespace(messages=SimpleNamespace(create=create))
        h.run("task", model="test", client=client)
        self.assertIn("budget exhausted", h.run("task", model="test", client=client))

class QuantTests(unittest.TestCase):
    def test_metrics_oracle(self):
        m = metrics([.1, -.2, .05, -.1], 4, 2)
        self.assertAlmostEqual(m["total_return"], 1.1 * .8 * 1.05 * .9 - 1)
        self.assertAlmostEqual(m["max_dd"], 1 - .8 * 1.05 * .9)
        self.assertAlmostEqual(m["cagr"], m["total_return"])
        self.assertAlmostEqual(m["cvar_95"], .2)
        self.assertEqual(m["max_dd_duration_periods"], 3)
    def test_fractional_tail_es(self):
        m = metrics([-.3, -.15] + [0] * 28, 30, 1)
        self.assertAlmostEqual(m["cvar_95"], (.3 + .5 * .15) / 1.5)
        self.assertAlmostEqual(m["var_95"], .15)
    def test_undefined_sharpe(self):
        self.assertIsNone(metrics([0, 0, 0], 252, 0)["sharpe"])
    def test_bootstrap_reproducible(self):
        rs = [.01, -.02, .03, -.01] * 10
        a = block_bootstrap(rs, 17)
        self.assertEqual(a, block_bootstrap(rs, 17))
        self.assertLessEqual(*a["mean_return_ci_95"])
        self.assertFalse(a["selection_adjusted"])
    def test_contract_multiplier_fx(self):
        gate = RiskGate(RiskLimits(allowed_symbols=("FUT",), price_buffer_bps=0))
        snap = Snapshot(NOW, "100000", "0", {}, {"FUT": "10"}, {"FUT": Instrument(multiplier="50", fx_to_account="2")})
        with self.assertRaises(Rejected):
            gate.check("FUT", "1", snap, [], NOW)
    def test_gross_and_leverage(self):
        limits = RiskLimits(allowed_symbols=("ABC",), max_gross_notional=100, price_buffer_bps=0)
        snap = PaperExecutor().state
        with self.assertRaises(Rejected):
            RiskGate(limits).check("ABC", "10", snap, [], NOW)
        with self.assertRaises(Rejected):
            RiskGate(replace(limits, max_gross_notional=10000, max_leverage=.01)).check("ABC", "10", snap, [], NOW)
    def test_causality_passes(self):
        assert_closed_bar_causality(signals, synthetic_bars(45))
    def test_causality_current_leak_detected(self):
        with self.assertRaisesRegex(AssertionError, "current bar"):
            assert_closed_bar_causality(lambda bars: [b["close"] for b in bars], synthetic_bars(15))
    def test_causality_future_leak_detected(self):
        with self.assertRaisesRegex(AssertionError, "truncation"):
            assert_closed_bar_causality(lambda bars: [bars[-1]["close"]] * len(bars), synthetic_bars(15))
    def test_fingerprint_cross_process(self):
        code = "from demo import SyntheticBacktester; print(SyntheticBacktester().fingerprint)"
        output = subprocess.check_output([sys.executable, "-c", code], text=True).strip()
        self.assertEqual(output, SyntheticBacktester().fingerprint)
    def test_demo_end_to_end_and_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = str(Path(tmp) / "demo.sqlite")
            subprocess.check_output([sys.executable, "demo.py", "--state", state], text=True)
            report = json.loads(Path(state).with_suffix(".report.json").read_text())
            for key in ["comparison", "walk_forward", "stress", "final"]:
                self.assertNotIn("error", report[key])
            self.assertTrue(report["final"]["simulation"])
            resumed = json.loads(subprocess.check_output([sys.executable, "demo.py", "--state", state], text=True))
            self.assertEqual(resumed["phase"], "FINALIZED")
            self.assertEqual(resumed["backtests_used"], 15)

if __name__ == "__main__":
    unittest.main()
