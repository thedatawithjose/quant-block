const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { loadState, saveState, recordImports, setLastSelected, statePath } = require('../lib/state');
const { ensureDocsDir, importDocs } = require('../lib/docs');

const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'kb-state-'));

test('F07: loadState returns defaults when file missing or corrupt', () => {
  const root = tmp();
  assert.deepStrictEqual(loadState(root), { imports: [], lastSelected: null });
  fs.mkdirSync(path.join(root, 'data'), { recursive: true });
  fs.writeFileSync(statePath(root), '{not json');
  assert.deepStrictEqual(loadState(root), { imports: [], lastSelected: null });
  fs.writeFileSync(statePath(root), JSON.stringify({ imports: 'x', lastSelected: 5 }));
  assert.deepStrictEqual(loadState(root), { imports: [], lastSelected: null });
});

test('F07: state survives a "restart" (save then load from disk)', () => {
  const root = tmp();
  let s = loadState(root);
  s = recordImports(s, [{ name: 'a.md', source: '/x/a.md' }], new Date('2026-01-02T03:04:05Z'));
  s = setLastSelected(s, 'a.md');
  saveState(root, s);
  const again = loadState(root);
  assert.deepStrictEqual(again.imports, [{ name: 'a.md', source: '/x/a.md', importedAt: '2026-01-02T03:04:05.000Z' }]);
  assert.strictEqual(again.lastSelected, 'a.md');
});

test('F07: recordImports replaces same-name entry, does not mutate input', () => {
  const s0 = { imports: [{ name: 'a.md', source: '/o', importedAt: 'old' }], lastSelected: null };
  const s1 = recordImports(s0, [{ name: 'a.md', source: '/n' }], new Date(0));
  assert.strictEqual(s0.imports[0].source, '/o');
  assert.strictEqual(s1.imports.length, 1);
  assert.strictEqual(s1.imports[0].source, '/n');
});

test('F07: importDocs reports records with source path of copied files only', () => {
  const root = tmp();
  const src = tmp();
  const dir = ensureDocsDir(root);
  fs.writeFileSync(path.join(src, 'a.md'), 'a');
  fs.writeFileSync(path.join(src, 'b.png'), 'b');
  const r = importDocs(dir, [path.join(src, 'a.md'), path.join(src, 'b.png')]);
  assert.deepStrictEqual(r.records, [{ name: 'a.md', source: path.join(src, 'a.md') }]);
});

test('F07: wiring: main.js and preload expose state channels', () => {
  const main = fs.readFileSync(path.join(__dirname, '..', 'main.js'), 'utf8');
  const pre = fs.readFileSync(path.join(__dirname, '..', 'preload.js'), 'utf8');
  for (const c of ['state:get', 'state:select']) {
    assert.ok(main.includes(c), `main.js missing ${c}`);
    assert.ok(pre.includes(c), `preload.js missing ${c}`);
  }
});
