# Hyperion-Lab: implementación E2E y checklist de aceptación

Fecha: 18 de noviembre de 2026. Edición: entrega verificable local 1.

Este es el punto de entrada único. Contiene el recorrido ejecutable, el mapa del código, los contratos de los módulos que faltan, su orden de implementación y sus pruebas de aceptación. No hace falta recuperar las conversaciones anteriores ni buscar los informes anteriores para seguirlo.

## 1. Qué se entrega y qué se puede afirmar

**Se entrega código completo del flujo local disponible, un paquete corregido, un verificador por módulo y un laboratorio persistente de 12 pasos. No se entrega todavía un Hyperion integrado con Pi, aislamiento, proveedores de agentes y motor Quant.** Los módulos M09–M16 de este documento son la especificación de implementación pendiente, no componentes que ya existan.

La base inspeccionada fue `hyperion-revision.zip`, SHA-256 `f7fef6777748aa3898ffc4df67bce715435a83fa0a0702ac35328c5535ee9eae`. Ese ZIP contenía seis archivos, colocaba `local_flow.py` en la raíz y omitía `LOCAL-FLOW.md` y `SOURCE-HASHES.json`, aunque su informe los mencionaba. El ejemplo esperaba estar en `examples/` y falló al ejecutarlo desde el ZIP extraído. Aquí se restaura esa ubicación, se etiqueta la revisión del ejemplo como simulación y se entrega este manual y un manifiesto nuevo. Los cuatro archivos del motor y sus pruebas originales se conservan sin cambios; la corrección está en el empaquetado y las herramientas de validación agregadas.

Los informes históricos de migración indican 49 pruebas Python y 48 pruebas Pi. **Esas 97 pruebas no se incluyen ni se vuelven a ejecutar en esta entrega**: sus fuentes no estaban dentro del ZIP. No se suman a los resultados nuevos. La suite local disponible tiene 57 pruebas: 15 externas y 42 legacy.

Regla de aceptación: un módulo se marca aceptado cuando su evidencia existe y tú has revisado qué demuestra. Un `PASS` técnico no prueba funcionalidades fuera del alcance del caso. Una casilla marcada en este manual no cambia la autoridad del programa.

## 2. Mapa completo y orden de trabajo

| ID | Responsabilidad | Estado en esta entrega | Dependencias |
|---|---|---|---|
| M00 | Paquete, herramientas y manifiesto | Ejecutable | Python y Git |
| M01 | Contrato congelado | Ejecutable; autoridad local de confianza | M00 |
| M02 | Repositorio, base y candidato exacto | Ejecutable | M01 |
| M03 | Alcance del cambio | Ejecutable; evaluación posterior | M02 |
| M04 | Aceptación externa sobre snapshot | Ejecutable; sin sandbox | M01–M03 |
| M05 | Revisión de entrega | Ejecutable; identidad declarada | M02, M04 |
| M06 | Cierre e invalidación de evidencia | Ejecutable para el flujo externo | M01–M05 |
| M07 | Compatibilidad con flujo legacy | Ejecutable; conserva garantías antiguas | M00 |
| M08 | Demostración E2E y reproducción | Ejecutable; revisiones simuladas | M00–M07 |
| M09 | Store transaccional, auditoría y recuperación | Pendiente | M01, M02, M06 |
| M10 | Contrato v2, plan y autoridad verificable | Pendiente | M09 |
| M11 | Runner aislado y control de capacidades | Pendiente | M09, M10 |
| M12 | Agentes, orquestación y presupuestos | Pendiente | M09–M11 |
| M13 | Integración real de Pi | Pendiente | M10–M12 |
| M14 | Dominio Quant integrado | Pendiente | M09–M12 |
| M15 | Cierre v2, evidencia y revisión autenticada | Pendiente | M09–M12; M13/M14 según tarea |
| M16 | Entrega, CI, recuperación y aceptación final | Pendiente para el sistema integrado | M13–M15 |

Se pueden implementar M13 y M14 en cualquier orden después de M12. Para declarar completo el alcance que incluye ambos, los dos tienen que pasar. No agregar más capas de prompts como sustituto de estos módulos.

## 3. Arranque único del paquete

Entorno de referencia de esta revisión: Linux, Python 3.12.14, Git 2.52.0. No hay dependencias Python de terceros para este recorrido. No se probó Windows ni se certificó una matriz de otras versiones. Se necesita `git` y un shell POSIX para algunas pruebas legacy. No hace falta configurar nombre o correo global de Git: los fixtures los configuran localmente.

Extrae el ZIP en una carpeta nueva y abre una terminal **dentro de `hyperion-e2e/`**. Todos los comandos relativos de esta guía parten de esa carpeta.

```bash
python3 -V
git --version
python3 -B verificar.py --modulo M00
python3 -B verificar.py --modulo todos
```

Resultado esperado del último comando: `PASS M00` hasta `PASS M08`, salida del verificador `0`, `automated_tests_run: 57` y `passed: true` en el `resultado.json` indicado en pantalla. M08 agrega dos recorridos E2E y dos controles del laboratorio; no se contabiliza como 57 pruebas adicionales.

El verificador crea una carpeta nueva en `validaciones/` para cada ejecución y guarda stdout, stderr, comandos, códigos y resultados. Detiene la secuencia ante el primer módulo fallido. Puedes dar `--salida /ruta/nueva` para elegir dónde conservarla. Esa ruta debe no existir. No uses `python -O`: el ejemplo y parte de la aceptación usan `assert` y la optimización puede desactivarlos.

**Si falla:** conserva esa carpeta, revisa el `.stderr.txt` del módulo, corrige el problema y ejecuta de nuevo en otra carpeta de resultados. No edites la evidencia fallida ni marques el módulo como aprobado por haber pasado otro. Un cambio de fuente invalida el manifiesto: no lo regeneres únicamente para esconder una divergencia; registra y revisa la modificación.

