const { answerWithCitations } = require('./cite');
const { MAX_TURNS } = require('./state');

const STOPWORDS = new Set(['que', 'los', 'las', 'una', 'del', 'con', 'por', 'para', 'como', 'cual', 'donde']);
const MAX_FOLLOW_UP_WORDS = 2;

const norm = (s) => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

// Significant words in order of appearance, in their original form (> 2 letters, not stopwords).
// Duplicates are kept: each occurrence counts.
function significantWords(question) {
  return question.split(/[^\p{L}\p{N}\p{M}]+/u).filter((t) => {
    const n = norm(t);
    return n.length > 2 && !STOPWORDS.has(n);
  });
}

function effectiveQueryFor(history, question) {
  const own = question.trim();
  const words = significantWords(question);
  if (!history.length || words.length > MAX_FOLLOW_UP_WORDS) return own;
  return [history[history.length - 1].effectiveQuery, ...words].join(' ');
}

// Pure: returns { history, turn } without mutating the input history.
function askInConversation(history, question, index) {
  const prev = Array.isArray(history) ? history : [];
  if (typeof question !== 'string' || !question.trim()) return { history: [...prev], turn: null };
  const effectiveQuery = effectiveQueryFor(prev, question);
  // Nothing searchable or nothing indexed: no real answer, so no turn is added (or persisted).
  const hasChunks = index && Array.isArray(index.chunks) && index.chunks.length > 0;
  if (!hasChunks || !/[\p{L}\p{N}]{2}/u.test(effectiveQuery)) return { history: [...prev], turn: null };
  const { answer, citations } = answerWithCitations(index, effectiveQuery);
  const turn = { q: question.trim(), effectiveQuery, a: answer, citations };
  return { history: [...prev, turn].slice(-MAX_TURNS), turn };
}

module.exports = { askInConversation, MAX_TURNS };
