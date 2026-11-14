# Code Style Guide

Coding, formatting, template, and frontend conventions for **RRSS Creators Analyzer**.

---

## 1. Python & Django Standards

### 1.1 Formatting, Linting & Static Typing
- **Python `3.14.x`**: Use modern type syntax (`list[str]`, `dict[str, Any]`, `int | None`).
- **Ruff** ([`pyproject.toml`](file:///home/diego/Proyectos/rrss-creators-analyzer/pyproject.toml)):
  - Max line length: `88` characters (Python), `119` characters (templates).
  - Single-line imports enforced (`lint.isort.force-single-line = true`).
  - Django lint rules (`DJ`) enabled: models must define `__str__` and avoid `null=True` on string fields (`CharField`, `TextField`, `URLField`).
- **Mypy**:
  - Explicit parameter and return type annotations required on all `services.py`, `selectors.py`, and utility functions.
  - Configured with `mypy_django_plugin.main` and `mypy_drf_plugin.main`.

### 1.2 Model Section Ordering (`models.py`)
1. Inner `TextChoices` / `IntegerChoices` (if model-specific).
2. Relationship fields (`ForeignKey`, `OneToOneField`, `ManyToManyField`).
3. Domain data fields (`CharField`, `IntegerField`, `DecimalField`, `DateTimeField`, `GeneratedField`).
4. Tag/audit managers (`tags = TaggableManager()`, `history = HistoricalRecords()`).
5. Custom manager (`objects = ...`).
6. `class Meta` (`verbose_name`, `verbose_name_plural`, `ordering`, `indexes`, `constraints`, `permissions`).
7. `__str__(self) -> str`.
8. `get_absolute_url(self) -> str`.
9. Read-only `@property` display helpers.

### 1.3 Naming Conventions
- **Models**: Singular `PascalCase` (`Creator`, `Channel`, `StreamingSession`, `Video`, `VideoPublication`).
- **Tables (`django-tables2`)**: `<ModelName>Table`.
- **Filters (`django-filter`)**: `<ModelName>Filter`.
- **Wizards (`django-formtools`)**: `<Flow>WizardView` and `<Flow><Step>Form`.
- **Services**: `<Domain>Service` with imperative `snake_case` `@classmethod`s (`create_creator`, `record_session`).
- **Selectors**: `<Domain>Selector` with query prefixes (`get_by_id`, `get_visible_queryset`, `get_performance_summary`).

---

## 2. Django Templates & Semantic HTML5

### 2.1 `djLint` Rules
All templates in `rrss_creatos_analyzer/` must pass `djLint` (profile `django`, 2-space indent):
- Blank line after `{% load ... %}` and `{% extends ... %}`.
- Self-close void elements (`<img ... />`, `<input ... />`, `<hr />`, `<br />`).
- Always include descriptive `alt` and `meta` attributes (`H017`, `H035`).

### 2.2 Semantic HTML5 (No `div`-Soup)
Use semantic elements whenever applicable:
- `<header>`, `<nav aria-label="...">`, `<main id="main-content">`, `<section aria-labelledby="...">`, `<article>`, `<aside>`, `<figure>`/`<figcaption>`, and `<time datetime="YYYY-MM-DDTHH:MM:SSZ">`.

### 2.3 Multi-Step Wizard Templates (`django-formtools`)
- Render progress inside `<nav aria-label="Wizard progress">`.
- Include `{{ wizard.management_form }}` immediately inside `<form method="post">`.
- Render the active step form via `{% crispy wizard.form %}`.
- Provide Cancel (`<a>`), Back (`<button name="wizard_goto_step" value="{{ wizard.steps.prev }}">` when present), and Next/Submit (`<button type="submit">`).

---

## 3. CSS & Bootstrap 5

1. Prefer Bootstrap 5 grid, spacing, flex, and semantic theme utilities (`text-body-secondary`, `bg-body-tertiary`) over custom CSS.
2. Define custom platform brand tokens and dark-mode overrides via CSS custom properties in [`rrss_creatos_analyzer/static/css/project.css`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/static/css/project.css).
3. Avoid inline `style="..."` attributes in templates except for dynamic computed CSS variables (e.g., progress bar width).

---

## 4. Vanilla JS & Web Components

The frontend does **not** use SPA frameworks (React, Vue, Angular) or Node build pipelines.

- **Vanilla ES6+ JS**: Bootstrap tooltip/popover initialization, copy-to-clipboard, confirmation prompts, and keyboard shortcuts.
- **Native Web Components (`Custom Elements`)**: Encapsulate stateful client widgets (`<rrss-metrics-chart>`, `<rrss-date-range-picker>`, `<rrss-video-roi-preview>`).
  - Use a hyphenated `rrss-` tag prefix.
  - Render in **Light DOM** by default so Bootstrap 5 styles apply automatically.
  - Bind listeners with `AbortController` in `connectedCallback()` and call `abort()` in `disconnectedCallback()`.
  - Pass server data safely via `data-*` attributes and Django's `{{ data|json_script:"..." }}`.
