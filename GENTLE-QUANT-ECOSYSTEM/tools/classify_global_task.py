#!/usr/bin/env python3
"""Deterministic reference classifier for Gentle global task routing."""

from __future__ import annotations

import argparse
import json


PROTECTED_SURFACES = (
    "trading signal", "signal semantics", "quantitative mathematics",
    "fill semantics", "execution timing", "execution semantics", "look-ahead",
    "causal timing", "fees", "slippage", "accounting", "pnl",
    "position sizing", "risk calculation", "portfolio calculation",
    "backtest", "tradingview parity", "economically meaningful",
)


def contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def route(task: str, domain: str = "") -> dict[str, object]:
    """Classify task wording; domain is context and intentionally not a selector."""
    text = task.lower()
    protected = contains_any(text, PROTECTED_SURFACES)
    ui = contains_any(text, ("visual", "layout", "typography", "navigation", "dashboard", "sidebar", "ui", "ux"))
    software = contains_any(text, ("api", "integration", "bug", "loading", "backend", "frontend", "service", "state management"))
    data = contains_any(text, ("duplicates", "duplicate", "gaps", "missing bars", "timestamp", "ingestion", "schema", "lineage", "normalization"))
    data_science = contains_any(text, ("clustering", "classification", "anomaly detection", "machine learning", "ml", "feature engineering"))
    quant_research = contains_any(text, ("trading hypothesis", "alpha", "portfolio research", "backtesting methodology", "risk methodology"))
    expected_shortfall = "expected shortfall" in text or "cvar" in text
    approved_spec = contains_any(text, ("approved", "already specified", "existing specification"))

    if expected_shortfall and ui:
        workflow = ["quant-developer", "software-engineer", "ui-ux-engineer", "quant-validator"]
        if not approved_spec:
            workflow.insert(0, "quant-researcher")
        return {
            "task_class": "MIXED",
            "primary_specialist": workflow[0],
            "additional_specialists": workflow[1:],
            "workflow": workflow,
            "quant_specification": "APPROVED" if approved_spec else "REQUIRED_BEFORE_IMPLEMENTATION",
            "protected_quant_semantics": "CHANGED",
            "domain_used_as_selector": False,
        }
    if protected:
        return {
            "task_class": "QUANT_IMPLEMENTATION",
            "primary_specialist": "quant-developer",
            "additional_specialists": ["quant-validator"],
            "workflow": ["quant-developer", "quant-validator"],
            "protected_quant_semantics": "CHANGED",
            "domain_used_as_selector": False,
        }
    if quant_research:
        return {
            "task_class": "QUANT_RESEARCH",
            "primary_specialist": "quant-researcher",
            "additional_specialists": ["quant-validator"],
            "workflow": ["quant-researcher", "quant-validator"],
            "domain_used_as_selector": False,
        }
    if data:
        return {
            "task_class": "DATA_ENGINEERING",
            "primary_specialist": "data-engineer",
            "additional_specialists": [],
            "workflow": ["data-engineer"],
            "domain_used_as_selector": False,
        }
    if data_science:
        return {
            "task_class": "DATA_SCIENCE",
            "primary_specialist": "data-scientist",
            "additional_specialists": [],
            "workflow": ["data-scientist"],
            "domain_used_as_selector": False,
        }
    if ui:
        additional = ["software-engineer"] if software or "port" in text else []
        return {
            "task_class": "UI_UX",
            "primary_specialist": "ui-ux-engineer",
            "additional_specialists": additional,
            "workflow": ["ui-ux-engineer", *additional],
            "protected_quant_semantics": "UNCHANGED",
            "domain_used_as_selector": False,
        }
    return {
        "task_class": "SOFTWARE_ENGINEERING",
        "primary_specialist": "software-engineer",
        "additional_specialists": [],
        "workflow": ["software-engineer"],
        "domain_used_as_selector": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("--domain", default="")
    args = parser.parse_args()
    print(json.dumps(route(args.task, args.domain), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
