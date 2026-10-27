# Changelog

Todos los cambios notables en **RRSS Creators Analyzer** se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Integración y documentación oficial de **`django-formtools`** (`formtools.wizard.views.SessionWizardView`) para la gestión de formularios y flujos asistidos en múltiples pasos (*wizards*):
  - Actualización de `.agents/rules/` (`views.md`, `templates.md`, `architecture.md`, `structure.md`, `services.md`, `tdd.md`) con patrones canónicos de implementación, integración con `crispy-bootstrap5`, manejo seguro de estado en sesión, desacoplamiento del servicio atómico en `done()` y directivas de testing TDD.
  - Actualización de la documentación técnica ([`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md), [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md), [`AGENTS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/AGENTS.md), [`README.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/README.md), [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/STYLE_GUIDE.md) y [`DESING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DESING.md)) especificando los casos de uso del dominio: *onboarding* de creadores y contratos, configuración de campañas con patrocinadores, liquidaciones financieras mensuales y asistentes interactivos de ingesta masiva.
- Documentación integral del proyecto adaptada a la arquitectura single-tenant en Django:
  - [`README.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/README.md): Resumen ejecutivo, stack tecnológico, estructura y comandos con `uv`.\
  - [`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md): Especificación técnica del dominio (`creators`, `streams`, `videos`, `alerts`, `imports`, `analytics`), mapeo de migraciones desde [`old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations) y arquitectura de caché con `DiskCache` sobre `SQLite`.
  - [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md): Reglas de arquitectura en capas (`Models`, `Selectors`, `Services`, `Views`), directivas de uso de `django-tables2`, `django-filter`, `django-crispy-forms`, `django-formtools` y `django-widget-tweaks`, política estricta de Signals y TDD.
  - [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/STYLE_GUIDE.md): Estándares de Python 3.14 (`Ruff`, `Mypy`), HTML5 semántico (`djLint`), Bootstrap 5, JS Vanilla y Web Components.
  - [`DESING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DESING.md): Guía de diseño UI/UX para dashboards analíticos, tokens visuales por plataforma (`Twitch`, `YouTube`, `Kick`, `TikTok`), steppers de asistentes y accesibilidad WCAG 2.1 AA.
  - [`SECURITY.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/SECURITY.md): Política de seguridad, matriz RBAC para la compañía (`company_admin`, `manager`, `analyst`, `creator`) y seguridad en SQLite/DiskCache.
  - [`CONTRIBUTING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CONTRIBUTING.md): Convenciones de Git, Conventional Commits y flujo de calidad.
  - [`AGENTS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/AGENTS.md): Contexto y directrices operativas para agentes de IA.
- Incorporación en [`old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations) de los esquemas SQL legados como referencia del modelo de dominio (creadores, canales, sesiones de streaming, alertas/strikes, videos en 3 entidades y vistas analíticas).
- Instalación y configuración en [`pyproject.toml`](file:///home/diego/Proyectos/rrss-creators-analyzer/pyproject.toml) de las librerías clave del ecosistema Django:
  - `diskcache` para almacenamiento en caché en disco/memoria.
  - `django-tables2` para tablas de datos interactivas y exportables.
  - `django-filter` para filtrado declarativo.
  - `django-crispy-forms` y `crispy-bootstrap5` para formularios estilizados con Bootstrap 5.
  - `django-widget-tweaks` para personalización de controles de formulario en plantillas.
  - `django-formtools` para asistentes y formularios en múltiples pasos.
  - `django-autocomplete-light`, `django-import-export`, `django-simple-history` y `django-taggit`.

### Changed
- Rediseño arquitectónico del sistema: paso de un esquema multi-tenant en PostgreSQL/Supabase (con RLS y `organization_id`) a una aplicación **single-tenant (única compañía)** en **Django 6.0** utilizando **SQLite** (modo WAL) y **DiskCache** por restricciones de despliegue.

---

## [0.1.0] - 2026-10-25

### Added
- Inicialización del proyecto base con **Cookiecutter Django** (Python `3.14`, Django `6.0.9`).
- Aplicación inicial `users` con `django-allauth[mfa]` y hash de contraseñas Argon2.
- Configuración de herramientas de calidad: `ruff`, `mypy`, `djlint`, `pytest` y `coverage`.
