const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const Module = require('node:module');
const { conversationToMarkdown, exportConversation } = require('../lib/export');

const read = (f) => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');
const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'kb-export-'));
const NOW = new Date('2024-03-05T07:08:09.123Z');
const cite = (o = {}) => ({ doc: 'a.md', chunkId: 'a.md#1', line: 3, text: 't', ...o });
const turn = (o = {}) => ({ q: 'hola', effectiveQuery: 'hola', a: 'resp', citations: [], ...o });
const lines = (s) => s.split('\n');

test('F18-1: empty history', () => {
  assert.strictEqual(conversationToMarkdown([], { now: NOW }),
    '# Conversación\n\n_Exportada: 2024-03-05T07:08:09.123Z · 0 turnos_\n\n_Sin turnos_\n');
});

test('F18-2: one turn with citations, optional section, ms now', () => {
  const h = [turn({ citations: [cite(), cite({ chunkId: 'a.md#2', line: 9, section: 'Intro' }), cite({ section: '' })] })];
  assert.strictEqual(conversationToMarkdown(h, { now: NOW.getTime() }),
    '# Conversación\n\n_Exportada: 2024-03-05T07:08:09.123Z · 1 turno_\n\n## 1. hola\n\nresp\n\n**Fuentes:**\n' +
    '- a.md · a.md#1 · línea 3\n- a.md · a.md#2 · línea 9 · sección: Intro\n- a.md · a.md#1 · línea 3\n');
});

test('F18-3: two turns, order, plural, default now', () => {
  const out = conversationToMarkdown([turn({ q: 'uno' }), turn({ q: 'dos', a: 'b' })], { now: NOW });
  assert.match(out, /· 2 turnos_/);
  assert.ok(out.indexOf('## 1. uno') < out.indexOf('## 2. dos'));
  assert.match(conversationToMarkdown([turn()]), /_Exportada: \d{4}-\d\d-\d\dT[\d:.]+Z · 1 turno_/);
});

test('F18-4: q flattened, answer normalized and headings escaped', () => {
  const out = conversationToMarkdown([turn({ q: '  a \n\n b\t c  ', a: 'x\r\n# t\r## u  \rz   \n\n' })], { now: NOW });
  assert.ok(out.includes('## 1. a b c\n\nx\n\\# t\n\\## u  \nz\n'));
  assert.ok(!out.includes('\r'));
});

test('F18-5: tolerant of bad turns; single trailing newline; invariant', () => {
  const h = [{ q: 5, a: null }, turn({ q: '# x\n## y', a: '# a\n## b', citations: undefined }), turn({ a: '' }), turn({ a: '   \n\n' })];
  const out = conversationToMarkdown(h, { now: NOW });
  assert.ok(out.endsWith('\n') && !out.endsWith('\n\n'));
  const ls = lines(out);
  assert.strictEqual(ls.filter((l) => l.startsWith('# ')).length, 1);
  assert.strictEqual(ls.filter((l) => l.startsWith('## ')).length, 4);
  assert.ok(!out.includes('Fuentes'));
  assert.ok(out.includes('## 1.\n') || out.includes('## 1. \n'));
});

test('F18-6: does not mutate input', () => {
  const h = [turn({ q: ' a\nb ', a: '# x\r\n', citations: [cite()] })];
  const copy = JSON.parse(JSON.stringify(h));
  conversationToMarkdown(h, { now: NOW });
  assert.deepStrictEqual(h, copy);
});

test('F18-7: exportConversation errors with EINVAL and writes nothing', () => {
  const root = tmp();
  for (const bad of [undefined, null, [], 'x', {}, { length: 1 }]) {
    assert.throws(() => exportConversation(root, bad, { now: NOW }), (e) => e instanceof Error && e.code === 'EINVAL');
  }
  assert.ok(!fs.existsSync(path.join(root, 'data')));
  fs.rmSync(root, { recursive: true });
});

