# Casos de Uso — Voz del Ciudadano

## Diagrama de Actores y Casos de Uso (textual)

```
Actores: Ciudadano No Verificado | Ciudadano Verificado | Proponente | Sistema

Ciudadano No Verificado:
  └── CU-01: Registrarse en el sistema
  └── CU-02: Ver listado de propuestas
  └── CU-03: Ver detalle de una propuesta

Ciudadano Verificado (hereda de No Verificado):
  └── CU-04: Verificar identidad (DPI/cédula)
  └── CU-05: Firmar una propuesta
  └── CU-06: Añadir comentario a una propuesta
  └── CU-07: Añadir recurso de apoyo a una propuesta
  └── CU-08: Crear una propuesta legislativa

Proponente (es Ciudadano Verificado que creó la propuesta):
  └── CU-09: Añadir modificación a su propuesta

Sistema (automatizado):
  └── CU-10: Congelar propuesta al alcanzar 25,000 firmas
  └── CU-11: Expirar propuesta al cumplir 90 días sin firmas suficientes
  └── CU-12: Enviar propuesta congelada al Congreso
```

---

## CU-01: Registrarse en el sistema

| Campo | Detalle |
|-------|---------|
| **Actor** | Ciudadano No Verificado |
| **Precondición** | El usuario no tiene cuenta en el sistema |
| **Postcondición** | El ciudadano queda registrado con estado `NO_VERIFICADO` |
| **Patrón relacionado** | — |

**Flujo principal:**
1. El usuario accede a la pantalla de registro.
2. Ingresa nombre, correo electrónico, número de DPI/cédula y contraseña.
3. El sistema valida que el correo no esté registrado.
4. El sistema crea la cuenta y redirige al dashboard.

**Flujos alternativos:**
- 3a. El correo ya existe → el sistema muestra mensaje de error.
- 2a. El formato del DPI es inválido → el sistema muestra mensaje de error.

---

## CU-02: Ver listado de propuestas

| Campo | Detalle |
|-------|---------|
| **Actor** | Ciudadano No Verificado |
| **Precondición** | Ninguna (pantalla pública) |
| **Postcondición** | Se muestra el listado de propuestas con su estado y conteo de firmas |
| **Patrón relacionado** | Facade (ProposalFacade.get_all_proposals) |

**Flujo principal:**
1. El usuario accede a la URL raíz del sistema (`/`).
2. El sistema consulta todas las propuestas mediante la Facade.
3. Se muestra una tarjeta por propuesta con: título, estado, firmas actuales, días restantes.

---

## CU-03: Ver detalle de una propuesta

| Campo | Detalle |
|-------|---------|
| **Actor** | Ciudadano No Verificado |
| **Precondición** | La propuesta existe en el sistema |
| **Postcondición** | Se muestra el documento completo con comentarios, recursos y firmas |
| **Patrón relacionado** | Composite (renderizado del árbol), Decorator (comentarios, recursos, modificaciones) |

**Flujo principal:**
1. El usuario hace clic en una propuesta del listado.
2. La Facade recupera el documento completo de la propuesta.
3. El Composite renderiza la estructura jerárquica del documento.
4. Los Decorators añaden comentarios, recursos y modificaciones al renderizado.
5. Se muestra la página de detalle con todas las secciones.

---

## CU-04: Verificar identidad

| Campo | Detalle |
|-------|---------|
| **Actor** | Ciudadano No Verificado |
| **Precondición** | El ciudadano tiene cuenta pero no está verificado |
| **Postcondición** | El ciudadano queda con estado `VERIFICADO` |
| **Patrón relacionado** | Adapter (IDVerificationAdapter) |

**Flujo principal:**
1. El ciudadano accede a su perfil y selecciona "Verificar identidad".
2. El sistema llama al IDVerificationAdapter con el número de DPI del ciudadano.
3. El Adapter delega la validación al servicio externo (simulado).
4. Si válido, el estado del ciudadano cambia a `VERIFICADO`.

**Flujos alternativos:**
- 4a. El DPI no es válido → el sistema muestra "Verificación fallida".

---

## CU-05: Firmar una propuesta

| Campo | Detalle |
|-------|---------|
| **Actor** | Ciudadano Verificado |
| **Precondición** | El ciudadano está verificado y la propuesta está `ACTIVA` |
| **Postcondición** | La firma queda registrada y el contador se incrementa en 1 |
| **Patrón relacionado** | Proxy (CitizenVerificationProxy), Facade (ProposalFacade.sign_proposal) |

**Flujo principal:**
1. El ciudadano hace clic en "Firmar propuesta" en la vista de detalle.
2. El Proxy verifica que el ciudadano esté verificado.
3. El Proxy verifica que el ciudadano no haya firmado ya esta propuesta.
4. La Facade registra la firma con timestamp y hash del ciudadano.
5. La Facade verifica si se alcanzaron las 25,000 firmas → si sí, ejecuta CU-10.
6. Se actualiza el contador visible en la interfaz.

