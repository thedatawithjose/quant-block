const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { ensureDocsDir, listDocs, importDocs, docInfo } = require('../lib/docs');

function setup() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'kb-'));
  const src = fs.mkdtempSync(path.join(os.tmpdir(), 'kb-src-'));
  return { dir: ensureDocsDir(root), src };
}

test('F05: importDocs copies .md/.txt, skips other extensions', () => {
  const { dir, src } = setup();
  fs.writeFileSync(path.join(src, 'a.md'), '# A');
  fs.writeFileSync(path.join(src, 'b.txt'), 'b');
  fs.writeFileSync(path.join(src, 'c.png'), 'x');
  const r = importDocs(dir, [path.join(src, 'a.md'), path.join(src, 'b.txt'), path.join(src, 'c.png')]);
  assert.deepStrictEqual(r.imported, ['a.md', 'b.txt']);
  assert.strictEqual(r.skipped.length, 1);
  assert.deepStrictEqual(listDocs(dir), ['a.md', 'b.txt']);
});

test('F14: importDocs renames on collision and never overwrites', () => {
  const { dir, src } = setup();
  fs.writeFileSync(path.join(dir, 'a.md'), 'original');
  fs.writeFileSync(path.join(dir, 'a (2).md'), 'second');
  fs.writeFileSync(path.join(src, 'a.md'), 'nuevo');
  const r = importDocs(dir, [path.join(src, 'a.md')]);
  assert.deepStrictEqual(r.imported, ['a (3).md']);
  assert.deepStrictEqual(r.renamed, [{ from: 'a.md', to: 'a (3).md' }]);
  assert.deepStrictEqual(r.records, [{ name: 'a (3).md', source: path.join(src, 'a.md') }]);
  assert.deepStrictEqual(r.skipped, []);
  assert.strictEqual(fs.readFileSync(path.join(dir, 'a.md'), 'utf8'), 'original');
  assert.strictEqual(fs.readFileSync(path.join(dir, 'a (2).md'), 'utf8'), 'second');
  assert.strictEqual(fs.readFileSync(path.join(dir, 'a (3).md'), 'utf8'), 'nuevo');
});

test('F14: same name twice in one call, plus extension skip and no rename when free', () => {
  const { dir, src } = setup();
  const other = fs.mkdtempSync(path.join(os.tmpdir(), 'kb-src2-'));
  fs.writeFileSync(path.join(src, 'a.md'), 'uno');
  fs.writeFileSync(path.join(other, 'a.md'), 'dos');
  fs.writeFileSync(path.join(src, 'c.png'), 'x');
  fs.writeFileSync(path.join(src, 'b.txt'), 'b');
  const r = importDocs(dir, [path.join(src, 'a.md'), path.join(other, 'a.md'), path.join(src, 'c.png'), path.join(src, 'b.txt')]);
  assert.deepStrictEqual(r.imported, ['a.md', 'a (2).md', 'b.txt']);
  assert.deepStrictEqual(r.renamed, [{ from: 'a.md', to: 'a (2).md' }]);
  assert.deepStrictEqual(r.skipped, [{ file: 'c.png', reason: 'extension' }]);
  assert.deepStrictEqual(r.records.map((x) => x.name), ['a.md', 'a (2).md', 'b.txt']);
  assert.strictEqual(fs.readFileSync(path.join(dir, 'a.md'), 'utf8'), 'uno');
  assert.strictEqual(fs.readFileSync(path.join(dir, 'a (2).md'), 'utf8'), 'dos');
});

test('F05: importDocs tolerates missing source and bad input', () => {
  const { dir, src } = setup();
  const r = importDocs(dir, [path.join(src, 'nope.md'), 42]);
  assert.deepStrictEqual(r.imported, []);
  assert.strictEqual(r.skipped.length, 2);
  assert.deepStrictEqual(importDocs(dir, undefined).imported, []);
});

test('F06: docInfo returns name, size in bytes, mtime and content', () => {
  const { dir } = setup();
  fs.writeFileSync(path.join(dir, 'a.md'), 'hola ñ'); // 7 bytes in utf8
  const i = docInfo(dir, 'a.md');
  assert.strictEqual(i.name, 'a.md');
  assert.strictEqual(i.size, 7);
  assert.strictEqual(i.content, 'hola ñ');
  assert.ok(!Number.isNaN(Date.parse(i.mtime)));
});

test('F06: docInfo rejects traversal and bad extensions', () => {
  const { dir } = setup();
  assert.throws(() => docInfo(dir, '../x.md'));
  assert.throws(() => docInfo(dir, 'x.png'));
});
