# ENFORCEMENT-MATRIX-TEMPLATE.md

## 1. Propósito

Este documento es la plantilla para crear el:

`ENFORCEMENT-MATRIX.md`

de cada proyecto.

Su función es responder, para cada regla aplicable de `AGENT-RULES.md`:

> ¿Qué control real existe para comprobar que esta regla se cumple?

Este documento NO sustituye `AGENT-RULES.md`.

`AGENT-RULES.md` define **qué debe cumplirse**.

`ENFORCEMENT-MATRIX.md` registra:

* cómo se controla;
* dónde está el control;
* cómo se comprueba;
* qué evidencia existe;
* qué ocurre si falla;
* qué controles faltan.

La matriz es un registro de auditoría.

Los tests, validadores, gates, permisos, verificadores, monitorización y revisiones constituyen el enforcement real.

---

## 2. Regla fundamental

Una regla escrita NO demuestra que esté implementada.

Un agente MUST NOT clasificar un control como `IMPLEMENTED` únicamente porque:

* la regla aparece en `AGENT-RULES.md`;
* existe código que aparentemente la cumple;
* el propio agente escribió el control;
* el propio agente escribió el test;
* el propio agente afirma que funciona;
* la matriz fue modificada para indicar `IMPLEMENTED`.

`IMPLEMENTED` requiere evidencia verificable.

---

## 3. Relación con AGENT-RULES

Cada control MUST estar vinculado a un `RULE_ID` existente en `AGENT-RULES.md`.

Ejemplo:

```text
RULE_ID = POINT_IN_TIME_ONLY
```

Una misma regla MAY tener varios controles.

Ejemplo:

```text
RULE_ID = POINT_IN_TIME_ONLY

CTRL-TIME-001
CTRL-TIME-002
CTRL-TIME-003
```

La regla vive únicamente en `AGENT-RULES.md`.

La matriz MUST NOT crear una segunda versión normativa de la misma regla.

---

## 4. Estados permitidos

Cada control debe utilizar uno de estos estados:

### IMPLEMENTED

El control:

* existe;
* está conectado al comportamiento que pretende controlar;
* puede comprobarse;
* ha sido comprobado;
* existe evidencia verificable de su funcionamiento.

### PARTIAL

Existe parte del control, pero falta algún elemento material.

Ejemplos:

* existe el test pero no se ejecuta automáticamente;
* existe el validador pero no bloquea;
* existe el control pero faltan datos necesarios;
* existe evidencia incompleta.

### MISSING

El control requerido no existe.

### MANUAL_ONLY

El control depende actualmente de revisión humana y no existe comprobación automática equivalente.

Esto no implica necesariamente que el control sea incorrecto.

Debe quedar explícito que depende de intervención humana.

### NOT_APPLICABLE

La regla o control no aplica realmente al proyecto o alcance evaluado.

Debe existir una justificación concreta.

`NOT_APPLICABLE` MUST NOT utilizarse como bypass para evitar implementar un control difícil.

### UNKNOWN

No existe evidencia suficiente para determinar el estado.

`UNKNOWN` MUST NOT convertirse automáticamente en `IMPLEMENTED`.

---

## 5. Prioridad del control

La prioridad de la regla procede de `AGENT-RULES.md`.

La prioridad del control indica la urgencia de implementar o reparar ese mecanismo concreto.

Valores permitidos:

```text
CRITICAL
HIGH
MEDIUM
LOW
```

### CRITICAL

Su ausencia puede permitir un fallo capaz de invalidar resultados, romper una garantía P0/P1 material o permitir una transición que debería estar bloqueada.

### HIGH

Control importante cuya ausencia deja una exposición material, aunque existan otras defensas.

### MEDIUM

Mejora significativamente la capacidad de detección o auditoría.

### LOW

Control complementario o de menor impacto directo.

---

## 6. Tipos de control

Utilizar, cuando corresponda, las mismas clases definidas por `AGENT-RULES.md`.

### AGENT_POLICY

Instrucción de comportamiento que debe seguir el agente.

Por sí sola no constituye enforcement determinista.

### SOFTWARE_INVARIANT

Propiedad que el software puede comprobar directamente.

Ejemplo:

```text
available_at <= decision_time
```

### SCHEMA_VALIDATION

Comprueba que estructuras, campos, tipos y estados requeridos sean válidos.

### DETERMINISTIC_GATE

