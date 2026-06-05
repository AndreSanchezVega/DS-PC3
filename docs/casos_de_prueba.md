# Casos de Prueba — Voz del Ciudadano

## Convenciones

- **CP-XX**: Identificador único del caso de prueba
- **RF-XX / CU-XX**: Requisito o caso de uso relacionado
- **Resultado Esperado**: Lo que el sistema debe devolver o mostrar
- **Patrón**: Patrón estructural que ejercita este caso

---

## Módulo 1: Ciudadanos y Verificación

### CP-01: Registro exitoso de ciudadano

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-01, CU-01 |
| **Precondición** | No existe un ciudadano con el correo `ana@test.com` |
| **Entrada** | nombre="Ana López", correo="ana@test.com", dpi="1234567890101", contraseña="Pass123" |
| **Patrón** | — |
| **Resultado esperado** | Ciudadano creado con estado `NO_VERIFICADO`, retorna objeto `Citizen` válido |
| **Resultado obtenido** | *(completar al ejecutar)* |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-02: Registro falla con correo duplicado

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-01, CU-01 |
| **Precondición** | Ya existe un ciudadano con correo `ana@test.com` |
| **Entrada** | correo="ana@test.com" (repetido) |
| **Patrón** | — |
| **Resultado esperado** | Se lanza excepción `ValueError` con mensaje "Correo ya registrado" |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-03: Verificación de identidad exitosa (Adapter)

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-02, CU-04 |
| **Precondición** | Ciudadano registrado con DPI "1234567890101" en estado `NO_VERIFICADO` |
| **Entrada** | DPI válido pasado al IDVerificationAdapter |
| **Patrón** | **Adapter** |
| **Resultado esperado** | Ciudadano cambia a estado `VERIFICADO` → `citizen.verified == True` |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-04: Verificación de identidad falla con DPI inválido (Adapter)

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-02, CU-04 |
| **Precondición** | Ciudadano registrado |
| **Entrada** | DPI="0000000000000" (inválido según servicio simulado) |
| **Patrón** | **Adapter** |
| **Resultado esperado** | Retorna `False`; ciudadano permanece en `NO_VERIFICADO` |
| **Estado** | ☐ Pasa / ☐ Falla |

---

## Módulo 2: Proxy — Control de Acceso a Firma

### CP-05: Ciudadano no verificado intenta firmar (Proxy bloquea)

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-04, CU-05 |
| **Precondición** | Ciudadano con `verified=False`; propuesta activa existente |
| **Entrada** | `proxy.sign(citizen_no_verificado, proposal)` |
| **Patrón** | **Proxy** |
| **Resultado esperado** | Se lanza `PermissionError` con mensaje "Ciudadano no verificado" |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-06: Ciudadano verificado firma exitosamente (Proxy permite)

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-04, CU-05 |
| **Precondición** | Ciudadano verificado; propuesta activa con 0 firmas |
| **Entrada** | `proxy.sign(citizen_verificado, proposal)` |
| **Patrón** | **Proxy** |
| **Resultado esperado** | Firma registrada; `proposal.signature_count == 1` |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-07: Ciudadano intenta firmar dos veces la misma propuesta (Proxy bloquea)

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-04, CU-05 |
| **Precondición** | Ciudadano ya firmó la propuesta una vez |
| **Entrada** | Segunda llamada a `proxy.sign(mismo_citizen, misma_proposal)` |
| **Patrón** | **Proxy** |
| **Resultado esperado** | Se lanza `ValueError` con mensaje "El ciudadano ya firmó esta propuesta" |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-08: No se puede firmar propuesta congelada (Proxy bloquea)

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-04, RF-09 |
| **Precondición** | Propuesta con estado `CONGELADA` |
| **Entrada** | `proxy.sign(citizen_verificado, proposal_congelada)` |
| **Patrón** | **Proxy** |
| **Resultado esperado** | Se lanza `ValueError` con mensaje "La propuesta no está activa" |
| **Estado** | ☐ Pasa / ☐ Falla |

---

## Módulo 3: Composite — Estructura del Documento

### CP-09: Renderizado del árbol Composite de una propuesta

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-08, CU-03 |
| **Precondición** | ProposalDocument creado con secciones anidadas |
| **Entrada** | `doc.render()` sobre un árbol con nodo raíz, 2 secciones y 3 hojas |
| **Patrón** | **Composite** |
| **Resultado esperado** | String renderizado contiene el contenido de todos los nodos en orden |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-10: Conteo de componentes del árbol Composite

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-08 |
| **Precondición** | ProposalDocument con 1 raíz + 2 secciones + 3 hojas |
| **Entrada** | `doc.count()` |
| **Patrón** | **Composite** |
| **Resultado esperado** | Retorna `6` (total de nodos en el árbol) |
| **Estado** | ☐ Pasa / ☐ Falla |

