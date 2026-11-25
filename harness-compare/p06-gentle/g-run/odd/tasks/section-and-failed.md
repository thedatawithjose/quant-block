# F16 + F17: citation sections/doc filter, visible index failures
Session 2 of 2. Branch: master (local commits only, no push). Prior session: odd/tasks/import-and-content-reindex.md (F14/F15).

## Specs
- S1 (F16): each citation from `answerWithCitations(index, question, opts)` has `section`: nearest heading text (no #) at or before the chunk start line in its doc, else `null`.
- S2 (F16): `opts.docs` (array of names) restricts search; empty/absent = all; no match -> `citations: []` and `answer` a string.
- S3 (F17): indexer `status()` has `failed: [{ doc, message }]`, reset each run.
- S4 (F17): log `index.done` includes `failed` (number) and `durationMs` (number).
- S5 (F17): UI shows failed docs.
- Constraints: no new deps, renderer has no fs access, Q&A local.

## Tasks
- [x] T1 S1-S2 section in chunkDoc (lib/chunk.js), filter in lib/cite.js; main.js/preload pass opts; UI shows section — test/section-failed.test.js
- [x] T2 S3-S5 lib/indexer.js failed + durationMs; renderer #index-failed
- [ ] Pending: no UI control to pick docs for filtering (opts.docs only reachable via window.kb.askCited(question, {docs})); conversation flow (lib/conversation.js) does not pass opts; UI untested in Electron (no display).

## Notes
- Section is computed at chunk time and stored on chunks; indexer VERSION bumped to 2 so old persisted indexes reindex once.
- Failure test uses chmod 000 (does not work as root).

## Log
L1: F16 Citas con seccion y filtro de documentos / F17 Fallos de indexacion visibles (sesion 2 de 2).
