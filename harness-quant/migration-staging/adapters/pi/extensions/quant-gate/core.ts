import { existsSync, lstatSync, readFileSync, realpathSync } from "node:fs";
import { basename, dirname, join, resolve, sep } from "node:path";
import { homedir } from "node:os";
import { AUDIT_REL } from "./audit.ts";

export const POLICY_REL = join(".governance", "quant-gate.json");

export interface Policy {
	protected: string[];
	orchestratorWritable: string[];
	orchestratorRestricted: boolean | "quant-mode";
	completionGate: boolean | "quant-mode";
	completionMaxContinues: number;
}
export type PolicyState = { status: "none" } | { status: "invalid"; error: string } | { status: "ok"; policy: Policy };
export type Decision = { block: false } | { block: true; reason: string };
export interface GateInput {
	root: string;
	toolName: string;
	input: Record<string, unknown>;
	isChild: boolean;
	env: Record<string, string | undefined>;
	quantMode?: boolean;
}

export function findRoot(start: string): string | undefined {
	let dir = resolve(start);
	for (;;) {
		if (existsSync(join(dir, POLICY_REL))) return dir;
		const parent = dirname(dir);
		if (parent === dir) return undefined;
		dir = parent;
	}
}

export function loadPolicy(root: string): PolicyState {
	const file = join(root, POLICY_REL);
	if (!existsSync(file)) return { status: "none" };
	let raw: unknown;
	try {
		raw = JSON.parse(readFileSync(file, "utf8"));
	} catch (e) {
		return { status: "invalid", error: `cannot parse JSON: ${(e as Error).message}` };
	}
	if (typeof raw !== "object" || raw === null || Array.isArray(raw)) return { status: "invalid", error: "root must be an object" };
	const o = raw as Record<string, unknown>;
	const strings = (key: string, fallback: string[]): string[] | string => {
		const v = o[key];
		if (v === undefined) return fallback;
		if (!Array.isArray(v) || v.some((x) => typeof x !== "string" || x === "")) return `${key} must be a list of non-empty strings`;
		return v as string[];
	};
	const prot = strings("protected", []);
	if (typeof prot === "string") return { status: "invalid", error: prot };
	const writable = strings("orchestrator_writable", ["odd/"]);
	if (typeof writable === "string") return { status: "invalid", error: writable };
	const restricted = o.orchestrator_restricted;
	if (restricted !== undefined && typeof restricted !== "boolean" && restricted !== "quant-mode") {
		return { status: "invalid", error: 'orchestrator_restricted must be true, false or "quant-mode"' };
	}
	const gate = o.completion_gate;
	if (gate !== undefined && typeof gate !== "boolean" && gate !== "quant-mode") {
		return { status: "invalid", error: 'completion_gate must be true, false or "quant-mode"' };
	}
	const max = o.completion_max_continues;
	if (max !== undefined && (typeof max !== "number" || !Number.isInteger(max) || max < 0 || max > 5)) {
		return { status: "invalid", error: "completion_max_continues must be an integer from 0 to 5" };
	}
	return {
		status: "ok",
		policy: {
			protected: prot,
			orchestratorWritable: writable,
			orchestratorRestricted: restricted ?? true,
			completionGate: gate ?? true,
			completionMaxContinues: max ?? 2,
		},
	};
}

function exists(p: string): boolean {
	try {
		lstatSync(p);
		return true;
	} catch {
		return false;
	}
}

// Absolute path with ".." folded and symlinks resolved, also for paths that do not exist yet.
function canon(p: string, root: string): string {
	let cur = resolve(root, p);
	const tail: string[] = [];
	while (!exists(cur)) {
		const parent = dirname(cur);
		if (parent === cur) break;
		tail.unshift(basename(cur));
		cur = parent;
	}
	let real = cur;
	try {
		real = realpathSync(cur);
	} catch {
		// keep the unresolved path
	}
	return tail.length ? join(real, ...tail) : real;
}

function entryMatches(target: string, entry: string, root: string): boolean {
	const isDir = entry.endsWith("/");
	const abs = canon(entry, root);
	return isDir ? target === abs || target.startsWith(abs + sep) : target === abs;
}

function ownEntries(): string[] {
	return [join(homedir(), ".pi", "agent", "extensions", "quant-gate") + "/"];
}

function isProtected(p: string, root: string, policy: Policy): boolean {
	const target = canon(p, root);
	const list = [...policy.protected, POLICY_REL, AUDIT_REL, ...ownEntries()];
	return list.some((e) => entryMatches(target, e, root));
}

// Inside the project but outside the paths the orchestrator may write.
function orchestratorMayNotWrite(p: string, root: string, policy: Policy): boolean {
	const realRoot = canon(".", root);
	const target = canon(p, root);
	const inside = target === realRoot || target.startsWith(realRoot + sep);
	return inside && !policy.orchestratorWritable.some((e) => entryMatches(target, e, root));
}

const WRITE_TOOL = /(^|__)(write|edit)$/;

// Quote-aware split on ; && || | and newlines.
function splitSegments(cmd: string): string[] {
	const out: string[] = [];
	let cur = "";
	let quote = "";
	for (let i = 0; i < cmd.length; i++) {
		const c = cmd[i];
		if (quote) {
			cur += c;
			if (c === quote) quote = "";
			continue;
		}
		if (c === '"' || c === "'") {
			quote = c;
			cur += c;
			continue;
		}
		if (c === ";" || c === "\n" || c === "|" || (c === "&" && cmd[i + 1] === "&")) {
			out.push(cur);
			cur = "";
			if (c === "&" || (c === "|" && cmd[i + 1] === "|")) i++;
			continue;
		}
		cur += c;
	}
	out.push(cur);
	return out.map((s) => s.trim()).filter(Boolean);
}

