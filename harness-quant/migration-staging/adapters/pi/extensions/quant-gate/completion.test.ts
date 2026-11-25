import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, utimesSync, realpathSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { openItems, activeOpenItems, buildNudge, settleAction } from "./completion.ts";
import { loadPolicy } from "./core.ts";

const doc = (tasks: string, extra = "") => `# F\n\n## Specs\n- [ ] not a task, in Specs\n\n## Tasks\n${tasks}\n\n## Log\n- [ ] not a task, in Log\n${extra}`;

test("unchecked items under ## Tasks are open; checked ones and other sections are not", () => {
	const items = openItems(doc("- [x] T1 done\n- [ ] T2 pending\n- [ ] T3 also pending"));
	assert.deepEqual(items, ["T2 pending", "T3 also pending"]);
});

test("BLOCKED, HUMAN_DECISION_REQUIRED, DROPPED and CANCELLED with a reason resolve an item", () => {
	const t = [
		"- [ ] T1 x BLOCKED: waiting for the bid/ask file",
		"- [ ] T2 y HUMAN_DECISION_REQUIRED: which duplicate rule",
		"- [ ] T3 z DROPPED: user changed scope",
		"- [ ] T4 w CANCELLED - superseded by T9",
	].join("\n");
	assert.deepEqual(openItems(doc(t)), []);
});

test("a keyword without a reason does not resolve the item", () => {
	assert.deepEqual(openItems(doc("- [ ] T1 x BLOCKED\n- [ ] T2 y HUMAN_DECISION_REQUIRED:")), ["T1 x BLOCKED", "T2 y HUMAN_DECISION_REQUIRED:"]);
});

test("the Tasks heading is matched case-insensitively and ends at the next ## heading", () => {
	assert.deepEqual(openItems("## tasks\n- [ ] A\n## Notes\n- [ ] B\n"), ["A"]);
});

test("a doc without a Tasks section has no open items", () => {
	assert.deepEqual(openItems("# x\n- [ ] loose\n"), []);
});

function project() {
	const root = realpathSync(mkdtempSync(join(tmpdir(), "qcomp-")));
	mkdirSync(join(root, "odd", "tasks"), { recursive: true });
	return root;
}
const put = (root: string, name: string, text: string, mtimeMs?: number) => {
	const f = join(root, "odd", "tasks", name);
	writeFileSync(f, text);
	if (mtimeMs !== undefined) utimesSync(f, mtimeMs / 1000, mtimeMs / 1000);
};

test("only docs modified since the session start count", () => {
	const root = project();
	const since = Date.now() - 1000;
	put(root, "old.md", doc("- [ ] OLD"), since - 60_000);
	put(root, "new.md", doc("- [ ] NEW"));
	const open = activeOpenItems(root, since);
	assert.equal(open.length, 1);
	assert.equal(open[0].doc, "odd/tasks/new.md");
	assert.deepEqual(open[0].items, ["NEW"]);
});

test("several active docs are aggregated; resolved docs are omitted", () => {
	const root = project();
	const since = Date.now() - 1000;
	put(root, "a.md", doc("- [ ] A1"));
	put(root, "b.md", doc("- [x] B1"));
	put(root, "c.md", doc("- [ ] C1\n- [ ] C2"));
	const open = activeOpenItems(root, since);
	assert.deepEqual(open.map((o) => o.doc).sort(), ["odd/tasks/a.md", "odd/tasks/c.md"]);
});

test("no odd/tasks directory means nothing open", () => {
	const root = realpathSync(mkdtempSync(join(tmpdir(), "qcomp-")));
	assert.deepEqual(activeOpenItems(root, 0), []);
});

test("nudge names each doc and item, caps the list, and says how to resolve", () => {
	const many = Array.from({ length: 15 }, (_, i) => `item ${i + 1}`);
	const text = buildNudge([{ doc: "odd/tasks/a.md", items: many }]);
	assert.match(text, /odd\/tasks\/a\.md/);
	assert.match(text, /item 1\b/);
	assert.doesNotMatch(text, /item 15\b/);
	assert.match(text, /5 more/);
	assert.match(text, /BLOCKED/);
});

const OPEN = [{ doc: "odd/tasks/a.md", items: ["T1"] }];
const base = { open: OPEN, continues: 0, max: 2, isChild: false, outcome: "completed", env: {} as Record<string, string | undefined>, enabled: true };

test("settleAction continues while under the cap and warns once the cap is reached", () => {
	assert.equal(settleAction(base), "continue");
	assert.equal(settleAction({ ...base, continues: 1 }), "continue");
	assert.equal(settleAction({ ...base, continues: 2 }), "warn");
	assert.equal(settleAction({ ...base, max: 0 }), "warn");
});

test("settleAction allows when nothing is open", () => {
	assert.equal(settleAction({ ...base, open: [] }), "allow");
});

test("settleAction never nudges subagents, aborted or failed runs, a disabled gate, or QUANT_GATE=off", () => {
	assert.equal(settleAction({ ...base, isChild: true }), "allow");
	assert.equal(settleAction({ ...base, outcome: "aborted" }), "allow");
	assert.equal(settleAction({ ...base, outcome: "error" }), "allow");
	assert.equal(settleAction({ ...base, enabled: false }), "allow");
	assert.equal(settleAction({ ...base, env: { QUANT_GATE: "off" } }), "allow");
});

function policyWith(extra: Record<string, unknown>) {
	const root = realpathSync(mkdtempSync(join(tmpdir(), "qpol-")));
	mkdirSync(join(root, ".governance"));
	writeFileSync(join(root, ".governance", "quant-gate.json"), JSON.stringify({ protected: [], ...extra }));
	return loadPolicy(root);
}

test("completion policy defaults and overrides", () => {
	const d = policyWith({});
	assert.ok(d.status === "ok" && d.policy.completionGate === true && d.policy.completionMaxContinues === 2);
	const o = policyWith({ completion_gate: false, completion_max_continues: 4 });
	assert.ok(o.status === "ok" && o.policy.completionGate === false && o.policy.completionMaxContinues === 4);
});

test("invalid completion policy values make the policy invalid", () => {
	for (const bad of [{ completion_gate: "yes" }, { completion_max_continues: -1 }, { completion_max_continues: 6 }, { completion_max_continues: 1.5 }, { completion_max_continues: "2" }]) {
		assert.equal(policyWith(bad).status, "invalid", JSON.stringify(bad));
	}
});
