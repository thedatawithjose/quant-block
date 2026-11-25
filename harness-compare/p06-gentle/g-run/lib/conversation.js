const { answerWithCitations } = require('./cite');

const MAX_TURNS = 20;
const STOPWORDS = ['que', 'los', 'las', 'una', 'del', 'con', 'por', 'para', 'como', 'cual', 'donde'];

const norm = (s) => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

// Normalized words with more than 2 letters that are not stopwords, in order.
function significantWords(question) {
  if (typeof question !== 'string') return [];
  return norm(question)
    .split(/[^\p{L}\p{N}]+/u)
    .filter((w) => w.length >= 3 && !STOPWORDS.includes(w));
}

// Questions with <= 2 significant words extend the previous turn's effective query.
function effectiveQuery(history, question) {
  const q = typeof question === 'string' ? question.trim() : '';
  const words = significantWords(q);
  const prev = Array.isArray(history) && history.length ? history[history.length - 1] : null;
  if (words.length >= 3 || !prev || typeof prev.effectiveQuery !== 'string') return q;
  return `${prev.effectiveQuery} ${words.join(' ')}`.trim();
}

// Pure: returns a new history and the new turn (null when the question is empty).
function askInConversation(history, question, index) {
  const base = Array.isArray(history) ? history : [];
  if (typeof question !== 'string' || !question.trim()) return { history: [...base], turn: null };
  const eq = effectiveQuery(base, question);
  const { answer, citations } = answerWithCitations(index, eq);
  const turn = { q: question.trim(), effectiveQuery: eq, a: answer, citations };
  return { history: [...base, turn].slice(-MAX_TURNS), turn };
}

module.exports = { MAX_TURNS, askInConversation, effectiveQuery, significantWords };
