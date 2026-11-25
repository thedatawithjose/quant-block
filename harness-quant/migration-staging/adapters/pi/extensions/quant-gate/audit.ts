import { appendFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";

export const AUDIT_REL = join(".governance", "quant-gate.audit.jsonl");
const MAX_TARGET = 200;

export interface AuditInput {
	kind: "tool" | "settle" | "mode";
	isChild: boolean;
	toolName?: string;
	input?: Record<string, unknown>;
	decision: string;
	reason?: string;
	extra?: Record<string, unknown>;
}
export interface AuditRecord {
	ts: string;
	kind: "tool" | "settle" | "mode";
	actor: "orchestrator" | "subagent";
	tool?: string;
	target?: string;
	decision: string;
	reason?: string;
	extra?: Record<string, unknown>;
}

function targetOf(toolName: string | undefined, input: Record<string, unknown> | undefined): string | undefined {
	if (!toolName || !input) return undefined;
	if (typeof input.command === "string") return input.command.slice(0, MAX_TARGET);
	if (toolName === "subagent_run" && typeof input.agent === "string") return `agent:${input.agent}`.slice(0, MAX_TARGET);
	const p = input.path ?? input.file_path;
	return typeof p === "string" ? p.slice(0, MAX_TARGET) : undefined;
}

export function auditRecord(a: AuditInput): AuditRecord {
	const rec: AuditRecord = { ts: new Date().toISOString(), kind: a.kind, actor: a.isChild ? "subagent" : "orchestrator", decision: a.decision };
	if (a.toolName) rec.tool = a.toolName;
	const target = targetOf(a.toolName, a.input);
	if (target !== undefined) rec.target = target;
	if (a.reason) rec.reason = a.reason;
	if (a.extra) rec.extra = a.extra;
	return rec;
}

// Append-only from the extension's side. A logging failure must never break the session.
export function appendAudit(root: string, rec: AuditRecord): boolean {
	try {
		const file = join(root, AUDIT_REL);
		mkdirSync(dirname(file), { recursive: true });
		appendFileSync(file, JSON.stringify(rec) + "\n");
		return true;
	} catch {
		return false;
	}
}
