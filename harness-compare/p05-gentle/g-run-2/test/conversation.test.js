const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { chunkDoc } = require('../lib/chunk');
const { extractMeta } = require('../lib/meta');
const { answerWithCitations } = require('../lib/cite');
const { askInConversation, clearConversation, significantWords, MAX_TURNS } = require('../lib/conversation');
const { loadState, saveState, statePath } = require('../lib/state');

const docs = {
  'a.md': '# Gatos\n\nLos gatos duermen mucho.\n\nLos perros ladran fuerte.',
  'b.txt': 'Texto sin relacion.\n\nOtro parrafo sobre GATOS y perros.',
};
const index = { docs: {}, chunks: [] };
for (const [n, t] of Object.entries(docs)) { index.docs[n] = extractMeta(n, t); index.chunks.push(...chunkDoc(n, t)); }
const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'kb-conv-'));

test('F13: MAX_TURNS is 20', () => assert.strictEqual(MAX_TURNS, 20));

test('F13: significantWords drops short words and the stop list (accent/case-insensitive)', () => {
  assert.deepStrictEqual(significantWords('Que los gatos de la CUÁL con por para como donde una del las'), ['gatos']);
  assert.deepStrictEqual(significantWords('el es gatos'), ['gatos']);
});

test('F13: first turn without history uses the question itself as effective query', () => {
  const { history, turn } = askInConversation([], 'y?', index);
  assert.strictEqual(turn.q, 'y?');
  assert.strictEqual(turn.effectiveQuery, 'y?');
  assert.deepStrictEqual(history, [turn]);
});

test('F13: question with 3+ significant words is its own effective query', () => {
  const h1 = askInConversation([], 'gatos duermen mucho', index).history;
  const { turn } = askInConversation(h1, 'perros ladran fuerte', index);
  assert.strictEqual(turn.effectiveQuery, 'perros ladran fuerte');
});

test('F13: follow-up with <=2 significant words appends them to previous effective query', () => {
  const h1 = askInConversation([], 'gatos duermen mucho', index).history;
  const r2 = askInConversation(h1, 'y los perros?', index);
  assert.strictEqual(r2.turn.effectiveQuery, 'gatos duermen mucho perros');
  const r3 = askInConversation(r2.history, 'que es?', index);
  assert.strictEqual(r3.turn.effectiveQuery, 'gatos duermen mucho perros');
  const r4 = askInConversation(r3.history, 'relacion', index);
  assert.strictEqual(r4.turn.effectiveQuery, 'gatos duermen mucho perros relacion');
});

test('F13: 2 significant words is a follow-up, 3 is not (boundary)', () => {
  const h = askInConversation([], 'gatos duermen mucho', index).history;
  assert.strictEqual(askInConversation(h, 'perros ladran', index).turn.effectiveQuery, 'gatos duermen mucho perros ladran');
  assert.strictEqual(askInConversation(h, 'perros ladran fuerte', index).turn.effectiveQuery, 'perros ladran fuerte');
});

test('F13: answer and citations come from answerWithCitations(index, effectiveQuery)', () => {
  const h = askInConversation([], 'gatos duermen mucho', index).history;
  const { turn } = askInConversation(h, 'perros', index);
  const exp = answerWithCitations(index, turn.effectiveQuery);
  assert.strictEqual(turn.a, exp.answer);
  assert.deepStrictEqual(turn.citations, exp.citations);
});

test('F13: askInConversation does not mutate history and returns a new array', () => {
  const h = askInConversation([], 'gatos duermen mucho', index).history;
  const snap = JSON.stringify(h);
  const r = askInConversation(h, 'perros', index);
  assert.strictEqual(JSON.stringify(h), snap);
  assert.notStrictEqual(r.history, h);
  assert.strictEqual(r.history.length, 2);
  assert.strictEqual(r.history[1], r.turn);
});

