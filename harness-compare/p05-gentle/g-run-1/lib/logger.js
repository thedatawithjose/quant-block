const fs = require('node:fs');
const path = require('node:path');

// Structured logger: one JSON object per line -> stderr and (optionally) a file.
// log.info('index.doc.ok', { doc, chunks }); log.error('index.doc.failed', { doc, err })
function createLogger({ file = null, stream = process.stderr, now = () => new Date() } = {}) {
  if (file) fs.mkdirSync(path.dirname(file), { recursive: true });
  const write = (level, event, fields = {}) => {
    const f = { ...fields };
    if (f.err instanceof Error) f.err = { name: f.err.name, message: f.err.message, stack: String(f.err.stack).split('\n').slice(0, 4).join(' | ') };
    const line = JSON.stringify({ ts: now().toISOString(), level, event, ...f }) + '\n';
    try { if (stream) stream.write(line); } catch { /* logging never throws */ }
    if (file) { try { fs.appendFileSync(file, line); } catch { /* logging never throws */ } }
  };
  return { info: (e, f) => write('info', e, f), warn: (e, f) => write('warn', e, f), error: (e, f) => write('error', e, f) };
}

module.exports = { createLogger };
