# Global Task Routing Policy

Gentle selects specialists from the **nature of the requested work**. Repository domain supplies context and project governance supplies boundaries; neither turns every change into Quant work.

## Routing order

1. Identify the requested outcome and the smallest work class that can deliver it.
2. Inspect the project's protected semantic surfaces and explicit routing overrides.
3. Escalate only the portions that can alter a protected surface.
4. Decompose genuinely mixed work into ordered specialist handoffs.
5. Stop after the requested outcome is implemented, verified, evidenced, accepted, and `DONE`.

`project_type: quantitative` is not a routing rule.

## Global classes

| Class | Primary specialist | Use for |
| --- | --- | --- |
| `UI_UX` | `ui-ux-engineer` | Visual design, hierarchy, navigation, layout, usability, and presentation. |
| `SOFTWARE_ENGINEERING` | `software-engineer` | Application/frontend/backend implementation, APIs, integration, bugs, persistence, and application tests. |
| `DATA_ENGINEERING` | `data-engineer` | Ingestion, schemas, normalization, lineage, timestamps, gaps, duplicates, and data quality. |
| `DATA_SCIENCE` | `data-scientist` | Non-trading ML, statistical modeling, forecasting, clustering, and analytical experiments. |
| `QUANT_RESEARCH` | `quant-researcher` | Trading hypotheses, alpha/risk methodology, portfolio research, and backtest methodology. |
| `QUANT_IMPLEMENTATION` | `quant-developer` | Approved quantitative mathematics, fills, accounting, risk/portfolio calculations, indicators, and backtest mechanics. |
| `QUANT_VALIDATION` | `quant-validator` | Independent falsification of quantitative semantics, causality, leakage, numerical correctness, accounting, or parity. |
| `OPERATIONS` | Existing Gentle operations capability | Builds, CI, packaging, runtime configuration, logs, deployment, and environment diagnostics. |

`MIXED` is a decomposition result, not a specialist. It contains only the necessary classes in dependency order.

## Quant escalation boundary

Route the affected portion through the Quant path only if it can alter one or more project-declared protected surfaces, including trading signals, quantitative mathematics, market-data meaning, causal timing, fills, execution semantics, fees, slippage, accounting, PnL, position sizing, risk or portfolio calculations, backtesting results, platform parity, or other economically meaningful outputs.

An implementation that preserves those surfaces remains ordinary UI, software, data, data-science, or operations work. Quant validation is required only when the Quant portion or project governance requires independent validation; it is not a tax on every source-code modification.

## Mixed work

For a feature such as an Expected Shortfall dashboard:

1. Use `quant-researcher` only when the mathematical specification is absent or unresolved.
2. Use `quant-developer` for the approved quantitative implementation.
3. Use `software-engineer` for application/API integration.
4. Use `ui-ux-engineer` for the dashboard.
5. Use `quant-validator` only for the quantitative implementation when its protected semantics require independent validation.

The orchestrator must not invoke a role merely because it exists.

## Project routing responsibility

Project `.governance/ROUTING.yaml` inherits this global taxonomy. It declares project context, protected surfaces, local invariants, forbidden operations, human gates, and narrow overrides. It must not duplicate general class triggers or use repository type as a blanket Quant override.

## Convergence

Every class follows:

`scope -> work -> run -> verification -> evidence -> acceptance -> DONE`

Discoveries are classified as `BLOCKER`, `BACKLOG`, or `HARDENING`. Only a `BLOCKER` interrupts the active delivery path. Do not add adjacent features or unrelated refactors before verifying the requested outcome.

## Executable reference

`tools/classify_global_task.py` is a deterministic reference implementation for the acceptance scenarios. It demonstrates the routing decision and deliberately ignores repository domain as a specialist selector. It does not replace project governance, Task Packets, Handoffs, enforcement, or human gates.
