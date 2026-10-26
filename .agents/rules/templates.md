---
trigger: always_on
---

# RRSS Creators Analyzer: Templates & Frontend Guidelines

## Core Principles

1. **Server-Side Rendering (SSR) Semantic HTML5**:
   - Standard Django templates (`{% extends %}`, `{% block %}`, `{% include %}`) formatted with `djLint` (2-space indentation, profile `django`).
   - Strictly semantic HTML5 tags (`<main>`, `<header>`, `<nav>`, `<section>`, `<article>`, `<aside>`, `<figure>`, `<time>`). Avoid generic `<div>` soup.
   - No heavyweight SPA frameworks (no React, Vue, or Angular).
2. **Bootstrap 5 & Django Ecosystem Template Tags**:
   - Render tables with `{% load django_tables2 %}` and `{% render_table table %}`.
   - Render structured forms with `{% load crispy_forms_tags %}` and `{% crispy form %}` (`crispy-bootstrap5`).
   - Customize filter bar controls inline in templates using `{% load widget_tweaks %}` and `{% render_field filter.form.field class+="form-control form-control-sm" %}`.
3. **Vanilla JS & Native Web Components**:
   - Use Vanilla JavaScript (ES6+) for lightweight progressive enhancement and Bootstrap 5 component initialization.
   - Use native Custom Elements (`customElements.define("rrss-...", ...)`) for complex client-side interactive widgets (charts, ROI/RPM calculators, date-range pickers, import batch previews).
   - Pass structured data from Django to Web Components safely via `{{ data|json_script:"data-id" }}`.
4. **Accessibility (WCAG 2.1 AA)**:
   - Always associate labels with inputs, provide `aria-labelledby` on `<section>` and tables, and use `aria-live="polite"` for dynamic notifications.
