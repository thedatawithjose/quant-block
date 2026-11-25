// Splits text into paragraph chunks (separated by blank lines).
// id = `${docName}#${n}` (n is 1-based, in document order); line = 1-based start line.
function chunkDoc(docName, text) {
  if (typeof text !== 'string') return [];
  const chunks = [];
  const lines = text.split(/\r?\n/);
  // Widest line in the doc: chunks containing very wide lines are flagged for the UI to wrap.
  const widest = lines.reduce((m, l) => (l.length > m ? l.length : m), 0);
  let buf = [];
  let start = 0;
  const flush = () => {
    if (buf.length) {
      const n = chunks.length + 1;
      chunks.push({ id: `${docName}#${n}`, doc: docName, n, line: start, text: buf.join('\n'), wide: widest > 500 });
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
