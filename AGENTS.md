# AI Agent Operational Guide (AGENTS)

Essential context, infrastructure constraints, and coding standards for AI agents working on **RRSS Creators Analyzer**.

---

## 1. Project Context

- **Purpose**: **Django 6.0** (Python `3.14`) platform for tracking, auditing, and analyzing operational and financial performance for digital creators and streamers (`Twitch`, `YouTube`, `Kick`, `TikTok`, `Instagram`, `X`) within a single agency.
- **Legacy Reference**: [`old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations) contains legacy PostgreSQL/Supabase SQL schemas kept strictly as domain reference.
- **Rule Precedence**: The rules below override any multi-tenant assumptions in template boilerplate.

> [!IMPORTANT]
> ### Mandatory Architectural Constraints
> 1. **Single-Tenant Only**: Do NOT add `Organization` or `Tenant` models, `organization_id`/`tenant_id` columns, or tenant middleware.
> 2. **Database Portability (PostgreSQL + SQLite)**: Production uses **PostgreSQL 16+** (`psycopg` 3); local development and tests support **SQLite 3** (WAL mode). Avoid PostgreSQL-only ORM extensions (e.g., `ArrayField`, `MATERIALIZED VIEW`, `plpgsql` triggers) unless guarded; use `django-taggit` and ORM queries + cache instead.
> 3. **Caching & Async**: Production uses **Redis 7+** (`django-redis` + Celery/Celery Beat); local/test uses **DiskCache** (`diskcache.DjangoCache`) or `LocMemCache` with `CELERY_TASK_ALWAYS_EAGER = True`.
> 4. **Frontend**: Semantic HTML5 + **Bootstrap 5** (`crispy-bootstrap5`) + Vanilla ES6+ JS and native Web Components (`<rrss-*>`).
> 5. **Django Ecosystem First**: Prioritize `django-tables2`, `django-filter`, `django-crispy-forms`, `django-widget-tweaks`, `django-formtools` (`SessionWizardView`), `django-import-export`, `django-simple-history`, `django-auditlog`, `django-taggit`, `django-autocomplete-light`, `django-ratelimit`, and `django-simple-captcha`.

---

## 2. Documentation Map

- [`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md): Architecture, domain model, legacy SQL mapping, RBAC groups, and multi-step wizards.
- [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md): Layered design (`models.py`, `selectors.py`, `services.py`, `tables.py`, `filters.py`, `forms.py`, `views.py`), signal restrictions, and TDD rules.
- [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/STYLE_GUIDE.md): Python (`Ruff`, `Mypy`), template (`djLint`), HTML5, Bootstrap 5, and Web Component standards.
- [`DESIGN.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DESIGN.md): UI/UX tokens, platform badges, KPI cards, steppers, and WCAG 2.1 AA rules.
- [`SECURITY.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/SECURITY.md): RBAC permission matrix, IDOR rules, rate limiting, CAPTCHA, and demo safeguards.
- [`CONTRIBUTING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CONTRIBUTING.md): Branching, Conventional Commits, and PR checklist.
- [`CHANGELOG.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CHANGELOG.md): Release history.
- [`docs/requirements/`](file:///home/diego/Proyectos/rrss-creators-analyzer/docs/requirements): Module-level specifications and traceability matrix.

---

## 3. Coding Rules

1. **File Size Limit**: Keep every Python file at or under **400 lines**; split large modules into packages.
2. **Responsibility Boundaries**:
   - `models.py`: Schema, `TextChoices`, `CheckConstraint`, `UniqueConstraint`, `GeneratedField`, `HistoricalRecords()`. No business logic.
   - `selectors.py`: Read-only `QuerySet`s, `select_related`, `prefetch_related`, `annotate`, `Window(DenseRank())`, and `cache.get_or_set(...)`. Enforce permission-based scoping (`view_all_*` vs `creator__user=user`).
   - `services.py`: Stateless classes with `@classmethod` and `@transaction.atomic`. Never accept `HttpRequest`, `Form`, or `WizardView`. Invalidate cache in `transaction.on_commit(...)`.
   - `views.py`: Thin CBVs (`SingleTableMixin`, `FilterView`, `CreateView`, `UpdateView`, `DetailView`, `SessionWizardView`).
3. **Tables, Filters, Forms & Wizards**:
   - Tabular listings use `django_tables2.Table` (`{% render_table table %}`).
   - List filters use `django_filters.FilterSet` and `{% render_field %}` (`django-widget-tweaks`).
   - Standard forms use `crispy-bootstrap5`.
   - Multi-step workflows use `formtools.wizard.views.SessionWizardView` with `{{ wizard.management_form }}` and atomic `Service` calls inside `done()`.
4. **Signals**: Do NOT use `post_save`/`pre_save`/`m2m_changed`/`post_delete` for business logic, metric recalculation, or emails.
5. **Logging**: Use `logger = logging.getLogger(__name__)` with static `snake_case` event messages and structured `extra={...}` metadata.

---

## 4. Environment Commands (`uv`)

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run pytest
uv run mypy rrss_creatos_analyzer
uv run ruff check .
uv run ruff format .
uv run djlint rrss_creatos_analyzer/templates --lint
uv run djlint rrss_creatos_analyzer/templates --reformat
```