const unquote = (t: string): string => t.replace(/^(["'])(.*)\1$/s, "$2");
const WRAPPERS = new Set(["sudo", "env", "command", "nohup", "time", "exec", "nice"]);
const ANY_ARG = new Set(["rm", "mv", "unlink", "shred", "truncate", "chmod", "chown", "chgrp", "chattr", "tee"]);
const LAST_ARG = new Set(["cp", "install", "ln", "rsync"]);
const SHELLS = new Set(["sh", "bash", "zsh", "dash"]);
const INTERPRETERS = /^(python[\d.]*|node|perl|ruby)$/;
const WRITE_MARK = /open\s*\([^)]*['"][wax]\+?b?['"]|writeFile|write_text|write_bytes|\.write\(|to_csv|\bunlink\b|\bremove\(|\brename\(/;

// Best effort: returns the first path a command would mutate that `forbid` rejects.
function bashMutatesForbidden(command: string, root: string, policy: Policy, forbid: (p: string) => boolean): string | undefined {
	for (const segment of splitSegments(command)) {
		for (const m of segment.matchAll(/(?:^|\s)\d*>>?\s*("[^"]+"|'[^']+'|[^\s;&|<>]+)/g)) {
			const target = unquote(m[1]);
			if (forbid(target)) return target;
		}
		const tokens = (segment.match(/"[^"]*"|'[^']*'|\S+/g) ?? []).map(unquote);
		let i = 0;
		while (i < tokens.length && (WRAPPERS.has(basename(tokens[i])) || /^\w+=/.test(tokens[i]))) i++;
		if (i >= tokens.length) continue;
		const cmd = basename(tokens[i]);
		const args = tokens.slice(i + 1);
		const bad = (t: string): boolean => !t.startsWith("-") && forbid(t);
		if (SHELLS.has(cmd) && args[0] === "-c" && args[1]) {
			const inner = bashMutatesForbidden(args[1], root, policy, forbid);
			if (inner) return inner;
			continue;
		}
		if (ANY_ARG.has(cmd)) {
			const hit = args.find(bad);
			if (hit) return hit;
		} else if (cmd === "sed" || cmd === "perl") {
			if (args.some((a) => /^-[a-zA-Z]*i/.test(a))) {
				const hit = args.find(bad);
				if (hit) return hit;
			}
		} else if (LAST_ARG.has(cmd)) {
			const positional = args.filter((a) => !a.startsWith("-"));
			const last = positional[positional.length - 1];
			if (last && bad(last)) return last;
		} else if (cmd === "dd") {
			const hit = args.find((a) => a.startsWith("of=") && bad(a.slice(3)));
			if (hit) return hit.slice(3);
		}
		if (INTERPRETERS.test(cmd) && WRITE_MARK.test(segment)) {
			const named = [...policy.protected, POLICY_REL].find((e) => segment.includes(e.replace(/\/$/, "")));
			if (named) return named;
		}
	}
	return undefined;
}

export function decide(g: GateInput): Decision {
	if (g.env.QUANT_GATE === "off") return { block: false };
	const state = loadPolicy(g.root);
	if (state.status === "none") return { block: false };
	const isWrite = WRITE_TOOL.test(g.toolName);
	if (state.status === "invalid") {
		if (!isWrite) return { block: false };
		return { block: true, reason: `quant-gate: ${POLICY_REL} is invalid (${state.error}); write/edit are blocked until a human fixes it.` };
	}
	const policy = state.policy;
	const rule = policy.orchestratorRestricted;
	const restricted = !g.isChild && (rule === true || (rule === "quant-mode" && g.quantMode === true));
	const mayNot = `the orchestrator may only write under ${policy.orchestratorWritable.join(", ")}`;

	if (g.toolName === "bash") {
		const command = typeof g.input.command === "string" ? g.input.command : "";
		const forbid = (p: string): boolean => isProtected(p, g.root, policy) || (restricted && orchestratorMayNotWrite(p, g.root, policy));
		const hit = bashMutatesForbidden(command, g.root, policy, forbid);
		if (!hit) return { block: false };
		if (isProtected(hit, g.root, policy)) {
			return { block: true, reason: `quant-gate: this command would modify "${hit}", which is protected by ${POLICY_REL}. Write results to a new file instead.` };
		}
		return { block: true, reason: `quant-gate: ${mayNot}; this command would modify "${hit}". Delegate it to a specialist with subagent_run.` };
	}

	if (!isWrite) return { block: false };
	const raw = g.input.path ?? g.input.file_path;
	if (typeof raw !== "string" || raw === "") return { block: true, reason: "quant-gate: write/edit without a path cannot be checked, so it is blocked." };
	if (isProtected(raw, g.root, policy)) {
		return { block: true, reason: `quant-gate: "${raw}" is protected by ${POLICY_REL}. Do not modify it; write results to a new file instead.` };
	}
	if (restricted) {
		const target = canon(raw, g.root);
		if (!policy.orchestratorWritable.some((e) => entryMatches(target, e, g.root))) {
			return { block: true, reason: `quant-gate: ${mayNot}. Delegate "${raw}" to a specialist with subagent_run.` };
		}
	}
	return { block: false };
}

// The user's own input tells us whether Quant mode is on: `/quant-mode` and `/quant-mode on` enable it,
// `/quant-mode off` disables it, `/quant-mode status` and any other text leave it as it was.
export function quantModeFromInput(text: string, current: boolean): boolean {
	const m = text.match(/^\s*\/quant-mode(?:\s+(\S+))?\s*$/);
	if (!m) return current;
	const arg = (m[1] ?? "on").toLowerCase();
	if (arg === "off") return false;
	if (arg === "status") return current;
	return true;
}
