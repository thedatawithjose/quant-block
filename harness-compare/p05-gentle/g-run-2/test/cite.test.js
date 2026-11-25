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
  assert.match(r('main.js'), /qa:cited/);
  assert.match(r('preload.js'), /askCited/);
  assert.match(r('renderer/index.html'), /id="conversation"/); // F13: citations render inside each conversation turn
  assert.match(r('renderer/renderer.js'), /chunkId/);
});