Los archivos `evidence/` del paquete son evidencia de esta entrega. Los resultados que generes tú irán a `validaciones/`; no sobrescriben los anteriores.

## 4. Módulos existentes, uno por uno

### M00 — Paquete e integridad

**Archivos:** `hyperion.py`, `external_flow.py`, `test_hyperion.py`, `test_external_flow.py`, `examples/local_flow.py`, `paso_a_paso.py`, `verificar.py`, este manual y `MANIFEST.json`.

**Implementación:** `verificar.integrity()` compara SHA-256 de todos los archivos listados. Los registros de ejecución se identifican por separado; el manifiesto no se incluye a sí mismo.

**Ejecuta:** `python3 -B verificar.py --modulo M00`.

- [ ] La verificación no encuentra archivos ausentes ni hashes diferentes.
- [ ] `examples/local_flow.py` existe en esa ruta.
- [ ] El paquete se puede ejecutar después de extraerlo en otra carpeta.
- [ ] Entiendo que un manifiesto local detecta diferencias accidentales, no autentica al autor frente a alguien capaz de reemplazarlo todo.

**Rechazo:** archivo faltante o diferente → no avanzar. La existencia de `RESULTS.md` antiguo no sustituye esta verificación.

### M01 — Contrato congelado

**Código:** `external_flow.freeze`, `contract_hash`, `load`, `outside`, `exact_path`; entrada `hyperion.py … freeze`.

**Entrada:** repositorio explícito, base Git, identificador y versión de tarea, objetivo, lista de archivos autorizados, aceptación externa e ID de aceptación. `--allow` acepta archivos exactos relativos, no patrones.

**Salida:** `task.json` como marcador y `task.json.d/` con `contract.json`, copia de `acceptance.py`, `deliveries.json` y `evidence.json`. Los padres del archivo de tarea deben existir. El estado y la aceptación deben estar fuera del repositorio canónico.

**Algoritmo actual:** resuelve repositorio/base; valida entradas; copia aceptación; calcula su hash; calcula hash canónico del contrato; reserva la carpeta y escribe archivos. `load` vuelve a comprobar el contrato, la aceptación y el repositorio. Cambiar el original de aceptación después de `freeze` no cambia la copia congelada.

**Ejecuta:** `python3 -B verificar.py --modulo M01` → 5 pruebas.

- [ ] Rechaza contrato incompleto, rutas con traversal y patrones.
- [ ] Rechaza estado o aceptación dentro del repositorio, también por alias de ruta.
- [ ] No permite sobrescribir una tarea congelada.
- [ ] Una modificación de la copia de aceptación se detecta.
- [ ] Los comandos legacy no reemplazan el contrato externo.

**Límite:** el hash no es firma ni aprobación de un plan. Las escrituras son atómicas por archivo; todavía no forman una transacción común. Si `freeze` queda a medias, la carpeta queda reservada. Conservarla para inspección y usar otro ID/ruta; no borrarla automáticamente para fingir que el intento no existió.

### M02 — Identidad del repositorio y candidato

**Código:** `repository`, `resolve`, `deliver`, `snapshot`, `binding` en `external_flow.py`.

**Entrada:** referencia Git y ejecutor. **Salida:** entrega con UUID nuevo, raíz canónica y common Git dir, base, commit y tree, ejecutor, archivos cambiados y no autorizados.

**Binding obligatorio actual:** `delivery_id`, `contract_hash`, `repository`, `base_commit`, `commit`, `tree`. Aceptación y revisión tienen que coincidir en todos estos campos con la entrega vigente.

**Algoritmo:** resolver la referencia a un commit y tree concretos; calcular diferencia neta base→candidato; registrar entrega. Para validar, copiar blobs Git de ese candidato a un directorio temporal. Un `HEAD` que se mueve o un working tree sucio no cambia la entrega ya registrada. Cada nueva entrega, incluso del mismo commit, recibe otro UUID.

**Ejecuta:** `python3 -B verificar.py --modulo M02` → 2 pruebas.

- [ ] Rechaza referencias desconocidas, con aspecto de opción y objetos que no son commits.
- [ ] Rechaza ejecutor vacío.
- [ ] Validar usa el commit entregado, no el working tree actual.
- [ ] Se conservan commit y tree concretos en la evidencia.

**Límites:** no requiere que el candidato descienda de la base; compara árboles. No incorpora cambios sin commit ni hace fetch. La identidad de ruta no es identidad global autenticada. Snapshots sólo admiten archivos regulares; symlinks y submódulos no están soportados. Deben conservarse los objetos Git para poder reproducir la validación.

### M03 — Alcance del diff

**Código:** `scope` y prioridad de `status` en `external_flow.py`.

**Regla:** `git diff` compara base y candidato con renombres desactivados. Una renombración se observa como baja y alta; ambos nombres deben estar autorizados. El cierre queda en `BLOCKED_SCOPE` si cualquier archivo del cambio neto está fuera de `authorized_paths`.

**Ejecuta:** `python3 -B verificar.py --modulo M03` → 3 pruebas.

- [ ] Un cambio en README fuera de alcance bloquea aunque la aceptación pase.
- [ ] Una renombración evalúa ruta de origen y destino.
- [ ] Una eliminación no autorizada bloquea.
- [ ] Una aprobación no anula ese bloqueo.

**Límite exacto:** inspecciona el diff final base→candidato. No es vigilancia de todas las acciones ni de cambios intermedios posteriormente revertidos. Tampoco impide que un proceso escriba fuera del repositorio. La detección de alcance ocurre en el flujo de entrega/cierre; no es una frontera de ejecución.

### M04 — Aceptación sobre snapshot

**Código:** `validate` y `snapshot` en `external_flow.py`.

