const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { askInConversation, effectiveQuery, significantWords, MAX_TURNS } = require('../lib/conversation');
const { answerWithCitations } = require('../lib/cite');
const { loadState, saveState, setLastSelected, recordImports, statePath } = require('../lib/state');

const idx = {
  docs: { 'a.md': { title: 'A' } },
  chunks: [
    { id: 'a.md#1', doc: 'a.md', n: 1, line: 1, text: 'El oceano pacifico es el mas profundo' },
    { id: 'a.md#2', doc: 'a.md', n: 2, line: 4, text: 'La profundidad media del oceano es 4000 metros' },
    { id: 'a.md#3', doc: 'a.md', n: 3, line: 7, text: 'Las montanas son altas' },
  ],
};
const turnWith = (eq) => ({ q: eq, effectiveQuery: eq, a: 'x', citations: [] });
const read = (f) => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');
const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'kb-conv-'));

test('F13-1: no previous turn, one word', () => {
  const r = askInConversation([], 'oceano', idx);
  assert.strictEqual(r.turn.q, 'oceano');
  assert.strictEqual(r.turn.effectiveQuery, 'oceano');
  assert.strictEqual(r.history.length, 1);
  assert.strictEqual(r.turn.citations.length, 2);
  assert.deepStrictEqual(Object.keys(r.turn).sort(), ['a', 'citations', 'effectiveQuery', 'q']);
});

test('F13-2: follow-up with one word', () => {
  const h = askInConversation([], 'oceano', idx).history;
  const r = askInConversation(h, 'profundidad', idx);
  assert.strictEqual(r.turn.effectiveQuery, 'oceano profundidad');
  assert.strictEqual(r.turn.q, 'profundidad');
});

test('F13-3: short words do not count', () => {
  assert.deepStrictEqual(significantWords('Y la profundidad?'), ['profundidad']);
  assert.strictEqual(effectiveQuery([turnWith('oceano')], 'Y la profundidad?'), 'oceano profundidad');
});

test('F13-4: exactly 2 significant words is a follow-up', () => {
  assert.strictEqual(effectiveQuery([turnWith('oceano')], 'profundidad media'), 'oceano profundidad media');
});

test('F13-5: exactly 3 significant words is not a follow-up', () => {
  assert.strictEqual(effectiveQuery([turnWith('oceano')], 'profundidad media metros'), 'profundidad media metros');
});

test('F13-6: stopwords do not count', () => {
  assert.deepStrictEqual(significantWords('que es el oceano'), ['oceano']);
  assert.strictEqual(effectiveQuery([turnWith('montanas')], 'que es el oceano'), 'montanas oceano');
});

test('F13-6b: all-stopword question adds no trailing space', () => {
  assert.strictEqual(effectiveQuery([turnWith('oceano')], 'cuál dónde como'), 'oceano');
  assert.deepStrictEqual(significantWords('Cuál es la PROFUNDIDAD'), ['profundidad']);
});

test('F13-7: chaining', () => {
  let h = [];
  const eqs = [];
  for (const q of ['oceano', 'profundidad', 'metros']) {
    const r = askInConversation(h, q, idx);
    h = r.history;
    eqs.push(r.turn.effectiveQuery);
  }
  assert.deepStrictEqual(eqs, ['oceano', 'oceano profundidad', 'oceano profundidad metros']);
  const r0 = askInConversation(h, 'las montanas son altas', idx);
  assert.strictEqual(r0.history.length, 4);
});

test('F13-8: 3+ significant words reset the chain', () => {
  let h = [];
  for (const q of ['oceano', 'profundidad', 'metros']) h = askInConversation(h, q, idx).history;
  const r = askInConversation(h, 'las montanas son altas', idx);
  assert.strictEqual(r.turn.effectiveQuery, 'las montanas son altas');
});

test('F13-9: answer and citations come from the effective query', () => {
  const h = askInConversation([], 'oceano', idx).history;
  const r = askInConversation(h, 'profundidad', idx);
  assert.deepStrictEqual({ answer: r.turn.a, citations: r.turn.citations }, answerWithCitations(idx, 'oceano profundidad'));
  assert.ok(r.turn.citations.some((c) => c.chunkId === 'a.md#2'));
});