test('F18-8: writes file under data/exports, UTC name, relative path', () => {
  const root = tmp();
  const h = [turn()];
  const r = exportConversation(root, h, { now: new Date('2024-12-31T23:59:58Z') });
  assert.deepStrictEqual(r, { file: 'data/exports/conversacion-20241231-235958.md', turns: 1 });
  assert.strictEqual(fs.readFileSync(path.join(root, r.file), 'utf8'), conversationToMarkdown(h, { now: new Date('2024-12-31T23:59:58Z') }));
  fs.rmSync(root, { recursive: true });
});

test('F18-9: never overwrites, suffixes -2 -3, leaves no temp files', () => {
  const root = tmp();
  const dir = path.join(root, 'data', 'exports');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'conversacion-20240305-070809.md'), 'previo');
  const a = exportConversation(root, [turn()], { now: NOW });
  const b = exportConversation(root, [turn(), turn()], { now: NOW });
  assert.strictEqual(a.file, 'data/exports/conversacion-20240305-070809-2.md');
  assert.strictEqual(b.file, 'data/exports/conversacion-20240305-070809-3.md');
  assert.strictEqual(b.turns, 2);
  assert.strictEqual(fs.readFileSync(path.join(dir, 'conversacion-20240305-070809.md'), 'utf8'), 'previo');
  assert.deepStrictEqual(fs.readdirSync(dir).sort(), [
    'conversacion-20240305-070809-2.md', 'conversacion-20240305-070809-3.md', 'conversacion-20240305-070809.md']);
  fs.rmSync(root, { recursive: true });
});

test('F18-10: wiring in main, preload, renderer', () => {
  const m = read('main.js');
  assert.match(m, /ipcMain\.handle\('conv:export', \(_e, range\) => \{/);
  assert.match(m, /const opts = rangeOpts\(range\);/);
  assert.match(m, /const res = exportConversation\(__dirname, state\.conversation, opts\);/);
  assert.match(m, /const \{ from, to \} = resolveRange\(state\.conversation\.length, opts\);/);
  assert.match(m, /log\.info\('conv\.export', \{ file: res\.file, turns: res\.turns, from, to \}\);/);
  assert.match(read('preload.js'), /convExport:\s*\(range\)\s*=>\s*ipcRenderer\.invoke\('conv:export',\s*range\)/);
  assert.match(read('renderer/index.html'), /id="export"[^>]*>Exportar</);
  const r = read('renderer/renderer.js');
  assert.match(r, /kb\.convExport\(\)/);
  assert.match(r, /\$\('export-msg'\)\.textContent/);
  assert.doesNotMatch(r, /require\(/);
});

test('F18-11: citation fields are flattened; invariant holds with hostile citations', () => {
  const md = conversationToMarkdown([turn({ citations: [{ doc: 'x.md\n# INJECT', chunkId: 'c', line: 1, section: 's\n## EVIL' }] })], { now: NOW });
  const lines = md.split('\n');
  assert.strictEqual(lines.filter((l) => l.startsWith('# ')).length, 1);
  assert.strictEqual(lines.filter((l) => l.startsWith('## ')).length, 1);
  assert.ok(md.includes('- x.md # INJECT · c · línea 1 · sección: s ## EVIL\n'));
});

test('F18-12: malformed citations render sensibly, valid ones unchanged', () => {
  const md = conversationToMarkdown([turn({ citations: [null, 'abc', 5, { doc: 'd' }, cite({ section: 'S' })] })], { now: NOW });
  assert.ok(!md.includes('undefined'));
  assert.ok(md.includes('**Fuentes:**\n- d · ? · línea ?\n- a.md · a.md#1 · línea 3 · sección: S\n'));
  const only = conversationToMarkdown([turn({ citations: [null, 5] })], { now: NOW });
  assert.ok(!only.includes('Fuentes'));
});

test('F18-13: opts null/non-object tolerated; invalid now -> EINVAL', () => {
  assert.doesNotThrow(() => conversationToMarkdown([turn()], null));
  assert.doesNotThrow(() => conversationToMarkdown([turn()], 5));
  for (const now of ['nope', NaN, new Date('x')]) {
    assert.throws(() => conversationToMarkdown([turn()], { now }), (e) => e.code === 'EINVAL');
    const root = tmp();
    assert.throws(() => exportConversation(root, [turn()], { now }), (e) => e.code === 'EINVAL');
    fs.rmSync(root, { recursive: true });
  }
  const root = tmp();
  assert.ok(exportConversation(root, [turn()], null).file.startsWith('data/exports/'));
  fs.rmSync(root, { recursive: true });
});

test('F18-14: falls back when linkSync unsupported, no temp left, no overwrite', () => {
  const root = tmp();
  const dir = path.join(root, 'data', 'exports');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'conversacion-20240305-070809.md'), 'previo');
  const orig = fs.linkSync;
  fs.linkSync = () => { const e = new Error('nope'); e.code = 'EPERM'; throw e; };
  try {
    const r = exportConversation(root, [turn()], { now: NOW });
    assert.strictEqual(r.file, 'data/exports/conversacion-20240305-070809-2.md');
  } finally { fs.linkSync = orig; }
  assert.deepStrictEqual(fs.readdirSync(dir).sort(), ['conversacion-20240305-070809-2.md', 'conversacion-20240305-070809.md']);
  assert.strictEqual(fs.readFileSync(path.join(dir, 'conversacion-20240305-070809.md'), 'utf8'), 'previo');
  fs.rmSync(root, { recursive: true });
});

test('F18-15: renderer shows a Spanish error message for the export button', () => {
  assert.match(read('renderer/renderer.js'), /No se pudo exportar/);
});

test('F18-16: fallback never writes to a final name directly (atomic via temp + rename)', () => {
  const root = tmp();
  const dir = path.join(root, 'data', 'exports');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'conversacion-20240305-070809.md'), 'previo');
  const origLink = fs.linkSync;
  const origWrite = fs.writeFileSync;
  const writes = [];
  fs.linkSync = () => { const e = new Error('nope'); e.code = 'EPERM'; throw e; };
  fs.writeFileSync = (p, ...rest) => { writes.push(String(p)); return origWrite(p, ...rest); };
  let r;
  try { r = exportConversation(root, [turn()], { now: NOW }); } finally { fs.linkSync = origLink; fs.writeFileSync = origWrite; }
  assert.strictEqual(r.file, 'data/exports/conversacion-20240305-070809-2.md');
  assert.ok(writes.length > 0 && writes.every((p) => !/conversacion-[\d-]+(-\d+)?\.md$/.test(p)), writes.join(','));
  assert.match(fs.readFileSync(path.join(dir, 'conversacion-20240305-070809-2.md'), 'utf8'), /^# Conversación\n/);
  assert.strictEqual(fs.readFileSync(path.join(dir, 'conversacion-20240305-070809.md'), 'utf8'), 'previo');
  assert.deepStrictEqual(fs.readdirSync(dir).filter((f) => f.endsWith('.tmp')), []);
  fs.rmSync(root, { recursive: true });
});