**Entrada:** entrega actual y timeout, finito, mayor que 0 y máximo 30 segundos. **Salida:** registro `kind=acceptance`, binding, identidad/hash de aceptación, exit code, stdout, stderr y `timed_out`.

**Algoritmo:** verificar identidad del candidato; construir snapshot; ejecutar la aceptación congelada con Python `-I -B`, cwd en el snapshot; registrar resultado; volver a verificar el hash de aceptación. El fixture importa explícitamente el archivo del snapshot mediante `runpy`, porque el modo aislado de Python no agrega automáticamente ese cwd al import path.

**Ejecuta:** `python3 -B verificar.py --modulo M04` → 2 pruebas.

- [ ] El defecto original falla por `whitespace must be empty`, no por un error de preparación.
- [ ] La corrección satisface espacios y `Hello World`.
- [ ] Sin revisión, una aceptación exitosa conserva `PENDING_VALIDATION`.
- [ ] Un timeout se registra como fallo ligado a esa entrega.

**Distinción esencial:** el comando `validate` puede devolver código de proceso `0` porque logró registrar una aceptación fallida. Para aprobar, inspecciona el JSON: `state`, `acceptance.exit_code` y `timed_out`. No uses únicamente `$?` del CLI.

**Límite:** `-I` es aislamiento del entorno de importación de Python; no restringe permisos del sistema, red, memoria ni descendientes hostiles. La aceptación y el código probado se ejecutan con privilegios del usuario. Sólo usar esta versión con código de confianza. El código actual puede ejecutar la aceptación aun cuando el diff ya esté fuera de alcance; M11 debe impedir ejecutar candidatos inadmisibles en el modo reforzado.

### M05 — Revisión de entrega

**Código:** `review` en `external_flow.py`.

**Entrada:** UUID explícito, revisor, `approve` o `changes_requested`, motivo. **Salida:** registro de revisión con el binding de esa entrega. Se permite conservar revisiones históricas; no tienen efecto sobre una entrega diferente.

**Ejecuta:** `python3 -B verificar.py --modulo M05` → 1 prueba con múltiples rechazos.

- [ ] Ejecutar y revisar con el mismo identificador se rechaza, incluso con espacios alrededor.
- [ ] Revisor o motivo vacíos se rechazan.
- [ ] Una entrega inexistente se rechaza.
- [ ] Los rechazos probados no modifican archivos persistidos.

**Límite:** dos cadenas diferentes no prueban que participaron dos personas o procesos independientes. No hay autenticación. El laboratorio usa `ejecutor-simulado` y `revisor-simulado`, explícitamente ficticios. Un comando de aprobación registra una decisión; no realiza por sí solo una revisión de código.

### M06 — Cierre determinista e invalidación

**Código:** `status`, `BINDING` y registro de entregas en `external_flow.py`.

`status` deriva el veredicto de los JSON; no existe una transición terminal irrevocable almacenada como evento transaccional en esta versión.

| Condición actual, en orden de prioridad | Estado |
|---|---|
| Entrega con rutas no autorizadas | `BLOCKED_SCOPE` |
| Última aceptación coincidente falla o vence; o última revisión coincidente pide cambios | `NEEDS_CORRECTION` |
| Aceptación coincidente exitosa y revisión coincidente aprobada por ID distinto | `DONE` |
| Falta cualquier evidencia necesaria o todavía no hay entrega | `PENDING_VALIDATION` |

**Ejecuta:** `python3 -B verificar.py --modulo M06` → 1 prueba de secuencia.

- [ ] La falta de evidencia no puede producir `DONE`.
- [ ] Una petición de cambios impide el cierre.
- [ ] Una nueva entrega del mismo commit invalida la evidencia anterior para el cierre actual.
- [ ] Aprobar el UUID antiguo no aprueba el nuevo.
- [ ] La nueva entrega requiere su aceptación y revisión actuales.

**Límite:** gana el último registro coincidente de cada tipo. Una nueva revisión puede sustituir una petición de cambios anterior incluso sin nuevo commit; el programa no exige justificar cómo se resolvió cada hallazgo. Tampoco vincula hoy la aprobación al ID exacto del intento de aceptación. M15 debe resolver esas dos condiciones.

### M07 — Compatibilidad legacy

**Código:** clases de `hyperion.py`, comandos `init`, `propose`, `submit`, `status`; barrera `reject_legacy` para tareas externas.

**Ejecuta:** `python3 -B verificar.py --modulo M07` → 43 pruebas: 42 legacy y 1 de compatibilidad externa.

- [ ] Estados, gobernanza, parser, persistencia y CLI anteriores siguen pasando.
- [ ] Una tarea externa no se reemplaza mediante el flujo legacy.
- [ ] La salida y los significados de los dos modos se distinguen.

**Límite:** el `DONE` legacy se basa en su mecanismo anterior de criterios/evidencia narrativa. No adquiere automáticamente la verificación de snapshots del flujo externo. El `CLIAgent` legacy tampoco es un adaptador conectado a toda la cadena externa. No usar sus pruebas para afirmar que ya existe orquestación reforzada.

### M08 — E2E reproducible

**Código:** `examples/local_flow.py`, `paso_a_paso.py`, grupo M08 en `verificar.py`.

**Ejecuta:** `python3 -B verificar.py --modulo M08`.

- [ ] Pasa el ejemplo desde su ubicación corregida.
- [ ] Pasan los 12 pasos persistentes de la siguiente sección.
- [ ] Un intento de sobrescribir el laboratorio se rechaza.
- [ ] Un paso fuera de orden se rechaza.
- [ ] Los registros identifican todas las revisiones automáticas como simuladas.

El grupo crea un repositorio ficticio dentro de su carpeta de resultados. No instala nada en tus repositorios ni integra Pi. Cada invocación del CLI es un proceso separado; la prueba de reapertura comprueba lectura del estado entre procesos, no tolerancia a cortes durante una escritura.