test('F13-10: does not mutate input', () => {
  const h = [turnWith('oceano')];
  h.forEach((t) => { t.citations = Object.freeze([]); Object.freeze(t); });
  Object.freeze(h);
  const r = askInConversation(h, 'profundidad', idx);
  assert.strictEqual(h.length, 1);
  assert.strictEqual(h[0].effectiveQuery, 'oceano');
  assert.notStrictEqual(r.history, h);
  assert.strictEqual(r.history.at(-1), r.turn);
});

test('F13-11: cap of 20 turns', () => {
  assert.strictEqual(MAX_TURNS, 20);
  const mk = (n) => Array.from({ length: n }, (_, i) => ({ ...turnWith('x'), q: `q${i}` }));
  const r = askInConversation(mk(20), 'profundidad media metros', idx);
  assert.strictEqual(r.history.length, 20);
  assert.strictEqual(r.history[0].q, 'q1');
  assert.strictEqual(r.history.at(-1), r.turn);
  assert.strictEqual(askInConversation(mk(25), 'profundidad media metros', idx).history.length, 20);
});

test('F13-12: empty question adds nothing', () => {
  const h = [turnWith('oceano')];
  for (const q of ['', '   ', undefined, null]) {
    const r = askInConversation(h, q, idx);
    assert.strictEqual(r.turn, null);
    assert.deepStrictEqual(r.history, h);
    assert.notStrictEqual(r.history, h);
  }
});

test('F13-13: empty or null index', () => {
  const r = askInConversation([], 'hola mundo cruel', null);
  assert.strictEqual(r.turn.a, 'No hay documentos indexados.');
  assert.deepStrictEqual(r.turn.citations, []);
  assert.strictEqual(r.history.length, 1);
});

test('F13-14: persistence', () => {
  const root = tmp();
  assert.deepStrictEqual(loadState(root).conversation, []);
  fs.mkdirSync(path.dirname(statePath(root)), { recursive: true });
  fs.writeFileSync(statePath(root), '{bad');
  assert.deepStrictEqual(loadState(root).conversation, []);
  for (const bad of ['x', {}]) {
    fs.writeFileSync(statePath(root), JSON.stringify({ conversation: bad }));
    assert.deepStrictEqual(loadState(root).conversation, []);
  }
  let h = askInConversation([], 'oceano', idx).history;
  h = askInConversation(h, 'profundidad', idx).history;
  let s = loadState(root);
  s = require('../lib/state').setConversation(s, h);
  s = setLastSelected(s, 'a.md');
  s = recordImports(s, [{ name: 'a.md', source: '/x/a.md' }]);
  assert.deepStrictEqual(s.conversation, h);
  saveState(root, s);
  assert.deepStrictEqual(loadState(root).conversation, h);
  const ok = turnWith('ok');
  fs.writeFileSync(statePath(root), JSON.stringify({ conversation: [null, 5, { q: 1 }, ok] }));
  assert.deepStrictEqual(loadState(root).conversation, [ok]);
  const many = Array.from({ length: 25 }, (_, i) => ({ ...ok, q: `q${i}` }));
  fs.writeFileSync(statePath(root), JSON.stringify({ conversation: many }));
  const got = loadState(root).conversation;
  assert.strictEqual(got.length, 20);
  assert.strictEqual(got[0].q, 'q5');
});

test('F13-16: static wiring', () => {
  const m = read('main.js');
  for (const s of ["'conv:get'", "'conv:ask'", "'conv:clear'", "'conv.ask'", "'conv.clear'"]) assert.ok(m.includes(s), s);
  const p = read('preload.js');
  for (const s of ['convGet', 'convAsk', 'convClear']) assert.ok(p.includes(s), s);
  assert.ok(read('renderer/index.html').includes('Nueva conversacion'));
});

test('F13-17: previous turn without effectiveQuery does not produce "undefined"', () => {
  assert.strictEqual(effectiveQuery([{ q: 'a' }], 'montana'), 'montana');
});
