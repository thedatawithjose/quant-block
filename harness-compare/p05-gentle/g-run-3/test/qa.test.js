const test = require('node:test');
const assert = require('node:assert');
const { answer } = require('../lib/qa');

const doc = 'Linea uno sobre gatos.\nLinea dos sobre perros.\nOtra de GATOS negros.';

test('F03: answer finds matching lines case-insensitively', () => {
  const r = answer(doc, 'gatos');
  assert.match(r, /Linea uno/);
  assert.match(r, /GATOS negros/);
  assert.doesNotMatch(r, /perros/);
});

test('F03: answer handles no match, empty question, no document', () => {
  assert.match(answer(doc, 'zzz'), /No se encontr/);
  assert.match(answer(doc, '  '), /pregunta/i);
  assert.match(answer(null, 'gatos'), /documento/i);
});