## 5. Laboratorio: checklist paso a paso sin depender del chat

Elige una carpeta **nueva**. Por ejemplo, desde la raíz del paquete:

```bash
python3 -B paso_a_paso.py --directorio ../hyperion-laboratorio-01 --paso 1
```

Para cada fila siguiente ejecuta el mismo comando cambiando solamente el número de `--paso`. Se exige el orden 1→12. Abre `../hyperion-laboratorio-01/paso-NN.json` después de cada paso: contiene el resultado completo y cada comando con stdout, stderr y exit code. El manifiesto `laboratorio.json` registra el último paso terminado.

| Marca | Paso | Acción automática del fixture | Resultado que debes comprobar |
|---|---:|---|---|
| ☐ | 1 | Crea repo defectuoso, aceptación externa y contrato | `PENDING_VALIDATION`; `delivery=null` |
| ☐ | 2 | Entrega base y ejecuta aceptación | `NEEDS_CORRECTION`; stderr contiene la aserción de espacios |
| ☐ | 3 | Corrige, hace commit y entrega | `PENDING_VALIDATION`; nuevo `delivery_id` |
| ☐ | 4 | Ejecuta aceptación corregida | exit code de aceptación 0; revisión ausente; pendiente |
| ☐ | 5 | Intenta autorrevisión | CLI rechaza con código 1; hashes del estado no cambian |
| ☐ | 6 | Simula revisión que pide cambios | `NEEDS_CORRECTION` |
| ☐ | 7 | Simula aprobación vigente | `DONE` para esa entrega |
| ☐ | 8 | Entrega otra vez el mismo commit | UUID diferente; aceptación/revisión actuales vacías |
| ☐ | 9 | Valida nueva entrega y aprueba la anterior | Sigue `PENDING_VALIDATION` |
| ☐ | 10 | Aprueba la nueva entrega | `DONE` |
| ☐ | 11 | Cambia README sin autorización; valida y aprueba | Aceptación pasa, pero `BLOCKED_SCOPE` |
| ☐ | 12 | Consulta desde otro proceso | Sigue bloqueado; bindings de evidencia coinciden |

Consultar avance:

```bash
python3 -B paso_a_paso.py --directorio ../hyperion-laboratorio-01 --estado
```

Ejecutar todos los pasos de una vez en otro directorio nuevo:

```bash
python3 -B paso_a_paso.py --directorio ../hyperion-laboratorio-02 --todo
```

**Si un paso falla:** queda `paso-NN-FALLO.json` si el fallo ocurrió dentro de la ejecución del paso. Un error previo de argumentos/orden se comunica por stderr. No avances. Conserva los archivos, corrige la causa y empieza en otra carpeta; no se promete rollback de todo el fixture tras un fallo parcial.

**Por qué termina en `BLOCKED_SCOPE`:** el último caso es una prueba negativa deliberada. El laboratorio aprueba si detecta ese bloqueo. `PASS` del laboratorio y `DONE` de una tarea son cosas diferentes.

**Qué inspeccionar en un `DONE`:** `contract_hash`; UUID de entrega; commit/tree; paths no autorizados vacíos; aceptación con código 0 y sin timeout; revisión aprobada con revisor distinto; igualdad de los seis campos de binding. Eso comprueba el mecanismo local, no la calidad de una revisión humana que aquí no ocurrió.

## 6. Usar el CLI con una tarea real de confianza

Esta sección describe operaciones reales; no contiene una aprobación automática. No las ejecutes sobre un repositorio importante como parte del laboratorio.

1. Selecciona base y objetivo, escribe una aceptación que falle por el defecto y defina el resultado correcto.
2. Coloca aceptación y estado fuera del repositorio. Crea previamente la carpeta padre del estado.
3. Congela el contrato antes de implementar. Revisa alcance y aceptación.
4. Implementa y crea un commit candidato. Una edición sin commit no se entrega.
5. Entrega y valida. Inspecciona el JSON, incluyendo estado y resultado interno.
6. El revisor real inspecciona diff y evidencia del UUID concreto y registra su decisión.
7. Consulta estado. Si hay otro cambio, crea otra entrega y valida/revisa de nuevo.

Plantilla de comandos; sustituye las rutas, IDs y referencias entre `<…>` por valores reales. **No pegues los placeholders sin sustituirlos.** `--task-file` va antes del subcomando.

```bash
python3 -B hyperion.py --task-file '<estado-externo>/task.json' freeze \
  --repo '<repo>' --base '<commit-base>' \
  --task-id '<id>' --task-version '1' --objective '<objetivo>' \
  --allow 'src/archivo.py' 'tests/test_archivo.py' \
  --acceptance '<aceptacion-externa>/acceptance.py' --acceptance-id '<id-aceptacion>'

python3 -B hyperion.py --task-file '<estado-externo>/task.json' deliver \
  --commit '<commit-candidato>' --executor '<ejecutor>'

python3 -B hyperion.py --task-file '<estado-externo>/task.json' validate --timeout 10

python3 -B hyperion.py --task-file '<estado-externo>/task.json' status
```

Sólo después de una revisión real, el revisor usa el UUID obtenido de `delivery.delivery_id`:

```bash
python3 -B hyperion.py --task-file '<estado-externo>/task.json' review \
  --delivery-id '<UUID-exacto>' --reviewer '<revisor-real>' \
  --decision approve --rationale '<que-se-reviso-y-por-que-se-acepta>'
```

Para pedir cambios, usar `--decision changes_requested`. No editar directamente `evidence.json`, `deliveries.json` ni el contrato. No cambiar la aceptación para que un candidato defectuoso pase: un objetivo/alcance/oráculo diferente exige un contrato nuevo y trazabilidad hacia el anterior.

## 7. Implementación restante: contratos concretos por módulo

