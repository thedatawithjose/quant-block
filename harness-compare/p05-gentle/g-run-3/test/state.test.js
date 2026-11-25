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
  assert.deepStrictEqual(loadState(root), { imports: [], lastSelected: null, conversation: [] });
  fs.mkdirSync(path.join(root, 'data'), { recursive: true });
  fs.writeFileSync(statePath(root), '{not json');
  assert.deepStrictEqual(loadState(root), { imports: [], lastSelected: null, conversation: [] });
  fs.writeFileSync(statePath(root), JSON.stringify({ imports: 'x', lastSelected: 5 }));
  assert.deepStrictEqual(loadState(root), { imports: [], lastSelected: null, conversation: [] });
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

const good = (n) => ({ q: `q${n}`, effectiveQuery: `e${n}`, a: 'a', citations: [] });

test('F13: conversation defaults to [] for missing/corrupt/invalid', () => {
  const root = tmp();
  assert.deepStrictEqual(loadState(root).conversation, []);
  fs.mkdirSync(path.join(root, 'data'), { recursive: true });
  for (const raw of ['{not json', '{}', '{"conversation":"x"}', '{"conversation":{}}', '{"conversation":null}']) {
    fs.writeFileSync(statePath(root), raw);
    const s = loadState(root);
    assert.deepStrictEqual(s.conversation, [], raw);
    assert.deepStrictEqual(s.imports, []);
    assert.strictEqual(s.lastSelected, null);
  }
});

test('F13: invalid conversation items are dropped, keeping last 20', () => {
  const root = tmp();
  fs.mkdirSync(path.join(root, 'data'), { recursive: true });
  const conv = [good(1), null, 5, 'x', { q: 'a' }, { q: 1, effectiveQuery: 'e', a: 'a', citations: [] },
    { q: 'a', effectiveQuery: 'e', a: 'a', citations: 'no' }, good(2)];
  fs.writeFileSync(statePath(root), JSON.stringify({ conversation: conv }));
  assert.deepStrictEqual(loadState(root).conversation, [good(1), good(2)]);
  const many = Array.from({ length: 25 }, (_, i) => good(i));
  fs.writeFileSync(statePath(root), JSON.stringify({ conversation: many }));
  assert.deepStrictEqual(loadState(root).conversation, many.slice(-20));
});

test('F13: conversation survives a "restart" with imports and lastSelected', () => {
  const root = tmp();
  const { askInConversation } = require('../lib/conversation');
  const index = { chunks: [{ id: 'a#1', doc: 'a', n: 1, line: 1, text: 'masa solar' }], docs: {} };
  let conv = askInConversation([], 'masa solar', index).history;
  conv = askInConversation(conv, 'solar', index).history;
  let s = recordImports(loadState(root), [{ name: 'a.md', source: '/x/a.md' }], new Date(0));
  s = setLastSelected({ ...s, conversation: conv }, 'a.md');
  saveState(root, s);
  const again = loadState(root);
  assert.deepStrictEqual(again.conversation, conv);
  assert.strictEqual(again.lastSelected, 'a.md');
  assert.strictEqual(again.imports.length, 1);
  assert.strictEqual(fs.existsSync(`${statePath(root)}.tmp`), false);
});

test('F13: recordImports and setLastSelected keep conversation', () => {
  const s0 = { imports: [], lastSelected: null, conversation: [good(1)] };
  assert.deepStrictEqual(recordImports(s0, [{ name: 'a.md', source: '/s' }]).conversation, [good(1)]);
  assert.deepStrictEqual(setLastSelected(s0, 'x').conversation, [good(1)]);
  const root = tmp();
  saveState(root, setLastSelected(s0, 'x'));
  assert.deepStrictEqual(loadState(root).conversation, [good(1)]);
});

test('F13: clearing conversation is persisted', () => {
  const root = tmp();
  const s = { imports: [], lastSelected: null, conversation: [good(1)] };
  saveState(root, s);
  saveState(root, { ...s, conversation: [] });
  assert.deepStrictEqual(loadState(root).conversation, []);
  assert.deepStrictEqual(JSON.parse(fs.readFileSync(statePath(root), 'utf8')).conversation, []);
});
