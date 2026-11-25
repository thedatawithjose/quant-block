const { answerWithCitations } = require('./cite');

const MAX_TURNS = 20;
const MAX_SIGNIFICANT_FOR_FOLLOWUP = 2;
const STOP = new Set(['que', 'los', 'las', 'una', 'del', 'con', 'por', 'para', 'como', 'cual', 'donde']);

const norm = (s) => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

// Words longer than 2 letters that are not in the stop list (accent/case-insensitive); original spelling kept.
function significantWords(question) {
  return String(question || '').normalize('NFC').split(/[^\p{L}\p{N}]+/u).filter((w) => w.length > 2 && !STOP.has(norm(w)));
}

function effectiveQueryFor(history, question) {
  const words = significantWords(question);
  const prev = history.length ? history[history.length - 1] : null;
  if (!prev || words.length > MAX_SIGNIFICANT_FOR_FOLLOWUP) return String(question).normalize('NFC');
  return [prev.effectiveQuery, ...words].join(' ');
}

// Pure: returns a new history (oldest turns dropped beyond MAX_TURNS) and the new last turn.
function askInConversation(history, question, index) {
  const prior = Array.isArray(history) ? history : [];
  const effectiveQuery = effectiveQueryFor(prior, question);
  const { answer, citations } = answerWithCitations(index, effectiveQuery);
  const turn = { q: question, effectiveQuery, a: answer, citations };
  return { history: [...prior, turn].slice(-MAX_TURNS), turn };
}

function clearConversation() {
  return [];
}

module.exports = { MAX_TURNS, askInConversation, clearConversation, significantWords };