test('F18-17: a crash while writing leaves no final .md and no temp (link and fallback)', () => {
  for (const noLink of [false, true]) {
    const root = tmp();
    const dir = path.join(root, 'data', 'exports');
    const origLink = fs.linkSync;
    const origWrite = fs.writeFileSync;
    if (noLink) fs.linkSync = () => { const e = new Error('nope'); e.code = 'EPERM'; throw e; };
    const origCopy = fs.copyFileSync;
    fs.writeFileSync = (p, d, ...rest) => { origWrite(p, String(d).slice(0, 5), ...rest); throw new Error('crash'); };
    fs.copyFileSync = (src, dst) => { origWrite(dst, 'PARTIAL'); const e = new Error('crash ENOSPC'); e.code = 'ENOSPC'; throw e; };
    try { assert.throws(() => exportConversation(root, [turn()], { now: NOW }), /crash/); } finally { fs.linkSync = origLink; fs.writeFileSync = origWrite; fs.copyFileSync = origCopy; }
    assert.deepStrictEqual(fs.readdirSync(dir), []);
    fs.rmSync(root, { recursive: true });
  }
});

test('F18-18: sparse history keeps the invariant (holes are empty turns)', () => {
  for (const h of [new Array(2), [turn({ q: 'x' }), , turn({ q: 'z' })]]) { // eslint-disable-line no-sparse-arrays
    const md = conversationToMarkdown(h, { now: NOW });
    const ls = md.split('\n');
    assert.strictEqual(ls.filter((l) => l.startsWith('## ')).length, h.length);
    assert.strictEqual(ls.filter((l) => l.startsWith('# ')).length, 1);
    assert.match(md, new RegExp(`· ${h.length} turnos_`));
  }
  assert.ok(conversationToMarkdown([turn({ q: 'x' }), , turn({ q: 'z' })], { now: NOW }).includes('## 2. \n')); // eslint-disable-line no-sparse-arrays
});