**Todo lo que sigue es diseño pendiente.** Las rutas, interfaces, códigos y pruebas M09–M16 son objetivos de implementación, no comandos disponibles en este ZIP. El alcance completo no se puede aprobar con los nueve `PASS` de M00–M08.

Decisiones de diseño para evitar bifurcaciones: núcleo Python; persistencia SQLite; CLI externa como entrada de referencia; Pi como adaptador; Quant como dominio; agentes como productores de propuestas/artefactos. El evaluador de cierre es una función de evidencia verificada, no una respuesta del modelo.

### M09 — Store transaccional, auditoría y recuperación

**Archivos a crear:** `hyperion_core/store.py`, `hyperion_core/events.py`, `hyperion_core/migrations.py`, `tests/test_store.py`.

**Interfaz prevista:** `create_run(contract)`, `append_delivery(run_id, binding)`, `reserve_attempt(run_id, kind, request_id)`, `finish_attempt(attempt_id, result)`, `transition(run_id, expected_revision, event)`, `export_run(run_id)`, `verify_run(run_id)`.

**Modelo mínimo:** tablas `runs`, `contracts`, `deliveries`, `attempts`, `evidence`, `reviews`, `events`. Claves foráneas activadas; IDs únicos; `events` con secuencia, hash anterior y hash del evento; `runs.revision` para concurrencia optimista; `attempts.request_id` único para idempotencia. Evidencia con payload/hash y referencias a contrato, entrega e intento. Configuración del runner y su identidad también persistidas.

**Implementación en orden:**

1. Crear esquema versionado y migración explícita; rechazar una versión desconocida.
2. Unir actualización de estado, contadores y evento en la misma transacción. Usar el bloqueo de escritura de SQLite y control de revisión; no confiar sólo en mutex de proceso.
3. Reservar intento y presupuesto antes del efecto externo; confirmar transacción antes de lanzar proceso.
4. Finalizar intento en otra transacción; si hay caída entre lanzamiento y resultado, registrar estado incierto/interrumpido, nunca inventar éxito.
5. Recuperar al reiniciar sin repetir operaciones con efectos automáticamente. Idempotencia con recibos del backend para resolver operaciones ambiguas.
6. Exportar contrato, evidencia, eventos, versión y hashes; registrar política de retención y backup.
7. Importar JSON v1 sólo mediante importador explícito, preservando origen y hashes. Las revisiones v1 quedan clasificadas como identidad no autenticada; no promoverlas a aprobación v2.

**Checks de aceptación previstos:**

- [ ] M09-A: dos procesos consumen el último presupuesto disponible; exactamente uno obtiene la reserva.
- [ ] M09-B: caída después de reservar y antes de completar → reapertura conserva el consumo y marca interrupción.
- [ ] M09-C: fallo al registrar evento obligatorio → transacción revierte y no se lanza la operación.
- [ ] M09-D: repetir `request_id` no duplica intento, evidencia ni consumo.
- [ ] M09-E: alteración interna de evento se detecta; exportación y restauración conservan enlaces.
- [ ] M09-F: conflicto de revisión no pierde escrituras; devuelve error explícito.

**Bloqueo:** sin persistencia consistente no se continúa a ejecución. **Límite:** cadena hash local no prueba ausencia de truncamiento final ni protege frente al propietario que reconstruye todo. Para esa garantía se necesita anclaje externo o firma bajo autoridad separada; declarar su ausencia si no se implementa.

### M10 — Contrato v2, plan y autoridad

**Archivos:** `hyperion_core/contracts.py`, `hyperion_core/authority.py`, `schemas/task-v2.json`, `tests/test_contracts.py`.

**Contrato a validar:** `schema_version`, `task_id`, `task_version`, `domain`, `objective`, `completion_criteria`, `repository`, `base_commit`, `allowed_paths`, `prohibited_paths`, `authoritative_inputs` con hashes, `plan_hash`, `required_checks`, `review_policy`, `capabilities`, `budgets`, `runtime_digest`, `approval_policy` y `supersedes` cuando aplica.

Cada `completion_criterion` tiene ID y checks que lo demuestran. Cada check tiene ID, definición/hash, comando como vector de argumentos, entorno permitido, timeout, recursos, tipo de evidencia y condición de éxito. No admitir criterios sin cobertura; los casos no aplicables requieren justificación autorizada antes de ejecutar. Una lista vacía de checks no permite cierre por defecto.

**Aprobación prevista:** recibo emitido por autoridad externa al agente: `approval_id`, sujeto autenticado, `contract_hash`, `plan_hash`, capacidades concedidas, fecha, expiración/revocación y firma/recibo verificable. Un booleano en Markdown o un nombre escrito por el agente no autentica nada. Las capacidades de lectura, escritura, ejecución, red y publicación se representan por separado.

**Implementación:** validar tipos y semántica; congelar inputs; resolver conflictos de alcance; verificar autorización correspondiente; persistir revisión inmutable. Editar plan/contrato crea otra revisión e invalida las aprobaciones y evidencia afectadas. Contenido recuperado y archivos del repositorio son datos; no pueden conceder capacidades.

**Checks previstos:**

- [ ] M10-A: un `human_approved: true` dentro de un ejemplo no concede permiso.
- [ ] M10-B: cambiar un byte del plan/contrato invalida el recibo anterior.
- [ ] M10-C: identidad no autenticada, permiso expirado/revocado o capacidad ausente bloquean la operación correspondiente.
- [ ] M10-D: criterio sin check o check desconocido se rechaza antes de crear efectos.
- [ ] M10-E: un documento recuperado que ordena ampliar permisos no cambia la política.
- [ ] M10-F: objetivo, inputs y decisiones vigentes se reconstruyen tras reinicio.

