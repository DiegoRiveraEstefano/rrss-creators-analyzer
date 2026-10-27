# Changelog

Todos los cambios notables en **RRSS Creators Analyzer** se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Configuración de Ambiente de Producción para PostgreSQL y Redis**:
  - Configuración de `config/settings/production.py` para usar **PostgreSQL** mediante `psycopg` 3 (`DATABASES["default"] = env.db("DATABASE_URL")`) con transacciones atómicas (`ATOMIC_REQUESTS = True`) y reutilización de conexiones (`CONN_MAX_AGE`).
  - Configuración de la capa de caché distribuida en producción con **Redis** mediante `django-redis` (`django_redis.cache.RedisCache`), con tolerancia a caídas e integración con `REDIS_URL`.
  - Centralización de `REDIS_URL` para Celery Broker, Celery Result Backend y la caché de Django.
  - Actualización de dependencias en `pyproject.toml` y `uv.lock`: inclusión de `psycopg[binary]==3.3.6`, `django-redis==7.0.0` y `redis==8.1.0` en dependencias de producción del proyecto.
  - Reconfiguración integral de [`docker-compose.yml`](file:///home/diego/Proyectos/rrss-creators-analyzer/docker-compose.yml):
    - Servicio `postgres:16-alpine` con persistencia en `postgres_data`, variables de autenticación y healthcheck (`pg_isready`).
    - Servicio `redis:7-alpine` con persistencia en `redis_data` y healthcheck (`redis-cli ping`).
    - Configuración de `DATABASE_URL` y dependencias saludables (`postgres` y `redis` en `condition: service_healthy`) en los servicios `web`, `celery_worker` y `celery_beat`.
  - Actualización de scripts de contenedor ([`compose/web/entrypoint.sh`](file:///home/diego/Proyectos/rrss-creators-analyzer/compose/web/entrypoint.sh) y [`compose/celery/entrypoint.sh`](file:///home/diego/Proyectos/rrss-creators-analyzer/compose/celery/entrypoint.sh)) con comprobación activa de disponibilidad de PostgreSQL antes de ejecutar migraciones o iniciar workers.
  - Actualización de `Dockerfile.web`, `Dockerfile.celery` y `Dockerfile` incorporando bibliotecas `libpq-dev` y `libpq5`.
  - Adición de `DATABASE_URL` en [`.envs/.production/.postgres`](file:///home/diego/Proyectos/rrss-creators-analyzer/.envs/.production/.postgres) y regeneración de [`.env`](file:///home/diego/Proyectos/rrss-creators-analyzer/.env).
  - Actualización de la documentación en [`README.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/README.md), [`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md), [`SECURITY.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/SECURITY.md) y [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md).
- **Módulo de Gestión de Horarios y Cumplimiento (`schedules`)**:
  - Creación de la aplicación Django `rrss_creatos_analyzer.apps.schedules` para la planificación recurrente, generación de slots de transmisión, conciliación automática con emisiones en vivo (`StreamingSession`), auditoría de puntualidad y registro de licencias/excepciones.
  - Modelos relacionales normalizados:
    - `CreatorWeeklySchedule`: Pautas semanales recurrentes con control de solapamiento horario en base de datos.
    - `CreatorScheduleSlot`: Instancias fechadas de transmisión con control de horas pactadas, horas efectivas, desfase de inicio (`start_delay_minutes`) y estado de cumplimiento (`COMPLETED`, `LATE`, `PARTIAL`, `MISSED`, `JUSTIFIED_ABSENCE`).
    - `ScheduleException`: Justificaciones médicas, vacaciones o incidencias con aprobación de agencia y cascada sobre slots.
    - `CreatorScheduleComplianceSummary`: Consolidado mensual para liquidaciones y contratos con ratios de horas, días netos y puntualidad.
  - Servicios desacoplados y atómicos (`PatternService`, `ReconciliationService`, `ComplianceService` unificados en `ScheduleService`).
  - Selectores optimizados con filtrado por rol y consultas agregadas para calendarios y métricas.
  - Tablas (`django-tables2`), Filtros (`django-filter`), Formularios (`django-crispy-forms` / Bootstrap 5) y Vistas CBVs completas.
  - Vistas interactivas de Calendario cronológico de turnos y cumplimiento.
  - Cobertura completa de pruebas unitarias y de integración (41 tests, 100% pasando).
  - Documento de especificación formal de requerimientos en [`docs/requeriments/12_MODULO_SCHEDULES_Y_CUMPLIMIENTO_DE_TRANSMISIONES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/docs/requeriments/12_MODULO_SCHEDULES_Y_CUMPLIMIENTO_DE_TRANSMISIONES.md), con integración en la Matriz de Trazabilidad (`00` y `11`).
- Integración y documentación oficial de **`django-formtools`** (`formtools.wizard.views.SessionWizardView`) para la gestión de formularios y flujos asistidos en múltiples pasos (*wizards*):
  - Actualización de `.agents/rules/` (`views.md`, `templates.md`, `architecture.md`, `structure.md`, `services.md`, `tdd.md`) con patrones canónicos de implementación, integración con `crispy-bootstrap5`, manejo seguro de estado en sesión, desacoplamiento del servicio atómico en `done()` y directivas de testing TDD.
  - Actualización de la documentación técnica ([`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md), [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md), [`AGENTS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/AGENTS.md), [`README.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/README.md), [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/STYLE_GUIDE.md) y [`DESING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DESING.md)) especificando los casos de uso del dominio: *onboarding* de creadores y contratos, configuración de campañas con patrocinadores, liquidaciones financieras mensuales y asistentes interactivos de ingesta masiva.
- Documentación integral del proyecto adaptada a la arquitectura single-tenant en Django:
  - [`README.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/README.md): Resumen ejecutivo, stack tecnológico, estructura y comandos con `uv`.
  - [`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md): Especificación técnica del dominio (`creators`, `streams`, `videos`, `alerts`, `imports`, `analytics`), mapeo de migraciones desde [`old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations).
  - [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md): Reglas de arquitectura en capas (`Models`, `Selectors`, `Services`, `Views`), directivas de uso de `django-tables2`, `django-filter`, `django-crispy-forms`, `django-formtools` y `django-widget-tweaks`, política estricta de Signals y TDD.
  - [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/STYLE_GUIDE.md): Estándares de Python 3.14 (`Ruff`, `Mypy`), HTML5 semántico (`djLint`), Bootstrap 5, JS Vanilla y Web Components.
  - [`DESING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DESING.md): Guía de diseño UI/UX para dashboards analíticos, tokens visuales por plataforma (`Twitch`, `YouTube`, `Kick`, `TikTok`), steppers de asistentes y accesibilidad WCAG 2.1 AA.
  - [`SECURITY.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/SECURITY.md): Política de seguridad, matriz RBAC para la compañía (`company_admin`, `manager`, `analyst`, `creator`).
  - [`CONTRIBUTING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CONTRIBUTING.md): Convenciones de Git, Conventional Commits y flujo de calidad.
  - [`AGENTS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/AGENTS.md): Contexto y directrices operativas para agentes de IA.
- Incorporación en [`old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations) de los esquemas SQL legados como referencia del modelo de dominio.
- Instalación y configuración en [`pyproject.toml`](file:///home/diego/Proyectos/rrss-creators-analyzer/pyproject.toml) de las librerías clave del ecosistema Django:
  - `psycopg` para el motor de base de datos relacional PostgreSQL.
  - `redis` y `django-redis` para la infraestructura de caché distribuida y mensajería.
  - `diskcache` para almacenamiento en caché local en disco/memoria.
  - `django-tables2` para tablas de datos interactivas y exportables.
  - `django-filter` para filtrado declarativo.
  - `django-crispy-forms` y `crispy-bootstrap5` para formularios estilizados con Bootstrap 5.
  - `django-widget-tweaks` para personalización de controles de formulario en plantillas.
  - `django-formtools` para asistentes y formularios en múltiples pasos.
  - `django-autocomplete-light`, `django-import-export`, `django-simple-history` y `django-taggit`.

### Changed
- Adaptación arquitectónica del sistema: modelo **single-tenant (única compañía)** en **Django 6.0** configurado para operar con **PostgreSQL** y **Redis** en producción, y **SQLite** (modo WAL) y **DiskCache** en desarrollo/pruebas locales.

---

## [0.1.0] - 2026-10-25

### Added
- Inicialización del proyecto base con **Cookiecutter Django** (Python `3.14`, Django `6.0.9`).
- Aplicación inicial `users` con `django-allauth[mfa]` y hash de contraseñas Argon2.
- Configuración de herramientas de calidad: `ruff`, `mypy`, `djlint`, `pytest` y `coverage`.
