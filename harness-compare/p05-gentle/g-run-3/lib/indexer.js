const fs = require('node:fs');
const path = require('node:path');
const { listDocs, readDoc } = require('./docs');
const { chunkDoc } = require('./chunk');
const { extractMeta } = require('./meta');

// Index of every document: chunks + per-doc metadata.
// With opts.file it is persisted (JSON, atomic write) and reloaded on creation;
// start() then reindexes only new/modified docs (by mtime) and drops deleted ones.
// status(): { state: 'idle'|'indexing'|'done', done, total, chunks }
// done/total count only the docs being reindexed; chunks is the whole index.
const VERSION = 1;

function load(file) {
  const empty = { docs: {}, chunks: [], mtimes: {} };
  if (!file) return empty;
  try {
    const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
    if (raw.version !== VERSION || !raw.docs || !raw.mtimes || !Array.isArray(raw.chunks)) return empty;
    return { docs: raw.docs, chunks: raw.chunks, mtimes: raw.mtimes };
  } catch {
    return empty;
  }
}

function save(file, index) {
  const tmp = `${file}.tmp`;
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(tmp, JSON.stringify({ version: VERSION, ...index }));
  fs.renameSync(tmp, file);
}

function createIndexer(dir, opts = {}) {
  const file = opts.file || null;
  const log = opts.logger || { info() {}, warn() {}, error() {} };
  let index = load(file);
  let st = { state: 'idle', done: 0, total: 0, chunks: 0 };
  let running = null;

  const status = () => ({ ...st });

  async function run(onProgress) {
    const names = listDocs(dir);
    const mtime = (n) => { try { return fs.statSync(path.join(dir, n)).mtimeMs; } catch { return null; } };
    const current = new Map(names.map((n) => [n, mtime(n)]));
    const stale = names.filter((n) => current.get(n) === null || index.mtimes[n] !== current.get(n));
    const staleSet = new Set(stale);
    // Keep untouched docs; drop deleted and stale ones (stale are re-added below).
    const next = { docs: {}, chunks: [], mtimes: {} };
    for (const n of names) if (!staleSet.has(n) && index.docs[n]) { next.docs[n] = index.docs[n]; next.mtimes[n] = index.mtimes[n]; }
    next.chunks = index.chunks.filter((c) => next.docs[c.doc]);
    const dirty = stale.length > 0 || Object.keys(index.docs).length !== Object.keys(next.docs).length;

    log.info('index.start', { docs: names.length, stale: stale.length });
    st = { state: 'indexing', done: 0, total: stale.length, chunks: next.chunks.length };
    if (onProgress) onProgress(status());
    for (const name of stale) {
      await new Promise((r) => setImmediate(r)); // yield so the UI can paint progress
      try {
        const text = readDoc(dir, name);
        next.docs[name] = extractMeta(name, text);
        next.chunks.push(...chunkDoc(name, text));
        next.mtimes[name] = current.get(name); // unreadable docs get no mtime, so they are retried
        log.info('index.doc.ok', { doc: name, bytes: text.length });
      } catch (err) { /* unreadable doc: skipped, still counted as processed */
        log.error('index.doc.failed', { doc: name, err });
      }
      st = { ...st, done: st.done + 1, chunks: next.chunks.length };
      if (onProgress) onProgress(status());
    }
    index = next;
    if (file && dirty) { try { save(file, index); } catch { /* persistence is best effort */ } }
    st = { ...st, state: 'done' };
    log.info('index.done', { reindexed: stale.length, chunks: next.chunks.length, docs: Object.keys(next.docs).length });
    return status();
  }

  function start(onProgress) {
    if (!running) running = run(onProgress).finally(() => { running = null; });
    return running;
  }

  return { start, status, get: () => index };
}

module.exports = { createIndexer };
