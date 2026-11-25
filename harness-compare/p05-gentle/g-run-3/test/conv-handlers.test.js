const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const Module = require('node:module');

const ROOT = path.join(__dirname, '..');
const MAIN = path.join(ROOT, 'main.js');
const PRELOAD = path.join(ROOT, 'preload.js');

// Loads `file` with a fake `electron` (and, for main.js, redirected data dir, fake indexer and capture logger).
function load(file, overrides) {
  const orig = Module._load;
  Module._load = function (request, parent, ...rest) {
    if (request in overrides && parent && parent.filename === file) return overrides[request];
    return orig.call(this, request, parent, request in overrides ? false : rest[0]);
  };
  delete require.cache[file];
  try { require(file); } finally { Module._load = orig; delete require.cache[file]; }
}

async function bootMain({ indexer }) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'f13-'));
  const handlers = {};
  const logs = [];
  const realState = require('../lib/state');
  const electron = {
    app: { whenReady: () => ({ then: (fn) => { electron.ready = Promise.resolve().then(fn); } }), on() {} },
    BrowserWindow: Object.assign(function () { return { loadFile() {} }; }, { getAllWindows: () => [{}] }),
    ipcMain: { handle: (ch, fn) => { handlers[ch] = fn; } },
    dialog: {},
  };
  const cap = (level) => (event, fields) => logs.push({ level, event, ...fields });
  load(MAIN, {
    electron,
    './lib/docs': { ...require('../lib/docs'), ensureDocsDir: () => tmp },
    './lib/state': {
      ...realState,
      loadState: () => realState.loadState(tmp),
      saveState: (_root, s) => realState.saveState(tmp, s),
    },
    './lib/indexer': { createIndexer: () => indexer },
    './lib/logger': { createLogger: () => ({ info: cap('info'), warn: cap('warn'), error: cap('error') }) },
  });
  await electron.ready;
  const stateFile = path.join(tmp, 'data', 'state.json');
  const persisted = () => (fs.existsSync(stateFile) ? JSON.parse(fs.readFileSync(stateFile, 'utf8')).conversation : undefined);
  return { handlers, logs, persisted, cleanup: () => fs.rmSync(tmp, { recursive: true, force: true }) };
}

const goodIndex = { chunks: [{ id: 'a.md#1', doc: 'a.md', line: 1, text: 'gatos comen pescado' }], docs: {} };
const fakeIndexer = (get, started = []) => ({
  status: () => ({ state: started.length ? 'done' : 'idle' }),
  start: async () => { started.push(1); },
  get,
});

test('F13 AC19: preload bridges conv channels with correct arguments', () => {
  const calls = [];
  let exposed;
  load(PRELOAD, {
    electron: {
      contextBridge: { exposeInMainWorld: (_n, api) => { exposed = api; } },
      ipcRenderer: { invoke: (...a) => { calls.push(a); }, on() {} },
    },
  });
  exposed.convGet(); exposed.convAsk('gatos'); exposed.convClear();
  assert.deepStrictEqual(calls, [['conv:get'], ['conv:ask', 'gatos'], ['conv:clear']]);
});

test('F13 AC21: conv:ask and conv:clear persist state and log structured events', async () => {
  const started = [];
  const m = await bootMain({ indexer: fakeIndexer(() => goodIndex, started) });
  try {
    assert.deepStrictEqual(await m.handlers['conv:get'](), []);
    const r1 = await m.handlers['conv:ask']({}, 'gatos');
    assert.strictEqual(r1.history.length, 1);
    assert.strictEqual(started.length, 1);
    const r2 = await m.handlers['conv:ask']({}, 'dieta');
    assert.strictEqual(r2.turn.effectiveQuery, 'gatos dieta');
    assert.strictEqual(m.persisted().length, 2);
    assert.strictEqual((await m.handlers['conv:get']()).length, 2);
    const asks = m.logs.filter((l) => l.event === 'conv.ask');
    assert.strictEqual(asks.length, 2);
    assert.deepStrictEqual(
      [asks[0].level, asks[0].turns, asks[0].followUp, asks[0].effectiveQuery, asks[0].citations],
      ['info', 1, false, 'gatos', 1],
    );
    assert.strictEqual(asks[1].followUp, true);
    assert.deepStrictEqual(await m.handlers['conv:clear'](), []);
    assert.deepStrictEqual(m.persisted(), []);
    const clear = m.logs.find((l) => l.event === 'conv.clear');
    assert.deepStrictEqual([clear.level, clear.cleared], ['info', 2]);
  } finally { m.cleanup(); }
});

test('F13 D1/D-04: empty or unanswerable questions neither persist nor log conv.ask', async () => {
  const m = await bootMain({ indexer: fakeIndexer(() => goodIndex) });
  try {
    for (const q of ['', '   ', undefined, '???']) {
      const r = await m.handlers['conv:ask']({}, q);
      assert.strictEqual(r.turn, null);
      assert.deepStrictEqual(r.history, []);
    }
    assert.strictEqual(m.persisted(), undefined);
    assert.strictEqual(m.logs.filter((l) => l.event === 'conv.ask').length, 0);
  } finally { m.cleanup(); }
  const empty = await bootMain({ indexer: fakeIndexer(() => null) });
  try {
    assert.strictEqual((await empty.handlers['conv:ask']({}, 'gatos')).turn, null);
    assert.strictEqual(empty.persisted(), undefined);
  } finally { empty.cleanup(); }
});

test('F13 AC22: conv:ask failure logs conv.ask.failed, propagates and keeps state', async () => {
  let fail = false;
  const m = await bootMain({ indexer: fakeIndexer(() => { if (fail) throw new Error('index boom'); return goodIndex; }) });
  try {
    await m.handlers['conv:ask']({}, 'gatos');
    const before = m.persisted();
    fail = true;
    await assert.rejects(() => m.handlers['conv:ask']({}, 'dieta'), /index boom/);
    assert.deepStrictEqual(m.persisted(), before);
    assert.strictEqual((await m.handlers['conv:get']()).length, 1);
    const f = m.logs.find((l) => l.event === 'conv.ask.failed');
    assert.strictEqual(f.level, 'error');
    assert.strictEqual(f.err.message, 'index boom');
  } finally { m.cleanup(); }
});
