const test = require('node:test');
const assert = require('node:assert');
const { askInConversation, MAX_TURNS } = require('../lib/conversation');
const { answerWithCitations } = require('../lib/cite');

const index = {
  docs: { a: { title: 'A' } },
  chunks: [
    { id: 'a#1', doc: 'a', n: 1, line: 1, text: 'sistema solar planetas masa' },
    { id: 'a#2', doc: 'a', n: 2, line: 5, text: 'orbita distancia sol' },
  ],
};
const prevOf = (eq) => [{ q: 'x', effectiveQuery: eq, a: 'a', citations: [] }];
const eqOf = (hist, q) => askInConversation(hist, q, index).turn.effectiveQuery;
const deepFreeze = (o) => { Object.values(o).forEach((v) => { if (v && typeof v === 'object') deepFreeze(v); }); return Object.freeze(o); };

test('F13: exports askInConversation and MAX_TURNS=20', () => {
  assert.strictEqual(typeof askInConversation, 'function');
  assert.strictEqual(MAX_TURNS, 20);
});

test('F13: first question uses own trimmed query and real answer/citations', () => {
  const { history, turn } = askInConversation([], '  sistema solar  ', index);
  assert.strictEqual(turn.effectiveQuery, 'sistema solar');
  assert.strictEqual(turn.q, 'sistema solar');
  assert.strictEqual(history.length, 1);
  assert.strictEqual(history[0], turn);
  assert.deepStrictEqual(Object.keys(turn).sort(), ['a', 'citations', 'effectiveQuery', 'q']);
  const r = answerWithCitations(index, turn.effectiveQuery);
  assert.strictEqual(turn.a, r.answer);
  assert.deepStrictEqual(turn.citations, r.citations);
});

test('F13: follow-up with 1 or 2 significant words appends them', () => {
  const h = prevOf('sistema solar planetas');
  assert.strictEqual(eqOf(h, '¿Y la masa?'), 'sistema solar planetas masa');
  assert.strictEqual(eqOf(h, 'masa distancia'), 'sistema solar planetas masa distancia');
});

test('F13: 3 significant words is its own question (boundary 2 vs 3)', () => {
  const h = prevOf('sistema solar planetas');
  assert.strictEqual(eqOf(h, 'masa distancia orbita'), 'masa distancia orbita');
  assert.notStrictEqual(eqOf(h, 'masa distancia'), 'masa distancia');
});

test('F13: stopwords and short words are ignored', () => {
  const h = prevOf('sistema solar');
  assert.strictEqual(eqOf(h, 'que los las una del con por para como cual donde'), 'sistema solar');
  for (const w of ['que', 'los', 'las', 'una', 'del', 'con', 'por', 'para', 'como', 'cual', 'donde']) {
    assert.strictEqual(eqOf(h, `${w} masa`), 'sistema solar masa', w);
  }
  assert.strictEqual(eqOf(h, 'el la de y es'), 'sistema solar');
});

test('F13: normalization of case/accents/punctuation', () => {
  const h = prevOf('sistema solar');
  assert.strictEqual(eqOf(h, '¿QUÉ es la MASA?'), 'sistema solar MASA');
  assert.strictEqual(eqOf(h, 'Cuál órbita'), 'sistema solar órbita');
  assert.strictEqual(eqOf(h, 'CÓMO Dónde masa'), 'sistema solar masa');
  assert.strictEqual(eqOf(h, '¿masa,distancia;!'), 'sistema solar masa distancia');
});

test('F13: duplicate significant words are counted, not deduplicated (D5)', () => {
  const h = prevOf('sistema solar');
  assert.strictEqual(eqOf(h, 'masa masa'), 'sistema solar masa masa');
  assert.strictEqual(eqOf(h, 'masa masa masa'), 'masa masa masa');
});

