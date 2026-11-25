import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, symlinkSync, realpathSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { decide, findRoot } from "./core.ts";

function project(policy?: unknown | string): string {
	const root = realpathSync(mkdtempSync(join(tmpdir(), "qgate-")));
	mkdirSync(join(root, "data"));
	mkdirSync(join(root, "odd"));
	mkdirSync(join(root, ".governance"));
	writeFileSync(join(root, "data", "raw_candles.csv"), "ts\n");
	if (policy !== undefined) {
		const text = typeof policy === "string" ? policy : JSON.stringify(policy);
		writeFileSync(join(root, ".governance", "quant-gate.json"), text);
	}
	return root;
}
const POLICY = { protected: ["data/raw_candles.csv"] };
const orch = (root: string, toolName: string, input: Record<string, unknown>, env = {}) =>
	decide({ root, toolName, input, isChild: false, env });
const child = (root: string, toolName: string, input: Record<string, unknown>, env = {}) =>
	decide({ root, toolName, input, isChild: true, env });

test("no policy file: gate is off and findRoot returns undefined", () => {
	const root = project();
	assert.equal(findRoot(join(root, "data")), undefined);
	assert.equal(orch(root, "write", { path: "data/x.csv" }).block, false);
});

test("findRoot walks up to the directory holding the policy", () => {
	const root = project(POLICY);
	assert.equal(findRoot(join(root, "data")), root);
});

test("invalid policy fails closed for write and edit", () => {
	const root = project("{not json");
	const d = child(root, "write", { path: "data/x.csv" });
	assert.equal(d.block, true);
	assert.match((d as { reason: string }).reason, /invalid/i);
	assert.equal(child(root, "edit", { path: "data/x.csv" }).block, true);
});

test("protected file cannot be written or edited by anyone", () => {
	const root = project(POLICY);
	for (const fn of [orch, child]) {
		for (const tool of ["write", "edit"]) {
			const d = fn(root, tool, { path: "data/raw_candles.csv" });
			assert.equal(d.block, true, `${fn.name} ${tool}`);
			assert.match((d as { reason: string }).reason, /protected/i);
		}
	}
});

test("protected path is caught through absolute path, .. and symlink", () => {
	const root = project(POLICY);
	assert.equal(child(root, "write", { path: join(root, "data/raw_candles.csv") }).block, true);
	assert.equal(child(root, "write", { path: "data/../data/raw_candles.csv" }).block, true);
	symlinkSync(join(root, "data", "raw_candles.csv"), join(root, "data", "link.csv"));
	assert.equal(child(root, "write", { path: "data/link.csv" }).block, true);
});

test("subagent may write non-protected files", () => {
	const root = project(POLICY);
	assert.equal(child(root, "write", { path: "data/clean_candles.csv" }).block, false);
});

test("orchestrator may write only under odd/ by default", () => {
	const root = project(POLICY);
	assert.equal(orch(root, "write", { path: "odd/tasks/x.md" }).block, false);
	const d = orch(root, "write", { path: "data/clean.csv" });
	assert.equal(d.block, true);
	assert.match((d as { reason: string }).reason, /subagent/i);
	assert.equal(orch(root, "write", { path: "odd/../data/clean.csv" }).block, true);
	assert.equal(orch(root, "write", { path: "/tmp/outside.txt" }).block, true);
});

test("orchestrator_restricted false lifts the orchestrator rule only", () => {
	const root = project({ ...POLICY, orchestrator_restricted: false });
	assert.equal(orch(root, "write", { path: "data/clean.csv" }).block, false);
	assert.equal(orch(root, "write", { path: "data/raw_candles.csv" }).block, true);
});

test("orchestrator_writable overrides the default", () => {
	const root = project({ ...POLICY, orchestrator_writable: ["odd/", "notes/"] });
	assert.equal(orch(root, "write", { path: "notes/a.md" }).block, false);
});

test("policy file is protected even when not listed", () => {
	const root = project(POLICY);
	assert.equal(child(root, "write", { path: ".governance/quant-gate.json" }).block, true);
});

