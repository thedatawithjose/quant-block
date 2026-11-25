import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, realpathSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { decide, loadPolicy, quantModeFromInput } from "./core.ts";
import { completionEnabled } from "./completion.ts";
import { auditRecord } from "./audit.ts";

function project(policy: Record<string, unknown>): string {
	const root = realpathSync(mkdtempSync(join(tmpdir(), "qmode-")));
	mkdirSync(join(root, ".governance"));
	mkdirSync(join(root, "data"));
	writeFileSync(join(root, ".governance", "quant-gate.json"), JSON.stringify(policy));
	return root;
}
const POLICY = { protected: ["data/raw.db"], orchestrator_restricted: "quant-mode", completion_gate: "quant-mode" };
const call = (root: string, toolName: string, input: Record<string, unknown>, isChild: boolean, quantMode?: boolean) =>
	decide({ root, toolName, input, isChild, env: {}, quantMode });

test("with orchestrator_restricted 'quant-mode' the orchestrator is free until the mode is on", () => {
	const root = project(POLICY);
	assert.equal(call(root, "write", { path: "data/x.csv" }, false, undefined).block, false);
	assert.equal(call(root, "write", { path: "data/x.csv" }, false, false).block, false);
	assert.equal(call(root, "bash", { command: "echo x > data/x.csv" }, false, false).block, false);
	assert.equal(call(root, "write", { path: "data/x.csv" }, false, true).block, true);
	assert.equal(call(root, "bash", { command: "echo x > data/x.csv" }, false, true).block, true);
	assert.equal(call(root, "write", { path: "odd/tasks/a.md" }, false, true).block, false);
});

test("protected paths apply in every mode, for orchestrator and subagent", () => {
	const root = project(POLICY);
	for (const quantMode of [undefined, false, true]) {
		for (const isChild of [false, true]) {
			assert.equal(call(root, "write", { path: "data/raw.db" }, isChild, quantMode).block, true, `${quantMode} ${isChild}`);
			assert.equal(call(root, "bash", { command: "rm data/raw.db" }, isChild, quantMode).block, true, `${quantMode} ${isChild}`);
		}
	}
});

test("a subagent is never restricted by the quant-mode rule", () => {
	const root = project(POLICY);
	assert.equal(call(root, "write", { path: "data/x.csv" }, true, true).block, false);
});

test("orchestrator_restricted true and false keep their old meaning regardless of mode", () => {
	const always = project({ protected: [], orchestrator_restricted: true });
	assert.equal(call(always, "write", { path: "data/x.csv" }, false, false).block, true);
	const never = project({ protected: [], orchestrator_restricted: false });
	assert.equal(call(never, "write", { path: "data/x.csv" }, false, true).block, false);
});

test("policy values: 'quant-mode' accepted, other strings invalid", () => {
	const ok = loadPolicy(project(POLICY));
	assert.ok(ok.status === "ok" && ok.policy.orchestratorRestricted === "quant-mode" && ok.policy.completionGate === "quant-mode");
	assert.equal(loadPolicy(project({ orchestrator_restricted: "always" })).status, "invalid");
	assert.equal(loadPolicy(project({ completion_gate: "sometimes" })).status, "invalid");
});

test("completionEnabled resolves the three policy values", () => {
	assert.equal(completionEnabled(true, false), true);
	assert.equal(completionEnabled(false, true), false);
	assert.equal(completionEnabled("quant-mode", true), true);
	assert.equal(completionEnabled("quant-mode", false), false);
});

test("quantModeFromInput follows /quant-mode, off and status", () => {
	assert.equal(quantModeFromInput("/quant-mode", false), true);
	assert.equal(quantModeFromInput("/quant-mode on", false), true);
	assert.equal(quantModeFromInput("  /quant-mode  ", false), true);
	assert.equal(quantModeFromInput("/quant-mode off", true), false);
	assert.equal(quantModeFromInput("/quant-mode status", true), true);
	assert.equal(quantModeFromInput("/quant-mode status", false), false);
	assert.equal(quantModeFromInput("hacé algo normal", true), true);
	assert.equal(quantModeFromInput("hacé algo normal", false), false);
	assert.equal(quantModeFromInput("explicame /quant-mode off", true), true);
	assert.equal(quantModeFromInput("/quant-modes", false), false);
});

test("audit supports a mode record", () => {
	const r = auditRecord({ kind: "mode", isChild: false, decision: "on" });
	assert.equal(r.kind, "mode");
	assert.equal(r.decision, "on");
});
