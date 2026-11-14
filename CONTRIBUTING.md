# Contributing Guide

This document defines the Git workflow, commit conventions, engineering rules, and Pull Request checks for **RRSS Creators Analyzer**.

---

## 1. Git Branching

Direct commits to `main` are prohibited. Use dedicated branches:

- **Features**: `feature/<scope>-<short-description>` (e.g. `feature/streams-session-table`)
- **Bug fixes**: `bugfix/<scope>-<short-description>` (e.g. `bugfix/alerts-status-filter`)
- **Production hotfixes**: `hotfix/<short-description>`
- **Maintenance / Docs**: `chore/<scope>-<short-description>` or `docs/<short-description>`

---

## 2. Commit Messages (Conventional Commits)

Follow the **Conventional Commits** specification:

```text
<type>(<scope>): <short imperative summary>

- Technical explanation of what changed and why
- Reference to affected models, services, or rules
```

### Allowed Types
- `feat`: New user or system feature.
- `fix`: Bug fix.
- `docs`: Documentation changes (`*.md`, `/docs`).
- `style`: Formatting, Bootstrap 5 CSS, or lint fixes with no logic changes.
- `refactor`: Code restructuring without behavior changes.
- `perf`: Query optimization, DB indexing, or caching improvements.
- `test`: Adding or updating `pytest` / `factory-boy` tests.
- `chore`: Dependency updates (`pyproject.toml`, `uv.lock`), CI, or Docker config.

### Allowed Scopes
`users`, `permissions`, `members`, `creators`, `contracts`, `schedules`, `streams`, `videos`, `editors`, `campaigns`, `payouts`, `alerts`, `imports`, `exports`, `analytics`, `audit`, `logs`, `monitor`, `backups`, `core`, `demo`, `ui`, `docs`.

---

## 3. Mandatory Engineering Rules

Review [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md) and [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/STYLE_GUIDE.md) before writing code:

1. **Single-Tenant Architecture**: Never add `tenant_id` or `organization_id` fields or models.
2. **Layered Separation**:
   - Read queries and role-based filtering belong in `selectors.py`.
   - Mutations and `@transaction.atomic` workflows belong in `services.py`.
   - Zero business logic in `models.py`, `views.py`, or Django signals.
3. **Django Ecosystem First**: Use `django-tables2`, `django-filter`, `django-crispy-forms` (`crispy-bootstrap5`), `django-formtools` (`SessionWizardView`), and `django-widget-tweaks`.
4. **Clean Frontend**: Semantic HTML5 + Bootstrap 5 + Vanilla ES6+ / Web Components.

---

## 4. Pre-PR Quality Checks

Run all checks locally before opening a Pull Request:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy rrss_creatos_analyzer
uv run djlint rrss_creatos_analyzer/templates --lint
uv run pytest
```

### Pull Request Checklist
- [ ] All Python files stay within the **400-line** limit.
- [ ] New service methods have unit tests covering happy path, guard-clause errors (`BusinessLogicError`), and cache invalidation.
- [ ] List views and selectors prevent `N+1` queries (`select_related` / `prefetch_related`).
- [ ] Architectural or model changes are reflected in [`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md) and [`CHANGELOG.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CHANGELOG.md).
