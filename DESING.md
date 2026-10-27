# Guía de Diseño UI/UX (DESING)

Este documento define el sistema de diseño, lineamientos de interfaz de usuario (UI) y experiencia de usuario (UX) para **RRSS Creators Analyzer**. El objetivo es ofrecer una interfaz analítica de alta densidad de información, clara, accesible y rápida, construida sobre **HTML5 semántico**, **Bootstrap 5**, **librerías de plantillas de Django** y **Web Components**.

---

## 1. Principios de Diseño UX para Analítica de Creadores

1. **Claridad en Datos de Alta Densidad**:
   - Los talent managers y analistas consultan decenas de métricas simultáneamente (CCV, Peak Viewers, Horas transmitidas, Vistas de Video, Ingresos por Ads/Subs/Donaciones, ROI y RPM).
   - Priorizar tablas escaneables (`django-tables2`), números tabulares (`font-variant-numeric: tabular-nums`) y jerarquía visual clara entre métricas primarias (Ingresos combinados, CCV promedio) y secundarias.
2. **Identificación Visual Inmediata por Plataforma**:
   - Cada plataforma (`Twitch`, `YouTube`, `Kick`, `TikTok`) cuenta con un token de color e insignia semántica consistente en toda la aplicación.
3. **Visibilidad de Estado y Salud del Canal**:
   - Las alertas activas de canal (`dmca_strike`, `tos_violation`, `unusual_drop`, `suspicious_traffic`) deben destacarse inmediatamente en el perfil del creador y en el encabezado del dashboard según su severidad (`critical`, `warning`, `info`).
4. **Cero Fricción en Filtrado y Exportación**:
   - Todo listado analítico ofrece una barra de filtrado superior o lateral (`django-filter` + `django-widget-tweaks`) que mantiene el estado en los parámetros GET de la URL (permitiendo compartir enlaces de reportes filtrados entre managers).

---

## 2. Sistema de Tokens Visuales y Paleta de Colores (Bootstrap 5)

El sistema aprovecha el soporte nativo de modos de color de Bootstrap 5 (`data-bs-theme="light"` y `data-bs-theme="dark"`) junto con variables CSS personalizadas definidas en [`rrss_creatos_analyzer/static/css/project.css`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/static/css/project.css).

### 2.1 Variables CSS del Dominio (`:root`)

```css
:root {
  /* Identidad principal de la plataforma */
  --rrss-primary: #0f766e;
  --rrss-primary-hover: #115e59;

  /* Colores oficiales por Plataforma de Streaming / Video */
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

  /* Tipografía para métricas numéricas */
  --font-mono-metrics: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

[data-bs-theme="dark"] {
  --platform-twitch-text: #bf94ff;
  --platform-youtube-text: #ff6b6b;
  --platform-kick-text: #53fc18;
  --platform-tiktok-text: #00f2ea;
}
```

### 2.2 Semántica de Estados y Severidades

| Contexto de Dominio | Valor | Clase Bootstrap 5 Recomendada | Uso Visual |
|---|---|---|---|
| **Estado del Creador** | `active` | `.badge.text-bg-success` | Creador en activo transmitiendo/publicando |
| **Estado del Creador** | `inactive` | `.badge.text-bg-secondary` | Creador en pausa o baja temporal |
| **Estado del Creador** | `suspended` | `.badge.text-bg-danger` | Creador suspendido o con cuenta bloqueada |
| **Severidad de Alerta** | `info` | `.alert-info` / `.badge.text-bg-info` | Notificación informativa de canal |
| **Severidad de Alerta** | `warning` | `.alert-warning` / `.badge.text-bg-warning` | Advertencia TOS, caída inusual de CCV |
| **Severidad de Alerta** | `critical` | `.alert-danger` / `.badge.text-bg-danger` | Strike de DMCA o riesgo inminente de baneo |
| **Estado de Video** | `draft` / `editing` | `.badge.text-bg-warning` | En producción antes de publicar |
| **Estado de Video** | `ready` | `.badge.text-bg-info` | Listo para programar publicación |
| **Estado de Video** | `published` | `.badge.text-bg-success` | Publicado y generando métricas |