Bloqueo objetivo que impide una transición cuando una condición requerida falla.

### INDEPENDENT_VERIFIER

Revisión separada cuyo objetivo es intentar detectar defectos y puede vetar la progresión.

### HUMAN_REVIEW

Revisión humana requerida para determinadas decisiones o cambios materiales.

### MONITORING

Control continuo destinado a detectar deterioro, drift o nuevos fallos.

### AUDIT_LOG

Registro trazable que permite reconstruir qué ocurrió, con qué inputs y bajo qué versión.

Un control MAY utilizar varias clases.

---

## 7. Columnas obligatorias

Cada fila de la matriz representa UN control concreto.

### RULE_ID

Regla de `AGENT-RULES.md` que el control protege.

Ejemplo:

```text
POINT_IN_TIME_ONLY
```

---

### CONTROL_ID

Identificador único del control.

Formato recomendado:

```text
CTRL-[DOMINIO]-[NÚMERO]
```

Ejemplos:

```text
CTRL-TIME-001
CTRL-DATA-002
CTRL-EVIDENCE-001
CTRL-SYCO-001
```

---

### QUÉ_PROTEGE

Descripción breve, en lenguaje normal, del riesgo que intenta evitar.

Ejemplo:

```text
Evita que información futura afecte decisiones históricas.
```

---

### TIPO_DE_CONTROL

Clase o clases de enforcement utilizadas.

Ejemplo:

```text
SOFTWARE_INVARIANT
DETERMINISTIC_GATE
```

---

### CONTROL_CONCRETO

Explica exactamente qué hace el control.

Ejemplo:

```text
Modificar datos posteriores a T y comprobar que la decisión calculada en T permanece inalterada.
```

Evitar frases vagas como:

```text
Comprobar causalidad.
```

Debe quedar claro qué se comprueba.

---

### UBICACIÓN_DEL_CONTROL

Ruta, archivo, configuración o sistema donde vive el control.

Ejemplos:

```text
tests/causality/test_future_data_invariance.py
```

```text
.github/workflows/critical-tests.yml
```

Si todavía no existe:

```text
MISSING
```

---

### DEPENDENCIAS

Qué necesita el control para funcionar correctamente.

Ejemplo:

```text
- timestamps válidos
- available_at disponible
- dataset versionado
- test runner operativo
```

Una dependencia crítica ausente puede convertir un control aparentemente completo en `PARTIAL`.

---

### RIESGO_SI_NO_EXISTE

Describe el fallo que podría quedar sin detectar.

Ejemplo:

```text
Un backtest podría utilizar información futura y presentar resultados falsamente favorables.
```

---

### PRIORIDAD_DEL_CONTROL

Uno de:

```text
CRITICAL
HIGH
MEDIUM
LOW
```

---

### ESTADO

Uno de:

```text
IMPLEMENTED
PARTIAL
MISSING
MANUAL_ONLY
NOT_APPLICABLE
UNKNOWN
```

---

### ACCIÓN_PENDIENTE

Si el estado no es `IMPLEMENTED`, indicar exactamente qué falta.

Ejemplo:

```text
Crear una prueba de invariancia que altere datos T+1 y comprobar que las decisiones hasta T no cambian.
```

Si está completamente implementado:

```text
NONE
```

---

### QUÉ_PASA_SI_FALLA

Consecuencia concreta del fallo.

Ejemplos:

```text
INVALIDATE_RESULT
```

```text
BLOCK_MERGE
```

```text
NEEDS_REMEDIATION
```

```text
HITL
```

```text
WARNING
```

Debe corresponder con la severidad y con `AGENT-RULES.md`.

---

### EVIDENCIA

Prueba verificable de que el control existe y funciona.

Puede incluir:

* test;
* resultado de test;
* reporte CI;
* log;
* configuración;
* validator;
* gate;
* evidencia de revisión independiente;
* revisión humana documentada.

Ejemplo:

```text
tests/causality/test_future_data_invariance.py
CI run: PASS
```

Sin evidencia suficiente, el estado MUST NOT ser `IMPLEMENTED`.

---

### QUIÉN_PUEDE_MODIFICAR_EL_CONTROL

Indica quién puede modificar el mecanismo que actúa como defensa.

Ejemplos:

```text
Agente puede proponer cambios; requiere revisión humana.
```

```text
Solo mantenedor autorizado.
```