**Salida:** `ValidatedContract` inmutable y recibos de autoridad. **Fallo:** `BLOCKED_CONTRACT` o `BLOCKED_AUTHORITY`, con causas verificables, sin ejecutar el agente.

### M11 — Frontera real de herramientas y runner

**Archivos:** `hyperion_core/runner.py`, `hyperion_core/capabilities.py`, `adapters/sandbox/`, `tests/test_runner_boundary.py`.

**Interfaz:** `Runner.execute(ExecutionRequest) -> ExecutionReceipt`. Request incluye contrato, entrega, check/intento, argv, cwd lógico, inputs, capabilities y límites. Receipt incluye backend/imagen, hash de inputs, tiempos, exit/signal/timeout, límites efectivos, logs y hash de outputs.

**Implementación:**

1. Elegir y documentar un backend de aislamiento Linux real. No sustituirlo por análisis de cadenas de shell. El backend debe demostrar las restricciones prometidas antes de habilitarse.
2. El supervisor y Store quedan fuera del alcance del candidato. Snapshot de entrada inmutable; directorios de salida explícitos; sin montar directorios personales ni credenciales del host.
3. Denegar red por defecto salvo capacidad concreta; limitar procesos, memoria, CPU, tiempo, disco y stdout/stderr.
4. Toda herramienta ejecutora, shell, herramienta alternativa, proceso en background o agente hijo atraviesa ese supervisor; una vía no mediada bloquea el modo reforzado.
5. Verificar alcance antes de ejecutar y capturar outputs después. Una allowlist de paths complementa, pero no reemplaza, la frontera de permisos.
6. Matar y recoger todo el grupo/entorno de ejecución al vencer el plazo. Registrar truncamiento de logs y agotamiento de recursos explícitamente.
7. Preferir no montar symlinks/submódulos en v1; si se agregan, diseñar su resolución y pruebas específicas antes de declararlos soportados.

**Checks previstos, con canarios y destinos de prueba:**

- [ ] M11-A: escritura por path traversal, symlink o ruta absoluta fuera de salida no afecta el canario externo.
- [ ] M11-B: script, shell, herramienta alternativa y background reciben la misma restricción.
- [ ] M11-C: candidato no puede modificar aceptación, Store, contrato ni código del supervisor.
- [ ] M11-D: timeout elimina descendientes; no quedan procesos escribiendo después de finalizar.
- [ ] M11-E: red denegada realmente; límite de memoria, disco y output se observa en pruebas de carga acotadas.
- [ ] M11-F: fallo del backend impide ejecutar; no existe fallback silencioso a ejecución host.

**Fallo:** `BLOCKED_RUNNER` antes de efectos o `FAILED_RESOURCE_LIMIT` después del intento; jamás `DONE`. La identidad de imagen y configuración probadas debe entrar en el binding de evidencia.

### M12 — Agentes, orquestación y presupuestos

**Archivos:** `hyperion_core/orchestrator.py`, `hyperion_core/budgets.py`, `hyperion_core/agent_protocol.py`, `adapters/agents/`, `tests/test_orchestration.py`.

**Interfaz de agente:** `execute(TaskContext, ToolGateway) -> AgentResult`. Resultado estructurado: `completed`, `partial`, `blocked` o `failed`, artefactos propuestos, resumen, dudas y llamadas contabilizadas. `completed` significa que el agente terminó su parte; no determina `DONE`.

**Implementación:**

1. Construir contexto desde contrato congelado, eventos, candidatos y fallos vigentes. No depender de la memoria del chat.
2. Usar un adaptador determinista de prueba y un adaptador de proveedor/CLI explícito, ambos con el mismo protocolo y el mismo gateway.
3. Reservar presupuestos persistentes antes de cada llamada, check y ciclo de corrección. Límites separados para llamadas, tiempo total, herramientas, correcciones y revisiones.
4. Ejecutar en workspace acotado; obtener artefactos; materializar candidato; resolver commit/tree; evaluar alcance y checks por el runner.
5. Si falla, devolver fallos concretos al agente con presupuesto restante. Nueva edición → nueva entrega → evidencia nueva.
6. La última etapa sólo invoca M15; ninguna cadena emitida por el modelo puede saltarla.
7. Cancelación conserva evidencia e intentos gastados; reanudación exige la misma identidad o revisión explícita de contrato.

**Checks previstos:**

- [ ] M12-A: dos adaptadores producen el mismo comportamiento de cierre para el mismo fixture.
- [ ] M12-B: respuesta `completed` sin evidencia permanece pendiente.
- [ ] M12-C: JSON inválido, proveedor caído, timeout o resultado parcial no producen cierre.
- [ ] M12-D: agotar correcciones → `BLOCKED_BUDGET`; reiniciar no repone presupuesto.
- [ ] M12-E: nueva edición invalida toda evidencia afectada, también la revisión.
- [ ] M12-F: agente hijo no recibe capacidades mayores que su padre; ninguna herramienta accede directamente al Store.

**Salida:** candidatos y eventos; el cierre sigue perteneciendo al evaluador. No se exige crear múltiples agentes para tareas que no lo necesitan.

### M13 — Adaptador Pi vivo

**Archivos:** `adapters/pi/index.ts`, `adapters/pi/protocol.ts`, `adapters/pi/healthcheck.ts`, pruebas del adaptador y un escenario de integración en Pi.

**Implementación:** conectar hooks al gateway; handshake con versión de protocolo, run ID y capacidades; probar registro real en la instancia usada; traducir eventos sin duplicar políticas. La activación inicia o adjunta una ejecución del núcleo. Los recordatorios de checklist quedan como ayuda visual.

No reutilizar sin más los huecos del `quant-gate` histórico: comparación de nombre exacto `bash`, sólo ciertas herramientas write/edit, modo desactivable o política faltante no equivalen a cobertura total. El núcleo debe rechazar la operación no mediada aunque el adaptador olvide bloquearla.

