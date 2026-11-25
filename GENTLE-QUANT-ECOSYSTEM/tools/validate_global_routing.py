#!/usr/bin/env python3
"""Acceptance tests for the global work-nature routing policy."""

from classify_global_task import route


CASES = (
    ("A", "Port OpenTerminalUI visual system into Pine Lab without changing research logic.", "CIMA Quant", "UI_UX", "ui-ux-engineer", ("quant-developer", "quant-validator"), "UNCHANGED"),
    ("B", "Change Pine Lab fill semantics and execution timing.", "CIMA Quant", "QUANT_IMPLEMENTATION", "quant-developer", (), "CHANGED"),
    ("C", "Fix the Studies page API integration and loading-state bug.", "Chartpy Quant", "SOFTWARE_ENGINEERING", "software-engineer", ("quant-researcher", "quant-validator"), None),
    ("D", "Historical candles contain duplicates, gaps and timestamp inconsistencies.", "financial", "DATA_ENGINEERING", "data-engineer", ("quant-researcher",), None),
)


def main() -> int:
    for name, task, domain, task_class, primary, forbidden, semantics in CASES:
        result = route(task, domain)
        assert result["task_class"] == task_class, (name, result)
        assert result["primary_specialist"] == primary, (name, result)
        assert not result["domain_used_as_selector"], (name, result)
        assert all(role not in result["workflow"] for role in forbidden), (name, result)
        if semantics:
            assert result["protected_quant_semantics"] == semantics, (name, result)
        print(f"PASS {name}: {task_class} -> {result['workflow']}")

    unresolved = route("Add Expected Shortfall to Chartpy and expose it in a new visual dashboard.", "financial")
    approved = route("Implement the already approved Expected Shortfall specification in a new visual dashboard.", "financial")
    assert unresolved["task_class"] == "MIXED" and unresolved["workflow"][0] == "quant-researcher", unresolved
    assert approved["task_class"] == "MIXED" and approved["workflow"][0] == "quant-developer", approved
    assert "software-engineer" in approved["workflow"] and "ui-ux-engineer" in approved["workflow"], approved
    print(f"PASS E: unresolved={unresolved['workflow']}; approved={approved['workflow']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
