# Legacy harness migration inventory

Prepared material only: **no Hyperion integration, no extracted implementation, no external installation changes**. Sources are complete, byte-identical snapshots, not an installed harness. All paths below are relative to this directory unless absolute. `~` means `/home/datawithjose`.

## Verify the copies

`COPY-MANIFEST.json` records **every copied file**: absolute original, relative destination, SHA-256 and group. `ACTIVE-BASELINE.json` records original hashes plus consulted Pi settings (settings content is not copied). `GIT-BASELINE.txt` records the initially clean nested repository. See `verification/RESULTS.md` for execution outcomes.

| Material | Original | Destination | Dependencies and tests |
|---|---|---|---|
| Python engine, complete | `~/Documents/harness-quant/quant_harness_v2/quant_agent_harness.py` | `core/source/quant_harness_v2/quant_agent_harness.py` and `domains/quant/source/quant_harness_v2/quant_agent_harness.py` | Python 3.11+, standard library SQLite, POSIX `fcntl`; complete `tests/test_harness.py` in both copies |
| Synthetic executable adapter | `~/Documents/harness-quant/quant_harness_v2/demo.py` | Same filename under both Python source directories | Imports engine; imported by regression tests; retained as unique causal adapter, not obsolete demo |
| Temporal invariance helper | `~/Documents/harness-quant/quant_harness_v2/causality_checks.py` | Same filename under both Python source directories | Standard library; imported by tests and exercised against causal/leaky traces |
| Regression suite | `~/Documents/harness-quant/quant_harness_v2/tests/test_harness.py` | Same relative path under both Python source directories | Imports engine, demo and causality helper; fake executor/LLM, temporary SQLite state |
| Supporting documentation/evidence | `~/Documents/harness-quant/quant_harness_v2/{README.md,VALIDATION.md,TEST_RESULTS.txt,examples/synthetic_demo_report.json,.gitignore}` | Same relative paths under both Python source directories | README lists captured outputs as delivery evidence; retain timestamps/run IDs, do not treat them as disposable build output |
| Task contract specification | `~/Documents/GENTLE-QUANT-ECOSYSTEM/agents/TASK-PACKET-CONTRACT-SPEC.md` | `contracts/agents/TASK-PACKET-CONTRACT-SPEC.md` | References role/subagent/handoff/user-interaction contracts and governance/DCP sources; specification, not executable validation |
| Task contract template | `~/Documents/GENTLE-QUANT-ECOSYSTEM/templates/tasks/TASK-PACKET.template.yaml` | `contracts/templates/tasks/TASK-PACKET.template.yaml` | Same external specification dependencies; retained without normalization |
| Pi hook entrypoint | `~/.pi/agent/extensions/quant-gate/index.ts` | `adapters/pi/extensions/quant-gate/index.ts` | Pi ExtensionAPI type, `core.ts`, `completion.ts`, `audit.ts`; actual live Pi loading not established |
| Path policy and mode | `~/.pi/agent/extensions/quant-gate/core.ts` | `adapters/pi/extensions/quant-gate/core.ts` | Node built-ins and `audit.ts`; `core.test.ts`, `mode.test.ts` |
| Completion reminders | `~/.pi/agent/extensions/quant-gate/completion.ts` | `adapters/pi/extensions/quant-gate/completion.ts` | Node built-ins; `completion.test.ts`; legacy checkbox parsing retained as reference |
| Best-effort audit | `~/.pi/agent/extensions/quant-gate/audit.ts` | `adapters/pi/extensions/quant-gate/audit.ts` | Node built-ins; `audit.test.ts`; append failures return false, not equivalent to Python fail-propagating Store |
| Protection helper | `~/.pi/agent/extensions/quant-gate/protect.py` | `adapters/pi/extensions/quant-gate/protect.py` | Python/filesystem permissions; referenced by prompt; not executed against any project |
| Pi tests | `~/.pi/agent/extensions/quant-gate/{core.test.ts,completion.test.ts,audit.test.ts,mode.test.ts}` | Same filenames under `adapters/pi/extensions/quant-gate/` | Node with TypeScript stripping; no dependencies installed |
| Operational prompt, complete | `~/.pi/agent/prompts/quant-mode.md` | `adapters/pi/prompts/quant-mode.md` | Preflight helper, interval file, external GQE canon, quant-gate/protect paths; copied as data, not activated |

The two Python snapshots intentionally duplicate one origin so each destination retains a runnable source/test unit. They are **not** separate future implementations. Extract shared core once during a later integration task. No requested source path moved or required a substitute.

