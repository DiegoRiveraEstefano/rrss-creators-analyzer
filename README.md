# RRSS Creators Analyzer

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![Django 6.0](https://img.shields.io/badge/django-6.0-092E20.svg)](https://www.djangoproject.com/)
[![Bootstrap 5](https://img.shields.io/badge/bootstrap-5.x-7952B3.svg)](https://getbootstrap.com/)

**RRSS Creators Analyzer** is a **Django 6.0** web application for talent management, operational auditing, financial settlements, and multi-platform analytics (`Twitch`, `YouTube`, `Kick`, `TikTok`, `Instagram`, `X`) for a single content creator agency.

> [!IMPORTANT]
> **Single-Tenant / Single-Company Architecture**: Unlike the legacy SQL reference in [`old-migrations/`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations), this platform operates for a single agency. Production uses **PostgreSQL 16+** (`psycopg` 3) and **Redis 7+** (`django-redis` + Celery), while local development and tests run out of the box on **SQLite 3** (WAL mode) and **DiskCache** / `LocMemCache`.

---

## Table of Contents

1. [Core Capabilities](#core-capabilities)
2. [Tech Stack](#tech-stack)
3. [Quick Start (Local & Demo Mode)](#quick-start-local--demo-mode)
4. [Docker Compose Deployment (Production & Demo)](#docker-compose-deployment-production--demo)
5. [Demo Service, Retention & Security Controls](#demo-service-retention--security-controls)
6. [Development & Quality Commands](#development--quality-commands)
7. [Documentation](#documentation)
8. [Project Structure](#project-structure)
9. [License](#license)

---

## Core Capabilities

- **Creator Roster & Channels (`creators`, `contracts`)**: Centralized talent directory, multi-platform channel tracking, daily audience snapshots, confidential KYC profiles, and contractual revenue splits/quotas.
- **Schedule & Compliance Tracking (`schedules`)**: RFC 5545 `RRULE` recurring broadcast schedules, calendar slot generation, automatic reconciliation against live streams, exception approvals, and monthly compliance summaries.
- **Live Streaming Analytics (`streams`)**: Session duration (`hours_streamed` generated field), `avg_ccv`, `peak_viewers`, chat engagement, category segments, and itemized revenue (`ad_revenue`, `subs_revenue`, `donations_revenue`, `earnings_per_hour`).
- **Video & Post-Production Pipeline (`videos`, `editors`)**: Three-entity media model (`Video`, `VideoPublication`, `VideoRelation`) with `django-taggit`, editorial workflow, editor assignments, versioned cut revisions (`TaskRevision`), production cost allocation, net profit, ROI, and RPM.
- **Sponsorships & Financial Settlements (`campaigns`, `payouts`)**: Brand campaign budgets, deliverable tracking with proof URLs, and monthly creator payouts with dual approval and recoupment handling.
- **Channel Health & Alerts (`alerts`)**: DMCA strike tracking, ToS warnings, unusual CCV drop detection, and SLA resolution workflows.
- **Multi-Step Wizards (`django-formtools`)**: Guided `SessionWizardView` flows for creator onboarding, campaign setup, payout closing, and assisted CSV/XLSX import mapping.
- **Bulk Ingestion, Exports & Dashboards (`imports`, `exports`, `analytics`)**: `django-import-export` pipelines, cached rankings (`Window`/`DenseRank`), and consolidated agency KPIs.
- **Governance & Operations (`users`, `permissions`, `members`, `audit`, `logs`, `monitor`, `backups`)**: Native Django RBAC (`Group` / `Permission`), `django-simple-history`, `django-auditlog`, health diagnostics, and backup management.

---

## Tech Stack

- **Backend**: Python `3.14.x` (`uv`), Django `6.0.9`, Django REST Framework, `drf-spectacular`, Celery + `django-celery-beat`.
- **Persistence & Cache**: PostgreSQL 16+ / Redis 7+ (production), SQLite 3 WAL / `diskcache` (local & tests).
- **Auth & Security**: `django-allauth[mfa]`, `Argon2PasswordHasher`, `django-simple-captcha`, `django-ratelimit`, DRF throttling, native Django Groups/Permissions.
- **Django UI Ecosystem**: `django-tables2`, `django-filter`, `django-crispy-forms` (`crispy-bootstrap5`), `django-formtools`, `django-widget-tweaks`, `django-autocomplete-light`.
- **Frontend**: Semantic HTML5, Bootstrap 5, Vanilla ES6+ JavaScript, and native Web Components.

---

## Quick Start (Local & Demo Mode)

### Prerequisites
- Python `3.14.x`
- [`uv`](https://docs.astral.sh/uv/)

### Setup

1. **Install dependencies**:
   ```bash
   uv sync --all-groups
   ```

2. **Configure environment variables**:
   Create a `.env` file in the repository root (see `.env.example`):
   ```ini
   DJANGO_DEBUG=True
   DJANGO_SECRET_KEY=dev-secret-key-change-in-production
   DJANGO_READ_DOT_ENV_FILE=True
   DEMO_MODE=True
   ```

3. **Run migrations and seed demo data**:
   ```bash
   uv run python manage.py migrate
   uv run python manage.py seed_demo_data
   ```

4. **Start the development server**:
   ```bash
   uv run python manage.py runserver
   ```

---

## Docker Compose Deployment (Production & Demo)

[`docker-compose.yml`](file:///home/diego/Proyectos/rrss-creators-analyzer/docker-compose.yml) provisions `postgres:16-alpine`, `redis:7-alpine`, `web` (Gunicorn + Uvicorn ASGI workers), `celery_worker`, and `celery_beat`.

```bash
# 1. Generate .env from .envs/.production/ (update placeholders first)
uv run python merge_production_dotenvs_in_dotenv.py

# 2. Build and start services
docker compose up -d --build

# 3. Optional: seed demo data inside the running web container
docker compose exec web python manage.py seed_demo_data

# 4. Check container health and logs
docker compose ps
docker compose logs -f web
```

---

## Demo Service, Retention & Security Controls

When `DEMO_MODE=True` is enabled (intended for live portfolio previews):

- **Quick Demo Login**: One-click `POST` login buttons on the home and login pages allow instant testing across predefined roles (`Manager`, `Analyst`, `Finance`, `Creator`) without entering credentials.
- **Open Self-Registration**: Visitors can create their own accounts via `/accounts/signup/`, optionally choose a demo role, and are immediately assigned permissions so the dashboard is usable without `403` errors.
- **7-Day Automatic Data Retention**: Seeded baseline records are tracked in `DemoBaselineRecord` and preserved. User-created records and self-registered accounts older than `DEMO_DATA_RETENTION_DAYS` (default `7`) are purged daily by Celery Beat (`cleanup_expired_demo_data`) or manually via:
  ```bash
  uv run python manage.py cleanup_demo_data --days 7 --dry-run
  ```
- **Abuse Protection**:
  - `django-simple-captcha` on signup (and password reset) when `CAPTCHA_ENABLED=True`.
  - Rate limiting via `django-allauth` (`ACCOUNT_RATE_LIMITS`), `django-ratelimit` on sensitive web actions/uploads, and DRF `AnonRateThrottle` / `UserRateThrottle`.
  - Shared demo baseline accounts cannot change passwords, modify emails, or delete themselves from the UI.

---

## Development & Quality Commands

```bash
# Run test suite
uv run pytest

# Coverage report
uv run coverage run -m pytest && uv run coverage html

# Static type checking
uv run mypy rrss_creatos_analyzer

# Python linting and formatting
uv run ruff check .
uv run ruff format --check .

# Django template linting and formatting
uv run djlint rrss_creatos_analyzer/templates --lint
uv run djlint rrss_creatos_analyzer/templates --reformat
```

---

## Documentation

- [`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md): System architecture, domain model, legacy migration mapping, and multi-step wizard flows.
- [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md): Engineering rules (`Models -> Selectors -> Services -> Views`), Django ecosystem usage, signal policy, and TDD standards.
- [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/STYLE_GUIDE.md): Coding conventions for Python, `djLint` HTML5 templates, Bootstrap 5, and Web Components.
- [`DESIGN.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DESIGN.md): UI/UX tokens, platform color system, analytical table layout, steppers, and WCAG 2.1 AA accessibility.
- [`SECURITY.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/SECURITY.md): Authentication, RBAC permission matrix, IDOR protection, rate limits, CAPTCHA, and vulnerability reporting.
- [`CONTRIBUTING.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CONTRIBUTING.md): Git branching, Conventional Commits, and PR verification checklist.
- [`AGENTS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/AGENTS.md): Operational reference for AI coding agents.
- [`CHANGELOG.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CHANGELOG.md): Version history following Keep a Changelog.
- [`docs/requirements/`](file:///home/diego/Proyectos/rrss-creators-analyzer/docs/requirements): Module-by-module functional and business rule specifications.

---

## Project Structure

```text
rrss-creators-analyzer/
├── compose/                        # Docker entrypoints and start scripts (web, celery)
├── config/                         # Django configuration (settings, urls, asgi/wsgi, celery)
│   └── settings/                   # Modular settings (base, local, production, test)
├── docs/                           # Sphinx docs, SQL schema reference, and module requirements
├── old-migrations/                 # Legacy PostgreSQL/Supabase SQL reference
├── rrss_creatos_analyzer/          # Main Django project package
│   ├── apps/                       # 20 modular domain and operational Django apps
│   ├── contrib/                    # Contrib extensions (sites)
│   ├── static/                     # CSS (Bootstrap 5 tokens), Vanilla JS, Web Components
│   └── templates/                  # Semantic HTML5 templates (SSR)
└── tests/                          # Cross-cutting integration tests
```

---

## License

Licensed under **GPLv3**. See [`LICENSE`](file:///home/diego/Proyectos/rrss-creators-analyzer/LICENSE) and [`COPYING`](file:///home/diego/Proyectos/rrss-creators-analyzer/COPYING).