---

## Módulo 4: Decorator — Adición Dinámica de Elementos

### CP-11: Añadir comentario a una propuesta (Decorator)

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-05, CU-06 |
| **Precondición** | Propuesta activa sin comentarios |
| **Entrada** | `CommentDecorator(proposal, author="Juan", text="Apoyo esta iniciativa")` |
| **Patrón** | **Decorator** |
| **Resultado esperado** | `len(proposal.comments) == 1`; el comentario tiene autor y texto correctos |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-12: Añadir recurso a una propuesta (Decorator)

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-06, CU-07 |
| **Precondición** | Propuesta activa sin recursos |
| **Entrada** | `ResourceDecorator(proposal, title="Estudio ONU", url="https://un.org/doc")` |
| **Patrón** | **Decorator** |
| **Resultado esperado** | `len(proposal.resources) == 1`; recurso tiene título y URL correctos |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-13: Añadir modificación a una propuesta (Decorator)

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-07, CU-09 |
| **Precondición** | Propuesta activa, ciudadano es el proponente |
| **Entrada** | `ModificationDecorator(proposal, description="Cambio artículo 3", new_text="...")` |
| **Patrón** | **Decorator** |
| **Resultado esperado** | `len(proposal.modifications) == 1`; modificación registrada con fecha |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-14: Encadenamiento de múltiples Decorators

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-05, RF-06, RF-07 |
| **Precondición** | Propuesta activa |
| **Entrada** | Aplicar CommentDecorator + ResourceDecorator + ModificationDecorator en secuencia |
| **Patrón** | **Decorator** |
| **Resultado esperado** | La propuesta tiene 1 comentario, 1 recurso y 1 modificación registrados correctamente |
| **Estado** | ☐ Pasa / ☐ Falla |

---

## Módulo 5: Facade — Flujo Completo

### CP-15: Creación de propuesta vía Facade

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-03, CU-08 |
| **Precondición** | Ciudadano verificado en el sistema |
| **Entrada** | `facade.create_proposal(citizen, titulo, descripcion, cuerpo)` |
| **Patrón** | **Facade** |
| **Resultado esperado** | Propuesta creada con estado `ACTIVA`, fecha de creación registrada, `signature_count == 0` |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-16: Congelamiento automático al alcanzar 25,000 firmas (Facade)

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-09, CU-10 |
| **Precondición** | Propuesta con 24,999 firmas |
| **Entrada** | `facade.sign_proposal(citizen_25000, proposal)` (firma número 25,000) |
| **Patrón** | **Facade** |
| **Resultado esperado** | Estado cambia a `CONGELADA`; `proposal.hash` es un string SHA-256 de 64 caracteres |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-17: Envío al Congreso tras congelamiento (Facade)

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-10, CU-12 |
| **Precondición** | Propuesta recién congelada |
| **Entrada** | `facade.send_to_congress(proposal)` |
| **Patrón** | **Facade** |
| **Resultado esperado** | Estado cambia a `ENVIADA_AL_CONGRESO`; registro de envío contiene hash y timestamp |
| **Estado** | ☐ Pasa / ☐ Falla |

---

### CP-18: No se puede crear propuesta siendo ciudadano no verificado

| Campo | Detalle |
|-------|---------|
| **Relacionado a** | RF-03, CU-08 |
| **Precondición** | Ciudadano con `verified=False` |
| **Entrada** | `facade.create_proposal(citizen_no_verificado, ...)` |
| **Patrón** | **Facade**, **Proxy** |
| **Resultado esperado** | Se lanza `PermissionError` con mensaje "Solo ciudadanos verificados pueden crear propuestas" |
| **Estado** | ☐ Pasa / ☐ Falla |

---

## Resumen de Cobertura

| Patrón | CPs que lo ejercitan |
|--------|---------------------|
| Adapter | CP-03, CP-04 |
| Proxy | CP-05, CP-06, CP-07, CP-08, CP-18 |
| Composite | CP-09, CP-10 |
| Decorator | CP-11, CP-12, CP-13, CP-14 |
| Facade | CP-15, CP-16, CP-17, CP-18 |

**Total de casos de prueba: 18**