## Core extraction map

Line references refer to the unchanged `quant_agent_harness.py` in either Python snapshot.

| Symbols | Source lines | Reusable mechanism and boundary |
|---|---|---|
| `canonical`, `digest` | 32–39 | Deterministic JSON/hash helpers used by identity, requests and audit |
| `Store.__init__`, `guard`, `atomic` | 226–273 | SQLite WAL, FULL synchronous writes, append-only triggers; thread mutex and POSIX process file lock; BEGIN IMMEDIATE, COMMIT, rollback on BaseException. Callers supply locking; do not assume all operations share a transaction |
| `Store.get`, `put`, `event`, `verify`, `export_audit`, `close` | 274–308 | Persistent JSON state, chained events, sequential validation and JSONL export. Not an external signature; privileged rebuild or tail removal is not prevented |
| `Harness.__init__` | 423–457 | Persisted identity of config/registry/mode/limits/account; reopen mismatch rejects, phase/identity initialization is transactional |
| `Harness._capacity`, `_run` | 494–546 | Persistent backtest-attempt budget; attempt and STARTED state committed before adapter execution, so failure remains charged |
| `Harness.call`, `run` | 750 onward | Persistent tool-call and LLM-call counters plus audited calls. `run` also contains the optional Anthropic-specific loop: reference only, not portable core |

Keep the entire source now: Store/identity/counters are intertwined with research/order gates, tools and provider loop. Tests around lines 96–144 and 299–342 exercise restart identity, budgets and audit tamper detection. Do not infer direct coverage for isolated `Store.atomic` rollback or exported JSONL contents: no dedicated tests observed for these. Optional `anthropic` is imported only for the real provider client; offline tests use a stub. No dependency lockfile/package manifest exists in this Python unit; no new dependency was added.

## Quant domain extraction map

| Symbols | Source lines | Domain behavior and tests |
|---|---|---|
| `Costs`, `ResearchConfig`, `RunRequest`, `RunResult`, `Backtester` | 87–162 | Immutable boundaries, dataset/engine provenance, seed, costs, bar-close and NEXT_EVENT contract; adapter returns net returns and completed round trips |
| `utc`, `Harness._window`, `_run` | 54–69, 482–489, 498–546 | UTC, exclusive-end windows, ordered/nonoverlapping closed bars, dimension/provenance/finite-return validation |
| `Harness._stress_test` | 595–611 | Reruns engine at increased costs; tests around 175 onward; not a synthetic penalty on a previously calculated score |
| `Harness._final_validate`, `_research_open` | 612–638, 490–493 | Requires researched baseline, fixed holdout/costs, persists HOLDOUT_COMMITTED before execution. Failure consumes the holdout; success FINALIZED freezes research across restart |
| `metrics`, `block_bootstrap` | 165–223 | Supporting numerical logic used by engine and holdout report; preserve numerical regression tests |
| `SyntheticBacktester`, `signals` | `demo.py:28–80` | Prior-bar decisions, friction/funding approximation and boundary liquidation; unique runnable example and regression dependency |
| `assert_closed_bar_causality` | `causality_checks.py:6` | Determinism, prefix and current/future mutation probes; does not certify fills/accounting/cross-timeframe behavior |

Relevant tests: persistence/holdout/concurrency at `tests/test_harness.py:96–144`; cost stress near 175; numerical/temporal/demo/subprocess checks in `QuantTests` at 345 onward. Metadata equality cannot prove that a third-party engine actually applies the declared costs or executes causally. Synthetic results do not establish trading validity. Execution/risk/broker protocols remain in the full reference source but are not integrated or activated.

## Contract fields worth reusing later

| Purpose | Original fields |
|---|---|
| Identity/version | `schema_version`, `task_packet.task_id`, `task_version`, `project`, `assigned_role`, `created_at`, `status` |
| Objective/closure criteria | `objective.requested_outcome`, `reason`, `definition_of_completion`, `intended_downstream_consumer` |
| Scope | `scope.in_scope`, `out_of_scope`, `prohibited_changes`; `invariants.applicable`, `critical`, `preservation_required`, `known_conflicts` |
| Authoritative inputs and version evidence | `authoritative_inputs` (example `version`, `git_commit`, `hash`, `fingerprint`), `upstream_handoffs`, `change_control` |
| Checks/evidence | `required_outputs`, `verification.required_checks`, `not_applicable_checks`, `evidence_required`, `evidence_requirements` |
| Approval/authority | `authority`, `governance`, `human_authority.decisions_required`, `approval_already_granted`, `inferred_approval_allowed: false` |
| Execution/handoff/readiness | `execution.allowed_terminal_states`, `current_state`, timestamps; `downstream`; `completion_gate.ready_for_execution`, `blocking_reasons` |

