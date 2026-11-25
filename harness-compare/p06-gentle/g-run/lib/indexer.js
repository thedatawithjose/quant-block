const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { listDocs, readDoc } = require('./docs');
const { chunkDoc } = require('./chunk');
const { extractMeta } = require('./meta');

// Index of every document: chunks + per-doc metadata.
// With opts.file it is persisted (JSON, atomic write) and reloaded on creation;
// start() then reindexes only new/modified docs (by sha256 of the content, not mtime) and drops deleted ones.
// status(): { state: 'idle'|'indexing'|'done', done, total, chunks, failed: [{ doc, message }] }
// done/total count only the docs being reindexed; chunks is the whole index.
const VERSION = 2; // 2: chunks carry `section`; older files are reindexed

function load(file) {
  const empty = { docs: {}, chunks: [], hashes: {} };
  if (!file) return empty;
  try {
    const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
    // An old file (mtimes, no hashes) is treated as empty: everything is reindexed.
    if (raw.version !== VERSION || !raw.docs || !raw.hashes || !Array.isArray(raw.chunks)) return empty;
    return { docs: raw.docs, chunks: raw.chunks, hashes: raw.hashes };
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
  let st = { state: 'idle', done: 0, total: 0, chunks: 0, failed: [] };
  let running = null;

  const status = () => ({ ...st, failed: st.failed.map((f) => ({ ...f })) });

  async function run(onProgress) {
    const names = listDocs(dir);
    // Content of every doc (null when unreadable) and its hash; unreadable docs are always retried.
    const texts = new Map();
    const current = new Map();
    for (const n of names) {
      let text = null;
      try { text = readDoc(dir, n); } catch { /* unreadable */ }
      texts.set(n, text);
      current.set(n, text === null ? null : crypto.createHash('sha256').update(text).digest('hex'));
    }
    const stale = names.filter((n) => current.get(n) === null || index.hashes[n] !== current.get(n));
    const staleSet = new Set(stale);
    // Keep untouched docs; drop deleted and stale ones (stale are re-added below).
    const next = { docs: {}, chunks: [], hashes: {} };
    for (const n of names) if (!staleSet.has(n) && index.docs[n]) { next.docs[n] = index.docs[n]; next.hashes[n] = index.hashes[n]; }
    next.chunks = index.chunks.filter((c) => next.docs[c.doc]);
    const dirty = stale.length > 0 || Object.keys(index.docs).length !== Object.keys(next.docs).length;

    log.info('index.start', { docs: names.length, stale: stale.length });
    st = { state: 'indexing', done: 0, total: stale.length, chunks: next.chunks.length, failed: [] };
    const startedAt = Date.now();
    if (onProgress) onProgress(status());
    for (const name of stale) {
      await new Promise((r) => setImmediate(r)); // yield so the UI can paint progress
      try {
        const text = texts.get(name);
        if (text === null) throw new Error('unreadable document');
        next.docs[name] = extractMeta(name, text);
        next.chunks.push(...chunkDoc(name, text));
        next.hashes[name] = current.get(name); // unreadable docs get no hash, so they are retried
        log.info('index.doc.ok', { doc: name, bytes: text.length });
      } catch (err) { /* unreadable doc: skipped, still counted as processed */
        log.error('index.doc.failed', { doc: name, err });
        st.failed.push({ doc: name, message: err && err.message ? err.message : String(err) });
      }
      st = { ...st, done: st.done + 1, chunks: next.chunks.length };
      if (onProgress) onProgress(status());
    }
    index = next;
    if (file && dirty) { try { save(file, index); } catch { /* persistence is best effort */ } }
    st = { ...st, state: 'done' };
    log.info('index.done', { reindexed: stale.length, chunks: next.chunks.length, docs: Object.keys(next.docs).length, failed: st.failed.length, durationMs: Date.now() - startedAt });
    return status();
  }

  function start(onProgress) {
    if (!running) running = run(onProgress).finally(() => { running = null; });
    return running;
  }

  return { start, status, get: () => index };
}

module.exports = { createIndexer };
