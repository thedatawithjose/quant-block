const MAX_CITATIONS = 5;

const norm = (s) => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

// Heading lines (outside code fences) of one doc, rebuilt from its chunks: [{ line, text }] in order.
// A chunk has no blank lines, so line = chunk.line + offset is exact.
function headingsOf(chunks) {
  const out = [];
  let fenced = false;
  for (const c of chunks) {
    String(c.text).split(/\r?\n/).forEach((l, i) => {
      if (/^\s*(```|~~~)/.test(l)) { fenced = !fenced; return; }
      if (fenced) return;
      const m = /^(#{1,6})\s+(.+?)\s*#*\s*$/.exec(l);
      if (m) out.push({ line: c.line + i, text: m[2] });
    });
  }
  return out;
}

function sectionOf(headings, line) {
  let found = null;
  for (const h of headings) { if (h.line <= line) found = h.text; else break; }
  return found;
}

// Local grounded Q&A: ranks indexed chunks by how many question terms they contain.
// Every returned fragment is cited with doc + chunk id + start line. No external API.
function answerWithCitations(index, question, opts) {
  const terms = [...new Set(norm(question || '').split(/[^\p{L}\p{N}]+/u).filter((t) => t.length >= 2))];
  if (!terms.length) return { answer: 'Escribe una pregunta.', citations: [] };
  if (!index || !Array.isArray(index.chunks) || !index.chunks.length) {
    return { answer: 'No hay documentos indexados.', citations: [] };
  }
  const docs = opts && Array.isArray(opts.docs) && opts.docs.length ? new Set(opts.docs) : null;
  const pool = docs ? index.chunks.filter((c) => docs.has(c.doc)) : index.chunks;
  if (!pool.length) return { answer: 'Ningun documento seleccionado esta indexado.', citations: [] };
  const scored = [];
  pool.forEach((c, order) => {
    const t = norm(c.text);
    const score = terms.filter((w) => t.includes(w)).length;
    if (score) scored.push({ c, score, order });
  });
  if (!scored.length) return { answer: `No se encontro "${String(question).trim()}" en los documentos.`, citations: [] };
  scored.sort((a, b) => b.score - a.score || a.order - b.order);
  const heads = new Map();
  const headingsFor = (doc) => {
    if (!heads.has(doc)) heads.set(doc, headingsOf(index.chunks.filter((x) => x.doc === doc)));
    return heads.get(doc);
  };
  const citations = scored.slice(0, MAX_CITATIONS).map(({ c }) => ({
    doc: c.doc,
    title: (index.docs && index.docs[c.doc] && index.docs[c.doc].title) || c.doc,
    chunkId: c.id,
    line: c.line,
    section: sectionOf(headingsFor(c.doc), c.line),
    text: c.text,
  }));
  const answer = `${scored.length} fragmento(s) coinciden. Mejores:\n` +
    citations.map((c) => `- [${c.doc} ${c.chunkId}, linea ${c.line}] ${c.text.split('\n')[0]}`).join('\n');
  return { answer, citations };
}

module.exports = { answerWithCitations };