---

## 3. Arquitectura de Layout y Navegación Semántica

La interfaz se organiza en un layout de aplicación administrativa con **HTML5 semántico**:

```text
+-----------------------------------------------------------------------+
| <header class="navbar sticky-top"> Logo | Buscador Global | Perfil    |
+------------------+----------------------------------------------------+
| <nav> Sidebar    | <main id="main-content" class="container-fluid">   |
|                  |   <header> Breadcrumbs + Título + Botones Acción   |
| - Dashboard      |   +----------------------------------------------+ |
| - Creadores      |   | <section> KPI Cards (Row 4 cols Bootstrap)   | |
| - Streams        |   +----------------------------------------------+ |
| - Videos         |   | <aside> Barra de Filtros (django-filter)     | |
| - Ranking Global |   +----------------------------------------------+ |
| - Alertas/Strikes|   | <section> Tabla de Datos (django-tables2)    | |
| - Importaciones  |   |           o Gráficos (<rrss-metrics-chart>)  | |
+------------------+---+----------------------------------------------+ |
```

### Reglas de Layout
1. **Responsividad**:
   - En pantallas `>= lg` (`992px`), barra de navegación lateral fija y área principal fluida (`container-fluid`).
   - En móviles y tablets (`< lg`), el `<nav>` lateral se convierte en un componente `.offcanvas-lg` nativo de Bootstrap 5.
2. **Alineación Numérica en Tablas**:
   - Todas las columnas de métricas (`avg_ccv`, `peak_viewers`, `views_count`, `hours_streamed`, `total_earnings`, `roi_percentage`, `rpm_estimated`) deben alinearse a la derecha (`class="text-end font-monospace"` o `tabular-nums`) para facilitar la comparación vertical de cifras.
   - Los nombres, títulos, plataformas y estados se alinean a la izquierda (`text-start`).

---

## 4. Patrones de Componentes UI

### 4.1 Tarjetas de KPI (KPI Summary Cards)
Utilizadas en la parte superior del Dashboard General, del Perfil del Creador y del Resumen Mensual de Ingresos:
- Emplear `<article class="card h-100 shadow-sm border-0">`.
- Mostrar:
  1. Etiqueta superior en `text-body-secondary small text-uppercase fw-semibold`.
  2. Valor principal destacado en `h3 fw-bold mb-1 tabular-nums`.
  3. Indicador de variación o desglose secundario (ej. `"Streams: $1,200 | Videos: $450"`).

### 4.2 Tablas Interactivas (`django-tables2`)
- Envolver siempre `{% render_table table %}` en un contenedor `<div class="table-responsive">`.
- Clases base de tabla: `table table-hover table-striped align-middle mb-0`.
- Los encabezados ordenables (`th.orderable`) deben mostrar un indicador visual claro del sentido de ordenación (`asc` / `desc`).
- Incluir en el pie de la tarjeta el resumen de registros y la paginación compatible con Bootstrap 5.

### 4.3 Paneles de Filtrado (`django-filter` + `django-widget-tweaks`)
- Ubicar los filtros en un `<aside aria-label="Filtros">` inmediatamente encima de la tabla.
- Usar controles compactos (`form-control-sm`, `form-select-sm`) mediante `{% render_field %}` de `django-widget-tweaks` para no desplazar excesivamente el contenido principal hacia abajo.
- Mostrar un contador o insignia cuando haya filtros activos y un botón claro de **"Limpiar filtros"**.