test('F13: uno/sin/mas count as significant; chained follow-ups accumulate (AC5, AC7)', () => {
  const h = prevOf('gatos');
  for (const w of ['uno', 'sin', 'mas']) assert.strictEqual(eqOf(h, w), `gatos ${w}`);
  let hist = askInConversation([], 'gatos', index).history;
  hist = askInConversation(hist, 'dieta', index).history;
  const r = askInConversation(hist, 'seca', index);
  assert.strictEqual(r.turn.effectiveQuery, 'gatos dieta seca');
  const reset = askInConversation(r.history, 'alimentacion de gatos adultos', index);
  assert.strictEqual(reset.turn.effectiveQuery, 'alimentacion de gatos adultos');
  assert.strictEqual(askInConversation(reset.history, 'seca', index).turn.effectiveQuery, 'alimentacion de gatos adultos seca');
});

test('F13: follow-up citations come from the extended query (AC8)', () => {
  const h = askInConversation([], 'planetas', index).history;
  const r = askInConversation(h, 'distancia', index);
  assert.strictEqual(r.turn.effectiveQuery, 'planetas distancia');
  assert.deepStrictEqual(r.turn.citations, answerWithCitations(index, 'planetas distancia').citations);
  assert.ok(r.turn.citations.some((c) => c.chunkId === 'a#1'));
});

test('F13: no previous turn, or 3+ words, uses own question', () => {
  assert.strictEqual(eqOf([], '  masa  '), 'masa');
  assert.strictEqual(eqOf(prevOf('zzz'), ' masa distancia orbita '), 'masa distancia orbita');
});

test('F13: empty/invalid question appends nothing', () => {
  const h = prevOf('sistema');
  for (const q of ['', '   ', '\n\t', undefined, null, 42]) {
    const r = askInConversation(h, q, index);
    assert.strictEqual(r.turn, null);
    assert.deepStrictEqual(r.history, h);
    assert.notStrictEqual(r.history, h);
  }
});

test('F13: cap at 20 turns drops oldest', () => {
  let h = [];
  for (let i = 1; i <= 19; i++) h = askInConversation(h, `pregunta${i} uno`, index).history;
  assert.strictEqual(h.length, 19);
  h = askInConversation(h, 'pregunta20 uno', index).history;
  assert.strictEqual(h.length, 20);
  assert.strictEqual(h[0].q, 'pregunta1 uno');
  h = askInConversation(h, 'pregunta21 uno', index).history;
  assert.strictEqual(h.length, 20);
  assert.strictEqual(h[0].q, 'pregunta2 uno');
  assert.strictEqual(h[19].q, 'pregunta21 uno');
  h = askInConversation(h, 'pregunta22 uno', index).history;
  assert.strictEqual(h[0].q, 'pregunta3 uno');
  const big = Array.from({ length: 25 }, (_, i) => ({ q: `q${i}`, effectiveQuery: `q${i}`, a: 'a', citations: [] }));
  assert.strictEqual(askInConversation(big, 'masa', index).history.length, 20);
});

test('F13: does not mutate frozen input; non-array history treated as []', () => {
  const h = deepFreeze([{ q: 'x', effectiveQuery: 'sistema', a: 'a', citations: [{ doc: 'a' }] }]);
  const r = askInConversation(h, 'masa', index);
  assert.strictEqual(h.length, 1);
  assert.notStrictEqual(r.history, h);
  assert.strictEqual(r.history.length, 2);
  assert.ok(!Object.isFrozen(r.turn));
  for (const bad of [null, {}, 'x']) {
    const x = askInConversation(bad, 'masa', index);
    assert.strictEqual(x.history.length, 1);
    assert.strictEqual(x.turn.effectiveQuery, 'masa');
  }
});

test('F13: pure - same inputs give equal outputs', () => {
  const h = prevOf('sistema');
  assert.deepStrictEqual(askInConversation(h, 'masa', index), askInConversation(h, 'masa', index));
});

test('F13: questions without searchable words or without index add no turn', () => {
  const idx = { chunks: [{ id: 'a#1', doc: 'a', line: 1, text: 'gatos' }], docs: {} };
  for (const [q, i] of [['???', idx], ['gatos', null], ['gatos', { chunks: [] }]]) {
    const r = askInConversation([], q, i);
    assert.strictEqual(r.turn, null);
    assert.deepStrictEqual(r.history, []);
  }
});

test('F13: MAX_TURNS is shared with state.js', () => {
  assert.strictEqual(MAX_TURNS, require('../lib/state').MAX_TURNS);
});
