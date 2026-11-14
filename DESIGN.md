# UI/UX Design Guide (DESIGN)

Visual design system, layout structure, component patterns, and accessibility standards for **RRSS Creators Analyzer**, built with **semantic HTML5**, **Bootstrap 5**, **Django template libraries**, and **native Web Components**.

---

## 1. UX Design Principles

1. **High-Density Data Clarity**: Prioritize scannable `django-tables2` listings, `font-variant-numeric: tabular-nums` alignment, and clear hierarchy between primary KPIs (combined revenue, average CCV) and secondary breakdowns.
2. **Consistent Platform Recognition**: `Twitch`, `YouTube`, `Kick`, and `TikTok` each have dedicated color tokens and badges.
3. **Immediate Channel Health Visibility**: Active alerts (`dmca_strike`, `tos_violation`, `unusual_drop`, `suspicious_traffic`) surface on creator profiles and dashboards using semantic severity states (`critical`, `warning`, `info`).
4. **URL-Preserved Filtering**: Every analytical listing exposes a `django-filter` + `django-widget-tweaks` filter bar backed by `GET` query parameters so filtered views are shareable.

---

## 2. Visual Tokens & Color System (Bootstrap 5)

Supports Bootstrap 5 light and dark modes (`data-bs-theme="light"` / `"dark"`) with custom properties in [`rrss_creatos_analyzer/static/css/project.css`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/static/css/project.css):

```css
:root {
  --rrss-primary: #0f766e;
  --rrss-primary-hover: #115e59;

  --platform-twitch-bg: rgba(145, 70, 255, 0.12);
  --platform-twitch-text: #772ce8;
  --platform-twitch-border: rgba(145, 70, 255, 0.35);

  --platform-youtube-bg: rgba(255, 0, 0, 0.10);
  --platform-youtube-text: #cc0000;
  --platform-youtube-border: rgba(255, 0, 0, 0.30);

  --platform-kick-bg: rgba(83, 252, 24, 0.15);
  --platform-kick-text: #1b7a00;
  --platform-kick-border: rgba(83, 252, 24, 0.45);

  --platform-tiktok-bg: rgba(0, 242, 234, 0.12);
  --platform-tiktok-text: #007a76;
  --platform-tiktok-border: rgba(254, 44, 85, 0.35);

  --font-mono-metrics: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

[data-bs-theme="dark"] {
  --platform-twitch-text: #bf94ff;
  --platform-youtube-text: #ff6b6b;
  --platform-kick-text: #53fc18;
  --platform-tiktok-text: #00f2ea;
}
```

### Status & Severity Badges

| Domain Context | Value | Bootstrap 5 Class |
|---|---|---|
| Creator status | `active` / `inactive` / `suspended` | `.badge.text-bg-success` / `.text-bg-secondary` / `.text-bg-danger` |
| Alert severity | `info` / `warning` / `critical` | `.badge.text-bg-info` / `.text-bg-warning` / `.text-bg-danger` |
| Video status | `draft`/`editing` / `ready` / `published` | `.badge.text-bg-warning` / `.text-bg-info` / `.text-bg-success` |

---

## 3. Semantic Layout & Alignment

```text
+-----------------------------------------------------------------------+
| <header class="navbar sticky-top"> Brand | Navigation | Account       |
+------------------+----------------------------------------------------+
| <nav> Sidebar    | <main id="main-content" class="container-fluid">   |
| (offcanvas < lg) |   <header> Title + Breadcrumbs + Primary Actions   |
|                  |   <section> KPI Summary Cards                      |
|                  |   <aside> Compact Filter Bar (django-filter)       |
|                  |   <section> Data Table (django-tables2) / Charts   |
+------------------+----------------------------------------------------+
```

- **Numeric Columns**: Right-align (`text-end font-monospace` / `tabular-nums`) for `avg_ccv`, `peak_viewers`, `views_count`, `hours_streamed`, `total_earnings`, `roi_percentage`, and `rpm_estimated`. Left-align names, titles, platforms, and statuses.

---

## 4. Component Patterns

- **KPI Cards**: `<article class="card h-100 shadow-sm border-0">` with uppercase muted label, bold tabular metric (`h3`), and secondary breakdown.
- **Data Tables (`django-tables2`)**: Wrap `{% render_table table %}` in `<div class="table-responsive">` with `table table-hover table-striped align-middle mb-0` and clear sort indicators.
- **Filter Panels (`django-filter` + `django-widget-tweaks`)**: Compact `<aside aria-label="Filters">` using `form-control-sm` / `form-select-sm` and an explicit "Reset filters" link.
- **Management Forms (`crispy-bootstrap5`)**: Group related inputs inside `<fieldset>` + `<legend>` and use `PrependedText("$")` for currency fields.
- **Interactive Web Components**: `<rrss-kpi-sparkline>`, `<rrss-revenue-chart>`, `<rrss-video-roi-preview>`, and `<rrss-live-activity-feed>`.
- **Multi-Step Wizards (`django-formtools`)**: Centered `col-12 col-lg-8 mx-auto` container, `.progress` bar with dynamic `aria-valuenow`, consistent footer actions (`Cancel`, `Previous Step`, `Next Step` / `Finish & Save`), and a confirmation summary on the final step for financial/contract flows.

---

## 5. Accessibility (WCAG 2.1 Level AA)

1. Minimum contrast ratio of `4.5:1` (normal text) and `3:1` (large text/UI icons) in both light and dark themes.
2. Include a skip link (`<a class="visually-hidden-focusable" href="#main-content">`) and preserve `:focus-visible` outlines.
3. Render Django `messages` inside live regions (`role="status"` or `role="alert"`, `aria-live="polite"`) and associate tables with headings via `aria-labelledby` or `<caption>`.
