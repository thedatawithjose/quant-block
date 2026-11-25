const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { listDocs, readDoc } = require('./docs');
const { chunkDoc } = require('./chunk');
const { extractMeta } = require('./meta');

// Index of every document: chunks + per-doc metadata.
// With opts.file it is persisted (JSON, atomic write) and reloaded on creation;
// start() then reindexes only new/modified docs (by sha256 of content) and drops deleted ones.
// status(): { state: 'idle'|'indexing'|'done', done, total, chunks }
// failed: [{ doc, message }] of docs that could not be indexed in the last run (reset each run).
// done/total count only the docs being reindexed; chunks is the whole index.
const VERSION = 1;

function load(file) {
  const empty = { docs: {}, chunks: [], hashes: {} };
  if (!file) return empty;
  try {
    const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
    if (raw.version !== VERSION || !raw.docs || !Array.isArray(raw.chunks)) return empty;
    // Old files (mtimes, no hashes) load with no hashes, so everything is reindexed once.
    return { docs: raw.docs, chunks: raw.chunks, hashes: raw.hashes && typeof raw.hashes === 'object' ? raw.hashes : {} };
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
    const t0 = Date.now();
    const failed = [];
    const texts = new Map(); // doc -> { text, hash }; null when unreadable
    for (const n of names) {
      try {
        const text = readDoc(dir, n);
        texts.set(n, { text, hash: crypto.createHash('sha256').update(text).digest('hex') });
      } catch { texts.set(n, null); }
    }
    const stale = names.filter((n) => !texts.get(n) || index.hashes[n] !== texts.get(n).hash || !index.docs[n]);
    const staleSet = new Set(stale);
    // Keep untouched docs; drop deleted and stale ones (stale are re-added below).
    const next = { docs: {}, chunks: [], hashes: {} };
    for (const n of names) if (!staleSet.has(n)) { next.docs[n] = index.docs[n]; next.hashes[n] = index.hashes[n]; }
    next.chunks = index.chunks.filter((c) => next.docs[c.doc]);
    const dirty = stale.length > 0 || Object.keys(index.docs).length !== Object.keys(next.docs).length;

    log.info('index.start', { docs: names.length, stale: stale.length });
    st = { state: 'indexing', done: 0, total: stale.length, chunks: next.chunks.length, failed: [] };
    if (onProgress) onProgress(status());
    for (const name of stale) {
      await new Promise((r) => setImmediate(r)); // yield so the UI can paint progress
      try {
        const { text, hash } = texts.get(name) || { text: readDoc(dir, name) };
        next.docs[name] = extractMeta(name, text);
        next.chunks.push(...chunkDoc(name, text));
        next.hashes[name] = hash; // unreadable docs get no hash, so they are retried
        log.info('index.doc.ok', { doc: name, bytes: text.length });
      } catch (err) { /* unreadable doc: skipped, still counted as processed */
        failed.push({ doc: name, message: String((err && err.message) || err) });
        log.error('index.doc.failed', { doc: name, err });
      }
      st = { ...st, done: st.done + 1, chunks: next.chunks.length, failed: failed.slice() };
      if (onProgress) onProgress(status());
    }
    index = next;
    if (file && dirty) { try { save(file, index); } catch { /* persistence is best effort */ } }
    st = { ...st, state: 'done' };
    log.info('index.done', { reindexed: stale.length, chunks: next.chunks.length, docs: Object.keys(next.docs).length, failed: failed.length, durationMs: Date.now() - t0 });
    return status();
  }

  function start(onProgress) {
    if (!running) running = run(onProgress).finally(() => { running = null; });
    return running;
  }

  return { start, status, get: () => index };
}

module.exports = { createIndexer };
