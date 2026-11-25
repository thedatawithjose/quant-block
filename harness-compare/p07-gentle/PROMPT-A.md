Trabaja SOLO dentro de esta carpeta: /home/datawithjose/Documents/Workspace/harness-compare/p07-gentle/g-run (repo git propio, con el codigo de la app y la especificacion `TASK-F18.md`). No leas ni abras nada fuera de ella; en particular nada dentro de /home/datawithjose/Documents/Workspace/apex-hit. Commits locales, nunca push.

USA TU HARNESS HABITUAL de punta a punta (orquestacion, agentes, reglas, archivos de estado, forma de verificar). No uses nada de otro harness. Si tu flujo te hace crear documentos (ODD, Engram, etc.), crealos dentro de esta carpeta.

FASE A. Implementa F18 (`TASK-F18.md`, la especificacion manda) como un LOOP MAKER-CHECKER:
- Un agente IMPLEMENTA (maker); otro agente DISTINTO y con contexto limpio VERIFICA (checker), de forma independiente y esceptica: ejecuta el codigo, prueba entradas hostiles y casos limite, comprueba el cableado (canal IPC, puente, log, boton). El checker NO puede editar codigo ni tests; solo informa, con problemas numerados, severidad (alta/media/baja) y como reproducirlos, y un veredicto APPROVED o REJECTED.
- Si REJECTED, el maker corrige cada problema y se repite. Si APPROVED, se cuenta como aprobacion; el maker puede releer la especificacion por si hay defectos propios.
- Para cuando haya 3 APROBACIONES CONSECUTIVAS del checker, o a las 10 rondas. Lleva el estado del loop en un archivo (por ejemplo `loop-state.md`: ronda, aprobaciones consecutivas, veredicto y problemas de cada ronda).
- Tu, como orquestador, no implementas ni corriges a mano: delegas, lees el veredicto y registras. Si algo se bloquea o un agente falla, no cambies de estrategia en silencio: copia el mensaje de error LITERAL en el archivo de estado y dime que decidiste.

Antes de empezar anota la hora (`date +%T`); al acabar, otra vez.

Al terminar responde SOLO con: hora de inicio y fin; tabla por ronda (ronda, quien implemento, quien verifico, veredicto, numero de problemas y su severidad); cuantos agentes lanzaste y de que tipo/modelo; que archivos de estado dejaste; resultado literal de `npm test`; hashes de commit; errores literales y tus decisiones; cualquier intervencion. No digas que esta "aprobado" por tu cuenta: lo verificara otro proceso.
