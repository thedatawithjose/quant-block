// Splits text into paragraph chunks (separated by blank lines).
// id = `${docName}#${n}` (n is 1-based, in document order); line = 1-based start line;
// section = text of the nearest heading (without #) at or before the start line, or null.
function chunkDoc(docName, text) {
  if (typeof text !== 'string') return [];
  const chunks = [];
  const lines = text.split(/\r?\n/);
  // Widest line in the doc: chunks containing very wide lines are flagged for the UI to wrap.
  const widest = lines.reduce((m, l) => (l.length > m ? l.length : m), 0);
  let buf = [];
  let start = 0;
  const headingAt = new Map(); // 1-based line -> heading text
  lines.forEach((l, i) => { const m = /^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$/.exec(l); if (m && m[1]) headingAt.set(i + 1, m[1]); });
  const sectionFor = (line) => { for (let i = line; i >= 1; i--) if (headingAt.has(i)) return headingAt.get(i); return null; };
  const flush = () => {
    if (buf.length) {
      const n = chunks.length + 1;
      chunks.push({ id: `${docName}#${n}`, doc: docName, n, line: start, section: sectionFor(start), text: buf.join('\n'), wide: widest > 500 });
      buf = [];
    }
  };
  lines.forEach((l, i) => {
    if (l.trim() === '') { flush(); return; }
    if (!buf.length) start = i + 1;
    buf.push(l);
  });
  flush();
  return chunks;
}

module.exports = { chunkDoc };
