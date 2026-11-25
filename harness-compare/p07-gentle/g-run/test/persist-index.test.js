const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { createIndexer } = require('../lib/indexer');

function setup() {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'kbp-'));
  fs.writeFileSync(path.join(d, 'a.md'), '# A\n\nuno\n\ndos');
  fs.writeFileSync(path.join(d, 'b.txt'), 'solo texto');
  return { d, file: path.join(d, '..', path.basename(d) + '-index.json') };
}
const bump = (f) => { const t = new Date(Date.now() + 5000); fs.utimesSync(f, t, t); };

test('F12: index is written to the file and reloaded by a new indexer', async () => {
  const { d, file } = setup();
  await createIndexer(d, { file }).start();
  assert.ok(fs.existsSync(file));
  const ix2 = createIndexer(d, { file });
  assert.strictEqual(ix2.get().chunks.length, 4);
  assert.strictEqual(ix2.get().docs['a.md'].title, 'A');
});

test('F12: unchanged docs are not reindexed (0/0), index kept', async () => {
  const { d, file } = setup();
  await createIndexer(d, { file }).start();
  const seen = [];
  const r = await createIndexer(d, { file }).start((s) => seen.push(`${s.done}/${s.total}`));
  assert.deepStrictEqual(seen, ['0/0']);
  assert.deepStrictEqual(r, { state: 'done', done: 0, total: 0, chunks: 4, failed: [] });
});

test('F12: new and modified docs are reindexed, progress counts only those', async () => {
  const { d, file } = setup();
  await createIndexer(d, { file }).start();
  fs.writeFileSync(path.join(d, 'a.md'), '# A2\n\nuno\n\ndos\n\ntres');
  bump(path.join(d, 'a.md'));
  fs.writeFileSync(path.join(d, 'c.md'), 'nuevo');
  const ix = createIndexer(d, { file });
  const seen = [];
  const r = await ix.start((s) => seen.push(`${s.done}/${s.total}`));
  assert.deepStrictEqual(seen, ['0/2', '1/2', '2/2']);
  assert.strictEqual(r.chunks, 6);
  assert.strictEqual(ix.get().docs['a.md'].title, 'A2');
  assert.ok(ix.get().docs['c.md']);
});

test('F12: deleted docs are dropped from the index and the file', async () => {
  const { d, file } = setup();
  await createIndexer(d, { file }).start();
  fs.unlinkSync(path.join(d, 'b.txt'));
  const ix = createIndexer(d, { file });
  const r = await ix.start();
  assert.deepStrictEqual(r, { state: 'done', done: 0, total: 0, chunks: 3, failed: [] });
  assert.strictEqual(ix.get().docs['b.txt'], undefined);
  assert.ok(!ix.get().chunks.some((c) => c.doc === 'b.txt'));
  assert.strictEqual(createIndexer(d, { file }).get().chunks.length, 3);
});

test('F12: corrupt or missing index file falls back to full reindex', async () => {
  const { d, file } = setup();
  fs.writeFileSync(file, '{not json');
  const ix = createIndexer(d, { file });
  assert.strictEqual(ix.get().chunks.length, 0);
  const r = await ix.start();
  assert.strictEqual(r.total, 2);
  assert.strictEqual(r.chunks, 4);
});

test('F15: same-mtime content change is reindexed; touch without change is not', async () => {
  const { d, file } = setup();
  const a = path.join(d, 'a.md');
  await createIndexer(d, { file }).start();
  const st = fs.statSync(a);
  fs.writeFileSync(a, '# B\n\nuno\n\ndos'); // same length, different content
  fs.utimesSync(a, st.atime, st.mtime); // restore mtime
  const r = await createIndexer(d, { file }).start();
  assert.strictEqual(r.total, 1);
  const ix = createIndexer(d, { file });
  assert.strictEqual(ix.get().docs['a.md'].title, 'B');
  bump(a); // mtime only
  const r2 = await ix.start();
  assert.deepStrictEqual(r2, { state: 'done', done: 0, total: 0, chunks: 4, failed: [] });
});

test('F15: persisted index stores hashes; old index without hashes loads and reindexes', async () => {
  const { d, file } = setup();
  await createIndexer(d, { file }).start();
  const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
  assert.ok(raw.hashes && /^[0-9a-f]{64}$/.test(raw.hashes['a.md']));
  delete raw.hashes;
  raw.mtimes = { 'a.md': 1, 'b.txt': 2 };
  fs.writeFileSync(file, JSON.stringify(raw));
  const ix = createIndexer(d, { file });
  const r = await ix.start();
  assert.strictEqual(r.total, 2);
  assert.strictEqual(r.chunks, 4);
  assert.ok(JSON.parse(fs.readFileSync(file, 'utf8')).hashes['b.txt']);
});

test('F12: main.js persists to data/index.json', () => {
  const m = fs.readFileSync(path.join(__dirname, '..', 'main.js'), 'utf8');
  assert.match(m, /index\.json/);
});
