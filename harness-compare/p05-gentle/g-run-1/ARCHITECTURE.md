# Architecture

Electron app, three layers. Only dependency: `electron` (dev).

| File | Role |
|---|---|
| `main.js` | Main process. Creates the window, creates `data/docs`, registers IPC handlers (`docs:list`, `docs:read`, `docs:info`, `docs:import`, `qa:ask`). New IPC channels go here. |
| `preload.js` | `contextBridge` exposes `window.kb`. The only door between renderer and main. `contextIsolation: true`. |
| `lib/docs.js` | Pure fs logic: `ensureDocsDir`, `listDocs` (.md/.txt), `readDoc` (rejects `../` and other extensions). No Electron imports, so it is unit-testable. |
| `lib/state.js` | Persistence: `loadState` (never throws), atomic `saveState`, `recordImports`, `setLastSelected`. File: `data/state.json` = `{imports:[{name,source,importedAt}], lastSelected}`. main.js keeps state in memory and saves on import/select (IPC `state:get`, `state:select`). |
| `lib/qa.js` | Local Q&A stub: case-insensitive line search in the selected document. |
| `lib/chunk.js` | `chunkDoc(name, text)`: paragraph chunks `{id: name#n, doc, n, line, text}`. |
| `lib/meta.js` | `extractMeta(name, text)`: `{name, title, words, headings}`. |
| `lib/indexer.js` | `createIndexer(dir, {file})`: persists to `data/index.json` (atomic, gitignored, version 1; corrupt/missing = full reindex), reloads on creation, reindexes only new/modified docs by mtime and drops deleted ones; `start(onProgress)`, `status()` (`idle/indexing/done`, done/total/chunks), `get()`. IPC `index:start`, `index:status`, event `index:progress`. |
| `lib/cite.js` | `answerWithCitations(index, q)`: local ranking of chunks; citations = doc + chunkId + line. IPC `qa:cited`. |
| `lib/conversation.js` | `askInConversation(history, question, index)` -> `{history, turn}` (pure, no mutation, `MAX_TURNS=20`). Follow-up rule: <=2 significant words (3+ letters, not in the stopword list) extend the previous turn's `effectiveQuery`. History persisted under `conversation` in `data/state.json` (`loadState` returns `[]` if missing/invalid). IPC `conv:get`, `conv:ask`, `conv:clear`; logs `conv.ask`, `conv.clear`. |
| `renderer/` | UI (`index.html`, `renderer.js`). No Node access. |
| `test/` | `node:test`; run `npm test`. |

## Conventions
- New fs/domain logic goes in `lib/` with a test first; `main.js` only wires IPC.
- Every new renderer capability needs a preload method plus an IPC handler.
- Persistent state lives under `data/` (docs in `data/docs`).

## Not built yet
Nothing pending. Index is persisted in `data/index.json`; at start and after import only new/modified docs are reindexed (progress n/total counts only those).

## Layer rules (enforced by `scripts/check-architecture.sh`)
- `renderer/` has no Node/Electron access; it only calls `window.kb`.
- `lib/` never imports `electron`.
- `preload.js` requires only `electron`.
- Logging: `lib/logger.js` (JSON lines to `data/app.log`); `main.js` creates it and passes it to `lib/` modules that need it.
