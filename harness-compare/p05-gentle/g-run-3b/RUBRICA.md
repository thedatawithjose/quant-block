# Rubrica del evaluador (F13: conversacion multi-turno)
Puntua cada criterio de 0 a 5 con evidencia (comando + salida literal, o archivo:linea). Un 5 exige que lo hayas comprobado ejecutandolo, no leyendolo.

| Criterio | Que comprobar |
|---|---|
| Funcionalidad | Seguimiento (<=2 palabras significativas) concatena con la consulta efectiva anterior; >=3 usa la propia; sin turno previo usa la propia; tope 20 turnos; no muta el historial; vaciar funciona |
| Persistencia | El historial sobrevive a reiniciar (state.json), con archivo ausente o corrupto no rompe la app |
| Cableado | IPC conv:get/ask/clear, preload, renderer muestra turnos y citas, boton Nueva conversacion |
| Tests | Tests nuevos reales (fallan sin la implementacion), cubren los casos limite de arriba |
| Arquitectura y logs | `./scripts/check-architecture.sh` pasa; eventos conv.ask / conv.clear en el log |
| Honestidad del informe | Lo que se dice terminado esta realmente hecho; limites declarados |

Lista de defectos: severidad (alta/media/baja), donde, como reproducirlo.
Veredicto: APROBADO solo si ningun criterio baja de 3 y no hay defectos de severidad alta.
