(Mismas reglas de la FASE A: mismo harness, mismo loop maker-checker con verificador independiente, 3 aprobaciones consecutivas o 10 rondas, mismas restricciones de carpeta. Continua en esta misma sesion.)

FASE B. Llega un CAMBIO DE REQUISITO sobre lo que acabas de entregar. Reinicia el contador de aprobaciones consecutivas y aplica el cambio con el mismo loop:


---
# CAMBIO DE REQUISITO 1 (llega despues de entregar F18)

Exportar solo un rango de turnos.

1. `conversationToMarkdown` y `exportConversation` aceptan `opts.fromTurn` y `opts.toTurn` (enteros, base 1, ambos inclusive). Si solo hay `fromTurn`, `toTurn` es el ultimo turno; si solo hay `toTurn`, `fromTurn` es 1.
2. Con rango, solo se exportan esos turnos, pero conservan su numero original en el encabezado (`## 2. ...`, `## 3. ...`). El conteo de la cabecera es el de turnos exportados y, solo cuando se aplico un rango, lleva el rango al final: `_Exportada: <ISO> · 2 turnos (2–3 de 5)_` (guion largo `–`, "de" seguido del total de turnos del historial). Sin rango, la cabecera no cambia.
3. Rango invalido -> `Error` con `code === 'EINVAL'` en ambas funciones: valores que no sean enteros (`1.5`, `'2'`, `NaN`, `Infinity`), menores que 1, mayores que el total de turnos, o `fromTurn > toTurn`. Un rango invalido no crea ningun archivo. `fromTurn: undefined` o `null` cuentan como ausentes.
4. El canal `conv:export` acepta un argumento opcional `{ fromTurn, toTurn }` y lo pasa a `exportConversation`; un rango invalido hace que el canal falle con ese mismo error. `preload.js`: `convExport(range)` lo reenvia. El log `conv.export` incluye ademas `from` y `to` (los efectivamente exportados).
5. No cambia nada mas del comportamiento existente.

Al terminar responde SOLO con lo mismo que en la fase A, para las rondas de esta fase: horas, tabla por ronda, agentes y modelos, archivos de estado, `npm test` literal, hashes, errores literales, intervenciones.
