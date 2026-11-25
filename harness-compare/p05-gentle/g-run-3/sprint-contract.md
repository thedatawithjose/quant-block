# Sprint contract — F13 conversacion multi-turno

Fuente: `TASK-F13.md`. Evaluacion: `RUBRICA.md` (APROBADO solo si ningun criterio < 3 y sin defectos de severidad alta).
Este contrato se deriva de la especificacion, no de la implementacion existente. Cada AC se verifica con un comando o asercion concreta; un AC solo cuenta como cumplido si se ejecuto y se registra la salida literal.

Alcance de archivos: `lib/conversation.js`, `lib/state.js`, `main.js`, `preload.js`, `renderer/index.html`, `renderer/renderer.js`, `test/*.test.js` (nuevos/extendidos), `README.md`, `ARCHITECTURE.md`. `package.json` y dependencias: sin cambios.

## 0. Decisiones sobre ambiguedades (vinculantes)

| # | Ambiguedad | Decision |
|---|---|---|
| D1 | Pregunta vacia, solo espacios o no-string (`undefined`, `null`, numero) | `askInConversation` no lanza. Devuelve `{ history: <array nuevo con los mismos turnos>, turn: null }`; no se agrega turno y no se llama a `answerWithCitations`. El handler `conv:ask` en ese caso no guarda estado, no escribe `conv.ask` y devuelve `{ history, turn: null }`. El renderer no invoca `convAsk` con entrada vacia. |
| D2 | Normalizacion para clasificar palabras | `String(s).toLowerCase().normalize('NFD')` quitando marcas combinantes U+0300–U+036F (igual que `lib/cite.js`). `Qué`, `QUE`, `que` son la misma palabra; `Cuál`=`cual`; `Dónde`=`donde`. |
| D3 | Deteccion de palabras | Tras normalizar, partir con `/[^\p{L}\p{N}]+/u` y descartar vacios. Digitos cuentan como caracteres de palabra (`2024` = 4 letras). Puntuacion (`¿ ? , .`) no forma parte de la palabra. |
| D4 | Palabra significativa | Token normalizado con longitud >= 3 que NO esta en el conjunto exacto de 11 stopwords: `que los las una del con por para como cual donde`. Cualquier otra palabra (`uno`, `sin`, `sus`, `mas`, `cuando`, `quien`, `el`-no, etc.) es significativa si tiene >= 3 letras. Tokens de 1–2 letras nunca cuentan. |
| D5 | Duplicados | No se deduplican: se cuentan tal cual aparecen (`"gato gato"` = 2 palabras significativas). |
| D6 | Regla de seguimiento | Sea `n` el numero de palabras significativas. Si `n >= 3` o `history` esta vacio -> `effectiveQuery = question.trim()`. Si `n <= 2` y hay turno previo -> `effectiveQuery = [prev.effectiveQuery, ...palabras].join(' ')`, con `prev` = ultimo elemento de `history` y `palabras` = las palabras significativas en el orden de la pregunta, escritas en su forma original (sin signos de puntuacion, caso/acentos tal como se escribieron). Con `n = 0` (ej. `"que es"`) el resultado es exactamente `prev.effectiveQuery` (sin espacio final). Exactamente 2 -> seguimiento; exactamente 3 -> propia pregunta. No se deduplica contra `prev.effectiveQuery`. |
| D7 | `turn.q` | Es la pregunta tal como se recibio, con `trim()` aplicado. |
| D8 | Forma del turno | `turn = { q, effectiveQuery, a, citations }` con `a` = `answer` y `citations` = `citations` devueltos por `answerWithCitations(index, effectiveQuery)` (llamado exactamente una vez con `effectiveQuery`, no con `q`). `turn` es identico (`deepStrictEqual`) a `history[history.length-1]`. |
| D9 | Tope | `MAX_TURNS === 20`. Si tras agregar hay > 20 turnos se descartan los mas antiguos: `history.length <= 20` y el ultimo es el turno nuevo. |
| D10 | No mutacion | La entrada `history` (array y sus turnos) no se modifica (ni push, ni shift, ni cambio en turnos, ni congelado accidental requerido). `history` devuelto es un array distinto (`!==`) de la entrada, incluso en el caso D1. |
| D11 | `state.json` invalido | `loadState(root).conversation` es `[]` si: archivo ausente, JSON corrupto, `conversation` no es array (objeto, string, null, numero). Turnos individuales invalidos (sin `q`/`effectiveQuery`/`a` string o `citations` no-array, o no-objeto) se descartan, conservando los validos en orden; si hay > 20 validos se queda con los ultimos 20. `loadState` nunca lanza. |
| D12 | `saveState` | Conserva la clave `conversation` tal cual se le pasa (escritura atomica existente) y `imports`/`lastSelected` no se pierden. Un `saveState` + `loadState` ida y vuelta devuelve los mismos turnos. |
| D13 | Estado en main | `main.js` mantiene `state.conversation` en memoria y guarda tras `conv:ask` (con turno) y `conv:clear`. Las operaciones de import/select existentes no borran `conversation`. |
| D14 | Indexacion en `conv:ask` | Si el indexador no esta en `done`, se arranca antes de responder; luego `indexer.get()` se pasa como `index`. |

