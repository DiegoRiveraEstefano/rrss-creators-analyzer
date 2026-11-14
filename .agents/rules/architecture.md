---
trigger: always_on
---

# RRSS Creators Analyzer: 12-Factor App & Architecture Guidelines

**Context:** Single-Tenant / Single-Company Creator & Streamer Analytics Platform (Python 3.14+, Django 6.0, PostgreSQL 16+ & Redis 7+ in production, SQLite WAL & DiskCache locally, Bootstrap 5, Semantic HTML5, Vanilla JS & Web Components).

## Core Directives

### 1. Configuration in Environment (Factor III)
- Never hardcode credentials, secrets, host names, or ports.
- Use `django-environ` reading from `.env`.
- Database and cache URLs/paths are configurable via environment variables (`DATABASE_URL`, `REDIS_URL`, `SQLITE_DB_PATH`, `DISKCACHE_DIR`).

### 2. Single-Tenant Architecture (No Multi-Tenancy)
- The system operates exclusively for a **single company/agency**.
- **Strictly Prohibited**: Do NOT add `Organization`/`Tenant` models, `tenant_id` / `organization_id` foreign keys, or `ContextVar` tenant middleware.
- Access control is governed by native Django `Group` and `Permission` checks (`user.has_perm(...)`) enforced in Views, Selectors, and Services.

### 3. Portable Persistence & Caching
- **Production**: PostgreSQL 16+ (`psycopg` 3, `ATOMIC_REQUESTS=True`) and Redis 7+ (`django-redis` cache + Celery broker/backend).
- **Local & Tests**: SQLite 3 (`PRAGMA journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout=5000`, `foreign_keys=ON`) and `diskcache.DjangoCache` / `LocMemCache`.
- Keep `@transaction.atomic` blocks short and avoid PostgreSQL-only extensions (`MATERIALIZED VIEW`, `ArrayField`) so local SQLite compatibility is preserved.

### 4. Maximize Django Ecosystem Capabilities
- Prioritize native Django features (`QuerySet.annotate`, `Window`, `DenseRank`, `GeneratedField`, `CheckConstraint`, `UniqueConstraint`, CBVs) and standard project libraries:
  - `django-tables2` for all data tables, sorting, pagination, and export.
  - `django-filter` for declarative queryset filtering.
  - `django-crispy-forms` (`crispy-bootstrap5`) and `django-widget-tweaks` for form rendering.
  - `django-formtools` (`SessionWizardView`) for sequential, multi-step wizards.
  - `django-import-export` for CSV/XLSX batch imports and exports.
  - `django-simple-history` and `django-auditlog` for model audit trails.
  - `django-taggit` for content tags and `django-autocomplete-light` for relational selects.

### 5. Explicit Cache Invalidation & Strict Signal Policy
- Zero business logic inside Django signals.
- Analytical cache keys are invalidated explicitly from the `Service` layer using `transaction.on_commit(...)`.
