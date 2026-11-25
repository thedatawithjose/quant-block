const test = require('node:test');
const assert = require('node:assert');
const { extractMeta } = require('../lib/meta');

test('F09: title from first # heading, word count and headings list', () => {
  const m = extractMeta('guia.md', '# Mi guia\n\nHola mundo\n\n## Seccion A\ntexto aqui\n### Sub\n');
  assert.strictEqual(m.name, 'guia.md');
  assert.strictEqual(m.title, 'Mi guia');
  assert.deepStrictEqual(m.headings, ['Mi guia', 'Seccion A', 'Sub']);
  assert.strictEqual(m.words, 9);
});

test('F09: title falls back to filename without extension', () => {
  assert.strictEqual(extractMeta('notas.txt', 'sin encabezado').title, 'notas');
  assert.strictEqual(extractMeta('b.md', '## solo h2\ntexto').title, 'b');
});

test('F09: first level-1 heading wins; ignores # inside code fences; empty/invalid safe', () => {
  const m = extractMeta('c.md', '## x\n# Principal\n```\n# no es titulo\n```\n# Otro');
  assert.strictEqual(m.title, 'Principal');
  assert.deepStrictEqual(m.headings, ['x', 'Principal', 'Otro']);
  assert.deepStrictEqual(extractMeta('d.md', ''), { name: 'd.md', title: 'd', words: 0, headings: [] });
  assert.strictEqual(extractMeta('d.md', null).words, 0);
});
