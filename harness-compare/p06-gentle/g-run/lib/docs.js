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

// Copies files with allowed extensions into dir; never overwrites. On a name collision the copy
// gets " (2)", " (3)"... before the extension (flag COPYFILE_EXCL makes the check race-free).
function importDocs(dir, sources) {
  const imported = [];
  const skipped = [];
  const records = [];
  const renamed = [];
  for (const src of Array.isArray(sources) ? sources : []) {
    if (typeof src !== 'string') { skipped.push({ file: String(src), reason: 'invalid' }); continue; }
    const name = path.basename(src);
    const ext = path.extname(name);
    if (!EXTS.has(ext.toLowerCase())) { skipped.push({ file: name, reason: 'extension' }); continue; }
    const stem = name.slice(0, name.length - ext.length);
    try {
      for (let n = 1; ; n++) {
        const finalName = n === 1 ? name : `${stem} (${n})${ext}`;
        try {
          fs.copyFileSync(src, path.join(dir, finalName), fs.constants.COPYFILE_EXCL);
        } catch (err) {
          if (err.code === 'EEXIST') continue;
          throw err;
        }
        imported.push(finalName);
        records.push({ name: finalName, source: src });
        if (finalName !== name) renamed.push({ from: name, to: finalName });
        break;
      }
    } catch {
      skipped.push({ file: name, reason: 'error' });
    }
  }
  return { imported, skipped, records, renamed };
}

module.exports = { ensureDocsDir, listDocs, readDoc, docInfo, importDocs };
