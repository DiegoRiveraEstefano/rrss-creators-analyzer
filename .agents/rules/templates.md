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
   - Render multi-step forms with **`django-formtools`** (`SessionWizardView`), ensuring `{{ wizard.management_form }}` is always present and steps are visually guided via Bootstrap 5 steppers/progress bars.
3. **Vanilla JS & Native Web Components**:
   - Use Vanilla JavaScript (ES6+) for lightweight progressive enhancement and Bootstrap 5 component initialization.
   - Use native Custom Elements (`customElements.define("rrss-...", ...)`) for complex client-side interactive widgets (charts, ROI/RPM calculators, date-range pickers, import batch previews).
   - Pass structured data from Django to Web Components safely via `{{ data|json_script:"data-id" }}`.
4. **Accessibility (WCAG 2.1 AA)**:
   - Always associate labels with inputs, provide `aria-labelledby` on `<section>` and tables, and use `aria-live="polite"` for dynamic notifications.

## Canonical Multi-Step Wizard Template Pattern (`django-formtools`)

When building templates for `SessionWizardView`, provide clear step navigation, accessible indicators, and full Crispy integration:

```html
{% extends "base.html" %}
{% load crispy_forms_tags %}
{% load i18n %}

{% block content %}
  <main id="main-content" class="container py-4">
    <header class="mb-4">
      <h1 class="h3 mb-1">{% block wizard_title %}Asistente de Configuración{% endblock %}</h1>
      <p class="text-body-secondary mb-3">
        Paso {{ wizard.steps.step1 }} de {{ wizard.steps.count }}:
        <span class="fw-semibold">{{ step_title|default:wizard.steps.current }}</span>
      </p>

      <!-- Stepper / Barra de Progreso Semántica -->
      <nav aria-label="Progreso del asistente">
        <div
          class="progress"
          role="progressbar"
          aria-label="Progreso"
          aria-valuenow="{{ wizard.steps.step1 }}"
          aria-valuemin="1"
          aria-valuemax="{{ wizard.steps.count }}"
          style="height: 8px;"
        >
          <div
            class="progress-bar bg-primary"
            style="width: {% widthratio wizard.steps.step1 wizard.steps.count 100 %}%"
          ></div>
        </div>
      </nav>
    </header>

    <section aria-labelledby="wizard-step-section" class="card shadow-sm">
      <div class="card-body p-4">
        <form method="post" enctype="multipart/form-data" novalidate>
          {% csrf_token %}
          {# OBLIGATORIO: el management_form preserva el estado del asistente #}
          {{ wizard.management_form }}

          <div class="mb-4">
            {% crispy wizard.form %}
          </div>

          <footer class="d-flex justify-content-between align-items-center pt-3 border-top">
            <div>
              <a href="{% url 'creators:list' %}" class="btn btn-outline-secondary btn-sm">
                Cancelar
              </a>
            </div>

            <div class="d-flex gap-2">
              {% if wizard.steps.prev %}
                <button
                  name="wizard_goto_step"
                  type="submit"
                  value="{{ wizard.steps.prev }}"
                  class="btn btn-secondary"
                >
                  &laquo; Paso anterior
                </button>
              {% endif %}

              <button type="submit" class="btn btn-primary">
                {% if wizard.steps.step1 == wizard.steps.count %}
                  Finalizar y Guardar
                {% else %}
                  Siguiente paso &raquo;
                {% endif %}
              </button>
            </div>
          </footer>
        </form>
      </div>
    </section>
  </main>
{% endblock %}
```
