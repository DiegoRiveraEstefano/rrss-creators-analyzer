# Guía Operativa para Agentes de IA (AGENTS)

Este documento proporciona el contexto esencial, las restricciones de infraestructura y las reglas de arquitectura que cualquier Agente de IA o asistente de programación debe seguir al trabajar en **RRSS Creators Analyzer**.

---

## 1. Contexto Fundamental del Proyecto

- **Propósito**: Sistema en **Django 6.0** (Python `3.14`) para rastrear, auditar y analizar el rendimiento operativo y financiero de los streamers y creadores de contenido (`Twitch`, `YouTube`, `Kick`, `TikTok`) pertenecientes a una compañía.
- **Referencia del Dominio Antiguo**: En [`/old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations) se encuentran las 10 migraciones SQL del sistema anterior (PostgreSQL/Supabase). Úsalas como referencia exacta de las entidades, campos, métricas y vistas analíticas que el negocio necesita, pero **adaptadas a las reglas actuales del proyecto**.
- **Reglas en `.agents/rules/`**: Los archivos en [`/.agents/rules/`](file:///home/diego/Proyectos/rrss-creators-analyzer/.agents/rules) provienen de una plantilla base multi-tenant; **este proyecto adapta dichas reglas** con las siguientes decisiones obligatorias que tienen precedencia absoluta:

> [!IMPORTANT]
> ### Decisiones Arquitectónicas con Precedencia Absoluta
> 1. **NO ES MULTI-TENANT**: El sistema pertenece a una única compañía. **No agregues** modelos `Organization` / `Tenant`, ni campos `organization_id` / `tenant_id`, ni `TenantContextMixin`.
> 2. **Base de Datos SQLite**: Por restricciones de despliegue se utiliza **SQLite 3** (con `PRAGMA journal_mode=WAL;`). No utilices características exclusivas de PostgreSQL (como `MATERIALIZED VIEW`, `ArrayField` o triggers en `plpgsql`).
> 3. **Caché con DiskCache / Memoria**: Se usa **`diskcache`** (`diskcache.DjangoCache`) y `LocMemCache` para cachear agregaciones, rankings y métricas que en el sistema antiguo eran vistas materializadas.
> 4. **Frontend**: **HTML5 semántico** + **Bootstrap 5** (`crispy-bootstrap5`) + **JavaScript Vanilla (ES6+)** y **Web Components nativos (Custom Elements)** para interacciones complejas.
> 5. **Uso Máximo del Ecosistema Django**: Prioriza siempre el uso de **`django-tables2`**, **`django-filter`**, **`django-crispy-forms`**, **`django-widget-tweaks`**, **`django-formtools`** (para asistentes y formularios en múltiples pasos), **`django-import-export`**, **`django-simple-history`**, **`django-taggit`** y **`django-autocomplete-light`**.

---

## 2. Mapa de Documentación del Repositorio

Antes de realizar cambios en el código, consulta el documento específico:

- [`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md): Mapeo completo de [`old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations) a modelos de Django (`Creator`, `Channel`, `StreamingSession`, `Video`, `VideoPublication`, `VideoRelation`, `ChannelAlert`, `ImportBatch`), flujos guiados en múltiples pasos (`django-formtools`) y reemplazo de vistas materializadas por `Selectors` + `DiskCache`.
- [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md): Arquitectura en capas (`models.py`, `selectors.py`, `services.py`, `tables.py`, `filters.py`, `forms.py`, `views.py`), uso de `django-formtools` (`SessionWizardView`) para formularios multi-paso, prohibición de lógica de negocio en Signals y directivas TDD.
- [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/STYLE_GUIDE.md): Convenciones de Python (`Ruff`, `Mypy`), plantillas HTML5 (`djLint`), Bootstrap 5, asistentes multi-paso y estructura de Web Components (`<rrss-*>`).
- [`DESING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DESING.md): Guía UI/UX, colores e insignias por plataforma (`Twitch`, `YouTube`, `Kick`, `TikTok`), diseño de KPIs, steppers/asistentes multi-paso, tablas y accesibilidad.
- [`SECURITY.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/SECURITY.md): Matriz de permisos por rol (`company_admin`, `manager`, `analyst`, `creator`) y seguridad sobre SQLite/DiskCache.
- [`CONTRIBUTING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CONTRIBUTING.md): Convenciones de ramas, Conventional Commits y checklist de calidad.
- [`CHANGELOG.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CHANGELOG.md): Historial de cambios (debe actualizarse en cada tarea relevante).

---

## 3. Reglas Rápidas de Codificación para el Agente

1. **Límite de Tamaño de Archivo**:
   - Ningún archivo Python debe superar las **400 líneas**. Divide en submódulos si es necesario.
2. **Separación de Responsabilidades (CQRS Ligero)**:
   - **`models.py`**: Solo definición de esquema, `TextChoices`, `CheckConstraint`, `UniqueConstraint`, `GeneratedField` e `HistoricalRecords()`.
   - **`selectors.py`**: Solo lecturas (`QuerySet`), `select_related`, `prefetch_related`, `annotate`, `Window(expression=DenseRank())` y lecturas cacheadas en `DiskCache`. Filtra por `creator__user=user` cuando `user.role == "creator"`.
   - **`services.py`**: Clases sin estado con `@classmethod` y `@transaction.atomic`. Cero objetos `HttpRequest`, `Form` o `WizardView`. Invalida las claves de `DiskCache` mediante `transaction.on_commit(...)`.
   - **`views.py`**: Class-Based Views delgadas (`SingleTableMixin`, `FilterView`, `CreateView`, `UpdateView`, `DetailView`, o `SessionWizardView` para flujos multi-paso).
3. **Tablas, Filtros y Formularios**:
   - Todo listado tabular usa `django_tables2.Table` en `tables.py` y `{% render_table table %}` en el template.
   - Todo buscador o filtro de listado usa `django_filters.FilterSet` en `filters.py`.
   - Los formularios de creación/edición usan `django-crispy-forms` (`crispy-bootstrap5`).
   - Todo flujo secuencial o formulario en múltiples pasos (onboarding de creadores, configuración de campañas, aprobación de liquidaciones, mapeo asistido de importaciones) usa obligatoriamente **`django-formtools`** (`SessionWizardView`), asegurando `{{ wizard.management_form }}` en la plantilla y delegando la persistencia a un `Service` atómico en `done()`.
   - Los formularios de filtrado rápido en plantillas usan `{% render_field %}` de `django-widget-tweaks`.
4. **Signals**:
   - **Prohibido** usar señales (`post_save`, `pre_save`, etc.) para lógica de negocio, recálculo de métricas o efectos secundarios. Hazlo explícitamente en el `Service`.
5. **Logging**:
   - Usa únicamente `import logging; logger = logging.getLogger(__name__)` con mensajes estáticos en `snake_case` y contexto en `extra={...}`.

---

## 4. Comandos de Ejecución en el Entorno (`uv`)

Todos los comandos dentro del proyecto deben ejecutarse a través de **`uv run`**:

```bash
# Ejecutar migraciones
uv run python manage.py makemigrations
uv run python manage.py migrate

# Ejecutar suite de tests (Pytest)
uv run pytest

# Verificar tipos (Mypy)
uv run mypy rrss_creatos_analyzer

# Linter y formateador de Python (Ruff)
uv run ruff check .
uv run ruff format .

# Linter y formateador de plantillas HTML/Django (djLint)
uv run djlint rrss_creatos_analyzer/templates --lint
uv run djlint rrss_creatos_analyzer/templates --reformat
```