test('F18-19: citation fields without prototype or hostile toString do not throw', () => {
  const hostile = { toString() { throw new Error('boom'); } };
  let md;
  assert.doesNotThrow(() => {
    md = conversationToMarkdown([turn({ citations: [{ doc: Object.create(null), chunkId: hostile, line: Object.create(null), section: Object.create(null) }] })], { now: NOW });
  });
  assert.ok(md.includes('- ? · ? · línea ?\n'));
});

test('F18-20: empty q keeps the literal template "## 1. "', () => {
  assert.ok(conversationToMarkdown([turn({ q: '' })], { now: NOW }).includes('\n## 1. \n'));
});

test('F18-21: fallback without hard links never overwrites a file that appears late (race)', () => {
  const root = tmp();
  const dir = path.join(root, 'data', 'exports');
  fs.mkdirSync(dir, { recursive: true });
  const prev = path.join(dir, 'conversacion-20240305-070809.md');
  fs.writeFileSync(prev, 'PREVIO-ORIGINAL');
  const origLink = fs.linkSync;
  const origExists = fs.existsSync;
  fs.linkSync = () => { const e = new Error('nope'); e.code = 'EPERM'; throw e; };
  fs.existsSync = () => false;
  let res;
  try { res = exportConversation(root, [turn()], { now: new Date('2024-03-05T07:08:09.123Z') }); } finally { fs.linkSync = origLink; fs.existsSync = origExists; }
  assert.strictEqual(fs.readFileSync(prev, 'utf8'), 'PREVIO-ORIGINAL');
  assert.strictEqual(res.file, 'data/exports/conversacion-20240305-070809-2.md');
  assert.strictEqual(fs.readFileSync(path.join(root, res.file), 'utf8'), conversationToMarkdown([turn()], { now: new Date('2024-03-05T07:08:09.123Z') }));
  assert.deepStrictEqual(fs.readdirSync(dir).sort(), ['conversacion-20240305-070809-2.md', 'conversacion-20240305-070809.md']);
  fs.rmSync(root, { recursive: true });
});

test('F18-22: opts.now null is treated as absent (defaults to the current time)', () => {
  const md = conversationToMarkdown([turn()], { now: null });
  assert.ok(!md.includes('1970-01-01'));
  assert.ok(md.includes(`_Exportada: ${new Date().getUTCFullYear()}-`));
  const root = tmp();
  const { file } = exportConversation(root, [turn()], { now: null });
  assert.ok(!file.includes('19700101'));
  fs.rmSync(root, { recursive: true });
});

test('F18-23: .gitignore ignores data/exports/', () => {
  const gi = fs.readFileSync(path.join(__dirname, '..', '.gitignore'), 'utf8').split('\n');
  assert.ok(gi.includes('data/exports/'));
});

test('F18-23: fallback failing mid-copy (ENOSPC) or at rename leaves no partial .md, .lock or temp', () => {
  for (const mode of ['copy', 'rename']) {
    const root = tmp();
    const dir = path.join(root, 'data', 'exports');
    fs.mkdirSync(dir, { recursive: true });
    const origLink = fs.linkSync;
    const origCopy = fs.copyFileSync;
    const origRename = fs.renameSync;
    const origWrite = fs.writeFileSync;
    fs.linkSync = () => { const e = new Error('nope'); e.code = 'EPERM'; throw e; };
    fs.copyFileSync = (src, dst) => { origWrite(dst, 'PARTIAL'); const e = new Error('disk full'); e.code = 'ENOSPC'; throw e; };
    if (mode === 'rename') fs.renameSync = () => { const e = new Error('disk full'); e.code = 'ENOSPC'; throw e; };
    try {
      if (mode === 'rename') assert.throws(() => exportConversation(root, [turn()], { now: NOW }), /disk full/);
      else { // copyFileSync must not be the write path: export succeeds with the full content
        const r = exportConversation(root, [turn()], { now: NOW });
        assert.strictEqual(fs.readFileSync(path.join(root, r.file), 'utf8'), conversationToMarkdown([turn()], { now: NOW }));
        fs.rmSync(path.join(root, r.file));
      }
    } finally {
      fs.linkSync = origLink; fs.copyFileSync = origCopy; fs.renameSync = origRename;
    }
    assert.deepStrictEqual(fs.readdirSync(dir), [], mode);
    fs.rmSync(root, { recursive: true });
  }
});

