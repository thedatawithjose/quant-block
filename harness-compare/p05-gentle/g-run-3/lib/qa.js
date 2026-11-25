// Local stub: returns the lines of the document that contain the question text.
function answer(docText, question) {
  if (typeof docText !== 'string') return 'Selecciona un documento primero.';
  const q = String(question || '').trim().toLowerCase();
  if (!q) return 'Escribe una pregunta.';
  const hits = docText.split(/\r?\n/).filter((l) => l.toLowerCase().includes(q));
  if (!hits.length) return `No se encontro "${question.trim()}" en el documento.`;
  return `${hits.length} coincidencia(s):\n` + hits.map((l) => `- ${l.trim()}`).join('\n');
}

module.exports = { answer };
