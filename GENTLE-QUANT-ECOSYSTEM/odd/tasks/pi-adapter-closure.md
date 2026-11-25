# Feature: pi-adapter-closure

Branch: `fix/pi-adapter-closure`
Base: `bf1ebe8`
Commit: single work unit, `fix(pi): declare runtime capabilities and correct wrapper provenance`

## Objective

Close the two Pi runtime adapter defects confirmed by the read-only Gentle runtime smoke test.

1. `adapters/pi/` provided no capability manifest, so the runtime capability
   declarations required by `adapters/RUNTIME-ADAPTER-SPEC.md` §2, §12 and §14 were
   absent for the Pi adapter.
2. Generated Pi specialist wrappers stamped `Canonical commit: 2421aeb` while their
   content corresponded to `bf1ebe8`. The generator resolved Git `HEAD` unconditionally,
   so a generation performed from a working tree with uncommitted canonical inputs
   recorded a revision that did not describe the emitted content.

## Non-goals

- No modification of CIMA, Chartpy, or any consuming project repository.
- No modification of Quant workflows, specialist roles, DCP semantics, routing logic,
  providers, models, or Engram.
- No redesign of Pi integration beyond the two defects above.
- No additional hardening beyond what the two defects require.

## Scope surfaces

- `adapters/pi/generate_registration.py`
- `adapters/pi/capability-manifest.yaml` (new)
- `adapters/pi/validate_registration.py` (new)
- Deployment target `~/.pi/agent/agents/` is a runtime deployment artifact, not canonical authority.

## Tasks

| # | Task | Status | Evidence |
|---|---|---|---|
| 1 | Record runtime backup path and canonical-input cleanliness model | DONE | Existing backups `agents.bak-20260927T150357`, `agents.bak-20260927T150820`; the DCP root is not a Git worktree, so DCP provenance is hash-based |
| 2 | Create feature branch in GQE | DONE | `fix/pi-adapter-closure` from `bf1ebe8` |
| 3 | Write ODD task doc | DONE | this file |
| 4 | Fix provenance generation | DONE | Generator now stamps the real canonical revision and fails closed; see below |
| 5 | Add Pi capability manifest | DONE | `adapters/pi/capability-manifest.yaml` |
| 6 | Add Pi adapter validation suite | DONE | `adapters/pi/validate_registration.py`, 29 checks |
| 7 | Run verification suite | DONE | see below |
| 8 | Regenerate and reinstall wrappers | DONE | performed in this work unit; installer prints `backup=<path>` |
| 9 | Commit work unit, confirm GQE clean | DONE | this commit; `git status` clean afterwards |

## Task 4 evidence — provenance is now fail-closed

`generate_registration.py` refuses to emit any wrapper unless the stamp it writes
actually describes the content:

- Uncommitted canonical input — the exact original defect condition:

  ```
  M agents/USER-INTERACTION-POLICY.md
  ERROR: canonical inputs are not committed at HEAD; refusing to stamp a
  revision that does not describe the generated content
  exit=1, wrappers emitted=0
  ```

- DCP drift, verified for all three parts and for a missing record under §7 of
  `USER-INTERACTION-POLICY.md`: every case aborts with `DCP provenance drift for
  <part>: recorded ..., observed ...`.
- Clean tree: stamp is the real revision, `source_commit=bf1ebe8912d5f69764f924e288d78b1774367f2e`.

The originality condition matters: `bf1ebe8` itself modified
`agents/USER-INTERACTION-POLICY.md`, so the previous stamp was produced from a dirty
canonical tree. That condition is now a hard failure rather than a silent falsehood.

## Task 5 evidence — capability manifest

`adapters/pi/capability-manifest.yaml`, schema v1.0, runtime Pi 0.87.1, maturity
`VALIDATING`, compatibility `SUPPORTED_WITH_LIMITATIONS`.

Declares, with an explicit `evidence_levels` vocabulary of `VERIFIED`, `DECLARED`,
`UNVERIFIED` and `UNSUPPORTED`:

- specialist child-context support and the separate-session behaviour Pi actually provides;
- `ISOLATED_PREFERRED` and `ISOLATED_REQUIRED` support status;
- specialist self-delegation restriction;
- per-specialist write-tool differences, including the quant-validator read-only boundary;
- how `CAPABILITY_BLOCKED` is produced, with the resolution rule, the required
  identification payload, governance anchors, and declared safe alternatives.

`isolation_semantics` states the demonstrated scope is `PROCESS_AND_CONTEXT` and lists
what is **not** demonstrated: model independence, provider independence, statistical
independence, and absence of cross-role shared memory. Independent validation under Pi
is therefore recorded as an independent context and tool boundary over the same model
family, and must not be presented as independent corroboration.

## Task 6 and 7 evidence — validation suite

`python3 adapters/pi/validate_registration.py` → `PASS: Pi adapter validation (29 checks)`, exit 0.

Covered: manifest presence and fail-closed contract; manifest covers exactly the
canonical specialists with isolation policy matching canonical `SUBAGENT.md`; two
independent generations byte-identical; provenance stamp equals canonical HEAD; every
wrapper resolves its canonical role contracts and the three canonical DCP sources and
none points at the vendored copy; every wrapper preserves its declared tool allowlist;
quant-validator keeps exactly `read, grep, find, bash` with no write tool; no wrapper
grants an agent-spawning tool.

The `CAPABILITY_BLOCKED` simulation resolves a required-but-unsatisfied capability and
observes exactly one explicit blockage, never a silent drop:

```
status: CAPABILITY_BLOCKED
missing_capability: filesystem_scope_restrictions
reason: support=UNAVAILABLE, evidence_level=DECLARED
affected_governance_rule: adapters/RUNTIME-ADAPTER-SPEC.md section 2 (Required Runtime Capabilities)
affected_workflow: quant-validator independent validation (simulation)
safe_alternative: Constrain the specialist task text to an explicit allowed path set ...
safe_alternative: Execute the work on a runtime adapter that declares filesystem scope enforcement.
```

Regression and routing unchanged:

- `tools/validate_dcp_inheritance.py` → PASS, 8/8 specialists inherit policy
- `tools/validate_global_routing.py` → PASS A–E
- UI sidebar probe → `UI_UX` / `ui-ux-engineer`, `domain_used_as_selector=false`
- fill timing probe → `QUANT_IMPLEMENTATION` / `quant-developer` + `quant-validator`

## Observed probe evidence (pre-implementation)

Read-only probe of the `quant-validator` specialist, used as manifest evidence:

- Parent conversation history visible to the child: `NONE VISIBLE`
- Effective tool set: `read`, `grep`, `find`, `bash`, `subagent_parent_message`
- Child-spawning capability: none; only a bounded parent-notification channel
- Write capability: none
- Canonical paths resolved: 4 GQE contracts + 3 canonical DCP documents

Two consequences feed the manifest:

- `ISOLATED_REQUIRED` is demonstrated at process/context scope only. Model and
  statistical independence are not demonstrated and are declared as such.
- `subagent_parent_message` is injected by the runtime and is absent from the wrapper's
  declared `tools:` list, so a declared list must not be read as the effective set.