**Checks previstos:**

- [ ] M13-A: se observa un hook real registrado y una llamada real que atraviesa el gateway.
- [ ] M13-B: política ausente/inválida o handshake fallido impide arrancar modo reforzado.
- [ ] M13-C: `QUANT_GATE=off` o un comando de desactivación no concede permisos sobre una ejecución reforzada existente.
- [ ] M13-D: write/edit, shell, background, herramientas alternativas e hijos conservan los mismos límites.
- [ ] M13-E: recargar Pi reconstruye run ID/estado desde el núcleo sin resetear presupuesto.
- [ ] M13-F: marcar checkboxes o terminar el turno no produce `DONE` sin M15.

**Evidencia exigida:** log de sesión real, versiones, llamadas/recibos y veredictos. Las pruebas unitarias de TypeScript y la presencia de archivos no sustituyen esta sesión.

### M14 — Dominio Quant

**Archivos:** `domains/quant/contracts.py`, `research.py`, `metrics.py`, `causality.py`, `adapters.py`, `tests/quant/`.

**Entrada necesaria antes de implementar:** fuente exacta del motor legacy y sus pruebas, identificadas por hash/commit; datasets autorizados y sus versiones; motor de backtest y contrato de costes. El inventario histórico identifica piezas, pero este ZIP no contiene esas fuentes. No recrearlas de memoria ni afirmar que fueron migradas por leer el inventario.

**Interfaz:** `DomainPlugin.validate_contract`, `required_checks`, `validate_result`; `Backtester.run(RunRequest) -> RunResult`. Request liga dataset/hash, engine/hash, seed, ventanas UTC, parámetros, costes y semántica temporal. Result liga request, retornos netos, operaciones terminadas y procedencia.

**Implementación:**

1. Extraer persistencia común una sola vez a M09 y mantener aritmética/reglas Quant en el dominio; evitar dos núcleos duplicados.
2. Validar ventanas con fin exclusivo, barras cerradas, orden y ausencia de solapes; política explícita de decisión y ejecución en evento posterior.
3. Ejecutar causalidad con prefijos y mutación de presente/futuro, determinismo y regresiones numéricas.
4. Reejecutar el motor con costes mayores para estrés; no restar una penalización artificial a una métrica ya calculada.
5. Exigir candidato investigado; comprometer holdout y presupuesto en Store antes del cálculo. Error o caída no habilitan otro uso encubierto.
6. Vincular un experimento/holdout a una identidad estable de investigación; crear otra tarea o cambiar UUID no debe permitir reutilizar la misma reserva del protocolo.
7. `FINALIZED` describe investigación terminada. El cierre de tarea sigue exigiendo evidencias y revisión de M15.
8. Mantener ejecución de órdenes/broker fuera de este alcance. Incorporarla sería otro contrato y autorización explícita.

**Checks previstos:**

- [ ] M14-A: preservar y ejecutar la suite legacy sobre fuente exacta disponible; informar número observado, no asumirlo.
- [ ] M14-B: un adaptador causal pasa y uno con fuga temporal falla por el criterio correcto.
- [ ] M14-C: costes afectan ejecuciones/resultados conforme al contrato; procedencia o resultados no finitos se rechazan.
- [ ] M14-D: dos procesos y reinicio no reutilizan holdout.
- [ ] M14-E: fallo tras compromiso consume la oportunidad y deja evidencia del fallo.
- [ ] M14-F: tarea de software sin dominio Quant no hereda reglas financieras.
- [ ] M14-G: recorrido Quant completo entra por el núcleo, ejecuta dominio y llega a revisión/cierre sin un canal paralelo.

**Límite:** un fixture sintético demuestra controles, no rentabilidad, calidad de datos de mercado ni validez económica. No declarar backtester real validado sin sus pruebas específicas.

### M15 — Evaluador de cierre v2 y revisión autenticada

**Archivos:** `hyperion_core/evidence.py`, `hyperion_core/review.py`, `hyperion_core/closure.py`, `tests/test_closure.py`.

**Binding v2:** además de los seis campos actuales, incorporar `run_id`, revisión de contrato/plan, `attempt_id`, `check_definition_hash`, inputs/dataset cuando aplica, `runtime_digest` y política. Una revisión debe referir al candidato **y al digest del conjunto exacto de resultados** revisados.

**Interfaz:** `evaluate(run_snapshot) -> Verdict(state, blockers, evidence_ids, review_ids)`. Se calcula en el núcleo; la persistencia del veredicto y evento ocurre con comparación de revisión en una transacción de M09.

**Predicado de cierre:** contrato y autoridad vigentes; alcance válido; candidato exacto; todos los checks obligatorios presentes y exitosos; runner/inputs correctos; presupuestos y restricciones respetados; revisión autenticada independiente del ejecutor; hallazgos bloqueantes resueltos; auditoría verificable; ninguna ejecución incierta ni evidencia desactualizada.

**Implementación:** validar recibos y conjunto completo de checks; ignorar evidencia ajena a la identidad actual; invalidar revisión al cambiar cualquier evidencia que cubra; exigir resolución explícita de hallazgos; hacer cierre por compare-and-swap de la revisión del run; emitir informe con cada razón de bloqueo. Conservar un cierre de entrega histórica aunque se abra otra entrega pendiente.

**Checks previstos:**

- [ ] M15-A: éxito del agente, checkboxes, `FINALIZED` Quant y aprobación narrativa no cierran por sí solos.
- [ ] M15-B: faltar un check, mezclar evidencias de candidatos o entornos, manipular recibo o usar revisión vieja bloquea.
- [ ] M15-C: cambio de resultado de aceptación después de revisar exige nueva revisión.
- [ ] M15-D: cambiar el nombre textual no permite autoaprobación; permisos/identidad provienen de M10.
- [ ] M15-E: una aprobación nueva sin resolver hallazgo bloqueante no cierra.
- [ ] M15-F: edición concurrente durante evaluación impide cerrar una revisión distinta de la evaluada.
- [ ] M15-G: el mismo snapshot de estado produce el mismo veredicto y motivos.

