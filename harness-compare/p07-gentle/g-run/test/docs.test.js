const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { ensureDocsDir, listDocs, readDoc } = require('../lib/docs');

function setup() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'kb-'));
  const dir = ensureDocsDir(root);
  fs.writeFileSync(path.join(dir, 'b.txt'), 'texto b');
  fs.writeFileSync(path.join(dir, 'a.md'), '# A');
  fs.writeFileSync(path.join(dir, 'img.png'), 'x');
  return dir;
}

test('F02: listDocs returns only .md/.txt, sorted', () => {
  assert.deepStrictEqual(listDocs(setup()), ['a.md', 'b.txt']);
});

test('F02: readDoc returns content', () => {
  assert.strictEqual(readDoc(setup(), 'b.txt'), 'texto b');
});

test('F02: readDoc rejects path traversal and bad extensions', () => {
  const dir = setup();
  assert.throws(() => readDoc(dir, '../x.md'));
  assert.throws(() => readDoc(dir, 'img.png'));
  assert.throws(() => readDoc(dir, 'missing.md'));
});
