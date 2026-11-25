import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { decide, findRoot, loadPolicy, quantModeFromInput } from "./core.ts";
import { activeOpenItems, buildNudge, completionEnabled, settleAction } from "./completion.ts";
import { appendAudit, auditRecord } from "./audit.ts";

// Runtime guardrail for Quant mode: blocks tool calls by policy (.governance/quant-gate.json).
// Off when the project has no policy file, or when Pi runs with QUANT_GATE=off.
export default function (pi: ExtensionAPI) {
	const started = Date.now();
	let continues = 0; // reminders sent since the last user message
	let warned = false;
	let quantMode = false; // learned from the user's own /quant-mode input; a new process starts off

	pi.on("input", async (event, ctx) => {
		const next = quantModeFromInput(event.text, quantMode);
		if (next !== quantMode) {
			quantMode = next;
			const root = findRoot(ctx.cwd ?? process.cwd());
			if (root && process.env.QUANT_GATE !== "off") appendAudit(root, auditRecord({ kind: "mode", isChild: false, decision: next ? "on" : "off" }));
		}
		return { action: "continue" as const };
	});

	pi.on("before_agent_start", async (event) => {
		if (event.messageType === "user") {
			continues = 0;
			warned = false;
		}
		return undefined;
	});

	// Phase 2: do not let the orchestrator end a turn while feature-doc items are open.
	pi.on("agent_before_settle", async (event, ctx) => {
		const root = findRoot(ctx.cwd ?? process.cwd());
		if (!root) return undefined;
		try {
			const state = loadPolicy(root);
			if (state.status !== "ok") return undefined;
			const open = activeOpenItems(root, started);
			const action = settleAction({
				open,
				continues,
				max: state.policy.completionMaxContinues,
				isChild: process.env.GENTLE_PI_AGENTS_CHILD === "1",
				outcome: event.outcome,
				env: process.env,
				enabled: completionEnabled(state.policy.completionGate, quantMode),
			});
			if ((open.length > 0 || action !== "allow") && process.env.QUANT_GATE !== "off") {
				appendAudit(root, auditRecord({ kind: "settle", isChild: process.env.GENTLE_PI_AGENTS_CHILD === "1", decision: action, extra: { open: open.reduce((a, d) => a + d.items.length, 0), continues } }));
			}
			if (action === "continue") {
				continues++;
				return { entries: [{ type: "custom_message", customType: "quant-gate", content: buildNudge(open), display: true }], continue: true };
			}
			if (action === "warn" && !warned) {
				warned = true;
				const n = open.reduce((a, d) => a + d.items.length, 0);
				const where = open.map((d) => d.doc).join(", ");
				return {
					entries: [{ type: "custom_message", customType: "quant-gate", content: `quant-gate: the turn ended with ${n} item(s) still open after ${continues} reminder(s) (${where}).`, display: true }],
				};
			}
		} catch {
			// never break the session from the completion check
		}
		return undefined;
	});

	pi.on("tool_call", async (event, ctx) => {
		const root = findRoot(ctx.cwd ?? process.cwd());
		if (!root) return undefined;
		try {
			const d = decide({
				root,
				toolName: event.toolName,
				input: (event.input ?? {}) as Record<string, unknown>,
				isChild: process.env.GENTLE_PI_AGENTS_CHILD === "1",
				env: process.env,
				quantMode,
			});
			if (process.env.QUANT_GATE !== "off") {
				appendAudit(root, auditRecord({ kind: "tool", isChild: process.env.GENTLE_PI_AGENTS_CHILD === "1", toolName: event.toolName, input: (event.input ?? {}) as Record<string, unknown>, decision: d.block ? "block" : "allow", reason: d.block ? d.reason : undefined }));
			}
			if (!d.block) return undefined;
			if (ctx.hasUI) ctx.ui.notify(d.reason, "warning");
			return { block: true, reason: d.reason };
		} catch (e) {
			// Fail closed: a gate that cannot decide must not let a mutation through.
			if (/(^|__)(write|edit|bash)$/.test(event.toolName)) {
				appendAudit(root, auditRecord({ kind: "tool", isChild: process.env.GENTLE_PI_AGENTS_CHILD === "1", toolName: event.toolName, decision: "block", reason: "internal error" }));
				return { block: true, reason: `quant-gate: internal error, call blocked (${(e as Error).message})` };
			}
			return undefined;
		}
	});
}
