# Changelog

All notable changes to **RRSS Creators Analyzer** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Open-Source & Interactive Demo Readiness**:
  - Standardized all repository documentation (`README.md`, `DOCS.md`, `GUIDELINES.md`, `STYLE_GUIDE.md`, `DESIGN.md`, `SECURITY.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CHANGELOG.md`, and `docs/requirements/`) into concise technical English.
  - Sanitized tracked environment templates in `.envs/` and added `.env.example` for safe public repository publishing.
  - Added `seed_demo_data` management command (idempotent) to populate RBAC roles, demo accounts, and realistic datasets across all 20 apps, tracked via `DemoBaselineRecord`.
  - Added **Quick Demo Login** buttons per role (`Manager`, `Analyst`, `Finance`, `Creator`) and automatic default group assignment on open registration (`AccountAdapter`) so new accounts access the dashboard without `403` errors.
  - Added 7-day automatic retention cleanup (`cleanup_demo_data` command and daily Celery Beat task) that purges expired user-created data and self-registered demo accounts while preserving baseline seed records.
  - Added multi-layer abuse protection: `django-simple-captcha` on signup/password reset, `django-allauth` `ACCOUNT_RATE_LIMITS`, `django-ratelimit` on sensitive web routes, DRF throttling, upload size caps, and shared demo account protections.
- **Production PostgreSQL & Redis Stack**:
  - Configured `config/settings/production.py` for PostgreSQL 16+ (`psycopg` 3, `ATOMIC_REQUESTS=True`, `CONN_MAX_AGE`) and Redis 7+ (`django-redis` cache + Celery broker/backend).
  - Updated `docker-compose.yml`, `Dockerfile.web`, `Dockerfile.celery`, and container entrypoints with healthchecks and PostgreSQL readiness checks.
- **Schedules & Compliance Module (`schedules`)**:
  - Added `rrss_creatos_analyzer.apps.schedules` with RFC 5545 `RRULE` patterns (`CreatorSchedulePattern`), dated slots (`CreatorScheduleSlot`), approved absences (`ScheduleException`), monthly compliance summaries (`CreatorScheduleComplianceSummary`), and calendar views.
- **Multi-Step Wizards (`django-formtools`)**:
  - Standardized `SessionWizardView` patterns for creator onboarding, campaign setup, payout closing, and assisted bulk imports.
- **Modular 20-App Domain Architecture**:
  - Implemented `users`, `permissions`, `members`, `creators`, `contracts`, `schedules`, `streams`, `videos`, `editors`, `campaigns`, `payouts`, `alerts`, `imports`, `exports`, `analytics`, `core`, `audit`, `logs`, `monitor`, and `backups`.

### Changed
- Adapted the legacy multi-tenant SQL design (`old-migrations/`) into a single-company Django 6.0 architecture supporting PostgreSQL + Redis in production and SQLite (WAL) + DiskCache locally.

---

## [0.1.0] - 2026-10-25

### Added
- Initialized project scaffold with Cookiecutter Django (Python `3.14`, Django `6.0.9`).
- Initial `users` app with `django-allauth[mfa]` and Argon2 password hashing.
- Configured `ruff`, `mypy`, `djlint`, `pytest`, and `coverage`.
