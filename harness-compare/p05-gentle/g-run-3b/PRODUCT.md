# Product

Local knowledge base: user keeps .md/.txt documents, browses them and asks questions about the selected one. Q&A is a local stub (no external API).

## Scope for this phase
1. Import: "Importar" button copies chosen .md/.txt into `data/docs`; never overwrite an existing file.
2. Detail: full content plus name, size in bytes, modification date.
3. Persistence (done, F07): survives restart: imported-documents record (source path, import date) and last selected document.

## Out of scope
Real LLM/API calls, other file types, sync, auth.