**Flujos alternativos:**
- 2a. Ciudadano no verificado → muestra "Debes verificar tu identidad para firmar".
- 3a. Ya firmó → muestra "Ya has firmado esta propuesta".
- 4a. Propuesta congelada o expirada → muestra "Esta propuesta ya no acepta firmas".

---

## CU-06: Añadir comentario

| Campo | Detalle |
|-------|---------|
| **Actor** | Ciudadano Verificado |
| **Precondición** | Propuesta en estado `ACTIVA` |
| **Postcondición** | El comentario queda registrado y visible en el detalle |
| **Patrón relacionado** | Decorator (CommentDecorator) |

**Flujo principal:**
1. En la vista de detalle, el ciudadano escribe un comentario y envía el formulario.
2. La Facade aplica el CommentDecorator a la propuesta.
3. El comentario queda almacenado con autor, texto y fecha.
4. La página se recarga mostrando el nuevo comentario.

---

## CU-07: Añadir recurso de apoyo

| Campo | Detalle |
|-------|---------|
| **Actor** | Ciudadano Verificado |
| **Precondición** | Propuesta en estado `ACTIVA` |
| **Postcondición** | El recurso queda registrado y visible en la sección de recursos |
| **Patrón relacionado** | Decorator (ResourceDecorator) |

**Flujo principal:**
1. El ciudadano ingresa título y URL del recurso en el formulario de la vista de detalle.
2. La Facade aplica el ResourceDecorator a la propuesta.
3. El recurso queda almacenado y se muestra en la sección "Recursos de apoyo".

---

## CU-08: Crear propuesta legislativa

| Campo | Detalle |
|-------|---------|
| **Actor** | Ciudadano Verificado |
| **Precondición** | El ciudadano está verificado |
| **Postcondición** | La propuesta queda creada en estado `ACTIVA` con el contador de 90 días iniciado |
| **Patrón relacionado** | Facade (ProposalFacade.create_proposal), Composite (ProposalDocument) |

**Flujo principal:**
1. El ciudadano accede a "Nueva Propuesta" desde el dashboard.
2. Ingresa título, descripción y cuerpo del texto normativo.
3. La Facade crea el ProposalDocument como árbol Composite.
4. Se registra la propuesta con estado `ACTIVA` y fecha de creación.
5. El sistema redirige a la vista de detalle de la nueva propuesta.

---

## CU-09: Añadir modificación

| Campo | Detalle |
|-------|---------|
| **Actor** | Proponente |
| **Precondición** | El ciudadano es el creador de la propuesta y está `ACTIVA` |
| **Postcondición** | La modificación queda registrada en el historial |
| **Patrón relacionado** | Decorator (ModificationDecorator) |

**Flujo principal:**
1. En la vista de detalle, el proponente accede a la sección "Modificaciones".
2. Ingresa descripción del cambio y el texto modificado.
3. La Facade aplica el ModificationDecorator a la propuesta.
4. La modificación queda en el historial con fecha.

---

## CU-10: Congelar propuesta (Sistema)

| Campo | Detalle |
|-------|---------|
| **Actor** | Sistema |
| **Precondición** | La propuesta alcanzó 25,000 firmas válidas |
| **Postcondición** | Estado = `CONGELADA`, hash SHA-256 generado, propuesta enviada al Congreso |
| **Patrón relacionado** | Facade (ProposalFacade.freeze_proposal) |

**Flujo principal:**
1. Al registrar la firma número 25,000, la Facade detecta el umbral.
2. Se genera el hash SHA-256 del contenido completo de la propuesta.
3. El estado cambia a `CONGELADA`.
4. Se ejecuta CU-12 (envío al Congreso).

---

## CU-12: Enviar propuesta al Congreso (Sistema)

| Campo | Detalle |
|-------|---------|
| **Actor** | Sistema |
| **Precondición** | La propuesta está en estado `CONGELADA` |
| **Postcondición** | Registro de envío creado con estado `ENVIADO` |
| **Patrón relacionado** | Facade (ProposalFacade.send_to_congress) |

**Flujo principal:**
1. La Facade crea un registro de envío con ID de propuesta, hash y timestamp.
2. El estado de la propuesta cambia a `ENVIADA_AL_CONGRESO`.
3. El registro queda disponible en la interfaz.

---

## Historias de Usuario (resumen ágil)

| ID | Historia |
|----|----------|
| HU-01 | **Como** ciudadano, **quiero** registrarme en el sistema, **para** poder participar en propuestas legislativas. |
| HU-02 | **Como** ciudadano, **quiero** ver las propuestas activas, **para** conocer las iniciativas en curso. |
| HU-03 | **Como** ciudadano verificado, **quiero** firmar una propuesta, **para** apoyar una iniciativa legislativa. |
| HU-04 | **Como** ciudadano verificado, **quiero** crear una propuesta, **para** impulsar cambios normativos desde la sociedad civil. |
| HU-05 | **Como** ciudadano verificado, **quiero** comentar y añadir recursos, **para** enriquecer el debate de una propuesta. |
| HU-06 | **Como** proponente, **quiero** que el sistema congele y envíe automáticamente mi propuesta al alcanzar 25,000 firmas, **para** no tener que hacer ese proceso manualmente. |