test("the gate's own code is protected", () => {
	const root = project(POLICY);
	const own = join(process.env.HOME ?? "", ".pi/agent/extensions/quant-gate/core.ts");
	assert.equal(child(root, "edit", { path: own }).block, true);
});

test("QUANT_GATE=off switches the gate off", () => {
	const root = project(POLICY);
	assert.equal(child(root, "write", { path: "data/raw_candles.csv" }, { QUANT_GATE: "off" }).block, false);
});

test("other tools are untouched", () => {
	const root = project(POLICY);
	assert.equal(orch(root, "read", { path: "data/raw_candles.csv" }).block, false);
	assert.equal(orch(root, "subagent_run", { agent: "x" }).block, false);
});

const BASH_BLOCKED = [
	"echo x > data/raw_candles.csv",
	"echo x >> data/raw_candles.csv",
	"cat a | tee data/raw_candles.csv",
	"rm data/raw_candles.csv",
	"rm -f ./data/raw_candles.csv",
	"mv data/raw_candles.csv /tmp/x",
	"cp /tmp/x data/raw_candles.csv",
	"sed -i s/a/b/ data/raw_candles.csv",
	"truncate -s 0 data/raw_candles.csv",
	"dd if=/dev/zero of=data/raw_candles.csv",
	"chmod 777 data/raw_candles.csv",
	`python3 -c "open('data/raw_candles.csv','w').write('x')"`,
	"ls && echo x > data/raw_candles.csv",
];
const BASH_ALLOWED = [
	"ls -la data",
	"cat data/raw_candles.csv",
	"head -5 data/raw_candles.csv",
	"sha256sum data/raw_candles.csv",
	"sha256sum data/raw_candles.csv > /tmp/h.txt",
	"cp data/raw_candles.csv data/clean_candles.csv",
	"python3 scripts/clean.py data/raw_candles.csv data/clean_candles.csv",
	`python3 -c "print(open('data/raw_candles.csv').read())"`,
];

test("bash: mutations of a protected path are blocked", () => {
	const root = project(POLICY);
	for (const command of BASH_BLOCKED) {
		assert.equal(child(root, "bash", { command }).block, true, command);
		assert.equal(orch(root, "bash", { command }).block, true, command);
	}
});

test("bash: reads and copies out of a protected path are allowed", () => {
	const root = project(POLICY);
	for (const command of BASH_ALLOWED) {
		assert.equal(child(root, "bash", { command }).block, false, command);
	}
});

test("bash: orchestrator cannot mutate project files outside its writable paths", () => {
	const root = project(POLICY);
	const blocked = [
		"echo x > data/clean.csv",
		"cat a | tee data/clean.csv",
		"cp data/raw_candles.csv data/clean.csv",
		"rm data/other.csv",
		"sed -i s/a/b/ data/other.csv",
		"mv odd/a.md data/a.md",
	];
	for (const command of blocked) {
		const d = orch(root, "bash", { command });
		assert.equal(d.block, true, command);
		assert.match((d as { reason: string }).reason, /orchestrator/i, command);
	}
});

test("bash: orchestrator keeps odd/, reads and targets outside the project", () => {
	const root = project(POLICY);
	for (const command of ["echo x > odd/tasks/a.md", "echo x > /tmp/h.txt", "cat data/raw_candles.csv", "ls data", "python3 scripts/x.py data/raw_candles.csv"]) {
		assert.equal(orch(root, "bash", { command }).block, false, command);
	}
});

test("bash: a subagent may write unprotected project files", () => {
	const root = project(POLICY);
	assert.equal(child(root, "bash", { command: "echo x > data/clean.csv" }).block, false);
	assert.equal(child(root, "bash", { command: "rm data/other.csv" }).block, false);
});

test("bash: orchestrator_restricted false lets the orchestrator use bash on unprotected files", () => {
	const root = project({ ...POLICY, orchestrator_restricted: false });
	assert.equal(orch(root, "bash", { command: "echo x > data/clean.csv" }).block, false);
});
