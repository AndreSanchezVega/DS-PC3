# Voz del Ciudadano 🗳️

Plataforma digital para el procesamiento de **Iniciativas Legislativas Ciudadanas**, desarrollada como proyecto universitario para el curso de Desarrollo de Software.

## Descripción

El sistema permite a colectivos civiles crear propuestas normativas, recolectar firmas de apoyo y, al alcanzar el límite constitucional de **25,000 firmas digitales válidas** en un plazo máximo de **90 días**, congelar criptográficamente el archivo y enviarlo automáticamente a la Oficina del Congreso.

## Patrones Estructurales Implementados

| Patrón | Clase principal | Propósito |
|--------|----------------|-----------|
| **Composite** | `ProposalDocument` | El documento de propuesta es un árbol de secciones, adjuntos y firmas |
| **Proxy** | `CitizenVerificationProxy` | Controla que solo ciudadanos verificados puedan firmar |
| **Decorator** | `CommentDecorator`, `ResourceDecorator`, `ModificationDecorator` | Añade dinámicamente elementos a una propuesta |
| **Adapter** | `IDVerificationAdapter` | Adapta distintos servicios de verificación de identidad |
| **Facade** | `ProposalFacade` | Punto de entrada único que orquesta creación, firma, congelamiento y envío |

## Estructura del Proyecto

```
DS-PC3/
├── docs/                        # Documentación del sistema
│   ├── requisitos_funcionales.md
│   ├── casos_de_uso.md
│   └── casos_de_prueba.md
├── src/                         # Código fuente
│   ├── models/                  # Modelos de dominio
│   ├── patterns/                # Implementación de patrones
│   ├── templates/               # Vistas HTML (Flask)
│   └── app.py                   # Servidor Flask
├── tests/                       # Casos de prueba (pytest)
└── requirements.txt
```

## Requisitos

- Python 3.10+
- Flask 3.x
- pytest

## Instalación y ejecución

```bash
pip install -r requirements.txt
cd src
python app.py
```

Luego abrir `http://localhost:5000` en el navegador.

## Tecnologías

- **Backend**: Python + Flask
- **Frontend**: HTML + Bootstrap 5
- **Patrones**: GoF Estructurales (Composite, Proxy, Decorator, Adapter, Facade)
- **Testing**: pytest

---

*Proyecto académico — Universidad — Curso Desarrollo de Software*