test('F18-24: fallback skips a name reserved by a lock file and cleans up its own lock', () => {
  const root = tmp();
  const dir = path.join(root, 'data', 'exports');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'conversacion-20240305-070809.md.lock'), '');
  const origLink = fs.linkSync;
  fs.linkSync = () => { const e = new Error('nope'); e.code = 'EPERM'; throw e; };
  let r;
  try { r = exportConversation(root, [turn()], { now: NOW }); } finally { fs.linkSync = origLink; }
  assert.strictEqual(r.file, 'data/exports/conversacion-20240305-070809-2.md');
  assert.deepStrictEqual(fs.readdirSync(dir).sort(), ['conversacion-20240305-070809-2.md', 'conversacion-20240305-070809.md.lock']);
  fs.rmSync(root, { recursive: true });
});

test('F18-25: opts.now with a year outside 0000-9999 throws EINVAL and writes nothing', () => {
  const root = tmp();
  for (const now of [8.64e15, -8.64e15, new Date(Date.UTC(10000, 0, 1))]) {
    assert.throws(() => exportConversation(root, [turn()], { now }), (e) => e.code === 'EINVAL');
  }
  assert.ok(!fs.existsSync(path.join(root, 'data')));
  fs.rmSync(root, { recursive: true });
});

test('F18-26: year below 1000 is zero-padded to 4 digits in the file name', () => {
  const root = tmp();
  const { file } = exportConversation(root, [turn()], { now: Date.UTC(999, 0, 1) });
  assert.strictEqual(file, 'data/exports/conversacion-09990101-000000.md');
  assert.ok(fs.existsSync(path.join(root, file)));
  fs.rmSync(root, { recursive: true });
});

test('F18-27: failing temp cleanup after a successful export does not turn it into an error', () => {
  const root = tmp();
  const origRm = fs.rmSync;
  fs.rmSync = (p, o) => {
    if (String(p).endsWith('.tmp')) { const e = new Error('busy'); e.code = 'EBUSY'; throw e; }
    return origRm(p, o);
  };
  let r;
  try { r = exportConversation(root, [turn()], { now: NOW }); } finally { fs.rmSync = origRm; }
  assert.strictEqual(r.file, 'data/exports/conversacion-20240305-070809.md');
  assert.strictEqual(fs.readFileSync(path.join(root, r.file), 'utf8'), conversationToMarkdown([turn()], { now: NOW }));
  fs.rmSync(root, { recursive: true });
});

// ---- Cambio de requisito 1: rango de turnos (S5-S9) ----
const five = () => [1, 2, 3, 4, 5].map((i) => turn({ q: `q${i}`, a: `a${i}` }));
const EINVAL = (e) => e instanceof Error && e.code === 'EINVAL';

test('F18-R1: range header is exact and turns keep their original number', () => {
  const out = conversationToMarkdown(five(), { now: NOW, fromTurn: 2, toTurn: 3 });
  assert.strictEqual(out,
    '# Conversación\n\n_Exportada: 2024-03-05T07:08:09.123Z · 2 turnos (2–3 de 5)_\n\n## 2. q2\n\na2\n\n## 3. q3\n\na3\n');
});

