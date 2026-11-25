# START-HERE.md

# ANTES DE COMENZAR CUALQUIER TAREA:


1. Leer completo DCP/dcp_01.md
2. Leer completo DCP/dcp_02.md
3. Leer completo DCP/dcp_03.md
4. Leer completo AGENT-RULES.md
5. Aplicar después las instrucciones de START-HERE.md
6. Leer ENFORCEMENT-MATRIX.md si existe para el proyecto


## Propósito

Este proyecto utiliza un framework global de control para agentes de IA.

Antes de modificar código, analizar resultados, generar conclusiones o proponer cambios, el agente MUST seguir este proceso.

## Orden de autoridad

1. `AGENT-RULES.md`
2. `START-HERE.md`
3. `ENFORCEMENT-MATRIX.md`
4. Instrucciones específicas de la tarea

Si existe una contradicción entre estos archivos, prevalece el de mayor nivel.

`START-HERE.md` MUST NOT modificar, reinterpretar ni debilitar una regla definida en `AGENT-RULES.md`.

---

## Inicio obligatorio

Antes de realizar trabajo material:

1. Lee `AGENT-RULES.md`.
2. Trátalo como la fuente normativa global.
3. No modifiques sus reglas para adaptarlas al proyecto.
4. Inspecciona la estructura, lenguaje, herramientas, tests y controles existentes del proyecto.
5. Crea o actualiza `ENFORCEMENT-MATRIX.md` utilizando `ENFORCEMENT-MATRIX-TEMPLATE.md`.
6. Determina qué reglas P0 y P1 son aplicables al proyecto.
7. Identifica qué mecanismos reales existen para hacer cumplir cada regla aplicable.

---

## Qué debes adaptar al proyecto

Adapta únicamente los elementos que dependen de la implementación concreta del proyecto, por ejemplo:

* tests;
* rutas;
* comandos;
* herramientas;
* validadores;
* comprobaciones automáticas;
* gates;
* configuración de integración;
* controles de acceso;
* evidencias de cumplimiento.

Las reglas globales no deben copiarse ni reescribirse innecesariamente.

`ENFORCEMENT-MATRIX.md` debe referenciar las reglas mediante su `RULE_ID`.

---

## Qué NO debes adaptar

No modifiques una regla global simplemente porque:

* el proyecto utiliza otro lenguaje;
* utiliza otro framework;
* el agente es diferente;
* la implementación resulta más difícil;
* una regla impide una solución propuesta;
* un test falla;
* una conclusión deseada no supera los controles.

Si una regla no aplica realmente al proyecto, puede clasificarse como:

`NOT_APPLICABLE`

pero debe existir una justificación concreta.

`NOT_APPLICABLE` MUST NOT utilizarse como mecanismo para evitar una regla incómoda.

---

## Auditoría inicial

Para cada regla P0 y P1 aplicable, determina su estado real.

Estados permitidos:

* `IMPLEMENTED`
* `PARTIAL`
* `MISSING`
* `MANUAL_ONLY`
* `NOT_APPLICABLE`

La ausencia de información o evidencia debe permanecer sin aprobar.

`UNKNOWN`, ausencia de test, ausencia de infraestructura o intención futura MUST NOT equivaler a `IMPLEMENTED`.

---

## Regla de evidencia

Una regla escrita no demuestra cumplimiento.

Para marcar un control como `IMPLEMENTED` debe existir evidencia verificable de que:

1. el mecanismo de control existe;
2. está conectado al comportamiento que pretende controlar;
3. existe una forma de comprobarlo;
4. la comprobación produce el resultado esperado;
5. el fallo del control produce la consecuencia definida cuando corresponda.

Ejemplos de evidencia:

* tests ejecutados;
* resultados de CI;
* validadores;
* gates;
* logs;
* configuración de permisos;
* resultados de verificación independiente;
* registros de revisión humana cuando sean necesarios.

---

## Prohibición de autoaprobación

El agente MUST NOT declarar un control `IMPLEMENTED` únicamente porque él mismo:

* escribió el código;
* creó el test;
* modificó la matriz;
* afirma que la implementación es correcta.

La clasificación debe apoyarse en evidencia verificable.

Modificar:

`MISSING → IMPLEMENTED`

dentro de `ENFORCEMENT-MATRIX.md` no constituye evidencia.

---

## Controles críticos

Cuando una regla dependa de mecanismos externos al razonamiento del agente —por ejemplo:

* causalidad;
* integridad temporal;
* cálculos;
* separación de datasets;
* validación de esquemas;
* permisos;
* integración;
* ejecución;
* protección de tests—

el agente MUST NOT afirmar que la regla está garantizada únicamente porque aparece en `AGENT-RULES.md`.

Debe existir enforcement técnico o declararse la limitación correspondiente.

---

## Compatibilidad con agentes

Este framework es independiente del agente utilizado.

Debe funcionar con:

* OpenCode;
* Codex;
* otros agentes actuales;
* agentes futuros.

Las funciones específicas de un proveedor pueden utilizarse como apoyo, pero ningún control crítico debe depender exclusivamente de una capacidad propietaria de un agente concreto.

El repositorio y sus controles deben continuar siendo auditables aunque cambie el agente.

---

## Resultado esperado de la adaptación

Al finalizar la evaluación inicial de un proyecto, el agente debe dejar:

1. `AGENT-RULES.md` sin modificaciones no autorizadas;
2. `ENFORCEMENT-MATRIX.md` creado o actualizado;
3. cada regla P0/P1 aplicable clasificada;
4. controles existentes identificados;
5. controles parciales identificados;
6. controles faltantes identificados;
7. evidencia asociada a cualquier estado `IMPLEMENTED`;
8. limitaciones y trabajo pendiente claramente visibles.

El agente MUST NOT ocultar controles faltantes para presentar el proyecto como más completo de lo que realmente está.

---

## Principio operativo

El objetivo de este framework no es confiar en que el agente recuerde comportarse correctamente.

El objetivo es separar:

```text
REGLA
↓
CONTROL
↓
COMPROBACIÓN
↓
EVIDENCIA
```

`AGENT-RULES.md` define qué debe cumplirse.

`ENFORCEMENT-MATRIX.md` registra cómo se controla y qué evidencia existe.

Los tests, validadores, gates, permisos y demás mecanismos del proyecto constituyen el enforcement real.
