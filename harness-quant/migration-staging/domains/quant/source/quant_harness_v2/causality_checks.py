"""Operator-side test helper. Not an agent tool and not a substitute for engine tests."""
import copy
from typing import Callable


def assert_closed_bar_causality(decide: Callable[[list[dict]], list], bars: list[dict]) -> None:
    """decide returns one state per bar OPEN, before that bar's OHLCV is known.

    At index i, only bars [:i] may inform that state. Test every prefix, mutate
    current OHLCV, then mutate all future OHLCV. Equality is exact by design.
    Does not inspect fill timing, PnL, funding, accounting or cross-timeframe data.
    Adapters with numerical nondeterminism need a separate declared tolerance.
    """
    baseline = decide(copy.deepcopy(bars))
    assert len(baseline) == len(bars), "one state per bar required"
    assert baseline == decide(copy.deepcopy(bars)), "nondeterministic decisions"
    for i in range(len(bars)):
        prefix = decide(copy.deepcopy(bars[:i + 1]))
        assert prefix == baseline[:i + 1], f"truncation invariance failed at {i}"
        for indexes, label in (([i], "current bar"), (range(i + 1, len(bars)), "future bars")):
            changed = copy.deepcopy(bars)
            for j in indexes:
                for field in ("open", "high", "low", "close"):
                    changed[j][field] *= 7
                changed[j]["volume"] *= 11
            output = decide(changed)
            assert output[:i + 1] == baseline[:i + 1], f"{label} affected decisions through {i}"