## 1. Criterios de aceptacion

### Funcionalidad — `lib/conversation.js`

- **AC1 (API).** `require('./lib/conversation')` exporta funcion `askInConversation` y `MAX_TURNS === 20`. Verif: `node -e "const c=require('./lib/conversation');console.log(typeof c.askInConversation,c.MAX_TURNS)"` imprime `function 20`. El modulo no importa `electron` ni usa `fs`/IPC (puro).
- **AC2 (primer turno).** Con `history=[]` y pregunta de 1 palabra significativa (`"gatos"`), `turn.effectiveQuery === "gatos"` y `turn.q === "gatos"`; `history.length === 1`.
- **AC3 (>=3 palabras).** Con turno previo, una pregunta con 3 palabras significativas (`"alimentacion de gatos adultos"` -> `alimentacion`, `gatos`, `adultos`) tiene `effectiveQuery` igual a la pregunta (trim), sin prefijo del turno anterior. Caso limite exacto 3.
- **AC4 (seguimiento 1 y 2 palabras).** Prev `effectiveQuery="gatos domesticos"`: `"alimentacion"` -> `"gatos domesticos alimentacion"`; `"dieta seca"` -> `"gatos domesticos dieta seca"`. Caso `n=2` exacto es seguimiento.
- **AC5 (stopwords y cortas ignoradas).** `"y que es"`, `"que los"`, `"de la"` (todas con 0 palabras significativas) con prev `"gatos"` -> `effectiveQuery === "gatos"` (D6, sin espacio final). `"como cuidar"` -> `"gatos cuidar"`. Verifica las 11 stopwords una por una (cada una sola no cuenta) y que `uno`, `sin`, `mas` si cuentan.
- **AC6 (mayusculas/acentos).** `"QUE"`, `"Qué"`, `"CUÁL"`, `"Dónde"`, `"PARA"` se tratan como stopwords (no cuentan); `"Alimentación"` cuenta como 1 palabra y en el seguimiento aparece como `Alimentación` (forma original). `"¿Cuál es la dieta?"` -> palabras significativas: `dieta` (`es`, `la` de <=2 letras no cuentan; `cuál` stopword) -> n=1 -> seguimiento.
- **AC7 (encadenado).** Tres turnos seguidos de seguimiento acumulan: `"gatos"` -> `"gatos"`; `"dieta"` -> `"gatos dieta"`; `"seca"` -> `"gatos dieta seca"` (usa la `effectiveQuery` del turno anterior, no `q`). Una pregunta de >=3 palabras reinicia la base.
- **AC8 (respuesta via cite).** Test con un indice sintetico `{docs, chunks}`: `turn.a` y `turn.citations` son `deepStrictEqual` a `answerWithCitations(index, turn.effectiveQuery)`; en un seguimiento las citas provienen de la consulta extendida (un chunk que solo contiene la palabra del turno previo aparece citado).
- **AC9 (vacio/espacios).** `""`, `"   "`, `"\n\t"`, `undefined`, `null`, `42` -> sin excepcion, `turn === null`, `history` con los mismos turnos y `history !== entrada` (D1/D10).
- **AC10 (tope 20).** Partiendo de 20 turnos, un `ask` mas devuelve `history.length === 20`, el primero original descartado, el ultimo es el nuevo. Partiendo de vacio y 25 `ask` consecutivos -> longitud 20, `history[0].q` es la pregunta 6. Con 19 -> 20 sin descartar.
- **AC11 (no mutacion).** Con `history` y turnos congelados (`Object.freeze` profundo) la llamada no lanza; tras la llamada `JSON.stringify(entrada)` es identico al de antes y `history` devuelto `!==` entrada. Tambien en el caso del tope (20 -> 20) la entrada sigue teniendo su primer turno.
- **AC12 (vaciar).** `conv:clear` deja `state.conversation === []`, `conv:get` posterior devuelve `[]`, `data/state.json` contiene `"conversation": []`, y un nuevo `ask` posterior se trata como primer turno (effectiveQuery = propia pregunta aunque tenga <=2 palabras).

