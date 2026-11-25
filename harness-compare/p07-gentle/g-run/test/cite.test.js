const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { chunkDoc } = require('../lib/chunk');
const { extractMeta } = require('../lib/meta');
const { answerWithCitations } = require('../lib/cite');

const docs = {
  'a.md': '# Gatos\n\nLos gatos duermen mucho.\n\nLos perros ladran.',
  'b.txt': 'Texto sin relacion.\n\nOtro parrafo sobre GATOS y perros.',
};
const index = { docs: {}, chunks: [] };
for (const [n, t] of Object.entries(docs)) { index.docs[n] = extractMeta(n, t); index.chunks.push(...chunkDoc(n, t)); }

test('F11: returns matching chunks with doc, chunk id and line citation', () => {
  const r = answerWithCitations(index, 'gatos');
  const cites = r.citations.map((c) => [c.doc, c.chunkId, c.line]);
  assert.deepStrictEqual(cites.sort(), [['a.md', 'a.md#1', 1], ['a.md', 'a.md#2', 3], ['b.txt', 'b.txt#2', 3]].sort());
  assert.ok(r.citations.every((c) => c.text && c.title));
  assert.match(r.answer, /a\.md#2/);
});

test('F11: ranks chunks matching more question terms first and ignores accents/case', () => {
  const r = answerWithCitations(index, 'GATOS perros');
  assert.strictEqual(r.citations[0].chunkId, 'b.txt#2');
  assert.deepStrictEqual(answerWithCitations(index, 'relación').citations.map((c) => c.chunkId), ['b.txt#1']);
});

test('F11: no match, empty question, missing index give no citations and a message', () => {
  assert.deepStrictEqual(answerWithCitations(index, 'zzz').citations, []);
  assert.match(answerWithCitations(index, 'zzz').answer, /No se encontr/);
  assert.match(answerWithCitations(index, '  ').answer, /pregunta/i);
  assert.deepStrictEqual(answerWithCitations(null, 'x').citations, []);
});

test('F11: wiring in main.js, preload.js and renderer', () => {
  const r = (f) => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');
  assert.match(r('renderer/index.html'), /id="citations"/);
  assert.match(r('renderer/renderer.js'), /chunkId/);
});

test('F16: citation.section is the nearest heading at or before the chunk start line, null if none', () => {
  const t = 'intro gatos\n\n# Uno\n\nparrafo gatos\n\n## Dos\ntexto\n\n```\n# no es titulo\n```\n\ncola gatos';
  const ix = { docs: {}, chunks: chunkDoc('s.md', t) };
  const by = Object.fromEntries(answerWithCitations(ix, 'gatos').citations.map((c) => [c.line, c.section]));
  assert.strictEqual(by[1], null);
  assert.strictEqual(by[5], 'Uno');
  assert.strictEqual(by[14], 'Dos');
  const h = answerWithCitations(ix, 'Dos').citations[0]; // chunk starting with its own heading
  assert.strictEqual(h.section, 'Dos');
  assert.strictEqual(answerWithCitations(index, 'duermen').citations[0].section, 'Gatos');
  assert.strictEqual(answerWithCitations(index, 'relacion').citations[0].section, null);
});

test('F16: opts.docs restricts the search; empty or missing means all; no match gives []', () => {
  const ids = (o) => answerWithCitations(index, 'gatos', o).citations.map((c) => c.doc);
  assert.deepStrictEqual([...new Set(ids({ docs: ['b.txt'] }))], ['b.txt']);
  assert.strictEqual(ids({ docs: [] }).length, 3);
  assert.strictEqual(ids({}).length, 3);
  assert.strictEqual(ids().length, 3);
  const none = answerWithCitations(index, 'gatos', { docs: ['nope.md'] });
  assert.deepStrictEqual(none.citations, []);
  assert.strictEqual(typeof none.answer, 'string');
  assert.ok(none.answer.length > 0);
  assert.deepStrictEqual(answerWithCitations(index, 'perros', { docs: ['a.md'] }).citations.map((c) => c.doc), ['a.md']);
});

test('F16: renderer shows the section', () => {
  const r = fs.readFileSync(path.join(__dirname, '..', 'renderer/renderer.js'), 'utf8');
  assert.match(r, /c\.section/);
});
