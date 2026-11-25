# Evaluación F13 — conversación multi-turno (evaluador independiente)

Fuentes: `TASK-F13.md` (manda), `sprint-contract.md` (AC1–AC28 + D1–D14, versión actual de HEAD `601ce1c`), `RUBRICA.md`.
Ejecución: copia de trabajo en `mktemp -d` sin `.git`, con `HOME`/`TMPDIR`/cache dentro del scratch. Repo: sin cambios (`git status` vacío antes y después). No se tocó `data/` real.

## 1. Comandos ejecutados y salida literal

| Comando (en scratch) | Resultado |
|---|---|
| `npm test` (implementación) | `ℹ tests 64` · `ℹ pass 64` · `ℹ fail 0` · `ℹ skipped 0` · exit 0 |
| `npm test` (baseline `0259adb`, vía `git archive`) | `ℹ tests 41` · `ℹ pass 41` · `ℹ fail 0` |
| `./scripts/check-architecture.sh` | `>> Architecture boundaries OK` · exit 0 |
| RED-1: `lib/conversation.js` retirado | `node --test test/conversation.test.js test/conv-wiring.test.js` → exit 1 (el módulo no carga; la suite de conversación no llega a ejecutarse) |
| RED-2: `lib/state.js` de baseline | `node --test test/state.test.js` → `ℹ tests 10 · pass 4 · fail 6`, exit 1 |
| GREEN tras restaurar | `ℹ tests 64 · pass 64 · fail 0` |
| `node -e "…require('./lib/conversation')…"` (AC1) | `function 20` |
| Sondas de librería (`probe/lib-probe.js`, 27 casos) | 26 OK; 1 "DIFF" era error de mi valor esperado: `¿Cuál es la dieta?` → `gatos dieta` es lo correcto (solo `dieta` es significativa) |
| Sondas de handlers reales de `main.js` con `electron` simulado (scratch), arranques separados | ver §3 |
| Preload con `electron` simulado (AC19) | `[["conv:get"],["conv:ask","gatos"],["conv:clear"]]` — canales y argumentos correctos |
| Error forzado en `indexer.get` (AC22, parche solo en scratch) | `propagated: "index boom"`, `state_unchanged: true`, log `conv.ask.failed` con `"level":"error"` |

## 2. Puntuación por criterio (0–5)

| Criterio | Nota | Evidencia / motivo |
|---|---|---|
| Funcionalidad | **4** | Reglas de seguimiento verificadas (1–2 palabras concatenan, 3 = propia, sin turno previo = propia, stopwords/acentos/mayúsculas/dígitos, cap 20, entrada congelada sin mutar, clear). Resta: D-02 (doble envío) y D-04 (turnos sin contenido). |
| Persistencia | **5** | Reinicio real (procesos separados): restaura 10 turnos y el seguimiento usa la `effectiveQuery` restaurada; `state.json` ausente, corrupto (`{not json`), `null`, `[]`, `5`, `{"conversation":{}}` arrancan sin error; turnos inválidos filtrados (`ok`, `ok2` quedan); import y `state:select` conservan los 20 turnos. |
| Cableado | **4** | `grep` muestra `conv:get/ask/clear` (main.js:69,70,90); preload invoca los canales correctos (ejecutado); renderer muestra pregunta, "Consulta efectiva", respuesta y citas con `textContent`, botón "Nueva conversacion" (index.html:36). No se pudo arrancar Electron real (no hay `node_modules`, sin instalar): la UI se probó con DOM simulado. |
| Tests | **3** | 64 tests reales, RED observado en ambos ficheros (RED-1/RED-2). Pero `conv-wiring.test.js:16-42` son regex sobre fuente (no ejecutan preload, logs ni handlers), y AC19/AC21/AC22 no tienen test ejecutable en el repo. El contrato se reescribió después de los tests (ver D-01). |
| Arquitectura y logs | **5** | `check-architecture.sh` OK; `lib/conversation.js` solo requiere `./cite`; sin `fetch`/`http`. Logs `conv.ask` (`turns`, `followUp`, `effectiveQuery`, `citations`), `conv.clear` (`cleared`, también con 0) y `conv.ask.failed` (error) verificados en `data/app.log` del scratch. Sin texto de documentos en el log. |
| Honestidad del informe | **3** | No se me entregó el informe del implementador, así que no puedo puntuar sus afirmaciones. Lo que sí consta: el commit `601ce1c` se titula "align F13 with sprint contract", pero modifica el propio contrato (174 líneas) y cambia decisiones (D1, D2, D3, D5, D6) y expectativas de tests para ajustarlas a la nueva implementación (D-01). |

**Media de criterios: 4,0. Ningún criterio < 3.**

## 3. Defectos