test('F13: history is capped at MAX_TURNS dropping the oldest', () => {
  let h = [];
  for (let i = 0; i < MAX_TURNS + 5; i++) h = askInConversation(h, `pregunta numero${i} gatos`, index).history;
  assert.strictEqual(h.length, MAX_TURNS);
  assert.strictEqual(h[0].q, 'pregunta numero5 gatos');
  assert.strictEqual(h[MAX_TURNS - 1].q, `pregunta numero${MAX_TURNS + 4} gatos`);
});

test('F13: clearConversation returns an empty history without mutating the input', () => {
  const h = askInConversation([], 'gatos duermen mucho', index).history;
  assert.deepStrictEqual(clearConversation(h), []);
  assert.strictEqual(h.length, 1);
});

test('F13: state defaults conversation to [] when missing or invalid', () => {
  const root = tmp();
  assert.deepStrictEqual(loadState(root).conversation, []);
  fs.mkdirSync(path.join(root, 'data'), { recursive: true });
  fs.writeFileSync(statePath(root), JSON.stringify({ imports: [], lastSelected: null }));
  assert.deepStrictEqual(loadState(root).conversation, []);
  fs.writeFileSync(statePath(root), JSON.stringify({ conversation: 'x' }));
  assert.deepStrictEqual(loadState(root).conversation, []);
  fs.writeFileSync(statePath(root), '{bad');
  assert.deepStrictEqual(loadState(root).conversation, []);
});

test('F13: conversation survives a restart and is capped on load; invalid turns dropped', () => {
  const root = tmp();
  let h = [];
  h = askInConversation(h, 'gatos duermen mucho', index).history;
  h = askInConversation(h, 'perros', index).history;
  saveState(root, { ...loadState(root), conversation: h });
  assert.deepStrictEqual(loadState(root).conversation, h);
  const many = Array.from({ length: 25 }, (_, i) => ({ q: `q${i}`, effectiveQuery: `q${i}`, a: 'a', citations: [] }));
  fs.writeFileSync(statePath(root), JSON.stringify({ conversation: [...many, null, { q: 1 }] }));
  const c = loadState(root).conversation;
  assert.strictEqual(c.length, MAX_TURNS);
  assert.strictEqual(c[0].q, 'q5');
});

