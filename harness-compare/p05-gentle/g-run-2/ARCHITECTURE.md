# Architecture

Electron app, three layers. Only dependency: `electron` (dev).

| File | Role |
|---|---|
| `main.js` | Main process. Creates the window, creates `data/docs`, registers IPC handlers (`docs:list`, `docs:read`, `docs:info`, `docs:import`, `qa:ask`, `conv:get`, `conv:ask`, `conv:clear`). New IPC channels go here. |
| `preload.js` | `contextBridge` exposes `window.kb`. The only door between renderer and main. `contextIsolation: true`. |
| `lib/docs.js` | Pure fs logic: `ensureDocsDir`, `listDocs` (.md/.txt), `readDoc` (rejects `../` and other extensions). No Electron imports, so it is unit-testable. |
| `lib/state.js` | Persistence: `loadState` (never throws), atomic `saveState`, `recordImports`, `setLastSelected`. File: `data/state.json` = `{imports:[{name,source,importedAt}], lastSelected, conversation:[turn]}` (`conversation` missing/invalid = `[]`, capped to `MAX_TURNS`). main.js keeps state in memory and saves on import/select (IPC `state:get`, `state:select`). |
| `lib/qa.js` | Local Q&A stub: case-insensitive line search in the selected document. |
| `lib/chunk.js` | `chunkDoc(name, text)`: paragraph chunks `{id: name#n, doc, n, line, text}`. |
| `lib/meta.js` | `extractMeta(name, text)`: `{name, title, words, headings}`. |
| `lib/indexer.js` | `createIndexer(dir, {file})`: persists to `data/index.json` (atomic, gitignored, version 1; corrupt/missing = full reindex), reloads on creation, reindexes only new/modified docs by mtime and drops deleted ones; `start(onProgress)`, `status()` (`idle/indexing/done`, done/total/chunks), `get()`. IPC `index:start`, `index:status`, event `index:progress`. |
| `lib/cite.js` | `answerWithCitations(index, q)`: local ranking of chunks; citations = doc + chunkId + line. IPC `qa:cited`. |
| `lib/conversation.js` | F13 multi-turn Q&A. `askInConversation(history, question, index)` -> `{history, turn}` (pure, never mutates `history`); turn = `{q, effectiveQuery, a, citations}`. Follow-up rule: 2 or fewer significant words (>2 letters, not in the stop list que/los/las/una/del/con/por/para/como/cual/donde) => effective query = previous turn's effective query + those words; otherwise the question itself. Answer via `answerWithCitations`. `MAX_TURNS = 20` (oldest dropped), `clearConversation`. Persisted under state.json `conversation`; IPC `conv:get`, `conv:ask`, `conv:clear`; logs `conv.ask`, `conv.clear`. |
| `renderer/` | UI (`index.html`, `renderer.js`). No Node access. |
| `test/` | `node:test`; run `npm test`. |

## Conventions
- New fs/domain logic goes in `lib/` with a test first; `main.js` only wires IPC.
- Every new renderer capability needs a preload method plus an IPC handler.
- Persistent state lives under `data/` (docs in `data/docs`).

## Pending / known limits
- Index is persisted in `data/index.json`; at start and after import only new/modified docs are reindexed (progress n/total counts only those).
- The GUI has not been run in Electron; only unit tests, a stubbed-electron run of `main.js` handlers and structural wiring checks cover F13.
- Effective query grows without bound under chained short follow-ups (each <=2-word follow-up appends to the previous effective query; only `MAX_TURNS` limits turns, not query length).
- The legacy `qa:cited` / `askCited` channel is still present alongside `conv:*`.
- `conv:ask` ignores empty/whitespace questions (no turn appended); `loadState` drops malformed citation items and the renderer skips malformed ones.

## Existing tests changed by F13
- `test/app.test.js`: required element ids now `conversation`, `conv-clear` (replacing `answer`).
- `test/cite.test.js`: citations render inside `#conversation` (replacing `#citations`).
- `test/state.test.js`: `loadState` defaults now include `conversation: []`.

## Layer rules (enforced by `scripts/check-architecture.sh`)
- `renderer/` has no Node/Electron access; it only calls `window.kb`.
- `lib/` never imports `electron`.
- `preload.js` requires only `electron`.
- Logging: `lib/logger.js` (JSON lines to `data/app.log`); `main.js` creates it and passes it to `lib/` modules that need it.
