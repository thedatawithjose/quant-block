const MAX_CITATIONS = 5;

const norm = (s) => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

// Local grounded Q&A: ranks indexed chunks by how many question terms they contain.
// Every returned fragment is cited with doc + chunk id + start line. No external API.
function answerWithCitations(index, question) {
  const terms = [...new Set(norm(question || '').split(/[^\p{L}\p{N}]+/u).filter((t) => t.length >= 2))];
  if (!terms.length) return { answer: 'Escribe una pregunta.', citations: [] };
  if (!index || !Array.isArray(index.chunks) || !index.chunks.length) {
    return { answer: 'No hay documentos indexados.', citations: [] };
  }
  const scored = [];
  index.chunks.forEach((c, order) => {
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
    text: c.text,
  }));
  const answer = `${scored.length} fragmento(s) coinciden. Mejores:\n` +
    citations.map((c) => `- [${c.doc} ${c.chunkId}, linea ${c.line}] ${c.text.split('\n')[0]}`).join('\n');
  return { answer, citations };
}

module.exports = { answerWithCitations };
