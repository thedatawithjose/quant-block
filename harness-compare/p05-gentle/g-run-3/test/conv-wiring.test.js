const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const read = (f) => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');

test('F13: renderer html has button and legacy ids', () => {
  const h = read('renderer/index.html');
  assert.match(h, /<button id="new-conv">Nueva conversacion<\/button>/);
  for (const id of ['answer', 'question', 'ask', 'citations']) assert.match(h, new RegExp(`id="${id}"`));
  const r = read('renderer/renderer.js');
  for (const s of ['kb.convGet', 'kb.convAsk', 'kb.convClear', "'turn'", "'cite'"]) assert.ok(r.includes(s), s);
  assert.doesNotMatch(r, /require\(/);
});

// Minimal fake DOM to exercise renderer.js without Electron or new dependencies.
function el(tag) {
  return {
    tag, children: [], className: '', textContent: '', value: '', listeners: {}, scrollTop: 0, scrollHeight: 99,
    classList: { add() {}, remove() {} },
    set innerHTML(v) { this.children = []; },
    appendChild(c) { this.children.push(c); return c; },
    append(...cs) { cs.forEach((c) => this.children.push(c)); },
    addEventListener(ev, fn) { this.listeners[ev] = fn; },
  };
}

test('F13: renderer renders turns, asks and clears (fake DOM)', async () => {
  const els = {};
  for (const id of ['import', 'import-msg', 'index-status', 'doc-list', 'doc-meta', 'doc-content', 'question', 'ask', 'ask-msg', 'answer', 'citations', 'new-conv']) els[id] = el('x');
  const turn = { q: 'masa', effectiveQuery: 'sistema masa', a: 'resp', citations: [{ doc: 'a.md', chunkId: 'a.md#1', line: 3, text: 'txt' }] };
  const calls = [];
  const kb = {
    getState: async () => ({ lastSelected: null }), listDocs: async () => [], indexStart: async () => ({ state: 'idle' }),
    onIndexProgress() {},
    convGet: async () => [turn],
    convAsk: async (q) => { calls.push(q); return { history: [turn, turn], turn }; },
    convClear: async () => { calls.push('clear'); return []; },
  };
  const doc = { getElementById: (id) => els[id], createElement: el, querySelectorAll: () => [] };
  vm.runInNewContext(read('renderer/renderer.js'), { document: doc, window: { kb } });
  const tick = () => new Promise((r) => setImmediate(r));
  await tick(); await tick();
  assert.strictEqual(els.answer.children.length, 1);
  const t = els.answer.children[0];
  assert.strictEqual(t.className, 'turn');
  assert.ok(t.children.some((c) => c.className === 'eq' && /sistema masa/.test(c.textContent)));
  assert.ok(t.children.some((c) => c.className === 'cite'));
  els.question.value = '   ';
  await els.ask.listeners.click();
  assert.deepStrictEqual(calls, []);
  els.question.value = ' masa ';
  await els.ask.listeners.click();
  assert.deepStrictEqual(calls, [' masa ']);
  assert.strictEqual(els.answer.children.length, 2);
  assert.strictEqual(els.question.value, '');
  await els['new-conv'].listeners.click();
  assert.strictEqual(els.answer.children.length, 0);
});

async function bootRenderer(kbOverrides) {
  const els = {};
  for (const id of ['import', 'import-msg', 'index-status', 'doc-list', 'doc-meta', 'doc-content', 'question', 'ask', 'ask-msg', 'answer', 'citations', 'new-conv']) els[id] = el('x');
  const kb = {
    getState: async () => ({ lastSelected: null }), listDocs: async () => [], indexStart: async () => ({ state: 'idle' }),
    onIndexProgress() {}, convGet: async () => [], ...kbOverrides,
  };
  const doc = { getElementById: (id) => els[id], createElement: el, querySelectorAll: () => [] };
  vm.runInNewContext(read('renderer/renderer.js'), { document: doc, window: { kb } });
  const tick = () => new Promise((r) => setImmediate(r));
  await tick(); await tick();
  return els;
}

test('F13: renderer ignores a second click while a question is in flight', async () => {
  let calls = 0;
  let release;
  const gate = new Promise((r) => { release = r; });
  const turn = { q: 'gatos', effectiveQuery: 'gatos', a: 'r', citations: [] };
  const els = await bootRenderer({ convAsk: async () => { calls++; await gate; return { history: [turn], turn }; } });
  els.question.value = 'gatos';
  const first = els.ask.listeners.click();
  await els.ask.listeners.click();
  assert.strictEqual(calls, 1);
  release();
  await first;
  assert.strictEqual(els.answer.children.length, 1);
  els.question.value = 'otra';
  await els.ask.listeners.click();
  assert.strictEqual(calls, 2);
});

test('F13: renderer shows feedback when convAsk fails and keeps the question', async () => {
  const els = await bootRenderer({ convAsk: async () => { throw new Error('boom'); } });
  els.question.value = 'gatos';
  await els.ask.listeners.click();
  assert.match(els['ask-msg'].textContent, /boom/);
  assert.strictEqual(els.question.value, 'gatos');
  els.question.value = 'perros';
  await els.ask.listeners.click();
  assert.match(els['ask-msg'].textContent, /boom/);
});

test('F13: renderer shows feedback when there is no turn', async () => {
  const els = await bootRenderer({ convAsk: async () => ({ history: [], turn: null }) });
  els.question.value = '???';
  await els.ask.listeners.click();
  assert.ok(els['ask-msg'].textContent.length > 0);
  assert.strictEqual(els.question.value, '???');
});
