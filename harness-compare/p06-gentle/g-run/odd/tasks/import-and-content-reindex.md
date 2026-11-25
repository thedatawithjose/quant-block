# F14 + F15: lossless import, content-hash reindex
Session 1 of 2. Branch: master (local commits only, no push).

## Specs
- S1 (F14): `importDocs(dir, sources)` no longer skips an existing name: copies as `a (2).md`, `a (3).md`... before the extension; never overwrites; also for two sources with the same name in one call.
- S2 (F14): `imported` and `records[].name` use the final name; new field `renamed: [{ from, to }]`.
- S3 (F14): disallowed extensions stay in `skipped` with reason "extension".
- S4 (F15): indexer decides what to reindex by sha256 of content (node:crypto), not mtime: same mtime + changed content -> reindexed; changed mtime + same content -> not.
- S5 (F15): persisted index stores the hashes; an old index file (no hashes) loads without error and reindexes.
- S6 (F15): `status().total` and `done` count only what is reindexed.
- Constraints: no new deps, renderer does not touch the filesystem, Q&A local.

## Tasks
- [x] T1 S1-S3 import rename (test/import.test.js, lib/docs.js, renderer message) — commit feat(import)
- [x] T2 S4-S6 hash reindex (test/persist-index.test.js, lib/indexer.js) — commit feat(index)

## Log
L1: F14 Importacion sin perdida / F15 Reindexado por contenido (ver especificacion del usuario, sesion 1 de 2).