test('F13: wiring: IPC channels, preload bridge, logs, UI button and no fs in renderer', () => {
  const rd = (f) => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');
  const main = rd('main.js'), pre = rd('preload.js'), html = rd('renderer/index.html'), rend = rd('renderer/renderer.js');
  for (const c of ['conv:get', 'conv:ask', 'conv:clear']) {
    assert.ok(main.includes(c), `main.js missing ${c}`);
    assert.ok(pre.includes(c), `preload.js missing ${c}`);
  }
  for (const e of ['conv.ask', 'conv.clear']) assert.ok(main.includes(`'${e}'`), `main.js missing log ${e}`);
  assert.ok(html.includes('Nueva conversacion'));
  assert.ok(rend.includes('convAsk') && rend.includes('convClear') && rend.includes('convGet'));
  assert.ok(!/require\(|node:/.test(rend));
});

test('D3: NFD (decomposed) input counts words like NFC', () => {
  const nfd = 'ca\u0301lculo ra\u0301pido';
  assert.deepStrictEqual(significantWords(nfd), ['cálculo', 'rápido']);
  const h = askInConversation([], 'gatos duermen mucho', index).history;
  assert.strictEqual(askInConversation(h, nfd, index).turn.effectiveQuery, 'gatos duermen mucho cálculo rápido');
  const three = 'ca\u0301lculo ra\u0301pido ni\u0303os';
  assert.strictEqual(askInConversation(h, three, index).turn.effectiveQuery, three.normalize('NFC'));
});

test('D1: loadState drops invalid citation items but keeps the turn', () => {
  const root = tmp();
  fs.mkdirSync(path.join(root, 'data'), { recursive: true });
  const ok = { doc: 'a.md', chunkId: 'a.md#1', line: 3, text: 'x' };
  const turn = { q: 'q', effectiveQuery: 'q', a: 'a', citations: [ok, null, 5, 'x', {}, { doc: 'a.md', chunkId: 'c', line: 'z', text: 't' }, { ...ok, text: 7 }] };
  fs.writeFileSync(statePath(root), JSON.stringify({ conversation: [turn] }));
  assert.deepStrictEqual(loadState(root).conversation, [{ ...turn, citations: [ok] }]);
});

test('D1: renderer tolerates malformed turns/citations', () => {
  const rend = fs.readFileSync(path.join(__dirname, '..', 'renderer/renderer.js'), 'utf8');
  assert.ok(/Array\.isArray\(t\.citations\)/.test(rend));
  assert.ok(/typeof c !== 'object'|!c \|\| typeof c/.test(rend));
});

// Runs main.js from a temp copy with a stub electron so __dirname (data/state.json, data/app.log) is isolated.
function bootMain() {
  const root = tmp();
  const repo = path.join(__dirname, '..');
  for (const f of ['main.js', 'preload.js']) fs.copyFileSync(path.join(repo, f), path.join(root, f));
  fs.cpSync(path.join(repo, 'lib'), path.join(root, 'lib'), { recursive: true });
  fs.mkdirSync(path.join(root, 'renderer'));
  const docsDir = path.join(root, 'data', 'docs');
  fs.mkdirSync(docsDir, { recursive: true });
  fs.writeFileSync(path.join(docsDir, 'a.md'), docs['a.md']);
  const handlers = {};
  const Module = require('node:module');
  const orig = Module._load;
  Module._load = function (req, ...rest) {
    if (req === 'electron') {
      return {
        app: { whenReady: () => ({ then: (fn) => { fn(); return Promise.resolve(); } }), on() {} , quit() {} },
        BrowserWindow: Object.assign(function () { return { loadFile() {} }; }, { getAllWindows: () => [], fromWebContents: () => null }),
        ipcMain: { handle: (ch, fn) => { handlers[ch] = fn; } },
        dialog: {},
      };
    }
    return orig.call(this, req, ...rest);
  };
  try { require(path.join(root, 'main.js')); } finally { Module._load = orig; }
  return { root, handlers };
}

test('D2/D4: main.js conv handlers persist, ignore blank questions, clear and log', async () => {
  const { root, handlers } = bootMain();
  assert.deepStrictEqual(await handlers['conv:get'](), []);
  for (const blank of ['', '   ', '\n\t', null, undefined]) {
    assert.deepStrictEqual(await handlers['conv:ask']({}, blank), []);
  }
  assert.deepStrictEqual(loadState(root).conversation, []);
  const h1 = await handlers['conv:ask']({}, 'gatos duermen mucho');
  assert.strictEqual(h1.length, 1);
  assert.deepStrictEqual(await handlers['conv:ask']({}, '  '), h1);
  const h2 = await handlers['conv:ask']({}, 'perros');
  assert.strictEqual(h2.length, 2);
  assert.strictEqual(h2[1].effectiveQuery, 'gatos duermen mucho perros');
  assert.deepStrictEqual(loadState(root).conversation, h2);
  assert.deepStrictEqual(await handlers['conv:get'](), h2);
  assert.deepStrictEqual(await handlers['conv:clear'](), []);
  assert.deepStrictEqual(loadState(root).conversation, []);
  const log = fs.readFileSync(path.join(root, 'data', 'app.log'), 'utf8');
  assert.strictEqual((log.match(/conv\.ask/g) || []).length, 2);
  assert.strictEqual((log.match(/conv\.clear/g) || []).length, 1);
});

test('D4: preload bridges the three conv channels to the matching invoke calls', () => {
  const pre = fs.readFileSync(path.join(__dirname, '..', 'preload.js'), 'utf8');
  assert.ok(/convGet:.*invoke\('conv:get'\)/.test(pre));
  assert.ok(/convAsk:.*invoke\('conv:ask'/.test(pre));
  assert.ok(/convClear:.*invoke\('conv:clear'\)/.test(pre));
});
