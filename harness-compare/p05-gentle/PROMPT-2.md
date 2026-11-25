Trabaja SOLO dentro de esta carpeta: /home/datawithjose/Documents/Workspace/harness-compare/p05-gentle/g-run-2 (repo git propio, con el codigo de la app, la especificacion `TASK-F13.md` y la rubrica `RUBRICA.md`). No leas ni abras nada fuera de ella; en particular nada dentro de /home/datawithjose/Documents/Workspace/apex-hit ni las otras carpetas g-run-*. Commits locales, nunca push.

USA TU HARNESS HABITUAL de punta a punta (orquestacion, agentes, reglas, archivos de estado, forma de verificar). No uses nada de otro harness. Si tu flujo te hace crear documentos (ODD, Engram, etc.), crealos dentro de esta carpeta.

Implementa F13 (`TASK-F13.md`, la especificacion manda).

BRAZO 2 (GENERADOR -> EVALUADOR -> CORRECCION):
1. Un agente GENERADOR implementa F13 y no se autoevalua con rubrica.
2. Un agente EVALUADOR DISTINTO, con contexto limpio, evalua con `RUBRICA.md` (puntua cada criterio 0-5 con evidencia ejecutada; lista de defectos con severidad alta/media/baja y como reproducirlos; veredicto APROBADO/RECHAZADO). El evaluador NO edita codigo ni tests.
3. Un agente (el generador u otro) corrige los defectos del evaluador. Una sola pasada de correccion; no hay segunda evaluacion.
Tu, como orquestador, no implementas ni corriges a mano: delegas y registras.

Antes de empezar anota la hora (`date +%T`); al acabar, otra vez. Si algo se bloquea o un agente falla, no cambies de estrategia en silencio: copia el mensaje de error LITERAL y dime que decidiste.

Al terminar responde SOLO con: hora de inicio y fin; cuantos agentes lanzaste, de que rol y modelo; que archivos de estado dejaste; resultado literal de `npm test` y de `./scripts/check-architecture.sh`; hashes de commit; defectos que encontro cada evaluacion (numero y severidad) y cuales se corrigieron; errores literales y tus decisiones; cualquier intervencion. No digas que esta "aprobado" por tu cuenta: lo verificara otro proceso.