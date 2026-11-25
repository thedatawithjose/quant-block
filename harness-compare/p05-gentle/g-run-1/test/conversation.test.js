const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { askInConversation, MAX_TURNS } = require('../lib/conversation');
const { loadState, saveState, statePath } = require('../lib/state');

const index = {
  docs: { 'a.md': { title: 'A' } },
  chunks: [
    { id: 'a.md#1', doc: 'a.md', n: 1, line: 1, text: 'El backup se guarda cada noche' },
    { id: 'a.md#2', doc: 'a.md', n: 2, line: 5, text: 'La restauracion usa el backup mas reciente' },
  ],
};
const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'kb-conv-'));

test('F13: MAX_TURNS is 20', () => assert.strictEqual(MAX_TURNS, 20));

test('F13: first question uses itself as effective query, turn is last of history', () => {
  const { history, turn } = askInConversation([], 'que es el backup', index);
  assert.strictEqual(history.length, 1);
  assert.strictEqual(turn, history[0]);
  assert.strictEqual(turn.q, 'que es el backup');
  assert.strictEqual(turn.effectiveQuery, 'que es el backup');
  assert.ok(turn.citations.length > 0);
  assert.ok(typeof turn.a === 'string');
});

test('F13: short follow-up (<=2 significant words) appends to previous effective query', () => {
  let r = askInConversation([], 'como funciona el backup nocturno', index);
  r = askInConversation(r.history, 'y la restauracion?', index);
  assert.strictEqual(r.turn.effectiveQuery, 'como funciona el backup nocturno restauracion');
  r = askInConversation(r.history, 'cual es?', index); // 0 significant words
  assert.strictEqual(r.turn.effectiveQuery, 'como funciona el backup nocturno restauracion');
});

test('F13: stopwords and 2-letter words are not significant; accents ignored', () => {
  let r = askInConversation([], 'backup nocturno completo', index);
  r = askInConversation(r.history, 'Cuál es el del para', index);
  assert.strictEqual(r.turn.effectiveQuery, 'backup nocturno completo');
  r = askInConversation(r.history, 'dónde restauracion reciente', index); // dónde is a stopword
  assert.strictEqual(r.turn.effectiveQuery, 'backup nocturno completo restauracion reciente');
});

test('F13: 3+ significant words use the question itself', () => {
  let r = askInConversation([], 'backup nocturno', index);
  r = askInConversation(r.history, 'como se hace la restauracion reciente', index);
  assert.strictEqual(r.turn.effectiveQuery, 'como se hace la restauracion reciente');
});

test('F13: does not mutate input history; caps at MAX_TURNS dropping oldest', () => {
  const h0 = [];
  const r1 = askInConversation(h0, 'backup nocturno completo', index);
  assert.strictEqual(h0.length, 0);
  assert.notStrictEqual(r1.history, h0);
  let h = [];
  for (let i = 0; i < 25; i++) {
    const frozen = Object.freeze([...h]);
    h = askInConversation(frozen, `pregunta numero ${i} backup`, index).history;
  }
  assert.strictEqual(h.length, MAX_TURNS);
  assert.strictEqual(h[0].q, 'pregunta numero 5 backup');
  assert.strictEqual(h[19].q, 'pregunta numero 24 backup');
});

test('F13: conversation persists in state.json; missing/invalid yields []', () => {
  const root = tmp();
  assert.deepStrictEqual(loadState(root).conversation, []);
  const { history } = askInConversation([], 'backup nocturno completo', index);
  saveState(root, { ...loadState(root), conversation: history });
  assert.deepStrictEqual(loadState(root).conversation, history);
  fs.writeFileSync(statePath(root), JSON.stringify({ conversation: 'x' }));
  assert.deepStrictEqual(loadState(root).conversation, []);
  fs.writeFileSync(statePath(root), JSON.stringify({ conversation: [1, null, { q: 'ok' }] }));
  assert.deepStrictEqual(loadState(root).conversation, []);
  fs.writeFileSync(statePath(root), '{corrupt');
  assert.deepStrictEqual(loadState(root).conversation, []);
});

test('F13: loadState keeps only the last MAX_TURNS persisted turns', () => {
  const root = tmp();
  const turns = Array.from({ length: 30 }, (_, i) => ({ q: `q${i}`, effectiveQuery: `q${i}`, a: 'a', citations: [] }));
  fs.mkdirSync(path.join(root, 'data'), { recursive: true });
  fs.writeFileSync(statePath(root), JSON.stringify({ conversation: turns }));
  const c = loadState(root).conversation;
  assert.strictEqual(c.length, 20);
  assert.strictEqual(c[0].q, 'q10');
});

test('F13: wiring: main.js, preload, renderer, logs', () => {
  const rd = (f) => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');
  for (const c of ['conv:get', 'conv:ask', 'conv:clear']) {
    assert.ok(rd('main.js').includes(c), `main.js missing ${c}`);
    assert.ok(rd('preload.js').includes(c), `preload.js missing ${c}`);
  }
  assert.ok(rd('main.js').includes("'conv.ask'") && rd('main.js').includes("'conv.clear'"));
  assert.ok(rd('renderer/index.html').includes('Nueva conversacion'));
  assert.ok(rd('renderer/renderer.js').includes('convGet'));
});
