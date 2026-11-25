import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, realpathSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { AUDIT_REL, auditRecord, appendAudit } from "./audit.ts";
import { decide } from "./core.ts";

function project(): string {
	const root = realpathSync(mkdtempSync(join(tmpdir(), "qaudit-")));
	mkdirSync(join(root, ".governance"));
	writeFileSync(join(root, ".governance", "quant-gate.json"), JSON.stringify({ protected: [] }));
	return root;
}

test("tool record carries actor, tool, target, decision, reason and an ISO timestamp", () => {
	const r = auditRecord({ kind: "tool", isChild: false, toolName: "write", input: { path: "data/x.csv" }, decision: "block", reason: "protected" });
	assert.equal(r.kind, "tool");
	assert.equal(r.actor, "orchestrator");
	assert.equal(r.tool, "write");
	assert.equal(r.target, "data/x.csv");
	assert.equal(r.decision, "block");
	assert.equal(r.reason, "protected");
	assert.match(r.ts, /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d/);
});

test("subagent actor and subagent_run target", () => {
	const r = auditRecord({ kind: "tool", isChild: true, toolName: "subagent_run", input: { agent: "quant-data-engineer", task: "x" }, decision: "allow" });
	assert.equal(r.actor, "subagent");
	assert.equal(r.target, "agent:quant-data-engineer");
});

test("bash target is the command, cut at 200 characters", () => {
	const r = auditRecord({ kind: "tool", isChild: false, toolName: "bash", input: { command: "x".repeat(500) }, decision: "allow" });
	assert.equal(r.target?.length, 200);
});

test("settle record keeps the action and the counts", () => {
	const r = auditRecord({ kind: "settle", isChild: false, decision: "continue", extra: { open: 3, continues: 1 } });
	assert.equal(r.kind, "settle");
	assert.equal(r.decision, "continue");
	assert.deepEqual(r.extra, { open: 3, continues: 1 });
});

test("appendAudit creates the file and appends one JSON object per line", () => {
	const root = project();
	assert.equal(appendAudit(root, auditRecord({ kind: "tool", isChild: false, toolName: "read", input: { path: "a" }, decision: "allow" })), true);
	assert.equal(appendAudit(root, auditRecord({ kind: "tool", isChild: true, toolName: "write", input: { path: "b" }, decision: "block", reason: "r" })), true);
	const lines = readFileSync(join(root, AUDIT_REL), "utf8").trim().split("\n");
	assert.equal(lines.length, 2);
	assert.equal(JSON.parse(lines[0]).target, "a");
	assert.equal(JSON.parse(lines[1]).actor, "subagent");
});

test("appendAudit never throws and reports failure", () => {
	const root = project();
	writeFileSync(join(root, "afile"), "x");
	assert.equal(appendAudit(join(root, "afile"), auditRecord({ kind: "tool", isChild: false, toolName: "read", input: {}, decision: "allow" })), false);
});

test("the audit file is protected from write, edit and inline bash mutation", () => {
	const root = project();
	for (const isChild of [true, false]) {
		const d = (toolName: string, input: Record<string, unknown>) => decide({ root, toolName, input, isChild, env: {} });
		assert.equal(d("write", { path: AUDIT_REL }).block, true);
		assert.equal(d("edit", { path: AUDIT_REL }).block, true);
		assert.equal(d("bash", { command: `echo x >> ${AUDIT_REL}` }).block, true);
		assert.equal(d("bash", { command: `truncate -s 0 ${AUDIT_REL}` }).block, true);
		assert.equal(d("bash", { command: `rm ${AUDIT_REL}` }).block, true);
		assert.equal(d("bash", { command: `cat ${AUDIT_REL}` }).block, false);
	}
});
