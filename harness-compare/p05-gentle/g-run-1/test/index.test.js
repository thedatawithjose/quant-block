const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { createIndexer } = require('../lib/indexer');

function tmpDocs() {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'kbidx-'));
  fs.writeFileSync(path.join(d, 'a.md'), '# A\n\nuno dos\n\ntres');
  fs.writeFileSync(path.join(d, 'b.txt'), 'solo texto');
  fs.writeFileSync(path.join(d, 'c.png'), 'ignorado');
  return d;
}

test('F10: status is idle before indexing', () => {
  const ix = createIndexer(tmpDocs());
  assert.deepStrictEqual(ix.status(), { state: 'idle', done: 0, total: 0, chunks: 0 });
});

test('F10: start indexes all docs, reports n/total progress and done state', async () => {
  const ix = createIndexer(tmpDocs());
  const seen = [];
  const final = await ix.start((s) => seen.push(`${s.done}/${s.total}`));
  assert.deepStrictEqual(seen, ['0/2', '1/2', '2/2']);
  assert.deepStrictEqual(final, { state: 'done', done: 2, total: 2, chunks: 4 });
  assert.deepStrictEqual(ix.status(), final);
  const idx = ix.get();
  assert.strictEqual(idx.chunks.length, 4);
  assert.strictEqual(idx.docs['a.md'].title, 'A');
  assert.strictEqual(idx.docs['b.txt'].title, 'b');
  assert.strictEqual(idx.docs['b.txt'].words, 2);
});

test('F10: status is "indexing" mid-run and a second start while running is a no-op', async () => {
  const ix = createIndexer(tmpDocs());
  let mid;
  const p = ix.start((s) => { if (s.done === 1) mid = ix.status().state; });
  const again = ix.start();
  await p; await again;
  assert.strictEqual(mid, 'indexing');
  assert.strictEqual(ix.status().state, 'done');
  assert.strictEqual(ix.get().chunks.length, 4);
});

test('F10: empty dir finishes as done 0/0; unreadable doc is skipped, not fatal', async () => {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'kbidx-'));
  const ix = createIndexer(d);
  assert.deepStrictEqual(await ix.start(), { state: 'done', done: 0, total: 0, chunks: 0 });
  fs.mkdirSync(path.join(d, 'dir.md'));
  const r = await createIndexer(d).start();
  assert.strictEqual(r.state, 'done');
});

test('F10: wiring in main.js, preload.js and renderer', () => {
  const r = (f) => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');
  assert.match(r('main.js'), /index:start/);
  assert.match(r('main.js'), /index:status/);
  assert.match(r('preload.js'), /indexStart/);
  assert.match(r('preload.js'), /indexStatus/);
  assert.match(r('renderer/index.html'), /id="index-status"/);
  assert.match(r('renderer/renderer.js'), /\$\{[^}]*done[^}]*\}\/\$\{[^}]*total/);
});
