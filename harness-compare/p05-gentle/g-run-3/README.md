# kb-electron-skeleton
App Electron minima de base de conocimiento. `npm install && npm start`; tests con `npm test`.

## Conversacion (F13)
El panel de preguntas muestra la conversacion como lista de turnos (pregunta, respuesta, citas), persistida en `data/state.json` (maximo 20 turnos). Las preguntas de 2 o menos palabras significativas (mas de 2 letras, sin "que los las una del con por para como cual donde"; sin ignorar repetidas) extienden la consulta del turno anterior. El boton "Nueva conversacion" la vacia. Logs: `conv.ask`, `conv.clear` en `data/app.log`.