**Salida:** `DONE` sólo bajo el predicado completo; resto de estados con razones. `DONE` de código nunca autoriza automáticamente merge, publicación o una orden financiera.

### M16 — Empaquetado, CI, operación y aceptación final

**Archivos:** `pyproject.toml`, configuración reproducible de dependencias/runtime, `tests/e2e/`, `scripts/package.py`, `scripts/verify_release.py`, definición de CI del proveedor elegido, manual de operación.

**Implementación:** separar paquete y estado; construir desde fuente identificada; fijar herramientas y dependencias externas cuando existan; generar manifiesto; extraer paquete en entorno limpio; ejecutar entradas públicas y casos negativos; guardar comandos, logs, hashes, versiones y resultados. CI reporta evidencia vinculada al commit exacto; un check de otro commit no se reutiliza.

La instalación real es una operación distinta del build: preparar configuración y backup antes de sustituirla, comprobar healthcheck después y disponer de rollback. Cambios de esquema necesitan política de compatibilidad y restauración probada; no asumir que bajar el binario revierte una migración de datos.

**Checks previstos:**

- [ ] M16-A: desde una extracción nueva se ejecutan todos los módulos obligatorios sin rutas absolutas de desarrollo.
- [ ] M16-B: escenario software válido llega a `DONE`; alcance indebido, evidencia incompleta y revisión vieja se bloquean.
- [ ] M16-C: escenario real Pi y escenario Quant integrado tienen evidencia identificada.
- [ ] M16-D: caída, recuperación, presupuesto agotado y restauración de backup se prueban.
- [ ] M16-E: falla el job si no descubre pruebas, hay skips no autorizados, falta un artefacto o divergen hashes.
- [ ] M16-F: prueba de frontera M11 se ejecuta en el mismo backend/configuración que la entrega.
- [ ] M16-G: instalación y rollback se prueban en entorno de prueba; aceptación humana sobre evidencia concreta.

**Definición final de completo:** todos los módulos del alcance acordado aceptados con evidencia de la misma versión; riesgos/limitaciones residuales explícitos; repositorio/candidato y entrega identificados; instalación verificada si estaba incluida. Ni el número de archivos ni una suite de un componente aislado sustituyen este criterio.

## 8. Reglas de avance y recibo de cada módulo

No iniciar una dependencia basándose sólo en que otro módulo fue escrito. El recibo mínimo de entrega de módulo debe contener:

```json
{
  "module": "Mxx",
  "status": "IMPLEMENTED_UNVERIFIED | VERIFIED | BLOCKED",
  "source_commit_or_manifest": "identidad exacta",
  "contract_hash": "identidad del alcance",
  "checks": [
    {"id": "Mxx-A", "command": ["comando", "argumentos"],
     "exit_code": 0, "expected": "resultado concreto", "observed": "resultado concreto",
     "stdout_artifact": "ruta", "stderr_artifact": "ruta"}
  ],
  "negative_cases": ["IDs de rechazos ejecutados"],
  "limitations": ["garantias que no se demostraron"],
  "review": {"kind": "real | simulated | absent", "receipt": "referencia o null"}
}
```

El JSON anterior es el formato objetivo de recibos por módulo; los resultados actuales de `verificar.py` usan su esquema documentado en `resultado.json`. No confundir el campo de estado del recibo con estados de tareas de Hyperion.

Un cambio después de verificar requiere evaluar qué pruebas y revisiones invalida. Nunca borrar un fallo del historial. Si se reduce el alcance, registrar qué módulos quedan excluidos y no llamar a esa entrega “sistema completo” respecto del alcance anterior.

## 9. Checklist maestra de aceptación personal

Las casillas empiezan vacías para que registres tu validación. Los resultados automatizados de esta entrega se conservan aparte.

- [ ] M00 — Puedo extraer, verificar hashes y ejecutar sin corregir rutas a mano.
- [ ] M01 — Contrato y aceptación quedan congelados y los rechazos no los sustituyen.
- [ ] M02 — Sé qué base, commit, tree y UUID se están evaluando.
- [ ] M03 — Un cambio fuera de alcance no se acepta aunque pasen las pruebas.
- [ ] M04 — Distingo error de infraestructura de fallo funcional y puedo leer logs.
- [ ] M05 — Distingo identidad declarada de una revisión real autenticada.
- [ ] M06 — Evidencia anterior no cierra una entrega nueva.
- [ ] M07 — La compatibilidad legacy pasa sin atribuirle garantías nuevas.
- [ ] M08 — Reproduje los 12 pasos y conservé sus resultados.
- [ ] M09 — Persistencia y presupuestos sobreviven a concurrencia y caída.
- [ ] M10 — Contrato/plan y autoridad están ligados y se invalidan correctamente.
- [ ] M11 — La frontera de ejecución se comprobó con intentos de escape acotados.
- [ ] M12 — Agente y correcciones atraviesan el núcleo y no pueden autodeclarar cierre.
- [ ] M13 — Pi está cargado y conectado en una sesión real verificable.
- [ ] M14 — Quant usa el núcleo y conserva causalidad, costes y holdout.
- [ ] M15 — El cierre autentica y vincula toda la evidencia de la versión actual.
- [ ] M16 — La entrega completa se reproduce, recupera y verifica desde cero.

**Estado honesto de esta entrega:** el flujo local M00–M08 es reproducible en el entorno comprobado, sujeto a los límites descritos. M09–M16 quedan sin aprobar y requieren implementación. No hay certificación de sistema integrado ni revisión independiente realizada por este paquete.