These fields are a design input, not an existing executable closure mechanism or proof bound to a change. `completion_gate` in the template means readiness for execution, not independently verified final closure. Preserve discrepancies: the specification requires a `user_interaction_policy` block with observed DCP hashes, while the template supplies paths under `authority` without those hashes; its role enum lists only four quant specialists although the specification admits general specialists too. Referenced contracts are external dependencies, not silently resolved or integrated here.

## Pi boundaries: actual interception, not claimed sandboxing

- `core.ts:91` `canon`: folds `..`, resolves existing symlink ancestors, appends nonexistent tail. `entryMatches`, `isProtected`, `orchestratorMayNotWrite` use canonical paths. `core.test.ts:56–62` covers absolute paths, `..` and existing symlinks; no dedicated nonexistent-tail test was observed.
- `index.ts` hooks `input` (14), `before_agent_start` (24), `agent_before_settle` (33), `tool_call` (70).
- Normal policy interception in `decide` covers bare/namespaced **write/edit** matching `/(^|__)(write|edit)$/`, with `path` or `file_path`. Bash inspection requires the exact tool name **`bash`**, using `input.command`; it is inline-command best effort, not arbitrary script analysis. It does not generally intercept `bash_background`, other mutation tools or all namespaced bash tools. Exception handling in `index.ts` uses the broader `/(^|__)(write|edit|bash)$/` fail-closed pattern.
- No policy means allow; `QUANT_GATE=off` bypasses; invalid policy blocks write/edit but does not generally block bash. Policy protection, root lookup, child mode and orchestrator writable paths are runtime dependencies. This is not a general execution sandbox.
- Completion reads recently modified task documents, sends bounded continues then a warning; children and non-completed outcomes bypass. Checkbox parsing is a legacy reminder, not authoritative closure.
- Prompt sections: `off/status/activate` dispatch and preflight; canonical-source loading; status markers/context reminders; hourly `quant-mode reassert` timer; specialist routing; finish-rule checklist reminders. The prompt references `~/.pi/agent/quant-mode/preflight.py`, `interval_seconds`, GQE canon and `quant-gate/protect.py`. None was activated by this migration.
- Pi `settings.json` was inspected for loading references; it does not explicitly register quant-gate. Presence plus prompt references does not establish actual runtime loading. Live hook registration, OS protection and human-approval behavior remain unverified.

## Cleanup ledger

### Copied

30 source/test/documentation files; every exact original/destination/hash is in `COPY-MANIFEST.json`. Original external installations are consulted/copied only. No secrets/configuration payloads or `.git` internals copied.

### Deleted

See `DELETED.json`: exact paths, pre-deletion hashes, size and regeneration rationale. Scope is only untracked CPython bytecode caches with their original `.py` sources retained. No database, audit export, report, Git object or recorded validation evidence qualifies for deletion.

### Archived

**None.** No obsolete, unreferenced source/documentation or replaced demo was confirmed. No archive move is justified merely by age or filename. If later archival is approved, preserve paths relative to `~/Documents/harness-quant/`; current snapshots are reusable source copies, not an assertion that the active code is obsolete.

### Retained because of active references or evidence

- `quant_harness_v2/demo.py` and `causality_checks.py`: test imports require them; demo is also a documented entrypoint.
- `quant_agent_harness.py`: demo/tests import it; Anthropic loop remains embedded and optional. No surgical deletion attempted.
- `TEST_RESULTS.txt` and `examples/synthetic_demo_report.json`: documented delivery evidence, even though new reports can be generated. New run IDs/timestamps are not the original evidence.
- External quant-gate modules: `index.ts` imports core/completion/audit; prompt references extension/protection helper and GQE canon. They stay in place; external installations are not cleanup targets.
- External task specification/template: retained at original paths; referenced from the prompt/canonical workflow. No GQE references to `harness-quant`/`quant_harness` were found in scoped search, which is not proof that no other consumer exists.

## Verification limits

Hash equality verifies copy integrity, not future portability or correct extraction. Active source/settings hashes plus nested Git status verify this task did not alter recorded active references. Python and Node tests exercise preserved offline behaviors in isolated copies; they do not verify the live Pi host, an external backtester, broker, real provider API, future Hyperion integration or every external consumer. No network API, broker, chmod/protect or Quant-mode activation is required for this task.