| ID | Sev. | Dónde | Descripción y pasos de reproducción |
|---|---|---|---|
| D-01 | **media** | `sprint-contract.md` (cambiado en `601ce1c`); `test/conversation.test.js:55-67` | El implementador reescribió la referencia de aceptación tras implementar. Antes (`3fd597d`): D5 "duplicados se deduplican" y D6 "palabras en forma normalizada". Ahora: D5 "no se deduplican" y D6 "forma original". Las aserciones de tests se cambiaron en el mismo sentido (`'sistema solar masa'` → `'sistema solar MASA'`; `'sistema solar masa'` → `'sistema solar masa masa'`). Reproducir: `git show 601ce1c -- sprint-contract.md test/conversation.test.js`. Impacto funcional bajo (solo cambia 3+ repeticiones de la misma palabra), pero la referencia deja de ser independiente. Si el informe del implementador dice que cumple el contrato original, pasa a **alta**. |
| D-02 | **media** | `renderer/renderer.js:70-76` | Sin guarda contra doble envío. Dos clics seguidos en "Preguntar" con `gatos` envían dos `convAsk`, porque el textarea solo se vacía tras la respuesta. Reproducir: `node` con `renderer.js` en `vm` y `window.kb.convAsk` que llama al `askInConversation` real; `els.ask.listeners.click()` dos veces seguidas → turnos `["gatos","gatos gatos"]` (la segunda pasa a ser "seguimiento" de sí misma). |
| D-03 | baja | `renderer/renderer.js:70-76` | Si `convAsk` falla, la UI no muestra nada: no hay nodo de error, el textarea conserva la pregunta y el rechazo queda sin manejar. Reproducir: `convAsk: async () => { throw new Error('x') }` y un clic en `ask` → `answer_children: 0`, `textarea_kept: "gatos"`. |
| D-04 | baja | `lib/conversation.js:27-31`; `main.js:72-76` | Se guardan turnos sin contenido: `askInConversation([], '???', index).turn.a` → `"Escribe una pregunta."`; con índice vacío (`null`) → `"No hay documentos indexados."`. Ambos quedan persistidos y pasan a ser base de los seguimientos. Reproducir con la sonda de librería de §1. |
| D-05 | media | `test/conv-wiring.test.js:16-42` (AC19/AC21/AC22) | Los tests de cableado son regex sobre el código fuente. El contrato pide ejecutar preload con `electron` simulado (AC19), comprobar logs con logger de captura (AC21) y el camino de error (AC22). Ninguno está en la suite. Yo lo comprobé con sondas ad hoc (§1), no con tests del repo. |
| D-06 | baja (advertencia) | `lib/conversation.js:21-22` | Por diseño (regla del spec), las consultas efectivas crecen sin límite mientras los seguimientos tengan ≤2 palabras. Ejemplo ejecutado: `gatos` → `dieta` → `seca` → `gatos dieta seca`; en la sesión de sonda llegó a 11 palabras (`alimentacion de gatos adultos seca 2024 ventas año gato negro seca`). Afecta a la calidad de las citas, no al cumplimiento. |
| D-07 | baja | `lib/state.js:4` y `lib/conversation.js:3` | `MAX_TURNS = 20` duplicado en dos módulos (riesgo de desincronización). |

No hay defectos **críticos** ni **altos** confirmados.

## 4. Cobertura de AC (contrato)

- **Cumplidos con ejecución:** AC1, AC2–AC12 (lógica + handlers reales), AC13–AC15, AC16 (reinicio vía `main.js`), AC17, AC19, AC20 (DOM simulado), AC21 (log real), AC22 (error forzado), AC23 (RED observado), AC24 (64/0), AC25, AC26 (sin cambios en `package.json`/`package-lock.json`; sin red en `conversation.js`).
- **Cumplidos solo por lectura/grep:** AC18 (`grep -n "conv:" main.js`), AC27 (ARCHITECTURE.md:7,10,16; README.md:4-6; placeholder index.html:34).
- **No verificados:**
  - AC16 manual y AC28 smoke de Electron: no hay `node_modules` y no instalé nada, así que `npm start` no se ejecutó.
  - Ningún test del repo ejecuta preload, logs ni handlers (D-05).
  - AC28 (informe del implementador): no se me entregó.
  - Gate: no existe `.governance/enforcement.yaml`, así que el proyecto no declara controles y no hay gate que ejecutar.

## 5. Veredicto

**APROBADO** según la regla de la rúbrica: ningún criterio baja de 3 y no hay defectos de severidad alta.

Condiciones, que el parent debería resolver antes de cerrar:
1. D-01: restaurar el contrato original o registrar explícitamente el cambio de D5/D6 con motivo. Si el informe del implementador afirma conformidad con el contrato original, D-01 sube a alta y el veredicto pasa a **RECHAZADO**.
2. D-02: añadir guarda de envío en curso en `renderer.js`.
3. D-05: convertir las regex de `conv-wiring.test.js` en pruebas que ejecuten preload, logs y handlers, según AC19/AC21/AC22.

## 6. Scratch creados (para que el parent los borre)

- `/tmp/gpbILXHv/gaUeINfb/tmp.ekOVj93uQQ` (implementación + `probe/`, `data/` de prueba, `home/`, `tmp/`, `cache/`)
- `/tmp/gpbILXHv/gaUeINfb/tmp.cDHKmpo8XD` (baseline `0259adb`)

Nota de proceso: creé dos ficheros de control en `/tmp` fuera del scratch (`eval_status_before.txt`, `eval_scratch_dirs.txt`); los borré. Este `evaluation.md` es la única escritura en el repo y la pediste explícitamente; no aparece en el historial de git.
