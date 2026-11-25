const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const read = (f) => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');

test('F01: main.js opens a BrowserWindow with isolation and preload', () => {
  const m = read('main.js');
  assert.match(m, /new BrowserWindow/);
  assert.match(m, /contextIsolation:\s*true/);
  assert.match(m, /nodeIntegration:\s*false/);
  assert.match(m, /preload/);
  assert.match(m, /ensureDocsDir/);
  assert.strictEqual(JSON.parse(read('package.json')).main, 'main.js');
});

test('F02/F03: renderer has panels and does not use node APIs', () => {
  const html = read('renderer/index.html');
  for (const id of ['doc-list', 'doc-content', 'question', 'ask', 'conversation', 'conv-clear']) {
    assert.match(html, new RegExp(`id="${id}"`));
  }
  assert.doesNotMatch(read('renderer/renderer.js'), /require\(/);
});
