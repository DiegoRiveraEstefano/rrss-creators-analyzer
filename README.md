# RRSS Creators Analyzer

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![Django 6.0](https://img.shields.io/badge/django-6.0-092E20.svg)](https://www.djangoproject.com/)
[![Bootstrap 5](https://img.shields.io/badge/bootstrap-5.x-7952B3.svg)](https://getbootstrap.com/)

**RRSS Creators Analyzer** es una plataforma integral desarrollada en **Django 6.0** diseñada para el seguimiento, auditoría, analítica y gestión de creadores de contenido y streamers (`Twitch`, `YouTube`, `Kick`, `TikTok`) pertenecientes a una compañía o agencia.

> [!IMPORTANT]
> **Arquitectura Single-Tenant / Single-Company**: A diferencia del esquema legado (ver [`old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations)), este sistema está diseñado específicamente para operar como una plataforma **single-tenant** para una única compañía. Por restricciones de infraestructura y simplicidad operativa en el despliegue, utiliza **SQLite** (en modo WAL optimizado) como motor de base de datos principal y **DiskCache** / memoria local para el sistema de caché.

---

## Tabla de Contenidos

1. [Características Principales](#características-principales)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Documentación del Proyecto](#documentación-del-proyecto)
4. [Requisitos e Instalación Local](#requisitos-e-instalación-local)
5. [Comandos de Desarrollo y Calidad](#comandos-de-desarrollo-y-calidad)
6. [Estructura del Proyecto](#estructura-del-proyecto)
7. [Licencia](#licencia)

---

## Características Principales

- **Directorio de Creadores y Canales (`creators`)**:
  - Gestión centralizada del roster de creadores (`active`, `inactive`, `suspended`) y vinculación opcional con cuentas de usuario del sistema.
  - Seguimiento multi-plataforma (`Twitch`, `YouTube`, `Kick`, `TikTok`) con métricas de seguidores, suscriptores y estado en vivo.
- **Analítica de Sesiones de Streaming (`streams`)**:
  - Registro detallado de transmisiones en vivo: duración, horas transmitidas, media de espectadores concurrentes (`avg_ccv`), pico de espectadores (`peak_viewers`), interacción en chat y nuevos seguidores.
  - Desglose financiero por sesión: ingresos por publicidad (`ad_revenue`), suscripciones (`subs_revenue`), donaciones (`donations_revenue`), ingresos totales e ingresos por hora (`earnings_per_hour`).
- **Gestión de Activos de Video y Publicaciones (`videos`)**:
  - Arquitectura en 3 entidades adaptada del sistema legado:
    1. **Videos (`Video`)**: Activo digital maestro, costos de producción, categoría, estado editorial (`draft`, `editing`, `ready`, `published`, `archived`) y etiquetas con `django-taggit`.
    2. **Publicaciones (`VideoPublication`)**: Distribución por plataforma (`standard`, `short/reel`, `vod`, `clip`, `teaser`) con métricas de vistas, likes, comentarios, compartidos, horas de visualización, `engagement_rate`, `estimated_revenue`, `net_profit`, `ROI` y `RPM`.
    3. **Relaciones (`VideoRelation`)**: Trazabilidad entre videos y sesiones de streaming en vivo (`derived_from_live`, `continuation`, `sequel`, `clip`, `spin_off`).
- **Sistema de Alertas y Sanciones (`alerts`)**:
  - Monitoreo de incidencias de canal: strikes de DMCA (`dmca_strike`), violaciones de términos de servicio (`tos_violation`), caídas inusuales de tráfico (`unusual_drop`) o tráfico sospechoso (`suspicious_traffic`).
  - Flujo de severidad (`info`, `warning`, `critical`) y estados de resolución (`active`, `resolved`, `appealed`).
- **Importación Masiva y Auditoría (`imports`)**:
  - Procesamiento y validación de lotes de datos (`ImportBatch`) mediante `django-import-export`.
  - Trazabilidad completa de cambios en modelos críticos mediante `django-simple-history`.
- **Dashboards y Reportes Consolidados (`analytics`)**:
  - Rankings globales de creadores (por ingresos combinados, CCV y horas transmitidas), resúmenes financieros mensuales y rendimiento comparativo por categoría/plataforma utilizando el ORM de Django y caché en disco (`DiskCache`).

---

## Stack Tecnológico

### Backend y Persistencia
- **Lenguaje**: Python `3.14.x` (gestionado con `uv`).
- **Framework Web**: Django `6.0.9` (Server-Side Rendering HTML-first, potenciado al máximo con sus capacidades nativas).
- **Base de Datos**: **SQLite 3** (configurado con `PRAGMA journal_mode=WAL;`, `synchronous=NORMAL`, `busy_timeout=5000` y `foreign_keys=ON` para alta concurrencia de lectura y despliegues contenidos).
- **Caché**: **DiskCache** (`diskcache`) en disco y `LocMemCache` en memoria para almacenar agregaciones analíticas, rankings y fragmentos de plantillas sin requerir demonios externos en despliegues restringidos.
- **Autenticación y Seguridad**: `django-allauth[mfa]` con soporte MFA, hash de contraseñas con `Argon2`, control de acceso basado en roles (`Groups` y `Permissions` nativos de Django: `company_admin`, `manager`, `analyst`, `creator`).

### Librerías Core del Ecosistema Django (Uso Prioritario)
- **Tablas de Datos**: `django-tables2` para listados paginados, ordenamiento multi-columna y exportación.
- **Filtrado**: `django-filter` para búsquedas declarativas y filtros combinados en vistas y APIs.
- **Formularios**: `django-crispy-forms` + `crispy-bootstrap5` para layouts estructurados y `django-widget-tweaks` para ajustes granulares en plantillas HTML.
- **Autocompletado y Etiquetas**: `django-autocomplete-light` (DAL) para selectores relacionales y `django-taggit` para categorización.
- **Importación/Exportación e Historial**: `django-import-export` y `django-simple-history`.

### Frontend (Sin Frameworks JS Pesados)
- **HTML**: HTML5 estrictamente semántico (`<main>`, `<section>`, `<article>`, `<nav>`, `<aside>`, `<header>`, `<figure>`).
- **Estilos**: **Bootstrap 5** (`crispy-bootstrap5`) combinado con variables CSS nativas para temas e indicadores de plataforma.
- **Interactividad**: **JavaScript Vanilla (ES6+)** para lógica ligera y **Web Components nativos (Custom Elements)** para widgets interactivos complejos (gráficos, selectores de rangos, previsualizadores).

---

## Documentación del Proyecto

Toda la normativa técnica, arquitectónica y de diseño del proyecto se encuentra documentada en los siguientes archivos en la raíz del repositorio:

- [`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md): Documentación general de la arquitectura, modelo de dominio (migración desde [`old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations) a modelos de Django), configuración de SQLite + DiskCache y flujos de negocio.
- [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md): Reglas arquitectónicas del proyecto (Capas `Models -> Selectors -> Services -> Views`, uso obligatorio de `django-tables2`, `django-filter`, `django-crispy-forms` y `django-widget-tweaks`, política estricta de Signals y TDD).
- [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/STYLE_GUIDE.md): Guía de estilo de código para Python (Ruff, Mypy), plantillas Django (`djLint`), HTML5 semántico, Bootstrap 5, JS Vanilla y Web Components.
- [`DESING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DESING.md): Guía de diseño UI/UX, paleta de colores por plataforma (`Twitch`, `YouTube`, `Kick`, `TikTok`), componentes de dashboards, tablas analíticas y accesibilidad.
- [`SECURITY.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/SECURITY.md): Política de seguridad, matriz de permisos por rol (RBAC en Django), protección de datos financieros, seguridad en SQLite/DiskCache y reporte de vulnerabilidades.
- [`CONTRIBUTING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CONTRIBUTING.md): Flujo de trabajo con Git, estándares de Conventional Commits, requisitos de pruebas con `pytest` y lista de verificación para Pull Requests.
- [`AGENTS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/AGENTS.md): Instrucciones operativas y contexto rápido para agentes de IA y asistentes de código que trabajen en este repositorio.
- [`CHANGELOG.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CHANGELOG.md): Registro histórico de cambios siguiendo el estándar *Keep a Changelog*.

---

## Requisitos e Instalación Local

### Prerrequisitos
- **Python**: `3.14.x`
- **Gestor de paquetes**: [`uv`](https://docs.astral.sh/uv/)

### Pasos de Configuración

1. **Clonar el repositorio e instalar dependencias**:
   ```bash
   uv sync --all-groups
   ```

2. **Configurar variables de entorno**:
   Crea un archivo `.env` en la raíz del proyecto (o configura las variables en tu entorno):
   ```ini
   DJANGO_DEBUG=True
   DJANGO_SECRET_KEY=dev-secret-key-change-in-production
   DJANGO_READ_DOT_ENV_FILE=True
   DATABASE_URL=sqlite:///db.sqlite3
   ```

3. **Ejecutar migraciones de base de datos**:
   ```bash
   uv run python manage.py migrate
   ```

4. **Crear un superusuario**:
   ```bash
   uv run python manage.py createsuperuser
   ```

5. **Iniciar el servidor de desarrollo**:
   ```bash
   uv run python manage.py runserver
   ```

---

## Comandos de Desarrollo y Calidad

### Pruebas Automatizadas y Cobertura (`pytest`)
```bash
# Ejecutar toda la suite de tests
uv run pytest

# Ejecutar con reporte de cobertura
uv run coverage run -m pytest
uv run coverage html
```

### Verificación de Tipos y Linting
```bash
# Chequeo estático de tipos con Mypy
uv run mypy rrss_creatos_analyzer

# Linting y formato de Python con Ruff
uv run ruff check .
uv run ruff format --check .

# Linting y formato de plantillas Django/HTML5 con djLint
uv run djlint rrss_creatos_analyzer/templates --lint
uv run djlint rrss_creatos_analyzer/templates --reformat
```

---

## Estructura del Proyecto

```text
rrss-creators-analyzer/
├── config/                         # Configuración global de Django (settings, urls, wsgi/asgi)
├── docs/                           # Documentación Sphinx adicional
├── old-migrations/                 # Referencia histórica del esquema SQL anterior (PostgreSQL/Supabase)
├── rrss_creatos_analyzer/          # Paquete principal de la aplicación
│   ├── contrib/                    # Extensiones de contrib (sites)
│   ├── core/                       # Mixins base (BaseModel, BaseService, BaseSelector, utilidades de caché)
│   ├── users/                      # Gestión de usuarios, perfiles y roles de la compañía
│   ├── creators/                   # Directorio de streamers/creadores y canales por plataforma
│   ├── streams/                    # Sesiones de streaming en vivo y métricas de audiencia/ingresos
│   ├── videos/                     # Activos de video, publicaciones por plataforma y relaciones
│   ├── alerts/                     # Alertas de canal, strikes DMCA/TOS e incidencias
│   ├── imports/                    # Lotes de importación masiva (CSV/XLSX) y auditoría
│   ├── analytics/                  # Dashboards, rankings y reportes agregados cacheados en DiskCache
│   ├── static/                     # Archivos estáticos (CSS Bootstrap 5, JS Vanilla y Web Components)
│   └── templates/                  # Plantillas HTML5 semánticas (SSR)
└── tests/                          # Pruebas de integración transversales
```

---

## Licencia

Distribuido bajo la licencia **GPLv3**. Consulta el archivo [`LICENSE`](file:///home/diego/Proyectos/rrss-creators-analyzer/LICENSE) y [`COPYING`](file:///home/diego/Proyectos/rrss-creators-analyzer/COPYING) para más detalles.
