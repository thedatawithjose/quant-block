const fs = require('node:fs');
const path = require('node:path');

const EXTS = new Set(['.md', '.txt']);

function ensureDocsDir(root) {
  const dir = path.join(root, 'data', 'docs');
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function listDocs(dir) {
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isFile() && EXTS.has(path.extname(e.name).toLowerCase()))
    .map((e) => e.name)
    .sort();
}

function readDoc(dir, name) {
  if (typeof name !== 'string' || name !== path.basename(name) || !EXTS.has(path.extname(name).toLowerCase())) {
    throw new Error('Invalid document name');
  }
  return fs.readFileSync(path.join(dir, name), 'utf8');
}

function docInfo(dir, name) {
  const content = readDoc(dir, name);
  const st = fs.statSync(path.join(dir, name));
  return { name, size: st.size, mtime: st.mtime.toISOString(), content };
}

// Copies files with allowed extensions into dir; never overwrites (flag 'wx' / COPYFILE_EXCL).
function importDocs(dir, sources) {
  const imported = [];
  const skipped = [];
  const records = [];
  for (const src of Array.isArray(sources) ? sources : []) {
    if (typeof src !== 'string') { skipped.push({ file: String(src), reason: 'invalid' }); continue; }
    const name = path.basename(src);
    if (!EXTS.has(path.extname(name).toLowerCase())) { skipped.push({ file: name, reason: 'extension' }); continue; }
    try {
      fs.copyFileSync(src, path.join(dir, name), fs.constants.COPYFILE_EXCL);
      imported.push(name);
      records.push({ name, source: src });
    } catch (err) {
      skipped.push({ file: name, reason: err.code === 'EEXIST' ? 'exists' : 'error' });
    }
  }
  return { imported, skipped, records };
}

module.exports = { ensureDocsDir, listDocs, readDoc, docInfo, importDocs };
