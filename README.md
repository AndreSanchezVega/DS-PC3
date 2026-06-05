# Voz del Ciudadano

Plataforma digital para el procesamiento de **Iniciativas Legislativas Ciudadanas**, desarrollada como proyecto universitario para el curso de Desarrollo de Software.

## Descripción

El sistema permite a colectivos civiles crear propuestas normativas y recolectar firmas de apoyo. Al alcanzar el límite constitucional de **25,000 firmas digitales válidas** en un plazo máximo de **90 días**, el sistema congela criptográficamente el documento (SHA-256) y lo envía automáticamente a la Oficina del Congreso.

## Patrones Estructurales Implementados

| # | Patrón | Clase principal | Propósito |
|---|--------|----------------|-----------|
| 1 | **Composite** | `ProposalDocument` | Documento como árbol jerárquico de secciones y hojas |
| 2 | **Proxy** | `CitizenVerificationProxy` | Controla que solo ciudadanos verificados puedan firmar o crear propuestas |
| 3 | **Decorator** | `CommentDecorator`, `ResourceDecorator`, `ModificationDecorator` | Añade comentarios, recursos y modificaciones dinámicamente |
| 4 | **Adapter** | `IDVerificationAdapter` | Adapta distintos proveedores de verificación de identidad (Registro Civil, Biométrico) |
| 5 | **Facade** | `ProposalFacade` | Punto de entrada único que orquesta todos los subsistemas |

## Estructura del Proyecto

```
DS-PC3/
├── docs/
│   ├── requisitos_funcionales.md   # 10 RF con criterios de aceptación
│   ├── casos_de_uso.md             # 12 CU + 6 historias de usuario
│   └── casos_de_prueba.md          # 18 casos de prueba
├── src/
│   ├── models/
│   │   ├── citizen.py              # Modelo Ciudadano
│   │   ├── proposal.py             # Modelo Propuesta (máquina de estados)
│   │   └── signature.py            # Modelo Firma digital
│   ├── patterns/
│   │   ├── composite.py            # Patrón Composite
│   │   ├── proxy.py                # Patrón Proxy
│   │   ├── decorator.py            # Patrón Decorator
│   │   ├── adapter.py              # Patrón Adapter
│   │   └── facade.py               # Patrón Facade
│   ├── templates/
│   │   ├── base.html               # Layout base Bootstrap 5
│   │   ├── dashboard.html          # Pantalla 1: listado de propuestas
│   │   └── proposal_detail.html    # Pantalla 2: detalle + firmas + árbol Composite
│   └── app.py                      # Servidor Flask
├── tests/
│   └── test_patterns.py            # 22 casos de prueba (pytest)
└── requirements.txt
```

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
py -m pip install -r requirements.txt
```

## Ejecutar la aplicación

```bash
py -m flask --app src/app run
```

Luego abrir **http://127.0.0.1:5000** en el navegador.

## Ejecutar los tests

```bash
py -m pytest tests/ -v
```

Resultado esperado: **22 passed**

## Tecnologías

- **Backend**: Python 3.11 + Flask 3.1
- **Frontend**: HTML + Bootstrap 5 + Bootstrap Icons
- **Patrones**: GoF Estructurales (Composite, Proxy, Decorator, Adapter, Facade)
- **Testing**: pytest 9.0

---

*Proyecto académico — Curso Desarrollo de Software*
