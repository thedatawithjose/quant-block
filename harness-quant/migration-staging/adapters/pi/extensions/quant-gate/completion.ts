import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

export interface OpenDoc {
	doc: string;
	items: string[];
}

const RESOLVED = /\b(?:BLOCKED|HUMAN_DECISION_REQUIRED|DROPPED|CANCELLED)\b\s*[:\-–—]?\s*\S{3}/;
const SHOWN_PER_DOC = 10;

// Open items: unchecked `- [ ]` lines under `## Tasks`, unless they carry a resolution keyword plus a reason.
export function openItems(text: string): string[] {
	const out: string[] = [];
	let inTasks = false;
	for (const line of text.split("\n")) {
		if (/^##\s/.test(line)) {
			inTasks = /^##\s+tasks\s*$/i.test(line);
			continue;
		}
		if (!inTasks) continue;
		const m = line.match(/^\s*[-*]\s+\[ \]\s+(.*\S)\s*$/);
		if (m && !RESOLVED.test(m[1])) out.push(m[1]);
	}
	return out;
}

// Feature docs touched since `sinceMs` (the Pi process start) that still have open items.
export function activeOpenItems(root: string, sinceMs: number): OpenDoc[] {
	const dir = join(root, "odd", "tasks");
	if (!existsSync(dir)) return [];
	const out: OpenDoc[] = [];
	for (const name of readdirSync(dir).filter((n) => n.endsWith(".md")).sort()) {
		const file = join(dir, name);
		try {
			if (statSync(file).mtimeMs < sinceMs) continue;
			const items = openItems(readFileSync(file, "utf8"));
			if (items.length) out.push({ doc: `odd/tasks/${name}`, items });
		} catch {
			// unreadable doc: skip it, the gate must not break the session
		}
	}
	return out;
}

export function buildNudge(open: OpenDoc[]): string {
	const lines = ["quant-gate: you are about to end your turn, but these items are still open in the feature docs:"];
	for (const d of open) {
		lines.push(`\n${d.doc}`);
		for (const it of d.items.slice(0, SHOWN_PER_DOC)) lines.push(`- [ ] ${it}`);
		if (d.items.length > SHOWN_PER_DOC) lines.push(`- ...and ${d.items.length - SHOWN_PER_DOC} more`);
	}
	lines.push(
		"\nDo one of these for every item before you finish: keep working on it; or mark it `- [x]` in the doc with the evidence; or mark it `BLOCKED: <blocker>`, `HUMAN_DECISION_REQUIRED: <decision needed>` or `DROPPED: <reason>` (quote the user if they stopped it). Then restate the original objective in one line. Never say the work is done while an item is open.",
	);
	return lines.join("\n");
}

export function completionEnabled(gate: boolean | "quant-mode", quantMode: boolean): boolean {
	return gate === "quant-mode" ? quantMode : gate;
}

export interface SettleInput {
	open: OpenDoc[];
	continues: number;
	max: number;
	isChild: boolean;
	outcome: string;
	env: Record<string, string | undefined>;
	enabled: boolean;
}

export function settleAction(s: SettleInput): "allow" | "continue" | "warn" {
	if (s.env.QUANT_GATE === "off" || !s.enabled || s.isChild || s.outcome !== "completed") return "allow";
	if (s.open.length === 0) return "allow";
	return s.continues < s.max ? "continue" : "warn";
}
