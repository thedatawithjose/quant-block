const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { ensureDocsDir } = require('../lib/docs');

test('F04: ensureDocsDir creates data/docs when missing and is idempotent', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'kb-'));
  const dir = ensureDocsDir(root);
  assert.strictEqual(dir, path.join(root, 'data', 'docs'));
  assert.ok(fs.statSync(dir).isDirectory());
  assert.doesNotThrow(() => ensureDocsDir(root));
});
