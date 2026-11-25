# Product

Local knowledge base: user keeps .md/.txt documents, browses them and asks questions about the selected one. Q&A is a local stub (no external API).

## Scope for this phase
1. Import: "Importar" button copies chosen .md/.txt into `data/docs`; never overwrite an existing file.
2. Detail: full content plus name, size in bytes, modification date.
3. Persistence (done, F07): survives restart: imported-documents record (source path, import date) and last selected document.
4. Conversation (F13): the Q&A panel is a multi-turn list (question, answer, citations), persisted in `data/state.json` and restored on restart; max 20 turns (oldest dropped); "Nueva conversacion" clears it. Short follow-ups (2 or fewer significant words) extend the previous turn's effective query.

## Out of scope
Real LLM/API calls, other file types, sync, auth.
