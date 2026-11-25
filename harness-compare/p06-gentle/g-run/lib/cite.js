const MAX_CITATIONS = 5;

const norm = (s) => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

// Local grounded Q&A: ranks indexed chunks by how many question terms they contain.
// Every returned fragment is cited with doc + chunk id + start line. No external API.
// opts.docs (array of doc names) restricts the search; empty or absent means all documents.
function answerWithCitations(index, question, opts = {}) {
  const terms = [...new Set(norm(question || '').split(/[^\p{L}\p{N}]+/u).filter((t) => t.length >= 2))];
  if (!terms.length) return { answer: 'Escribe una pregunta.', citations: [] };
  if (!index || !Array.isArray(index.chunks) || !index.chunks.length) {
    return { answer: 'No hay documentos indexados.', citations: [] };
  }
  const only = opts && Array.isArray(opts.docs) && opts.docs.length ? new Set(opts.docs) : null;
  const scored = [];
  index.chunks.forEach((c, order) => {
    if (only && !only.has(c.doc)) return;
    const t = norm(c.text);
    const score = terms.filter((w) => t.includes(w)).length;
    if (score) scored.push({ c, score, order });
  });
  if (!scored.length) return { answer: `No se encontro "${String(question).trim()}" en los documentos.`, citations: [] };
  scored.sort((a, b) => b.score - a.score || a.order - b.order);
  const citations = scored.slice(0, MAX_CITATIONS).map(({ c }) => ({
    doc: c.doc,
    title: (index.docs && index.docs[c.doc] && index.docs[c.doc].title) || c.doc,
    chunkId: c.id,
    line: c.line,
    section: c.section == null ? null : c.section,
    text: c.text,
  }));
  const answer = `${scored.length} fragmento(s) coinciden. Mejores:\n` +
    citations.map((c) => `- [${c.doc} ${c.chunkId}, linea ${c.line}] ${c.text.split('\n')[0]}`).join('\n');
  return { answer, citations };
}

module.exports = { answerWithCitations };
