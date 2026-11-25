#!/usr/bin/env python3
"""Validate the Pi runtime adapter against its canonical contracts.

Read-only with respect to the repository. Wrappers are generated into temporary
directories; the runtime agents directory is never touched.

Checks:

  1. the capability manifest exists, parses, and declares the fail-closed contract;
  2. every canonical specialist is declared with its canonical isolation policy;
  3. regeneration is deterministic and the provenance stamp equals canonical HEAD;
  4. every wrapper resolves its canonical role and canonical DCP sources;
  5. the tool boundary is preserved, including the read-only validator;
  6. a required capability the manifest does not satisfy yields an explicit
     CAPABILITY_BLOCKED payload and never a silent degradation;
  7. every wrapper declares the model its role maps to, and the independent
     validator runs on a different vendor from every role it reviews. While
     the generator sets a non-empty DECORRELATION_WAIVER, a failed vendor split
     is reported as WAIVED with the reason (never PASS) and is not a failure.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ADAPTER_ROOT = Path(__file__).resolve().parent
REPO_ROOT = ADAPTER_ROOT.parents[1]

MANIFEST_PATH = ADAPTER_ROOT / "capability-manifest.yaml"
GENERATOR_PATH = ADAPTER_ROOT / "generate_registration.py"
VENDORED_DCP_MARKER = "governance/core/DCP"

VALIDATOR_REQUIREMENTS = (
    "isolated_required",
    "delegation_forbidden",
    "independent_validator_context",
    "tool_restrictions",
)

SIMULATED_REQUIREMENTS = (
    "isolated_required",
    "filesystem_scope_restrictions",
)

PASSES: list[str] = []
WAIVERS: list[str] = []
FAILURES: list[str] = []


def check(condition: bool, message: str) -> bool:
    if condition:
        PASSES.append(message)
    else:
        FAILURES.append(message)
    return condition


def load_generator():
    spec = importlib.util.spec_from_file_location("gqe_pi_generator", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise SystemExit(f"FAIL: cannot load generator at {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_scalar(value: str):
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value in ("null", "~"):
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def read_manifest(path: Path) -> dict:
    """Minimal strict reader for the manifest shape this validator consumes.

    The repository keeps its validators standard-library only, so PyYAML is not
    used. The reader fails loudly on any shape it does not recognise instead of
    guessing.
    """
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        lines.append(line)

    def indentation(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def block(index: int, indent: int):
        if lines[index].strip().startswith("- "):
            items = []
            while index < len(lines):
                line = lines[index]
                if indentation(line) != indent or not line.strip().startswith("- "):
                    break
                items.append(parse_scalar(line.strip()[2:].strip()))
                index += 1
            return items, index
        mapping: dict = {}
        while index < len(lines):
            line = lines[index]
            current = indentation(line)
            if current < indent:
                break
            if current > indent:
                raise SystemExit(f"FAIL: unexpected manifest indentation: {line.strip()!r}")
            key, separator, value = line.strip().partition(":")
            if not separator:
                raise SystemExit(f"FAIL: unexpected manifest line: {line.strip()!r}")
            key = key.strip()
            value = value.strip()
            index += 1
            if value:
                mapping[key] = parse_scalar(value)
                continue
            if index < len(lines) and indentation(lines[index]) > current:
                mapping[key], index = block(index, indentation(lines[index]))
                continue
            mapping[key] = None
        return mapping, index

    parsed, _ = block(0, 0)
    if not isinstance(parsed, dict):
        raise SystemExit("FAIL: manifest root must be a mapping")
    return parsed


def canonical_specialists() -> dict[str, dict]:
    """Read the canonical specialist policy straight from SUBAGENT.md frontmatter."""
    specialists: dict[str, dict] = {}
    for path in sorted((REPO_ROOT / "agents").glob("*/SUBAGENT.md")):
        fields: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("---"):
                if fields:
                    break
                continue
            if line.startswith(" ") or ":" not in line:
                continue
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip('"')
        name = fields.get("name")
        if not name:
            raise SystemExit(f"FAIL: no name in canonical frontmatter: {path}")
        specialists[name] = fields
    return specialists


def capability_state(manifest: dict, name: str) -> tuple[bool, str | None]:
    capabilities = manifest.get("capabilities") or {}
    governance = manifest.get("governance_mapping") or {}
    if name in capabilities:
        entry = capabilities.get(name) or {}
        support = entry.get("support")
        level = entry.get("evidence_level")
        if support in ("NATIVE", "EMULATED") and level in ("VERIFIED", "DECLARED"):
            return True, None
        return False, f"support={support}, evidence_level={level}"
    if name in governance:
        entry = governance.get(name) or {}
        level = entry.get("evidence_level")
        if entry.get("supported") is True and level in ("VERIFIED", "DECLARED"):
            return True, None
        return False, f"supported={entry.get('supported')}, evidence_level={level}"
    return False, "not declared in the capability manifest"


def resolve_required(manifest: dict, required: tuple[str, ...], workflow: str) -> list[dict]:
    fail_closed = manifest.get("fail_closed") or {}
    anchors = fail_closed.get("governance_anchors") or {}
    alternatives = fail_closed.get("safe_alternatives") or {}
    blockages: list[dict] = []
    for name in required:
        satisfied, reason = capability_state(manifest, name)
        if satisfied:
            continue
        safe = alternatives.get(name) or ["No declared safe alternative; escalate to a human decision."]
        blockages.append(
            {
                "status": fail_closed.get("status_token", "CAPABILITY_BLOCKED"),
                "missing_capability": name,
                "reason": reason,
                "affected_governance_rule": anchors.get(name, "undeclared in the capability manifest"),
                "affected_workflow": workflow,
                "safe_alternatives": safe,
            }
        )
    return blockages


def generate_bundle(bundle: Path) -> dict[str, str]:
    subprocess.run(
        [sys.executable, str(GENERATOR_PATH), "--output", str(bundle)],
        check=True,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(bundle.glob("*.md"))}


def frontmatter_tools(text: str) -> list[str]:
    tools: list[str] = []
    in_tools = False
    for line in text.splitlines():
        if line.startswith("tools:"):
            in_tools = True
            continue
        if in_tools:
            if line.startswith("  - "):
                tools.append(line[4:].strip())
                continue
            break
    return tools


def main() -> int:
    generator = load_generator()

    # --- 1. capability manifest ------------------------------------------------
    if not check(MANIFEST_PATH.is_file(), "capability manifest exists"):
        report()
        return 1
    manifest = read_manifest(MANIFEST_PATH)
    check(bool(manifest.get("adapter")), "manifest declares the adapter block")
    check(bool(manifest.get("runtime")), "manifest declares the runtime block")
    check(bool(manifest.get("capabilities")), "manifest declares the capability matrix")

    fail_closed = manifest.get("fail_closed") or {}
    required_payload = fail_closed.get("required_payload") or []
    check(
        fail_closed.get("status_token") == "CAPABILITY_BLOCKED",
        "manifest declares the CAPABILITY_BLOCKED status token",
    )
    check(
        {"missing_capability", "affected_governance_rule", "affected_workflow", "safe_alternatives"}.issubset(
            set(required_payload)
        ),
        "manifest fail-closed payload covers the required identification fields",
    )
    levels = (manifest.get("evidence_levels") or {}).get("allowed") or []
    check(
        {"VERIFIED", "DECLARED", "UNVERIFIED", "UNSUPPORTED"}.issubset(set(levels)),
        "manifest distinguishes VERIFIED, DECLARED, UNVERIFIED and UNSUPPORTED",
    )

    isolation = manifest.get("isolation_semantics") or {}
    check(
        isolation.get("demonstrated_scope") == "PROCESS_AND_CONTEXT",
        "manifest scopes demonstrated isolation to process and context",
    )
    check(
        bool(isolation.get("not_demonstrated")),
        "manifest states explicitly what isolation is not demonstrated",
    )

    # --- 2. canonical specialist coverage --------------------------------------
    canonical = canonical_specialists()
    declared = manifest.get("specialist_support") or {}
    declared_specialists = {k: v for k, v in declared.items() if isinstance(v, dict)}
    check(
        {_key(name) for name in canonical} == set(declared_specialists),
        f"manifest covers exactly the canonical specialists ({len(canonical)} declared)",
    )
    policy_mismatch = [
        name
        for name, fields in canonical.items()
        if (declared_specialists.get(_key(name)) or {}).get("isolation") != fields.get("context")
    ]
    check(not policy_mismatch, f"manifest isolation policy matches canonical SUBAGENT.md{_detail(policy_mismatch)}")
    validator_policy = declared_specialists.get("quant_validator") or {}
    check(
        validator_policy.get("isolation") == "ISOLATED_REQUIRED",
        "manifest keeps quant-validator at ISOLATED_REQUIRED",
    )
    check(
        validator_policy.get("tool_boundary") == "READ_ONLY",
        "manifest records the quant-validator read-only tool boundary",
    )
    general = [name for name in canonical if not name.startswith("quant-")]
    check(
        all(
            (declared_specialists.get(_key(name)) or {}).get("isolation") == "ISOLATED_PREFERRED"
            for name in general
        ),
        f"manifest keeps general specialists at ISOLATED_PREFERRED ({len(general)} checked)",
    )

    # --- 3. deterministic regeneration and provenance ---------------------------
    with tempfile.TemporaryDirectory(prefix="gqe-pi-validate-a-") as first:
        with tempfile.TemporaryDirectory(prefix="gqe-pi-validate-b-") as second:
            bundle_a = generate_bundle(Path(first) / "bundle")
            bundle_b = generate_bundle(Path(second) / "bundle")
    check(
        bundle_a == bundle_b,
        "two independent generations from identical canonical inputs are byte-identical",
    )
    check(
        set(bundle_a) == {f"{name}.md" for name in generator.SPECIALISTS},
        f"bundle contains exactly the {len(generator.SPECIALISTS)} canonical specialist wrappers",
    )

    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()
    stamps = {}
    for name, text in bundle_a.items():
        match = re.search(r"Canonical commit: `([0-9a-f]{40,64})`", text)
        stamps[name] = match.group(1) if match else None
    drifted = [name for name, stamp in stamps.items() if stamp != head]
    check(
        not drifted,
        f"provenance stamp equals canonical HEAD {head[:12]}{_detail(drifted)}",
    )

    # --- 4. canonical role and DCP propagation ---------------------------------
    missing_role_paths = [
        name
        for name, text in bundle_a.items()
        if f"{generator.CANONICAL_ROOT}/agents/{name[:-3]}/ROLE.md" not in text
        or f"{generator.CANONICAL_ROOT}/agents/{name[:-3]}/SUBAGENT.md" not in text
    ]
    check(not missing_role_paths, f"all wrappers resolve their canonical role contracts{_detail(missing_role_paths)}")

    missing_dcp_paths = [
        name
        for name, text in bundle_a.items()
        if any(f"{generator.DCP_ROOT}/{part}" not in text for part in generator.DCP_PARTS)
    ]
    check(
        not missing_dcp_paths,
        f"all wrappers reference the {len(generator.DCP_PARTS)} canonical DCP sources{_detail(missing_dcp_paths)}",
    )
    vendored = [name for name, text in bundle_a.items() if VENDORED_DCP_MARKER in text]
    check(not vendored, f"no wrapper points at the non-authoritative vendored DCP copy{_detail(vendored)}")

    # --- 5. tool boundary -------------------------------------------------------
    wrong_tools = []
    for name, text in bundle_a.items():
        specialist = name[:-3]
        expected = list(generator.WRAPPER_TOOLS.get(specialist, generator.DEFAULT_TOOLS))
        if frontmatter_tools(text) != expected:
            wrong_tools.append(specialist)
    check(not wrong_tools, f"every wrapper preserves its declared tool allowlist{_detail(wrong_tools)}")

    validator_tools = set(frontmatter_tools(bundle_a["quant-validator.md"]))
    check(
        not validator_tools & {"edit", "write"},
        "the quant-validator wrapper grants no write or edit tool",
    )
    check(
        validator_tools == {"read", "grep", "find", "bash"},
        "the quant-validator wrapper retains exactly its read-only tool set",
    )
    spawn_tools = {"agent", "subagent", "subagent_run", "task", "delegate"}
    spawners = [
        name
        for name, text in bundle_a.items()
        if set(frontmatter_tools(text)) & spawn_tools
    ]
    check(not spawners, f"no wrapper grants an agent-spawning tool{_detail(spawners)}")

    # --- 6. capability resolution and CAPABILITY_BLOCKED simulation -------------
    satisfied = resolve_required(manifest, VALIDATOR_REQUIREMENTS, "quant-validator independent validation")
    check(
        not satisfied,
        f"a required validator capability set resolves without a blockage "
        f"({', '.join(VALIDATOR_REQUIREMENTS)})",
    )

    simulated = resolve_required(manifest, SIMULATED_REQUIREMENTS, "quant-validator independent validation (simulation)")
    check(
        len(simulated) == 1,
        "a required-but-unsatisfied capability yields exactly one blockage and is never silently dropped",
    )
    if simulated:
        blockage = simulated[0]
        check(
            blockage["status"] == "CAPABILITY_BLOCKED",
            "the blockage carries the CAPABILITY_BLOCKED status token",
        )
        check(
            blockage["missing_capability"] == "filesystem_scope_restrictions",
            "the blockage identifies the missing capability",
        )
        empty = [key for key in required_payload if not blockage.get(key)]
        check(not empty, f"the blockage payload is complete{_detail(empty)}")
        print("--- simulated capability blockage ---")
        for key in ("status", "missing_capability", "reason", "affected_governance_rule", "affected_workflow"):
            print(f"{key}: {blockage[key]}")
        for alternative in blockage["safe_alternatives"]:
            print(f"safe_alternative: {alternative}")
        print("---")

    # --- 7. model assignment and verification decorrelation ---------------------
    expected_models = {
        f"{name}.md": generator.WRAPPER_MODELS.get(name, generator.DEFAULT_MODEL)
        for name in generator.SPECIALISTS
    }
    wrong_models = [
        name
        for name, text in bundle_a.items()
        if frontmatter_model(text) != expected_models.get(name)
    ]
    check(
        not wrong_models,
        f"every wrapper declares the model its role maps to{_detail(wrong_models)}",
    )

    inheriting = [name for name, text in bundle_a.items() if not frontmatter_model(text)]
    check(
        not inheriting,
        f"no wrapper silently inherits the session model{_detail(inheriting)}",
    )

    auditor_model = frontmatter_model(bundle_a["quant-validator.md"])
    reviewed_models = {
        frontmatter_model(text)
        for name, text in bundle_a.items()
        if name != "quant-validator.md"
    }
    decorrelated = (
        auditor_model is not None
        and all(model is not None for model in reviewed_models)
        and all(
            model_vendor(model or "") != model_vendor(auditor_model)
            for model in reviewed_models
        )
    )
    decorrelation_message = (
        "the independent validator runs on a different vendor from every role it reviews "
        f"(validator={auditor_model}, reviewed={sorted(m for m in reviewed_models if m)})"
    )
    waiver = getattr(generator, "DECORRELATION_WAIVER", None)
    if not decorrelated and isinstance(waiver, str) and waiver.strip():
        WAIVERS.append(f"NOT satisfied, temporarily waived: {decorrelation_message} \u2014 reason: {waiver}")
    else:
        check(decorrelated, decorrelation_message)

    return report()


def frontmatter_model(text: str) -> str | None:
    """Model declared in a wrapper frontmatter block, or None when it inherits."""
    parts = text.split("---")
    if len(parts) < 3:
        return None
    for line in parts[1].splitlines():
        if line.startswith("model:"):
            return line.partition(":")[2].strip()
    return None


def model_vendor(model: str) -> str:
    """Vendor token of a provider-qualified id: `provider/vendor-model` or `provider/vendor/model`."""
    identifier = model.partition("/")[2] or model
    return identifier.partition("/")[0].partition("-")[0]


def _key(name: str) -> str:
    return name.replace("-", "_")


def _detail(items: list) -> str:
    return "" if not items else f" (offending: {', '.join(map(str, items))})"


def report() -> int:
    for message in PASSES:
        print(f"PASS: {message}")
    for message in WAIVERS:
        print(f"WAIVED: {message}")
    for message in FAILURES:
        print(f"FAIL: {message}")
    if FAILURES:
        print(f"FAIL: Pi adapter validation failed ({len(FAILURES)} checks)")
        return 1
    waived = f", {len(WAIVERS)} waived" if WAIVERS else ""
    print(f"PASS: Pi adapter validation ({len(PASSES)} checks{waived})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
