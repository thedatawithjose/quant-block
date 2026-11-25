const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { chunkDoc } = require('../lib/chunk');
const { extractMeta } = require('../lib/meta');
const { answerWithCitations } = require('../lib/cite');
const { createIndexer } = require('../lib/indexer');

const docs = {
  'a.md': 'intro gatos\n\n# Gatos\n\nLos gatos duermen.\n\n## Cuidados ##\n\nGatos comen.',
  'b.txt': 'Gatos sin encabezado.',
};
const index = { docs: {}, chunks: [] };
for (const [n, t] of Object.entries(docs)) { index.docs[n] = extractMeta(n, t); index.chunks.push(...chunkDoc(n, t)); }

test('F16: citation section is nearest heading at or before chunk start, else null', () => {
  const r = answerWithCitations(index, 'gatos');
  const sec = Object.fromEntries(r.citations.map((c) => [c.chunkId, c.section]));
  assert.deepStrictEqual(sec, { 'a.md#1': null, 'a.md#2': 'Gatos', 'a.md#3': 'Gatos', 'a.md#5': 'Cuidados', 'b.txt#1': null });
});

test('F16: opts.docs filters; empty/absent means all; no match gives [] and text', () => {
  const only = answerWithCitations(index, 'gatos', { docs: ['b.txt'] });
  assert.deepStrictEqual(only.citations.map((c) => c.doc), ['b.txt']);
  assert.strictEqual(answerWithCitations(index, 'gatos', { docs: [] }).citations.length, 5);
  assert.strictEqual(answerWithCitations(index, 'gatos', {}).citations.length, 5);
  const none = answerWithCitations(index, 'gatos', { docs: ['zzz.md'] });
  assert.deepStrictEqual(none.citations, []);
  assert.strictEqual(typeof none.answer, 'string');
});

test('F17: status.failed lists unreadable docs, resets each run; index.done logs failed and durationMs', async () => {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'kbf-'));
  fs.writeFileSync(path.join(d, 'ok.md'), 'hola');
  fs.writeFileSync(path.join(d, 'bad.md'), 'x'); fs.chmodSync(path.join(d, 'bad.md'), 0o000);
  const events = [];
  const ix = createIndexer(d, { logger: { info: (m, f) => events.push([m, f]), warn() {}, error() {} } });
  const r = await ix.start();
  assert.strictEqual(r.failed.length, 1);
  assert.strictEqual(r.failed[0].doc, 'bad.md');
  assert.strictEqual(typeof r.failed[0].message, 'string');
  const done = events.find((e) => e[0] === 'index.done')[1];
  assert.strictEqual(done.failed, 1);
  assert.strictEqual(typeof done.durationMs, 'number');
  fs.rmSync(path.join(d, 'bad.md'));
  assert.deepStrictEqual((await ix.start()).failed, []);
});
