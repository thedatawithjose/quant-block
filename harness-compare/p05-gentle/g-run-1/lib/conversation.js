const { answerWithCitations } = require('./cite');

const MAX_TURNS = 20;
const STOPWORDS = new Set(['que', 'los', 'las', 'una', 'del', 'con', 'por', 'para', 'como', 'cual', 'donde']);

const norm = (s) => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

// Words of 3+ letters that are not stopwords (compared without accents; original spelling kept).
function significantWords(question) {
  return (String(question || '').match(/\p{L}+/gu) || [])
    .filter((w) => w.length > 2 && !STOPWORDS.has(norm(w)));
}

// Follow-up rule: <=2 significant words extend the previous effective query.
function effectiveQueryFor(history, question) {
  const words = significantWords(question);
  const prev = history[history.length - 1];
  if (words.length > 2 || !prev) return question;
  return [prev.effectiveQuery, ...words].join(' ');
}

// Pure: returns a new history (capped to MAX_TURNS, oldest dropped) and the new turn.
function askInConversation(history, question, index) {
  const base = Array.isArray(history) ? history : [];
  const effectiveQuery = effectiveQueryFor(base, question);
  const { answer, citations } = answerWithCitations(index, effectiveQuery);
  const turn = { q: question, effectiveQuery, a: answer, citations };
  return { history: [...base, turn].slice(-MAX_TURNS), turn };
}

module.exports = { askInConversation, significantWords, MAX_TURNS };