test('F18-R2: only fromTurn runs to the last turn; only toTurn starts at 1', () => {
  const a = conversationToMarkdown(five(), { now: NOW, fromTurn: 4 });
  assert.match(a, /· 2 turnos \(4–5 de 5\)_/);
  assert.match(a, /## 4\. q4/);
  assert.match(a, /## 5\. q5/);
  assert.doesNotMatch(a, /## 3\./);
  const b = conversationToMarkdown(five(), { now: NOW, toTurn: 2 });
  assert.match(b, /· 2 turnos \(1–2 de 5\)_/);
  assert.match(b, /## 1\. q1/);
  assert.doesNotMatch(b, /## 3\./);
  assert.match(conversationToMarkdown(five(), { now: NOW, fromTurn: 3, toTurn: 3 }), /· 1 turno \(3–3 de 5\)_/);
});

test('F18-R3: without range (or null/undefined bounds) the output is unchanged', () => {
  const base = conversationToMarkdown(five(), { now: NOW });
  assert.match(base, /· 5 turnos_/);
  assert.doesNotMatch(base, /de 5/);
  assert.strictEqual(conversationToMarkdown(five(), { now: NOW, fromTurn: undefined, toTurn: null }), base);
});

test('F18-R4: invalid range -> EINVAL in conversationToMarkdown', () => {
  for (const r of [{ fromTurn: 1.5 }, { fromTurn: '2' }, { toTurn: NaN }, { toTurn: Infinity }, { fromTurn: -Infinity },
    { fromTurn: 0 }, { toTurn: 0 }, { fromTurn: -1 }, { fromTurn: 6 }, { toTurn: 6 }, { fromTurn: 4, toTurn: 3 }, { toTurn: '3' }]) {
    assert.throws(() => conversationToMarkdown(five(), { now: NOW, ...r }), EINVAL, JSON.stringify(r));
  }
});

test('F18-R5: invalid range -> EINVAL in exportConversation and no file or folder is created', () => {
  const root = tmp();
  for (const r of [{ fromTurn: 1.5 }, { fromTurn: '2' }, { toTurn: NaN }, { toTurn: Infinity },
    { fromTurn: 0 }, { toTurn: 0 }, { fromTurn: 6 }, { toTurn: 6 }, { fromTurn: 4, toTurn: 3 }]) {
    assert.throws(() => exportConversation(root, five(), { now: NOW, ...r }), EINVAL, JSON.stringify(r));
  }
  assert.ok(!fs.existsSync(path.join(root, 'data')));
  fs.rmSync(root, { recursive: true });
});

test('F18-R6: exportConversation writes only the range; null/undefined bounds count as absent', () => {
  const root = tmp();
  const r = exportConversation(root, five(), { now: NOW, fromTurn: 2, toTurn: 3 });
  assert.strictEqual(r.file, 'data/exports/conversacion-20240305-070809.md');
  assert.strictEqual(r.turns, 2);
  assert.strictEqual(fs.readFileSync(path.join(root, r.file), 'utf8'),
    conversationToMarkdown(five(), { now: NOW, fromTurn: 2, toTurn: 3 }));
  const full = exportConversation(root, five(), { now: NOW, fromTurn: null, toTurn: undefined });
  assert.strictEqual(full.turns, 5);
  assert.strictEqual(fs.readFileSync(path.join(root, full.file), 'utf8'), conversationToMarkdown(five(), { now: NOW }));
  fs.rmSync(root, { recursive: true });
});

test('F18-R7: range does not mutate the history', () => {
  const h = five();
  const snap = JSON.stringify(h);
  conversationToMarkdown(h, { now: NOW, fromTurn: 2, toTurn: 3 });
  assert.strictEqual(JSON.stringify(h), snap);
});

test('F18-R8: wiring accepts the optional range (channel, preload, log)', () => {
  const m = read('main.js');
  assert.match(m, /ipcMain\.handle\('conv:export', \(_e, range\)/);
  assert.match(m, /const opts = rangeOpts\(range\);\s+const res = exportConversation\(__dirname, state\.conversation, opts\);/);
  assert.match(m, /log\.info\('conv\.export', \{ file: res\.file, turns: res\.turns, from, to \}\)/);
  assert.match(read('preload.js'), /convExport:\s*\(range\)\s*=>\s*ipcRenderer\.invoke\('conv:export',\s*range\)/);
  assert.match(read('renderer/renderer.js'), /kb\.convExport\(\)/); // the existing button is unchanged
});

// Loads main.js with electron and side-effectful libs stubbed; returns the registered IPC handlers.
async function loadMain(history) {
  const calls = [];
  const logs = [];
  const handlers = {};
  const exp = require('../lib/export');
  const real = exp.exportConversation;
  exp.exportConversation = (root, h, opts) => { calls.push(opts); return { file: 'data/exports/x.md', turns: h.length }; };
  const stubs = {
    '../lib/docs': { ensureDocsDir: () => '/nonexistent' },
    '../lib/state': { loadState: () => ({ conversation: history }), saveState() {}, recordImports() {}, setLastSelected() {}, setConversation() {} },
    '../lib/indexer': { createIndexer: () => ({}) },
    '../lib/logger': { createLogger: () => ({ info: (ev, f) => logs.push([ev, f]), error() {} }) },
  };
  const saved = new Map();
  for (const [k, v] of Object.entries(stubs)) {
    const id = require.resolve(k, { paths: [__dirname] });
    saved.set(id, require.cache[id]);
    require.cache[id] = { id, filename: id, loaded: true, exports: v };
  }
  class BW { constructor() { this.webContents = {}; } loadFile() {} static getAllWindows() { return [1]; } static fromWebContents() {} }
  const electron = { app: { whenReady: () => Promise.resolve(), on() {}, quit() {} }, BrowserWindow: BW, ipcMain: { handle: (n, f) => { handlers[n] = f; } }, dialog: {} };
  const origLoad = Module._load;
  Module._load = function (req, ...rest) { return req === 'electron' ? electron : origLoad.call(this, req, ...rest); };
  const mainId = require.resolve('../main.js');
  delete require.cache[mainId];
  try {
    require(mainId);
    await new Promise((r) => setImmediate(r));
  } finally {
    Module._load = origLoad;
    exp.exportConversation = real;
    delete require.cache[mainId];
    for (const [id, prev] of saved) { if (prev) require.cache[id] = prev; else delete require.cache[id]; }
  }
  return { handlers, calls, logs };
}

test('F18-B2: conv:export rejects non-object range with EINVAL and exports nothing', async () => {
  const { handlers, calls, logs } = await loadMain([turn(), turn(), turn()]);
  for (const bad of ['abc', 5, true, [], [1, 2], 0, '']) {
    assert.throws(() => handlers['conv:export']({}, bad), (e) => e.code === 'EINVAL', `range ${JSON.stringify(bad)}`);
  }
  assert.strictEqual(calls.length, 0);
  assert.strictEqual(logs.filter(([ev]) => ev === 'conv.export').length, 0);
});

test('F18-B2: conv:export keeps undefined/null/{} as no range and forwards ranges', async () => {
  const { handlers, calls, logs } = await loadMain([turn(), turn(), turn()]);
  for (const ok of [undefined, null, {}]) {
    assert.deepStrictEqual(handlers['conv:export']({}, ok), { file: 'data/exports/x.md', turns: 3 });
  }
  assert.deepStrictEqual(calls.map((o) => o.fromTurn), [undefined, undefined, undefined]);
  assert.deepStrictEqual(logs.at(-1), ['conv.export', { file: 'data/exports/x.md', turns: 3, from: 1, to: 3 }]);
  handlers['conv:export']({}, { fromTurn: 2 });
  assert.deepStrictEqual(calls.at(-1), { fromTurn: 2, toTurn: undefined });
  assert.deepStrictEqual(logs.at(-1)[1].from, 2);
  assert.throws(() => handlers['conv:export']({}, { fromTurn: 9 }), (e) => e.code === 'EINVAL');
});

test('F18-B2: full range 1..N counts as ranged (presence of keys)', () => {
  const h = [turn({ q: 'a' }), turn({ q: 'b' })];
  assert.match(conversationToMarkdown(h, { now: NOW, fromTurn: 1, toTurn: 2 }), /· 2 turnos \(1–2 de 2\)_/);
  assert.doesNotMatch(conversationToMarkdown(h, { now: NOW }), /de 2/);
});
