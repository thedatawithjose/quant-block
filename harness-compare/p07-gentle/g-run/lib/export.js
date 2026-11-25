const fs = require('node:fs');
const path = require('node:path');

const oneLine = (s) => (typeof s === 'string' ? s : '').replace(/\s+/g, ' ').trim();

function answerText(a) {
  const s = typeof a === 'string' ? a : '';
  return s.replace(/\r\n?/g, '\n').trimEnd().split('\n').map((l) => (l.startsWith('#') ? `\\${l}` : l)).join('\n');
}

function field(v) {
  let s = '';
  try { s = v === undefined || v === null ? '' : oneLine(String(v)); } catch { /* unprintable value */ }
  return s || '?';
}
const isCite = (c) => c !== null && typeof c === 'object';

function citeLine(x) {
  return `- ${field(x.doc)} · ${field(x.chunkId)} · línea ${field(x.line)}` + (typeof x.section === 'string' && oneLine(x.section) ? ` · sección: ${oneLine(x.section)}` : '');
}

function invalid(msg) {
  const err = new Error(msg);
  err.code = 'EINVAL';
  return err;
}

function resolveNow(opts) {
  const o = opts !== null && typeof opts === 'object' ? opts : {};
  const now = o.now === undefined || o.now === null ? new Date() : new Date(o.now);
  if (Number.isNaN(now.getTime())) throw invalid('opts.now is not a valid date');
  return now;
}

const absent = (v) => v === undefined || v === null;

// Resolves opts.fromTurn/toTurn against the history length. Returns { from, to, ranged }; throws EINVAL.
function resolveRange(total, opts) {
  const o = opts !== null && typeof opts === 'object' ? opts : {};
  const ranged = !absent(o.fromTurn) || !absent(o.toTurn);
  if (!ranged) return { from: 1, to: total, ranged };
  const from = absent(o.fromTurn) ? 1 : o.fromTurn;
  const to = absent(o.toTurn) ? total : o.toTurn;
  for (const v of [from, to]) {
    if (!Number.isInteger(v) || v < 1 || v > total) throw invalid(`turn range value out of bounds (1-${total})`);
  }
  if (from > to) throw invalid('fromTurn must not be greater than toTurn');
  return { from, to, ranged };
}

// Strict reading of the IPC range argument: undefined/null/{} mean "no range"; any other
// non-plain-object (primitives, arrays) is EINVAL. Value checks stay in resolveRange.
function rangeOpts(range) {
  if (absent(range)) return { fromTurn: undefined, toTurn: undefined };
  if (typeof range !== 'object' || Array.isArray(range)) throw invalid('range must be an object { fromTurn, toTurn }');
  return { fromTurn: range.fromTurn, toTurn: range.toTurn };
}

// Pure: conversation history -> Markdown string (LF only, single trailing newline).
function conversationToMarkdown(history, opts = {}) {
  const turns = Array.isArray(history) ? Array.from(history) : []; // holes become undefined (empty turns)
  const now = resolveNow(opts);
  const total = turns.length;
  const { from, to, ranged } = resolveRange(total, opts);
  const n = ranged ? to - from + 1 : total;
  const span = ranged ? ` (${from}–${to} de ${total})` : '';
  const out = ['# Conversación', '', `_Exportada: ${now.toISOString()} · ${n} ${n === 1 ? 'turno' : 'turnos'}${span}_`];
  if (!n) out.push('', '_Sin turnos_');
  turns.forEach((t, i) => {
    if (i + 1 < from || i + 1 > to) return;
    const turn = t || {};
    out.push('', `## ${i + 1}. ${oneLine(turn.q)}`, '', answerText(turn.a));
    const cites = Array.isArray(turn.citations) ? turn.citations.filter(isCite) : [];
    if (cites.length) out.push('', '**Fuentes:**', ...cites.map(citeLine));
  });
  return out.join('\n').replace(/\n+$/, '') + '\n';
}

const pad = (v) => String(v).padStart(2, '0');

function stamp(d) {
  return `${String(d.getUTCFullYear()).padStart(4, '0')}${pad(d.getUTCMonth() + 1)}${pad(d.getUTCDate())}-${pad(d.getUTCHours())}${pad(d.getUTCMinutes())}${pad(d.getUTCSeconds())}`;
}

// Fallback without hard links: never writes to dest; reserves it with an exclusive lock file,
// then renames the finished temp over it (atomic). Returns false when the name is taken.
function placeWithLock(tmp, dest) {
  const lock = `${dest}.lock`;
  let fd;
  try {
    fd = fs.openSync(lock, 'wx');
  } catch (err) {
    if (err.code === 'EEXIST') return false;
    throw err;
  }
  try {
    try { fs.lstatSync(dest); return false; } catch (err) { if (err.code !== 'ENOENT') throw err; }
    fs.renameSync(tmp, dest);
    return true;
  } finally {
    fs.closeSync(fd);
    fs.rmSync(lock, { force: true });
  }
}

// Writes <root>/data/exports/conversacion-YYYYMMDD-HHMMSS[-N].md atomically, never overwriting.
function exportConversation(root, history, opts = {}) {
  if (!Array.isArray(history) || !history.length) {
    throw invalid('history must be a non-empty array');
  }
  const now = resolveNow(opts);
  const { from, to, ranged } = resolveRange(history.length, opts); // validated before touching the filesystem
  const year = now.getUTCFullYear();
  if (year < 0 || year > 9999) throw invalid('opts.now year must be within 0000-9999');
  const dir = path.join(root, 'data', 'exports');
  fs.mkdirSync(dir, { recursive: true });
  const base = `conversacion-${stamp(now)}`;
  const md = conversationToMarkdown(history, ranged ? { now, fromTurn: from, toTurn: to } : { now });
  const exported = to - from + 1;
  const tmp = path.join(dir, `.${base}.${process.pid}.${Date.now()}.tmp`);
  try {
    fs.writeFileSync(tmp, md);
    for (let k = 1; ; k++) {
      const name = k === 1 ? `${base}.md` : `${base}-${k}.md`;
      const dest = path.join(dir, name);
      try {
        fs.linkSync(tmp, dest); // fails with EEXIST instead of overwriting
      } catch (err) {
        if (err.code === 'EEXIST') continue;
        if (!placeWithLock(tmp, dest)) continue; // no hard-link support: lock + atomic rename
      }
      return { file: `data/exports/${name}`, turns: exported };
    }
  } finally {
    try { fs.rmSync(tmp, { force: true }); } catch { /* best effort: cleanup must not mask the result */ }
  }
}

module.exports = { conversationToMarkdown, exportConversation, resolveRange, rangeOpts };
