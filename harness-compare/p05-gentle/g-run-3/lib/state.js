const fs = require('node:fs');
const path = require('node:path');

const MAX_TURNS = 20;
const defaults = () => ({ imports: [], lastSelected: null, conversation: [] });

const validTurn = (t) => t && typeof t === 'object' && typeof t.q === 'string' && typeof t.effectiveQuery === 'string'
  && typeof t.a === 'string' && Array.isArray(t.citations);

function statePath(root) {
  return path.join(root, 'data', 'state.json');
}

// Never throws: missing/corrupt/invalid file yields defaults.
function loadState(root) {
  try {
    const raw = JSON.parse(fs.readFileSync(statePath(root), 'utf8'));
    const imports = Array.isArray(raw.imports)
      ? raw.imports.filter((i) => i && typeof i.name === 'string' && typeof i.source === 'string' && typeof i.importedAt === 'string')
      : [];
    const conversation = Array.isArray(raw.conversation) ? raw.conversation.filter(validTurn).slice(-MAX_TURNS) : [];
    return { imports, lastSelected: typeof raw.lastSelected === 'string' ? raw.lastSelected : null, conversation };
  } catch {
    return defaults();
  }
}

// Atomic write (temp file + rename) so a crash never leaves a half-written state.
function saveState(root, state) {
  const file = statePath(root);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(state, null, 2));
  fs.renameSync(tmp, file);
}

function recordImports(state, records, now = new Date()) {
  const names = new Set(records.map((r) => r.name));
  const kept = state.imports.filter((i) => !names.has(i.name));
  const added = records.map((r) => ({ name: r.name, source: r.source, importedAt: now.toISOString() }));
  return { ...state, imports: [...kept, ...added] };
}

function setLastSelected(state, name) {
  return { ...state, lastSelected: typeof name === 'string' ? name : null };
}

module.exports = { MAX_TURNS, statePath, loadState, saveState, recordImports, setLastSelected };
