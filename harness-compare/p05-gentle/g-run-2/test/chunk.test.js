const test = require('node:test');
const assert = require('node:assert');
const { chunkDoc } = require('../lib/chunk');

test('F08: splits paragraphs with stable ids and 1-based start line', () => {
  const text = '# Titulo\nlinea a\n\nSegundo parrafo\n\n\nTercero';
  const c = chunkDoc('a.md', text);
  assert.deepStrictEqual(c.map((x) => [x.id, x.line]), [['a.md#1', 1], ['a.md#2', 4], ['a.md#3', 7]]);
  assert.strictEqual(c[0].text, '# Titulo\nlinea a');
  assert.strictEqual(c[0].doc, 'a.md');
});

test('F08: ids are stable across runs and handle CRLF', () => {
  const t = 'uno\r\n\r\ndos';
  assert.deepStrictEqual(chunkDoc('x.txt', t), chunkDoc('x.txt', t));
  assert.deepStrictEqual(chunkDoc('x.txt', t).map((x) => [x.id, x.line, x.text]), [['x.txt#1', 1, 'uno'], ['x.txt#2', 3, 'dos']]);
});

test('F08: empty or invalid input gives no chunks', () => {
  assert.deepStrictEqual(chunkDoc('a.md', ''), []);
  assert.deepStrictEqual(chunkDoc('a.md', '\n \n'), []);
  assert.deepStrictEqual(chunkDoc('a.md', null), []);
});

test('regresion: documento enorme (150000 lineas) se trocea sin RangeError', () => {
  const text = Array.from({ length: 150000 }, (_, i) => `linea ${i + 1}`).join('\n');
  const chunks = chunkDoc('big.txt', text);
  assert.strictEqual(chunks.length, 1);
  assert.strictEqual(chunks[0].wide, false);
});
