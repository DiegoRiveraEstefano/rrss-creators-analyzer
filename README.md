# RRSS Creators Analyzer

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![Django 6.0](https://img.shields.io/badge/django-6.0-092E20.svg)](https://www.djangoproject.com/)
[![Bootstrap 5](https://img.shields.io/badge/bootstrap-5.x-7952B3.svg)](https://getbootstrap.com/)

**RRSS Creators Analyzer** es una plataforma integral desarrollada en **Django 6.0** diseñada para el seguimiento, auditoría, analítica y gestión de creadores de contenido y streamers (`Twitch`, `YouTube`, `Kick`, `TikTok`) pertenecientes a una compañía o agencia.

> [!IMPORTANT]
> **Arquitectura Single-Tenant / Single-Company**: A diferencia del esquema legado (ver [`old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations)), este sistema está diseñado específicamente para operar como una plataforma **single-tenant** para una única compañía. El entorno de **producción** está configurado para operar con **PostgreSQL** (con driver nativo `psycopg` 3) y **Redis** (para caché distribuida con `django-redis` y broker/backend de Celery), mientras que en desarrollo y pruebas locales soporta de forma transparente **SQLite** (en modo WAL optimizado) y **DiskCache** para máxima agilidad operativa.

---

## Tabla de Contenidos

1. [Características Principales](#características-principales)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Documentación del Proyecto](#documentación-del-proyecto)
4. [Requisitos e Instalación Local](#requisitos-e-instalación-local)
5. [Despliegue con Docker Compose (Producción)](#despliegue-con-docker-compose-producción)
6. [Comandos de Desarrollo y Calidad](#comandos-de-desarrollo-y-calidad)
7. [Estructura del Proyecto](#estructura-del-proyecto)
8. [Licencia](#licencia)

---

## Características Principales

- **Directorio de Creadores y Canales (`creators`)**:
  - Gestión centralizada del roster de creadores (`active`, `inactive`, `suspended`) y vinculación opcional con cuentas de usuario del sistema.
  - Seguimiento multi-plataforma (`Twitch`, `YouTube`, `Kick`, `TikTok`) con métricas de seguidores, suscriptores y estado en vivo.
- **Asistentes en Múltiples Pasos (`django-formtools`)**:
  - Incorporación guiada de talentos (`creators` / `contracts`): alta de perfil, vinculación de canales por plataforma y configuración de términos contractuales con reparto de ingresos (*revenue split*).
  - Flujos secuenciales para la configuración de campañas de patrocinio (`campaigns`), cierre de liquidaciones contables mensuales (`payouts`) y asistentes de ingesta masiva con mapeo interactivo de columnas (`imports`).
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
  - Rankings globales de creadores (por ingresos combinados, CCV y horas transmitidas), resúmenes financieros mensuales y rendimiento comparativo por categoría/plataforma utilizando el ORM de Django y caché (`Redis` en producción / `DiskCache` en local).

---

## Stack Tecnológico

### Backend y Persistencia
- **Lenguaje**: Python `3.14.x` (gestionado con `uv`).
- **Framework Web**: Django `6.0.9` (Server-Side Rendering HTML-first, potenciado al máximo con sus capacidades nativas).
- **Base de Datos**:
  - **Producción**: **PostgreSQL 16+** con `psycopg` 3 (`django.db.backends.postgresql`), transacciones atómicas (`ATOMIC_REQUESTS=True`) y persistencia en volumen `postgres_data`.
  - **Desarrollo y Testing**: **SQLite 3** (`PRAGMA journal_mode=WAL;`, `synchronous=NORMAL;`, `busy_timeout=5000;`, `foreign_keys=ON;`) o PostgreSQL.
- **Caché y Tareas Asíncronas**:
  - **Producción**: **Redis 7+** mediante `django-redis` y `redis-py` para caché de baja latencia (`CACHES["default"]`), gestión de sesiones y broker/result backend de **Celery** y **Celery Beat**.
  - **Desarrollo y Testing**: `diskcache` (`diskcache.DjangoCache`) y memoria local (`LocMemCache`) para desarrollo contenido.
- **Autenticación y Seguridad**: `django-allauth[mfa]` con soporte MFA, hash de contraseñas con `Argon2`, control de acceso basado en roles (`Groups` y `Permissions` nativos de Django: `company_admin`, `manager`, `analyst`, `creator`).

### Librerías Core del Ecosistema Django (Uso Prioritario)
- **Tablas de Datos**: `django-tables2` para listados paginados, ordenamiento multi-columna y exportación.
- **Filtrado**: `django-filter` para búsquedas declarativas y filtros combinados en vistas y APIs.
- **Formularios y Asistentes Multi-Paso**: `django-crispy-forms` + `crispy-bootstrap5` para layouts estructurados, `django-formtools` (`SessionWizardView`) para flujos secuenciales guiados (onboarding, contratos, campañas, liquidaciones) y `django-widget-tweaks` para ajustes granulares en plantillas HTML.
- **Autocompletado y Etiquetas**: `django-autocomplete-light` (DAL) para selectores relacionales y `django-taggit` para categorización.
- **Importación/Exportación e Historial**: `django-import-export` y `django-simple-history`.

### Frontend (Sin Frameworks JS Pesados)
- **HTML**: HTML5 estrictamente semántico (`<main>`, `<section>`, `<article>`, `<nav>`, `<aside>`, `<header>`, `<figure>`).
- **Estilos**: **Bootstrap 5** (`crispy-bootstrap5`) combinado con variables CSS nativas para temas e indicadores de plataforma.
- **Interactividad**: **JavaScript Vanilla (ES6+)** para lógica ligera y **Web Components nativos (Custom Elements)** para widgets interactivos complejos (gráficos, selectores de rangos, previsualizadores).

---

## Documentación del Proyecto

Toda la normativa técnica, arquitectónica y de diseño del proyecto se encuentra documentada en los siguientes archivos en la raíz del repositorio:

- [`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md): Documentación general de la arquitectura, modelo de dominio (migración desde [`old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations) a modelos de Django), asistentes multi-paso (`django-formtools`), configuración de bases de datos (PostgreSQL/SQLite) y caché (Redis/DiskCache), y flujos de negocio.
- [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md): Reglas arquitectónicas del proyecto (Capas `Models -> Selectors -> Services -> Views`, uso obligatorio de `django-tables2`, `django-filter`, `django-crispy-forms`, `django-formtools` y `django-widget-tweaks`, política estricta de Signals y TDD).
- [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/STYLE_GUIDE.md): Guía de estilo de código para Python (Ruff, Mypy), plantillas Django (`djLint`), HTML5 semántico, Bootstrap 5, asistentes multi-paso, JS Vanilla y Web Components.
- [`DESING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DESING.md): Guía de diseño UI/UX, paleta de colores por plataforma (`Twitch`, `YouTube`, `Kick`, `TikTok`), componentes de dashboards, steppers/asistentes multi-paso, tablas analíticas y accesibilidad.
- [`SECURITY.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/SECURITY.md): Política de seguridad, matriz de permisos por rol (RBAC en Django), protección de datos en PostgreSQL/Redis/SQLite, y reporte de vulnerabilidades.
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
   Crea un archivo `.env` en la raíz del proyecto (o utiliza los archivos base en `.envs/`):
   ```ini
   DJANGO_DEBUG=True
   DJANGO_SECRET_KEY=dev-secret-key-change-in-production
   DJANGO_READ_DOT_ENV_FILE=True
   DATABASE_URL=sqlite:///db.sqlite3
   REDIS_URL=redis://localhost:6379/0
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

## Despliegue con Docker Compose (Producción)

El stack de producción está contenerizado y orquestado mediante [`docker-compose.yml`](file:///home/diego/Proyectos/rrss-creators-analyzer/docker-compose.yml), el cual aprovisiona:

1. **`postgres`**: PostgreSQL 16 Alpine con healthcheck (`pg_isready`) y volumen persistente `postgres_data`.
2. **`redis`**: Redis 7 Alpine con healthcheck (`redis-cli ping`) y volumen persistente `redis_data`.
3. **`web`**: Aplicación Django 6 servida mediante Gunicorn y Uvicorn workers (`config.asgi:application`), con migraciones automáticas y recolección de estáticos en el arranque.
4. **`celery_worker`**: Worker de Celery para procesamiento de tareas asíncronas en segundo plano.
5. **`celery_beat`**: Planificador de tareas periódicas (`DatabaseScheduler`).

### Comandos de Despliegue

```bash
# 1. Combinar variables de entorno de producción (o definir .env)
uv run python merge_production_dotenvs_in_dotenv.py

# 2. Construir e iniciar todos los servicios en segundo plano
docker compose up -d --build

# 3. Verificar estado de los servicios y healthchecks
docker compose ps

# 4. Ver logs en tiempo real
docker compose logs -f web
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
├── compose/                        # Scripts de arranque y entrypoints de Docker (web, celery)
├── config/                         # Configuración global de Django (settings, urls, wsgi/asgi, celery)
│   └── settings/                   # Configuraciones modulares (base, local, production, test)
├── docs/                           # Documentación técnica, requerimientos y esquemas SQL
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
│   ├── analytics/                  # Dashboards, rankings y reportes agregados
│   ├── static/                     # Archivos estáticos (CSS Bootstrap 5, JS Vanilla y Web Components)
│   └── templates/                  # Plantillas HTML5 semánticas (SSR)
└── tests/                          # Pruebas de integración transversales
```

---

## Licencia

Distribuido bajo la licencia **GPLv3**. Consulta el archivo [`LICENSE`](file:///home/diego/Proyectos/rrss-creators-analyzer/LICENSE) y [`COPYING`](file:///home/diego/Proyectos/rrss-creators-analyzer/COPYING) para más detalles.
