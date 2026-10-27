# Guía de Estilo de Código (STYLE_GUIDE)

Esta guía define las convenciones de estilo, formato y estructura de código para **Python / Django**, **HTML5 Semántico / Templates**, **CSS / Bootstrap 5**, y **JavaScript Vanilla / Web Components** en **RRSS Creators Analyzer**.

---

## 1. Estándares de Python y Django

### 1.1 Formateo, Linting y Tipado Estático
- **Versión de Python**: `3.14.x`. Utilizar sintaxis moderna de tipado (`list[str]`, `dict[str, Any]`, `int | None`, `type` aliases).
- **Linter y Formateador (`Ruff`)**:
  - Longitud máxima de línea: `88` caracteres (configuración estándar de Ruff) para Python y `119` caracteres en templates (`djLint`).
  - Importaciones ordenadas con `isort` de una sola línea por importación (`lint.isort.force-single-line = true` según [`pyproject.toml`](file:///home/diego/Proyectos/rrss-creators-analyzer/pyproject.toml)).
  - Reglas de Django activas (`DJ` en Ruff): todos los modelos deben definir `__str__`, el orden de secciones del modelo debe ser consistente y no deben existir campos con `null=True` en tipos texto (`CharField`, `TextField`, `URLField`).
- **Verificación de Tipos (`Mypy`)**:
  - Todo método en `services.py`, `selectors.py` y funciones utilitarias **debe** incluir anotaciones de tipo explícitas para argumentos y valores de retorno (`-> QuerySet[Creator]`, `-> StreamingSession`, `-> None`).
  - Se utilizan los plugins `mypy_django_plugin.main` y `mypy_drf_plugin.main`.

### 1.2 Orden de Elementos dentro de un Modelo de Django
En todo archivo `models.py`, las clases de modelo deben respetar el siguiente orden interno:
1. Subclases de opciones (`TextChoices` / `IntegerChoices`) si son exclusivas del modelo.
2. Campos de relaciones (`ForeignKey`, `OneToOneField`, `ManyToManyField`).
3. Campos de datos del dominio (`CharField`, `IntegerField`, `DecimalField`, `DateTimeField`, `GeneratedField`).
4. Gestores de etiquetas o auditoría (`tags = TaggableManager()`, `history = HistoricalRecords()`).
5. `objects = CustomManager()` (si aplica).
6. Clase `Meta` (`verbose_name`, `verbose_name_plural`, `ordering`, `indexes`, `constraints`).
7. Método `__str__(self) -> str`.
8. Método `get_absolute_url(self) -> str` (si aplica).
9. Propiedades de solo lectura (`@property`) puramente de formato o presentación simple.

### 1.3 Nomenclatura en Python
- **Modelos**: Singular en `PascalCase` (`Creator`, `Channel`, `StreamingSession`, `Video`, `VideoPublication`, `VideoRelation`, `ChannelAlert`, `ImportBatch`).
- **Tablas (`django-tables2`)**: `<ModelName>Table` (ej. `CreatorTable`, `StreamingSessionTable`, `VideoPublicationTable`).
- **Filtros (`django-filter`)**: `<ModelName>Filter` (ej. `CreatorFilter`, `StreamingSessionFilter`).
- **Asistentes Multi-Paso (`django-formtools`)**: `<Flow>WizardView` (ej. `CreatorOnboardingWizardView`, `CampaignSetupWizardView`, `PayoutApprovalWizardView`).
- **Formularios de Paso en Asistentes**: `<Flow>Step<Name>Form` o `<Flow><Name>StepForm` (ej. `CreatorProfileStepForm`, `CreatorChannelsStepForm`, `CreatorContractStepForm`).
- **Servicios**: `<Domain>Service` con verbos imperativos claros en `snake_case` (`create_creator`, `record_session`, `publish_video`, `resolve_alert`).
- **Selectores**: `<Domain>Selector` con prefijos de consulta (`get_by_id`, `list_active_creators`, `get_monthly_revenue_summary`, `get_creator_rankings`).

---

## 2. Estándares de Plantillas Django y HTML5 Semántico

### 2.1 Reglas de `djLint`
Todas las plantillas en `rrss_creatos_analyzer/templates/` se validan y formatean con `djLint` (perfil `django`, indentación de `2` espacios):
- Línea en blanco obligatoria después de `{% load ... %}` y `{% extends ... %}`.
- Cerrar siempre etiquetas vacías (`<img ... />`, `<input ... />`, `<hr />`, `<br />`).
- Incluir siempre atributos `alt` en imágenes y `meta` descriptivos (`H017`, `H035`).

### 2.2 Uso Estrictamente Semántico de HTML5
- **Prohibido el "div-soup"**: No utilizar `<div>` genéricos cuando exista un elemento semántico apropiado en HTML5:
  - `<header>`: Encabezado global o cabecera de una sección/página (título, breadcrumbs y acciones principales).
  - `<nav aria-label="...">`: Navegación lateral (sidebar), barra superior, pestañas de plataforma, progreso de asistentes y paginación de tablas.
  - `<main id="main-content">`: Contenedor único del contenido principal de la vista.
  - `<section aria-labelledby="...">`: Agrupación temática (ej. sección de KPIs financieros, sección de tabla de sesiones, tarjeta del paso del asistente).
  - `<article>`: Unidad independiente de contenido repetible o autocontenido (ej. tarjeta de perfil de un creador, tarjeta de alerta crítica, detalle de un video).
  - `<aside>`: Paneles laterales de filtros (`django-filter`), resúmenes secundarios o metadatos del canal.
  - `<figure>` y `<figcaption>`: Contenedores para gráficos analíticos, miniaturas de videos (`thumbnail_url`) y avatares con leyenda.
  - `<time datetime="YYYY-MM-DDTHH:MM:SSZ">`: Todas las fechas de transmisión (`streamed_at`), publicación (`published_at`) y ocurrencia de alertas (`occurred_at`).

### 2.3 Integración de Librerías de Plantillas

```html
{% extends "base.html" %}
{% load crispy_forms_tags %}
{% load django_tables2 %}
{% load widget_tweaks %}

{% block content %}
  <main id="main-content" class="container-fluid py-4">
    <header class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-1">Sesiones de Streaming</h1>
        <p class="text-body-secondary mb-0">Registro histórico de transmisiones y métricas financieras</p>
      </div>
      <a href="{% url 'streams:create' %}" class="btn btn-primary">
        Registrar Sesión
      </a>
    </header>

    <aside aria-label="Filtros de búsqueda" class="card shadow-sm mb-4">
      <div class="card-body">
        <form method="get" class="row g-3 align-items-end">
          <div class="col-12 col-md-3">
            <label for="{{ filter.form.creator.id_for_label }}" class="form-label small fw-semibold">
              {{ filter.form.creator.label }}
            </label>
            {% render_field filter.form.creator class+="form-select form-select-sm" %}
          </div>
          <div class="col-12 col-md-3">
            <label for="{{ filter.form.platform.id_for_label }}" class="form-label small fw-semibold">
              {{ filter.form.platform.label }}
            </label>
            {% render_field filter.form.platform class+="form-select form-select-sm" %}
          </div>
          <div class="col-12 col-md-4">
            <label for="{{ filter.form.game_or_category.id_for_label }}" class="form-label small fw-semibold">
              {{ filter.form.game_or_category.label }}
            </label>
            {% render_field filter.form.game_or_category class+="form-control form-control-sm" placeholder="Ej. Just Chatting, Valorant..." %}
          </div>
          <div class="col-12 col-md-2 d-flex gap-2">
            <button type="submit" class="btn btn-sm btn-primary w-100">Filtrar</button>
            <a href="{% url 'streams:list' %}" class="btn btn-sm btn-outline-secondary">Limpiar</a>
          </div>
        </form>
      </div>
    </aside>

    <section aria-labelledby="sessions-table-heading" class="card shadow-sm">
      <div class="card-header bg-transparent py-3">
        <h2 id="sessions-table-heading" class="h6 mb-0">Listado de Transmisiones</h2>
      </div>
      <div class="table-responsive">
        {% render_table table %}
      </div>
    </section>
  </main>
{% endblock content %}
```

### 2.4 Integración de Asistentes en Múltiples Pasos (`django-formtools`)
- Las plantillas de asistentes deben estructurarse con una barra de progreso semántica dentro de `<nav aria-label="Progreso del asistente">`.
- Incluir de forma obligatoria `{{ wizard.management_form }}` inmediatamente después de la etiqueta `<form>` para mantener la integridad del estado de sesión.
- Renderizar el formulario del paso activo utilizando `{% crispy wizard.form %}`.
- La botonera de navegación debe incluir:
  - Botón de cancelación (`<a>`) a la izquierda.
  - Botón de retroceso opcional si `wizard.steps.prev` existe (`<button name="wizard_goto_step" type="submit" value="{{ wizard.steps.prev }}">`).
  - Botón de avance o finalización primario (`<button type="submit">`).

---

## 3. Estándares de CSS y Bootstrap 5

1. **Prioridad a Clases Utilitarias y Componentes de Bootstrap 5**:
   - Utilizar el sistema de grillas (`container-fluid`, `row`, `col-*`), utilidades de espaciado (`p-*`, `m-*`, `gap-*`), flexbox (`d-flex`, `justify-content-*`, `align-items-*`) y colores semánticos (`text-body-secondary`, `bg-body-tertiary`) de Bootstrap 5.
   - Evitar escribir CSS personalizado para layouts o componentes que Bootstrap 5 ya resuelve de forma nativa.
2. **Variables CSS (Custom Properties) en `project.css`**:
   - Cualquier personalización visual (como los colores de marca de `Twitch`, `YouTube`, `Kick`, `TikTok` o ajustes de tema claro/oscuro con `data-bs-theme`) debe definirse mediante variables CSS en `:root` dentro de [`rrss_creatos_analyzer/static/css/project.css`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/static/css/project.css).
3. **Cero Estilos Inline**:
   - Prohibido el uso del atributo `style="..."` en plantillas HTML, salvo cuando se trate de variables CSS dinámicas calculadas (ej. porcentajes en barras de progreso `style="--progress-width: 75%;"` o `style="width: 50%;"` en `.progress-bar`).

---

## 4. Estándares de JavaScript Vanilla y Web Components

El proyecto **no utiliza frameworks pesados de SPA** (ni React, ni Vue, ni Angular) ni requiere cadenas complejas de transpilación en Node para la lógica de negocio.

### 4.1 Cuándo usar JS Vanilla vs. Web Components
- **JavaScript Vanilla (ES6+ modular)**:
  - Inicialización de tooltips/popovers de Bootstrap 5.
  - Mejoras progresivas simples (confirmaciones, copiado al portapapeles, atajos de teclado).
- **Web Components Nativos (`Custom Elements`)**:
  - Para toda **interacción compleja con estado en el cliente**, tales como:
    - Gráficos interactivos de rendimiento de creadores (`<creator-metrics-chart>`).
    - Selectores rápidos de rango de fechas con preajustes (`<date-range-picker>`).
    - Previsualizadores de lotes de importación CSV/XLSX con validación previa (`<import-batch-preview>`).
    - Calculadoras de ROI/RPM en tiempo real en formularios de publicaciones (`<video-roi-calculator>`).
    - Buscadores dinámicos de relación entre videos y sesiones de streaming (`<video-relation-selector>`).

### 4.2 Convenciones para Web Components
1. **Prefijo de etiqueta obligatorio**: Todos los Custom Elements deben tener un nombre con guion, preferiblemente con el prefijo `rrss-` o descriptivo del dominio (`<rrss-metrics-chart>`, `<rrss-alert-counter>`, `<rrss-date-filter>`).
2. **Light DOM por defecto para compatibilidad con Bootstrap 5**:
   - A menos que se requiera aislamiento estricto de estilos, renderizar dentro del Light DOM (sin `attachShadow`) para que el componente herede automáticamente las clases y variables de **Bootstrap 5**.
3. **Ciclo de vida limpio**:
   - Registrar listeners en `connectedCallback()` y limpiarlos obligatoriamente en `disconnectedCallback()` (usando `AbortController` para `addEventListener`).
4. **Paso de datos desde Django**:
   - Pasar configuraciones simples mediante atributos `data-*` y estructuras de datos JSON mediante la etiqueta segura de Django `{{ data|json_script:"chart-data-id" }}` leída desde el Web Component.

```javascript
// Ejemplo canónico de Web Component en rrss_creatos_analyzer/static/js/components/metrics-chart.js
class RrssMetricsChart extends HTMLElement {
  #abortController = null;

  connectedCallback() {
    this.#abortController = new AbortController();
    const dataScriptId = this.dataset.sourceId;
    const scriptEl = dataScriptId ? document.getElementById(dataScriptId) : null;

    if (!scriptEl) return;

    const payload = JSON.parse(scriptEl.textContent);
    this.render(payload);
  }

  disconnectedCallback() {
    this.#abortController?.abort();
  }

  render(payload) {
    // Renderizado accesible y reactivo dentro del componente
  }
}

if (!customElements.get("rrss-metrics-chart")) {
  customElements.define("rrss-metrics-chart", RrssMetricsChart);
}
```