### Persistencia — `lib/state.js`

- **AC13 (round-trip).** `saveState(root,{imports:[],lastSelected:null,conversation:[t1,t2]})` y luego `loadState(root).conversation` `deepStrictEqual [t1,t2]`; `imports` y `lastSelected` se conservan. Test con directorio temporal.
- **AC14 (invalido -> []).** Archivo ausente; contenido `{not json`; `{"conversation":"x"}`; `{"conversation":{}}`; `{"conversation":null}`; `{}` -> `loadState(root).conversation` es `[]` y no lanza (D11). Los defaults de `imports`/`lastSelected` siguen funcionando.
- **AC15 (turnos invalidos).** `conversation:[valido, 5, null, {q:1}, {q:'a',effectiveQuery:'a',a:'x',citations:'no'}, valido2]` -> solo `[valido, valido2]`. Con 25 turnos validos -> los ultimos 20.
- **AC16 (supervivencia a reinicio).** Test de integracion: ejecutar el flujo `askInConversation` -> `saveState` -> (nuevo proceso/`loadState`) -> `askInConversation` sobre lo cargado; el seguimiento usa el `effectiveQuery` del turno restaurado. Verificacion manual/arranque: tras `npm start`, preguntar, cerrar y reabrir, el panel muestra los turnos (si no hay display disponible, declararlo como no verificado en el informe).
- **AC17 (no perder datos).** `recordImports`/`setLastSelected` conservan `conversation` (spread del estado); un `state:select` o import posterior no vacia el historial.

### Cableado