### 4.4 Formularios de Gestión (`django-crispy-forms`)
- Todos los formularios de creación/edición (`Creator`, `Channel`, `StreamingSession`, `Video`, `VideoPublication`, `ChannelAlert`) se estructuran con `crispy-bootstrap5`.
- Agrupar campos relacionados en `<fieldset>` con `<legend class="h6 border-bottom pb-2 mb-3">`:
  - Ejemplo en `StreamingSessionForm`:
    - Fieldset 1: *Datos del Stream y Canal* (`creator`, `channel`, `platform`, `session_title`, `game_or_category`, `streamed_at`, `duration_seconds`).
    - Fieldset 2: *Métricas de Audiencia* (`avg_ccv`, `peak_viewers`, `chat_messages_count`, `new_followers`).
    - Fieldset 3: *Desglose de Ingresos* (`ad_revenue`, `subs_revenue`, `donations_revenue` con `PrependedText("$")`).

### 4.5 Web Components de Interfaz Rica
Cuando se requiera interacción dinámica en el cliente, encapsularla en Web Components nativos:
- `<rrss-kpi-sparkline>`: Mini-gráfico de tendencia dentro de tarjetas KPI.
- `<rrss-revenue-chart>`: Gráfico comparativo de ingresos mensuales (Streams vs. Videos).
- `<rrss-video-roi-preview>`: Componente en el formulario de publicaciones que calcula en vivo el **Beneficio Neto**, **ROI (%)** y **RPM estimado** a medida que el analista ingresa costos de producción, vistas e ingresos estimados.
- `<rrss-live-activity-feed>`: Timeline unificado (equivalente a `v_recent_channel_activity`) con filtro rápido por pestañas (`Todos`, `Streams`, `Videos`, `Alertas`) sin recargar la página.

### 4.6 Asistentes y Formularios Multi-Paso (`django-formtools` / Steppers)
Para procesos de registro o configuración extensos (onboarding de talentos, contratos, campañas o liquidaciones financieras):
- **Contenedor enfocado**: Centrar el asistente en un contenedor optimizado (`col-12 col-lg-8 mx-auto`) para reducir dispersión y fatiga de usuario.
- **Barra de Progreso y Stepper Visual**:
  - Encabezado con número y nombre de paso: `<p class="text-body-secondary mb-2">Paso X de Y: <span class="fw-semibold">Título del Paso</span></p>`.
  - Componente `.progress` con altura compacta (`style="height: 6px;"` o `8px`) y valor `aria-valuenow` dinámico según el paso activo (`wizard.steps.step1`).
- **Botonera de Navegación Consistente**:
  - Alineación horizontal con `d-flex justify-content-between align-items-center pt-3 border-top`.
  - Enlace secundario "Cancelar" a la izquierda.
  - Botón "Paso anterior" (`btn-secondary` o `btn-outline-secondary`) si existe paso previo (`wizard.steps.prev`).
  - Botón primario de avance: "Siguiente paso »" o "Finalizar y Guardar" (`btn-primary`) en el último paso.
- **Resumen Previo a la Confirmación**:
  - En flujos críticos (como liquidaciones contables o términos contractuales), el paso final debe presentar un resumen claro de los datos capturados en los pasos anteriores antes de la confirmación final.

---

## 5. Accesibilidad (WCAG 2.1 Nivel AA)

1. **Contraste de Color**:
   - Garantizar una relación de contraste mínima de `4.5:1` en textos normales y `3:1` en textos grandes o componentes gráficos, tanto en tema claro como oscuro.
2. **Navegación por Teclado y Foco Visible**:
   - Incluir enlace `"Saltar al contenido principal"` (`<a class="visually-hidden-focusable" href="#main-content">`) al inicio de `base.html`.
   - Nunca eliminar `:focus-visible` en botones, enlaces de tablas o controles de formulario.
3. **Atributos ARIA y Regiones Vivas**:
   - Los contenedores de alertas y notificaciones de Django (`messages`) deben contar con `role="status"` o `role="alert"` y `aria-live="polite"`.
   - Toda tabla de `django-tables2` debe estar asociada a un título mediante `aria-labelledby` o incluir un `<caption>` descriptivo.
