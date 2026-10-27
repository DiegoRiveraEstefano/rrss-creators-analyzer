---
trigger: always_on
---

# RRSS Creators Analyzer: Codebase Structure & Directory Layout

## Directory Boundaries

```text
rrss-creators-analyzer/
├── config/                         # Django global configuration
│   ├── settings/                   # base.py, local.py, production.py, test.py
│   ├── urls.py                     # Root URL router
│   ├── celery_app.py               # Celery application instance
│   ├── wsgi.py / asgi.py           # WSGI/ASGI entrypoints
│   └── api_router.py               # DRF API router
│
├── old-migrations/                 # Legacy SQL migrations (reference only)
│
├── rrss_creatos_analyzer/          # Main application package
│   ├── apps/                       # Modular monolith applications
│   │   ├── core/                   # Shared infrastructure (BaseModel, CompanySettings, exceptions, cache helpers)
│   │   ├── users/                  # Custom User identity & profile
│   │   ├── permissions/            # Management of native Django Groups, Permissions & Role matrices
│   │   ├── members/                # Team onboarding, invitations & creator-team assignments
│   │   ├── audit/                  # Audit trail viewer & security/activity events (django-simple-history)
│   │   ├── logs/                   # Application log analyzer, parser & viewer
│   │   ├── monitor/                # Instance health, SQLite WAL/DB connection stats & DiskCache metrics
│   │   ├── backups/                # SQLite online backups, retention & restore management
│   │   ├── imports/                # ImportBatch & django-import-export ingestion pipelines
│   │   ├── exports/                # Report generation, CSV/XLSX exports & scheduled snapshots
│   │   ├── creators/               # Creator profiles, platform Channels & growth snapshots
│   │   ├── contracts/              # Creator contracts, revenue splits & monthly deliverables quotas
│   │   ├── streams/                # StreamingSession tracking, audience & revenue metrics, segments
│   │   ├── videos/                 # Video assets, VideoPublication metrics & VideoRelation links
│   │   ├── alerts/                 # ChannelAlert (DMCA strikes, TOS violations, anomalies)
│   │   ├── campaigns/              # Brand sponsorships, campaigns & creator deliverables
│   │   ├── payouts/                # Monthly creator financial settlements & agency commissions
│   │   └── analytics/              # Dashboards, leaderboards, DiskCache selectors & cache services
│   │
│   ├── static/                     # Static assets (Bootstrap 5 CSS, Vanilla JS & Web Components)
│   └── templates/                  # Semantic HTML5 Django SSR templates (including wizards/)
│
└── tests/                          # Cross-cutting integration test suite
```

## Modular Monolith Rules

1. **400-Line Limit**: No Python file may exceed 400 lines of code. Split large files into packages (e.g., `services/`, `selectors/`, `views/`, `tables/`, `wizards/`).
2. **Layer Separation inside each App (`rrss_creatos_analyzer/apps/<app_name>/`)**:
   - `models.py`: Declarations, fields, `TextChoices`, `CheckConstraint`, `UniqueConstraint`, `GeneratedField`, `HistoricalRecords`. Zero business logic.
   - `selectors.py`: All read queries, permission visibility filtering (`user.has_perm`), `select_related`/`prefetch_related`, ORM annotations, and `DiskCache` lookups. Zero mutations.
   - `services.py`: All mutation operations, business validations, `@transaction.atomic`, and `DiskCache` invalidation on commit.
   - `tables.py`: Declarative data tables using `django-tables2`.
   - `filters.py`: Declarative search/filter definitions using `django-filter`.
   - `forms.py` / `wizards.py`: Forms, step form definitions, and `crispy-bootstrap5` layouts (`django-crispy-forms`, `django-formtools`).
   - `views.py` (or `views/wizards.py`): Thin Class-Based Views (`SingleTableMixin`, `FilterView`, `CreateView`, `UpdateView`, `DetailView`, and `SessionWizardView` for multi-step flows).
   - `api/`: DRF serializers, views, and URLs.
   - `tests/`: Unit and integration tests (`factories.py`, `test_models.py`, `test_selectors.py`, `test_services.py`, `test_forms.py`, `test_views.py`, `test_wizards.py`, `test_urls.py`).