- **AC18 (IPC en main).** `main.js` registra `ipcMain.handle` para `conv:get` (devuelve el historial en memoria/persistido), `conv:ask` (D1, D8, D13, D14) y `conv:clear`. Verif: `grep -n "'conv:" main.js` muestra los 3 canales. `main.js` solo cablea: la logica vive en `lib/conversation.js`.
- **AC19 (preload).** `preload.js` expone en `window.kb` metodos que invocan exactamente `conv:get`, `conv:ask`, `conv:clear` (p. ej. `convGet`, `convAsk(question)`, `convClear`) y requiere solo `electron`. Verif: test que carga `preload.js` con `electron` simulado y comprueba que cada metodo llama `ipcRenderer.invoke` con el canal y argumentos correctos.
- **AC20 (renderer).** `renderer/index.html` tiene un boton con texto "Nueva conversacion" y un contenedor de turnos. `renderer/renderer.js` al cargar llama a `window.kb.convGet()` y renderiza los turnos en orden (pregunta, respuesta, citas con doc/chunkId/linea); al enviar llama a `convAsk` (ignora vacio/espacios, D1) y vuelve a renderizar; el boton llama a `convClear` y vacia la vista. Renderizado sin `innerHTML` con contenido de usuario/documento (usar `textContent`) para evitar inyeccion. Verif: lectura con `grep -n "convGet\|convAsk\|convClear\|Nueva conversacion" renderer/*` y un test (DOM simulado o analisis) si es viable; de lo contrario registrar como verificado solo por lectura/arranque.
- **AC21 (logs).** Una llamada efectiva a `conv:ask` registra `conv.ask` y `conv:clear` registra `conv.clear` con el logger existente (`lib/logger.js`), en JSON por linea con `ts`, `level`, `event`. `conv.ask` incluye al menos numero de turnos y si fue seguimiento (campos extra permitidos); `conv.clear` incluye cuantos turnos se borraron. Los logs no incluyen el texto de documentos completo. Verif: test que ejecuta los handlers con un logger de captura (o inspeccion de `data/app.log` tras ejecutar), y `grep conv.ask data/app.log`.
- **AC22 (errores).** Fallo en `conv:ask` (p. ej. indexador lanza) registra `conv.ask.failed` con `level:error` y propaga el error sin dejar estado a medio guardar.

### Tests

- **AC23 (tests reales).** `test/conversation.test.js` cubre AC2–AC11 y `test/state.test.js` cubre AC13–AC15, mas un test de cableado (AC18/AC19/AC21). Prueba de que fallan sin la implementacion: al mover temporalmente `lib/conversation.js` fuera, `node --test test/conversation.test.js` falla (exit != 0); restaurar despues y comprobar que pasa. Registrar ambas salidas.
- **AC24 (suite).** `npm test` termina con exit 0 y 0 fallos; registrar conteo literal de `pass`/`fail`.

### Arquitectura y dependencias

- **AC25 (arquitectura).** `./scripts/check-architecture.sh` imprime `>> Architecture boundaries OK` y exit 0. Ademas: `lib/*.js` sin `require('electron')`; `renderer/*.js` sin `require(`, `node:`, `process.`; `preload.js` solo requiere `electron`; el renderer no toca el sistema de archivos (solo `window.kb`).
- **AC26 (sin dependencias).** `git diff -- package.json package-lock.json` vacio; no hay `fetch`/`http`/`https`/APIs externas en `lib/conversation.js` ni en el flujo `conv:*` (Q&A local via `lib/cite.js`).

### Documentacion / ayuda

- **AC27 (docs).** `ARCHITECTURE.md` lista `lib/conversation.js`, los canales `conv:get/ask/clear` y la clave `conversation` en `state.json` (max 20) y los logs. `README.md` tiene seccion de conversacion (turnos, tope 20, regla de seguimiento <=2 palabras significativas, boton "Nueva conversacion", logs). Si la app tiene texto de ayuda/placeholder en la UI sobre el panel de preguntas, debe ser coherente con el comportamiento (indicar que preguntas cortas continuan la conversacion).
- **AC28 (informe honesto).** El informe final dice como verificar (`npm test`, `./scripts/check-architecture.sh`, `npm start` manual), lista lo que no se pudo ejecutar (p. ej. GUI de Electron si no hay display), y lo pendiente; no afirma nada no ejecutado. Si existe `.governance/enforcement.yaml`, se ejecuta `python3 ~/.config/opencode/vibe-guard/gate.py --project "$PWD"` y se reporta el exit literal; si no existe, se dice que el proyecto no declara controles.

## 2. Orden de verificacion final

1. `npm test` (AC24) 2. `./scripts/check-architecture.sh` (AC25) 3. `git diff --stat` (AC26, alcance) 4. comprobacion de falla sin implementacion (AC23) 5. `grep` de canales/preload/renderer/logs (AC18–AC21) 6. inspeccion de docs (AC27).

## 3. Fuera de alcance

Ranking/mejoras de `cite.js`, cambios en el indexador, streaming de respuestas, edicion o borrado de turnos individuales, uso de API externa.
