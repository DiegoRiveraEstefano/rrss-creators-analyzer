# Security Policy

This document describes authentication, native Django RBAC authorization, data protection across PostgreSQL/SQLite/Redis/DiskCache, demo abuse controls, and vulnerability reporting for **RRSS Creators Analyzer**.

---

## 1. Authentication & Session Security

1. **Authentication (`django-allauth[mfa]`)**:
   - Native MFA / TOTP support, recommended for `Company Admin`, `Manager`, and `Finance` roles.
   - Standard production deployments enforce email verification (`DJANGO_ACCOUNT_EMAIL_VERIFICATION=mandatory`). Public demo mode (`DEMO_MODE=True`) relaxes email verification (`none`) for zero-friction evaluation while enforcing CAPTCHA and rate limits.
2. **Password Hashing**:
   - Uses `Argon2PasswordHasher` (`argon2-cffi`) as the primary password hasher alongside Django's built-in password validators.
3. **Cookies & HTTP Headers**:
   - `SESSION_COOKIE_HTTPONLY = True`, `CSRF_COOKIE_HTTPONLY = True`, `X_FRAME_OPTIONS = "DENY"`.
   - Production enforces `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`, `SECURE_SSL_REDIRECT = True` (configurable), and HSTS headers.

---

## 2. Authorization (Native Django Groups & Permissions)

Unlike the legacy RLS design in [`old-migrations/20260904000004_rls_security_policies.sql`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations/20260904000004_rls_security_policies.sql), this single-company application uses `django.contrib.auth` `Group` and `Permission` tables:

- No hardcoded `role` column on `User`. Capabilities are granted through `auth_group` (`RoleGroupProfile`) and `PermissionRequiredMixin` / `user.has_perm("<app>.<codename>")`.

### Default Role Matrix

| Resource / Permission | `Company Admin` | `Manager` | `Analyst` | `Finance` | `Creator` |
|---|---|---|---|---|---|
| **Users & Groups (`users.*`, `permissions.*`)** | Full CRUD | `view_user` | None | None | Own profile only |
| **Creators (`creators.*`)** | CRUD + `view_all_creators` | `add`, `change`, `view` + `view_all_creators` | `view` + `view_all_creators` | `view` + `view_all_creators` | `view_creator` (own only) |
| **Contracts (`contracts.*`)** | Full CRUD | Read-only | None | Full CRUD | Own contract only |
| **Streams (`streams.*`)** | CRUD + `view_all_sessions` + `export_sessions` | `add`, `change`, `view` + `view_all_sessions` | `view` + `view_all_sessions` + `export_sessions` | `view` + `view_all_sessions` | `view_streamingsession` (own only) |
| **Videos (`videos.*`)** | CRUD + `view_all_videos` + `view_production_costs` | `add`, `change`, `view` + `view_all_videos` + `view_production_costs` | `view` + `view_all_videos` + `view_production_costs` | `view` + `view_all_videos` + `view_production_costs` | Own videos/publications only |
| **Alerts (`alerts.*`)** | CRUD + `view_all_alerts` + `resolve_channel_alert` | `add`, `change`, `view` + `view_all_alerts` + `resolve_channel_alert` | `view` + `view_all_alerts` | None | Own alerts only |
| **Imports (`imports.*`)** | Full CRUD | `add`, `view` | `add`, `view` | None | None |
| **Payouts (`payouts.*`)** | Full CRUD | Read-only | None | Full CRUD | Own payouts only |
| **Analytics (`analytics.*`)** | Company dashboard | Company dashboard | Company dashboard | Company dashboard | Personal metrics only |

### IDOR Prevention Rules
- Detail views must never query `Model.objects.get(pk=pk)` directly.
- All view querysets flow through a role-aware `Selector` accepting `user: User`:
  - If `user.has_perm("<app>.view_all_<models>")` is `True`, return the company-wide queryset.
  - Otherwise, restrict strictly to `creator__user=user` (or `CreatorTeamAssignment`).

---

## 3. Abuse Prevention, Rate Limiting & CAPTCHA

- **Auth Rate Limits (`django-allauth`)**: `ACCOUNT_RATE_LIMITS` throttles failed logins (`5/5m`), signups (`5/1h`), password resets, and email confirmations.
- **View Rate Limits (`django-ratelimit`)**: Protects quick-demo login, signup/account actions, bulk imports, exports, and write endpoints using the active cache backend (Redis in production, DiskCache/LocMemCache locally).
- **API Throttling (`DRF`)**: `AnonRateThrottle` and `UserRateThrottle` configured in `REST_FRAMEWORK`.
- **CAPTCHA (`django-simple-captcha`)**: Enabled on public registration and password reset forms when `CAPTCHA_ENABLED=True` (automatically disabled in test settings).
- **Upload & Demo Safeguards**:
  - `DATA_UPLOAD_MAX_MEMORY_SIZE` and `FILE_UPLOAD_MAX_MEMORY_SIZE` capped at 5 MB.
  - CSV/XLSX exports sanitize formula-injection prefixes (`=`, `+`, `-`, `@`).
  - In `DEMO_MODE=True`, shared baseline demo accounts cannot modify passwords/emails or delete their own accounts, and all user-created data is purged after 7 days.

---

## 4. Persistence, Secrets & Audit Integrity

- **SQL Injection Prevention**: Raw string interpolation in SQL (`raw()`, `extra()`, manual cursors) is prohibited. Use the Django ORM and `django-filter` exclusively.
- **Immutable Audit Trail**: `django-simple-history` and `django-auditlog` record mutations on critical domain models (`Creator`, `Contract`, `StreamingSession`, `Video`, `ChannelAlert`, `CreatorPayout`, `User`).
- **Secrets Management**: Never commit `DJANGO_SECRET_KEY`, database credentials, or SMTP/API keys. Use environment variables via `django-environ` and `.env` files ignored by Git.
- **Database Isolation**: Production `postgres` and `redis` containers communicate over Docker's private network; local SQLite (`db.sqlite3`) and `.cache/diskcache/` must remain outside `STATIC_ROOT` and `MEDIA_ROOT`.

---

## 5. Reporting Vulnerabilities

Do **not** open a public GitHub Issue for security vulnerabilities.

1. Contact the maintainer via private email (`security@example.com` or repository security advisory).
2. Include the affected component, reproduction steps (PoC), and potential impact.
3. Maintainers acknowledge reports within **48 hours** and coordinate remediation before public disclosure.
