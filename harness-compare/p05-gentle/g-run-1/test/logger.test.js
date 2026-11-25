const test = require('node:test');
const assert = require('node:assert');
const { createLogger } = require('../lib/logger');

test('logger writes one JSON line with level, event and serialized error', () => {
  const lines = [];
  const log = createLogger({ stream: { write: (s) => lines.push(s) }, now: () => new Date(0) });
  log.error('x.failed', { doc: 'a.md', err: new RangeError('boom') });
  const o = JSON.parse(lines[0]);
  assert.strictEqual(o.level, 'error');
  assert.strictEqual(o.event, 'x.failed');
  assert.strictEqual(o.ts, '1970-01-01T00:00:00.000Z');
  assert.strictEqual(o.err.name, 'RangeError');
  assert.strictEqual(o.err.message, 'boom');
});
