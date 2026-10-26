---
trigger: always_on
---

# RRSS Creators Analyzer: 12-Factor App & Architecture Guidelines

**Context:** Single-Tenant / Single-Company Creator & Streamer Analytics Platform (Python 3.14+, Django 6.0, SQLite in WAL mode, DiskCache, Bootstrap 5, HTML5 Semantic, Vanilla JS & Web Components).

## Core Directives

### 1. Configuration in Environment (Factor III)
- Never hardcode credentials, secrets, host names, or ports.
- Use `django-environ` reading from `.env`.
- Database and cache paths are configurable via environment variables (`DATABASE_URL=sqlite:///db.sqlite3`, `DISKCACHE_LOCATION`).

### 2. Single-Tenant Architecture (No Multi-Tenancy)
- The system operates exclusively for a **single company/agency**.
- **Strictly Prohibited**: Do NOT add `Organization`/`Tenant` models, `tenant_id` / `organization_id` foreign keys, or `ContextVar` tenant middleware.
- Access control is governed by user roles (`company_admin`, `manager`, `analyst`, `creator`) enforced in Views, Selectors, and Services.

### 3. Constrained Deployment Persistence: SQLite (WAL) & DiskCache
- **Database**: SQLite 3 is the primary database engine due to deployment constraints.
  - Must be configured with `PRAGMA journal_mode=WAL;`, `synchronous=NORMAL;`, `busy_timeout=5000;`, and `foreign_keys=ON;`.
  - Keep write transactions (`@transaction.atomic`) short and fast to avoid write locks. Never perform external HTTP requests or slow file parsing inside an open atomic block.
- **Cache**: `diskcache.DjangoCache` (disk-backed) and `LocMemCache` (in-memory) replace external Redis/Memcached and PostgreSQL `MATERIALIZED VIEW`s for analytical summaries and leaderboards.

### 4. Maximize Django Ecosystem Capabilities
- Prioritize native Django features (`QuerySet.annotate`, `Window`, `DenseRank`, `GeneratedField`, `CheckConstraint`, `UniqueConstraint`, CBVs) and standard project libraries:
  - `django-tables2` for all data tables, sorting, pagination, and export.
  - `django-filter` for declarative queryset filtering.
  - `django-crispy-forms` (`crispy-bootstrap5`) and `django-widget-tweaks` for form rendering.
  - `django-import-export` for CSV/XLSX batch imports and exports.
  - `django-simple-history` for model audit trails.
  - `django-taggit` for content tags and `django-autocomplete-light` for relational selects.

### 5. Explicit Cache Invalidation & Strict Signal Policy
- Zero business logic inside Django signals.
- Analytical cache keys in `DiskCache` are invalidated explicitly from the `Service` layer using `transaction.on_commit(...)`.

## Anti-patterns vs. Correct Implementations

| Pattern | Prohibited Anti-pattern | Mandatory Correct Approach | Rationale |
|---|---|---|---|
| Credentials | `SECRET_KEY = "xyz"` in repo | `env("DJANGO_SECRET_KEY")` | Security & runtime flexibility |
| Tenancy | Adding `tenant_id` / `organization_id` | Role-based scoping (`user.role`) | Single-company system design |
| Database | PostgreSQL-only `MATERIALIZED VIEW` / `ArrayField` | Django ORM `annotate`/`Window` + `DiskCache` / `django-taggit` | SQLite compatibility |
| Tables & Filters | Manual HTML tables & manual `request.GET` parsing | `django-tables2` (`Table`) + `django-filter` (`FilterSet`) | Consistency & Django ecosystem leverage |
| Side Effects | `post_save` recalculating metrics or sending emails | Explicit `Service` call + `transaction.on_commit(...)` | Atomic failure handling & predictability |
