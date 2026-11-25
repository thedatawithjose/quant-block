# Stage legacy harness-quant for migration
Objective: stage reusable sources and perform evidence-based cleanup; no Hyperion integration.
Branch/commits: N/A, delivery root is outside Git; preserve nested repository. Checks: hashes, references, isolated Python/Node suites. Forecast: <400 authored lines, unchanged source copies excluded.

## Specs
S1: "Crea `migration-staging/` dentro de `~/Documents/harness-quant/`, separado del código activo."
S2: "Si una pieza está entrelazada con el backtester, conserva el archivo completo en la copia de origen y señala los símbolos precisos que habría que extraer."
S3: "Conserva las pruebas y dependencias necesarias."
S4: "Estas instalaciones externas se consultan y se copian únicamente para preparar la migración."
S5: "**Borra** del directorio de `harness-quant` los archivos generados que hayas confirmado como prescindibles y reproducibles."
S6: "**Archiva** el código y la documentación obsoletos sin referencias activas, conservando su ruta relativa para poder restaurarlos. Una demo con comportamiento único o usada como prueba se conserva."
S7: "Crea `migration-staging/INVENTORY.md` con la ruta original, el destino, los símbolos relevantes, las dependencias y las pruebas asociadas de cada pieza."
S8: "Verifica que las copias existen y que los puntos de entrada activos conservan sus referencias. Indica qué comprobaste por inspección y qué quedó sin verificar en ejecución."

## Tasks
T1 | S1-S4 | inline | done | 30 byte-identical copies, COPY-MANIFEST.json and extraction/contract/Pi boundaries in INVENTORY.md; commit N/A (non-Git root).
T2 | S5-S6 | inline | done | Deleted exactly 3 untracked CPython caches (81,174 bytes), DELETED.json records hashes/sources; Git status unchanged; no proven obsolete archive candidates; commit N/A.
T3 | S7-S8 | gentle-ai-verify (context backstop) + inline documentation | done | Separate verifier: S1-S8 met, 49 Python + 48 Node tests passed, no failures/skips; parent spot check PASS: 30 copies, 22 active hashes, clean Git; verification/RESULTS.md and INTEGRITY.json recorded; commit N/A. Live Pi/API/broker/Hyperion execution unverified and outside scope. Risk: none (unchanged active source; cache-only cleanup).

## Log
L1 — Original request (verbatim):
Trabaja sobre la instalación antigua de **harness-quant** en esta PC. El objetivo de esta tarea es limpiar esa instalación y preparar una copia organizada de las piezas reutilizables para una futura incorporación a **Hyperion**. La integración queda para una tarea posterior.

**Contexto que necesitas.** Hyperion será un harness de propósito general para desarrollo, instalado en un directorio externo a los repositorios. Agentes intercambiables se conectarán a él para trabajar sobre el repositorio indicado. Hyperion fijará el alcance y los controles requeridos por el contrato de cada tarea, asociará las pruebas y la revisión independiente con la versión exacta del cambio y decidirá si la tarea puede cerrarse. El trading cuantitativo será el uso más frecuente y sus reglas se aplicarán mediante un módulo de dominio. Los repositorios no deberán instalar una copia del harness.

### 1. Prepara el material de migración

Crea `migration-staging/` dentro de `~/Documents/harness-quant/`, separado del código activo. Organiza allí las siguientes piezas. Los nombres y rutas vienen de una inspección previa. Si alguna ruta cambió, localiza el símbolo equivalente y registra dónde lo encontraste.

| Destino | Qué debes conservar y para qué |
|---|---|
| `core/` | En `~/Documents/harness-quant/quant_harness_v2/quant_agent_harness.py`, identifica `Store`, las transacciones SQLite, la comprobación de identidad al reabrir, los contadores persistentes y `event`, `verify` y `export_audit`. Interesan para guardar estado, intentos y evidencia. Conserva las pruebas y dependencias necesarias. Si una pieza está entrelazada con el backtester, conserva el archivo completo en la copia de origen y señala los símbolos precisos que habría que extraer. |
| `contracts/` | En `~/Documents/GENTLE-QUANT-ECOSYSTEM/`, copia `agents/TASK-PACKET-CONTRACT-SPEC.md` y `templates/tasks/TASK-PACKET.template.yaml`. Señala los campos aprovechables para objetivo, alcance, checks, aprobación y cierre. Estos archivos sirven como especificación para un futuro contrato ejecutable. |
| `domains/quant/` | Del motor Python conserva `ResearchConfig`, `RunRequest`, `RunResult`, `Backtester`, las validaciones temporales, los controles de costos y la lógica de holdout de un solo uso, junto con sus pruebas. Estas reglas pertenecen al módulo cuantitativo. |
| `adapters/pi/` | En `~/.pi/agent/extensions/quant-gate/`, conserva como referencia la normalización de rutas, las pruebas asociadas y los puntos de integración de `index.ts`. Indica qué herramientas intercepta realmente. Si conservas partes del prompt `~/.pi/agent/prompts/quant-mode.md`, identifica la función específica que cumplen, como activación o recordatorios. |

### 2. Retira lo obsoleto

Revisa los puntos de entrada, imports, pruebas y configuraciones de Pi antes de retirar archivos. Busca duplicados confirmados, demos reemplazadas y archivos generados que puedan regenerarse sin perder evidencia.

- **Borra** del directorio de `harness-quant` los archivos generados que hayas confirmado como prescindibles y reproducibles.
- **Archiva** el código y la documentación obsoletos sin referencias activas, conservando su ruta relativa para poder restaurarlos. Una demo con comportamiento único o usada como prueba se conserva.
- Si algo lo sigue usando Pi, `GENTLE-QUANT-ECOSYSTEM` u otro punto de entrada activo, déjalo en su ubicación y anota la dependencia. Esas instalaciones externas se consultan y se copian únicamente para preparar la migración.
- El bucle específico de Anthropic, las comprobaciones de aprobación basadas en texto y los checkboxes de cierre pueden quedar como referencias del sistema antiguo si siguen en uso. La migración del núcleo aprovechará los mecanismos ejecutables descritos en la tabla.

### 3. Entrega un inventario verificable

Crea `migration-staging/INVENTORY.md` con la ruta original, el destino, los símbolos relevantes, las dependencias y las pruebas asociadas de cada pieza. Registra por separado qué borraste, qué archivaste, qué copiaste y qué quedó bloqueado por una dependencia activa. Verifica que las copias existen y que los puntos de entrada activos conservan sus referencias. Indica qué comprobaste por inspección y qué quedó sin verificar en ejecución.

Cierra con las rutas del material preparado y del inventario. La tarea termina cuando la limpieza y el material de migración están listos.

L2 — Read-only explorer mapped source coupling and external references. Root contains only nested quant_harness_v2 Git repository, clean at inspection. Root itself is not Git; no commits or new Git initialization. No confirmed obsolete code. Existing generated caches confirmed by filesystem listing. No meaningful RED for byte-identical copies/documentation and cache cleanup: use structural integrity and existing functional suites instead.
