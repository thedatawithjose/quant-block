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
  assert.deepStrictEqual(ix.status(), { state: 'idle', done: 0, total: 0, chunks: 0, failed: [] });
});

test('F10: start indexes all docs, reports n/total progress and done state', async () => {
  const ix = createIndexer(tmpDocs());
  const seen = [];
  const final = await ix.start((s) => seen.push(`${s.done}/${s.total}`));
  assert.deepStrictEqual(seen, ['0/2', '1/2', '2/2']);
  assert.deepStrictEqual(final, { state: 'done', done: 2, total: 2, chunks: 4, failed: [] });
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
  assert.deepStrictEqual(await ix.start(), { state: 'done', done: 0, total: 0, chunks: 0, failed: [] });
  fs.mkdirSync(path.join(d, 'dir.md'));
  const r = await createIndexer(d).start();
  assert.strictEqual(r.state, 'done');
});

test('F10: wiring in main.js, preload.js and renderer', () => {
  const r = (f) => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');
  assert.match(r('main.js'), /index:start/);
  assert.match(r('preload.js'), /indexStart/);
  assert.match(r('renderer/index.html'), /id="index-status"/);
  assert.match(r('renderer/renderer.js'), /\$\{[^}]*done[^}]*\}\/\$\{[^}]*total/);
});

test('F17: status().failed lists unreadable docs, resets each run; index.done logs failed and durationMs', async () => {
  const d = tmpDocs();
  fs.writeFileSync(path.join(d, 'dir.md'), 'x');
  fs.chmodSync(path.join(d, 'dir.md'), 0o000); // unreadable (tests do not run as root)
  const events = [];
  const logger = { info: (e, f) => events.push([e, f]), warn() {}, error() {} };
  const ix = createIndexer(d, { logger });
  const r = await ix.start();
  assert.strictEqual(r.failed.length, 1);
  assert.strictEqual(r.failed[0].doc, 'dir.md');
  assert.ok(typeof r.failed[0].message === 'string' && r.failed[0].message.length > 0);
  assert.strictEqual(r.done, 3);
  const done = events.filter(([e]) => e === 'index.done')[0][1];
  assert.strictEqual(done.failed, 1);
  assert.strictEqual(typeof done.durationMs, 'number');
  assert.ok(done.durationMs >= 0);
  fs.chmodSync(path.join(d, 'dir.md'), 0o644);
  const r2 = await ix.start();
  assert.deepStrictEqual(r2.failed, []);
  assert.strictEqual(events.filter(([e]) => e === 'index.done')[1][1].failed, 0);
});

test('F17: renderer shows failed docs', () => {
  const r = fs.readFileSync(path.join(__dirname, '..', 'renderer/renderer.js'), 'utf8');
  assert.match(r, /\.failed/);
});
