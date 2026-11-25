# kb-electron-skeleton
App Electron minima de base de conocimiento. `npm install && npm start`; tests con `npm test`.

## Conversacion (F13)
El panel de preguntas muestra una conversacion multi-turno (pregunta, respuesta, citas), guardada en `data/state.json` (clave `conversation`, max 20 turnos). Una pregunta de seguimiento (2 o menos palabras significativas) se amplia con la consulta del turno anterior. El boton "Nueva conversacion" la vacia. Verificar: `npm test` y `./scripts/check-architecture.sh`; a mano: `npm start`, preguntar "gatos duermen mucho", luego "perros", reiniciar y comprobar que el historial sigue.
