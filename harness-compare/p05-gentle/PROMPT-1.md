Trabaja SOLO dentro de esta carpeta: /home/datawithjose/Documents/Workspace/harness-compare/p05-gentle/g-run-1 (repo git propio, con el codigo de la app, la especificacion `TASK-F13.md` y la rubrica `RUBRICA.md`). No leas ni abras nada fuera de ella; en particular nada dentro de /home/datawithjose/Documents/Workspace/apex-hit ni las otras carpetas g-run-*. Commits locales, nunca push.

USA TU HARNESS HABITUAL de punta a punta (orquestacion, agentes, reglas, archivos de estado, forma de verificar). No uses nada de otro harness. Si tu flujo te hace crear documentos (ODD, Engram, etc.), crealos dentro de esta carpeta.

Implementa F13 (`TASK-F13.md`, la especificacion manda).

BRAZO 1 (UN SOLO ROL): un unico agente planifica, implementa y se autoevalua con `RUBRICA.md` (ejecutando, con evidencia). No lances subagentes para este brazo; si tu harness te obliga a delegar, anota el mensaje literal y dime que hiciste.

Antes de empezar anota la hora (`date +%T`); al acabar, otra vez. Si algo se bloquea o un agente falla, no cambies de estrategia en silencio: copia el mensaje de error LITERAL y dime que decidiste.

Al terminar responde SOLO con: hora de inicio y fin; cuantos agentes lanzaste, de que rol y modelo; que archivos de estado dejaste; resultado literal de `npm test` y de `./scripts/check-architecture.sh`; hashes de commit; defectos que encontro cada evaluacion (numero y severidad) y cuales se corrigieron; errores literales y tus decisiones; cualquier intervencion. No digas que esta "aprobado" por tu cuenta: lo verificara otro proceso.