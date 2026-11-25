const path = require('node:path');

// Per-document metadata: title (first "# " heading, else filename without extension),
// word count and the list of headings (any level, outside code fences).
function extractMeta(name, text) {
  const src = typeof text === 'string' ? text : '';
  const headings = [];
  let title = null;
  let fenced = false;
  for (const l of src.split(/\r?\n/)) {
    if (/^\s*(```|~~~)/.test(l)) { fenced = !fenced; continue; }
    if (fenced) continue;
    const m = /^(#{1,6})\s+(.+?)\s*#*\s*$/.exec(l);
    if (!m) continue;
    headings.push(m[2]);
    if (m[1] === '#' && title === null) title = m[2];
  }
  const words = src.replace(/^#{1,6}\s/gm, '').split(/\s+/).filter(Boolean).length;
  return { name, title: title ?? path.basename(name, path.extname(name)), words, headings };
}

module.exports = { extractMeta };
