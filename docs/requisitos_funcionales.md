# Requisitos Funcionales — Voz del Ciudadano

## Contexto del Sistema

El Legislativo de la República requiere la plataforma digital **"Voz del Ciudadano"** para automatizar el procesamiento de Iniciativas Legislativas Ciudadanas. La plataforma permite a colectivos civiles crear propuestas normativas y recolectar firmas de apoyo. Al alcanzar **25,000 firmas digitales válidas** en un plazo máximo de **90 días**, el sistema congela criptográficamente el archivo y lo envía a la Oficina del Congreso.

---

## Actores del Sistema

| Actor | Descripción |
|-------|-------------|
| **Ciudadano no verificado** | Usuario registrado sin verificación de identidad completada |
| **Ciudadano verificado** | Usuario con DPI/cédula validada, puede firmar propuestas |
| **Proponente** | Ciudadano verificado que crea y gestiona una propuesta |
| **Sistema** | Componente automatizado que ejecuta congelamiento y envío |
| **Oficina del Congreso** | Receptor final de las propuestas congeladas |

---

## Requisitos Funcionales

### RF-01 — Registro y Autenticación de Ciudadanos
El sistema debe permitir a cualquier persona registrarse con nombre, correo electrónico y número de identificación (DPI/cédula).

**Criterios de aceptación:**
- El correo electrónico debe ser único en el sistema.
- El número de identificación debe tener formato válido (numérico, longitud definida).
- El sistema debe diferenciar ciudadanos verificados de no verificados.

---

### RF-02 — Verificación de Identidad del Ciudadano
El sistema debe verificar la identidad del ciudadano antes de permitirle firmar propuestas, mediante un servicio de validación de DPI/cédula.

**Criterios de aceptación:**
- Un ciudadano no verificado puede ver propuestas pero no firmarlas.
- La verificación debe ser procesada por un adaptador que soporte distintos proveedores de validación (simulado en demo).
- El estado de verificación debe quedar registrado en el perfil del ciudadano.

> **Patrón aplicado:** Adapter (IDVerificationAdapter), Proxy (CitizenVerificationProxy)

---

### RF-03 — Creación de Propuestas Legislativas
El sistema debe permitir a un ciudadano verificado crear una propuesta normativa, especificando título, descripción y texto del proyecto de ley.

**Criterios de aceptación:**
- Solo ciudadanos verificados pueden crear propuestas.
- La propuesta debe contener: título (máx. 200 caracteres), descripción breve, cuerpo del texto normativo.
- Al crearse, la propuesta inicia su contador de 90 días automáticamente.
- El estado inicial de la propuesta es `ACTIVA`.

> **Patrón aplicado:** Facade (ProposalFacade), Composite (ProposalDocument)

---

### RF-04 — Firma Digital de Propuestas
El sistema debe permitir a ciudadanos verificados firmar una propuesta activa, registrando la firma como única por ciudadano.

**Criterios de aceptación:**
- Un ciudadano solo puede firmar una propuesta una vez.
- No se puede firmar una propuesta con estado `CONGELADA` o `EXPIRADA`.
- Cada firma se registra con fecha, hora y hash del ciudadano.
- El contador de firmas se actualiza en tiempo real.

> **Patrón aplicado:** Proxy (CitizenVerificationProxy)

---

### RF-05 — Adición de Comentarios a Propuestas
El sistema debe permitir a ciudadanos verificados añadir comentarios de apoyo o análisis a una propuesta activa.

**Criterios de aceptación:**
- El comentario debe incluir texto (máx. 1,000 caracteres) y el autor.
- Los comentarios se muestran en orden cronológico en la vista de detalle.
- No se pueden añadir comentarios a propuestas congeladas o expiradas.

> **Patrón aplicado:** Decorator (CommentDecorator)

---

### RF-06 — Adición de Recursos de Apoyo
El sistema debe permitir adjuntar recursos externos (URLs de documentos, estudios o referencias) que respalden la propuesta.

**Criterios de aceptación:**
- El recurso debe incluir: título descriptivo y URL válida.
- Se pueden añadir múltiples recursos a una misma propuesta.
- Los recursos se visualizan en la sección de "Recursos de apoyo" en la vista de detalle.

> **Patrón aplicado:** Decorator (ResourceDecorator)

---

### RF-07 — Adición de Modificaciones a Propuestas
El sistema debe permitir al proponente registrar modificaciones o enmiendas al texto original de la propuesta.

**Criterios de aceptación:**
- Solo el proponente (creador) puede añadir modificaciones.
- La modificación debe incluir: descripción del cambio y texto modificado.
- Las modificaciones se registran con fecha y se muestran en el historial.

> **Patrón aplicado:** Decorator (ModificationDecorator)

---

### RF-08 — Estructura Jerárquica del Documento de Propuesta
El sistema debe representar internamente el documento de la propuesta como una estructura jerárquica de componentes (secciones, subsecciones, adjuntos, firmas).

**Criterios de aceptación:**
- El documento raíz contiene secciones de: encabezado, cuerpo normativo, firmas y anexos.
- Cada sección puede contener subsecciones anidadas.
- El sistema puede renderizar el árbol completo del documento para su visualización y exportación.

> **Patrón aplicado:** Composite (ProposalDocument, ProposalSection, ProposalLeaf)

---

### RF-09 — Congelamiento Criptográfico de Propuestas
Al alcanzar 25,000 firmas válidas o expirar los 90 días con firmas insuficientes, el sistema debe cambiar el estado de la propuesta y registrar un hash SHA-256 del contenido.

**Criterios de aceptación:**
- Al alcanzar 25,000 firmas: estado cambia a `CONGELADA`, se genera hash SHA-256 del documento completo.
- Al expirar 90 días sin alcanzar el límite: estado cambia a `EXPIRADA`.
- Una vez congelada, ningún campo del documento puede modificarse.

> **Patrón aplicado:** Facade (ProposalFacade)

---

### RF-10 — Envío Automático al Congreso
Al congelarse una propuesta, el sistema debe notificar automáticamente a la Oficina del Congreso con el documento y su hash criptográfico.

**Criterios de aceptación:**
- Se genera un registro de envío con: ID de propuesta, hash, fecha y hora de congelamiento.
- El envío queda registrado en el sistema con estado `ENVIADO`.
- La propuesta muestra el estado `ENVIADA AL CONGRESO` en la interfaz.

> **Patrón aplicado:** Facade (ProposalFacade)

---

## Requisitos No Funcionales (referencia)

| ID | Requisito |
|----|-----------|
| RNF-01 | El sistema debe responder en menos de 2 segundos para operaciones de firma |
| RNF-02 | Las contraseñas deben almacenarse con hash (SHA-256) |
| RNF-03 | El sistema debe soportar al menos 500 usuarios concurrentes |
| RNF-04 | La interfaz debe ser responsive (Bootstrap 5) |