```text
Agente puede modificar libremente.
```

Para controles críticos se debe evaluar especialmente si el mismo agente que produce el código puede debilitar también el control que debería detectarlo.

---

### BLOQUEA_INTEGRACIÓN

Valores:

```text
YES
NO
CONDITIONAL
NOT_APPLICABLE
```

`YES` significa que el fallo impide que el cambio sea considerado apto para integración.

`NO` significa que produce evidencia o advertencia pero no bloquea.

`CONDITIONAL` requiere explicar la condición.

---

### ALCANCE

Indica qué queda afectado si el control falla.

Ejemplos:

```text
Todos los backtests que utilicen este pipeline.
```

```text
Solo módulo de analytics.
```

```text
Conclusiones dependientes del dataset X.
```

Un fallo local no debe invalidar automáticamente componentes independientes.

---

### ÚLTIMA_VERIFICACIÓN

Fecha o referencia de la última comprobación válida.

Formato recomendado:

```text
YYYY-MM-DD
```

Si nunca se ha comprobado:

```text
NEVER
```

---

### RESPONSABLE_DE_VERIFICACIÓN

Quién o qué confirma que el control funciona.

Ejemplos:

```text
CI automático
```

```text
Verifier independiente
```

```text
CI automático + revisión humana si cambia el test
```

```text
Revisión humana
```

---

## 8. Matriz

Crear una fila por cada control.

| RULE_ID | CONTROL_ID | QUÉ_PROTEGE | TIPO_DE_CONTROL | CONTROL_CONCRETO | UBICACIÓN_DEL_CONTROL | DEPENDENCIAS | RIESGO_SI_NO_EXISTE | PRIORIDAD_DEL_CONTROL | ESTADO | ACCIÓN_PENDIENTE | QUÉ_PASA_SI_FALLA | EVIDENCIA | QUIÉN_PUEDE_MODIFICAR_EL_CONTROL | BLOQUEA_INTEGRACIÓN | ALCANCE | ÚLTIMA_VERIFICACIÓN | RESPONSABLE_DE_VERIFICACIÓN |
| ------- | ---------- | ----------- | --------------- | ---------------- | --------------------- | ------------ | ------------------- | --------------------- | ------ | ---------------- | ----------------- | --------- | -------------------------------- | ------------------- | ------- | ------------------- | --------------------------- |
|         |            |             |                 |                  |                       |              |                     |                       |        |                  |                   |           |                                  |                     |         |                     |                             |

---

## 9. Ejemplo

Este ejemplo es ilustrativo.

Debe sustituirse por la evidencia real del proyecto.

| RULE_ID              | CONTROL_ID      | QUÉ_PROTEGE                                                | TIPO_DE_CONTROL                            | CONTROL_CONCRETO                                                                                         | UBICACIÓN_DEL_CONTROL                            | DEPENDENCIAS                                                           | RIESGO_SI_NO_EXISTE                            | PRIORIDAD_DEL_CONTROL | ESTADO        | ACCIÓN_PENDIENTE | QUÉ_PASA_SI_FALLA                  | EVIDENCIA                  | QUIÉN_PUEDE_MODIFICAR_EL_CONTROL                                     | BLOQUEA_INTEGRACIÓN | ALCANCE                                            | ÚLTIMA_VERIFICACIÓN | RESPONSABLE_DE_VERIFICACIÓN                |
| -------------------- | --------------- | ---------------------------------------------------------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------- | ---------------------------------------------- | --------------------- | ------------- | ---------------- | ---------------------------------- | -------------------------- | -------------------------------------------------------------------- | ------------------- | -------------------------------------------------- | ------------------- | ------------------------------------------ |
| `POINT_IN_TIME_ONLY` | `CTRL-TIME-001` | Evitar que información futura afecte decisiones históricas | `SOFTWARE_INVARIANT`, `DETERMINISTIC_GATE` | Modificar información posterior a T y comprobar que las decisiones calculadas hasta T permanecen iguales | `tests/causality/test_future_data_invariance.py` | Timestamps correctos, información `available_at`, dataset reproducible | Backtests falsamente favorables por look-ahead | `CRITICAL`            | `IMPLEMENTED` | `NONE`           | `INVALIDATE_RESULT`, `BLOCK_MERGE` | Test ejecutado y CI `PASS` | Agente puede proponer cambios; cambios al control requieren revisión | `YES`               | Backtests y conclusiones dependientes del pipeline | `2026-09-18`        | CI automático + revisión si cambia el test |

---

## 10. Regla para IMPLEMENTED

Un control solo puede clasificarse como:

`IMPLEMENTED`

cuando las condiciones aplicables siguientes sean verdaderas:

```text
CONTROL EXISTS
AND
CONTROL IS CONNECTED TO THE TARGET BEHAVIOR
AND
VERIFICATION EXISTS
AND
VERIFICATION HAS BEEN EXECUTED
AND
EXPECTED RESULT WAS OBSERVED
AND
FAILURE CONSEQUENCE EXISTS WHEN REQUIRED
AND
EVIDENCE IS RECORDED
```

Si falta una condición material:

```text
IMPLEMENTED = FALSE
```

Utilizar:

```text
PARTIAL
MISSING
UNKNOWN
```

según corresponda.

---

## 11. Prohibición de autoaprobación

El mismo agente que desarrolla una implementación MAY:

* crear controles;
* crear tests;
* ejecutar tests;
* recopilar evidencia;
* proponer un estado.

Pero MUST NOT considerar su propia afirmación como evidencia suficiente.

Ejemplo inválido:

```text
ESTADO = IMPLEMENTED

EVIDENCIA =
"El agente confirma que funciona."
```

Modificar la propia matriz no demuestra cumplimiento.

---

## 12. Protección de controles críticos

Para controles `CRITICAL` y otros controles materiales se debe evaluar si el desarrollador o agente puede:

* borrar el test;
* cambiar el resultado esperado;
* desactivar el workflow;
* modificar el gate;
* cambiar el dataset utilizado por el test;
* convertir un fallo en warning;
* alterar la matriz para ocultar el problema.

Cuando esto sea posible sin revisión, debe registrarse como riesgo o control parcial.

El sistema SHOULD evitar que quien produce el cambio pueda también autoaprobar la eliminación de la defensa crítica que evalúa ese mismo cambio.

---

## 13. Auditoría inicial de un proyecto

Al aplicar este framework a un proyecto nuevo:

1. Leer `AGENT-RULES.md`.
2. Extraer todas las reglas P0 y P1.
3. Determinar cuáles son aplicables.
4. Identificar controles ya existentes.
5. No asumir que un test por su nombre demuestra cobertura.
6. Examinar qué comprueba realmente cada control.
7. Registrar su ubicación.
8. Registrar evidencia existente.
9. Clasificar cada control.
10. Identificar controles faltantes.
11. Priorizar primero los riesgos críticos.
12. Crear acciones pendientes concretas.

No implementar controles nuevos durante la auditoría inicial salvo instrucción específica.

Primero debe conocerse el estado real.

---

## 14. Auditoría de cambios

Cuando se modifique un componente que afecte un control existente, revisar:

```text
¿Sigue existiendo?
¿Sigue ejecutándose?
¿Sigue comprobando la misma propiedad?
¿Sus dependencias siguen siendo válidas?
¿Puede todavía provocar el bloqueo esperado?
¿La evidencia sigue siendo vigente?
```

Si alguna respuesta es desconocida, revisar el estado del control.

---

## 15. Principio de independencia del agente

Esta matriz debe funcionar independientemente de que el proyecto sea desarrollado mediante:

* OpenCode;
* Codex;
* otro agente;
* un humano;
* combinación de varios agentes.

Los controles críticos SHOULD residir en el proyecto o en infraestructura reproducible, no únicamente dentro de funciones propietarias de un agente concreto.

Cambiar de agente MUST NOT eliminar silenciosamente las defensas principales del proyecto.

---

## 16. Resultado esperado

Una matriz completa debe permitir responder rápidamente:

```text
¿Qué reglas aplican?

¿Cuáles están realmente protegidas?

¿Cómo están protegidas?

¿Dónde viven los controles?

¿Qué evidencia tenemos?

¿Qué falta?

¿Qué riesgos siguen abiertos?

¿Qué falla si un control se rompe?

¿Puede el propio agente evadirlo?

¿Qué controles debemos implementar primero?
```

El objetivo no es conseguir que todas las filas digan `IMPLEMENTED`.

El objetivo es representar honestamente el estado real del proyecto.

Una matriz con controles `MISSING` claramente identificados es más útil que una matriz aparentemente completa basada en evidencia débil.
