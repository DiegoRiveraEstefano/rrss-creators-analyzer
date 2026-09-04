# Design System & Arquitectura Visual: `rrss-creators-analyzer`
**Plataforma SaaS Multi-Tenant de Business Intelligence y Analítica para Streaming**

---

## 1. Visión General del Producto y Objetivos de Diseño

`rrss-creators-analyzer` es una plataforma SaaS de alto rendimiento dirigida a **agencias de talentos, mánagers y creadores de contenido de streaming** (Twitch, YouTube Gaming, Kick, TikTok Live). 

### Objetivos Clave de UX/UI:
1. **Densidad de Información sin Sobrecarga:** Jerarquía visual estricta para explorar tablas masivas, KPIs financieros y analíticas de retención.
2. **Contexto Multi-Tenant y Cambio de Rol Fluido:** Distinción inmediata e intuitiva entre la vista de Agencia/Mánager (visión global de roster y comparativas) y la vista de Creador Individual (métricas personales y monetización).
3. **Flujo de Importación Confiable e Interactivo:** Feedback en tiempo real para la validación y normalización en cliente de archivos CSV/Excel antes de la persistencia en Supabase.
4. **Modo Oscuro Profesional:** Estética tipo Bloomberg Terminal / Linear / Datadog adaptada a la cultura del streaming digital.

---

## 2. Paleta de Colores y Tokens

### 2.1 Tokens Fundacionales (Fondo y Superficies)
- **Background Base:** `#090D16` (Deep Obsidian / Navy Black)
- **Surface Level 1 (Sidebars / Cards):** `#111827` (Rich Slate)
- **Surface Level 2 (Modales / Dropdowns / Popovers):** `#1F2937`
- **Surface Border / Divider:** `#2D3748` / `rgba(255, 255, 255, 0.08)`
- **Surface Elevated Glow:** `rgba(99, 102, 241, 0.08)`

### 2.2 Colores de Marca y Acento
- **Brand Primary (Electric Indigo / Violet):** `#6366F1` (Hover: `#4F46E5`, Active: `#4338CA`)
  - Uso: Acciones principales, botones primarios, selector activo.
- **Brand Secondary (Streamer Cyan):** `#06B6D4` (Hover: `#0891B2`)
  - Uso: Métricas de concurrencia en vivo, gráficos de viewers, enlaces de plataforma.
- **Brand Accent (Vivid Purple):** `#8B5CF6`

### 2.3 Colores Semánticos y de Estado (Analytics & Alerts)
- **Success / Positive Trend (Emerald):** `#10B981` (Fondo badge: `rgba(16, 185, 129, 0.12)`)
  - Uso: Crecimiento de suscriptores, ingresos incrementales, subida de retención.
- **Warning / Notice (Amber):** `#F59E0B` (Fondo badge: `rgba(245, 158, 11, 0.12)`)
  - Uso: Alertas de streaming, bajada súbita de horas emitidas, advertencias en importación CSV.
- **Danger / Sanction (Rose/Crimson):** `#EF4444` (Fondo badge: `rgba(239, 68, 68, 0.12)`)
  - Uso: Strikes/sanciones de canal, errores de validación de esquema, infracciones de ToS.
- **Info (Sky Blue):** `#38BDF8`

### 2.4 Tipografía y Colores de Texto
- **Text Primary (Headings & Key Metrics):** `#F9FAFB` (High contrast, 95% opacity)
- **Text Secondary (Subtitles & Labels):** `#9CA3AF`
- **Text Muted / Placeholders:** `#6B7280`
- **Text Inverse:** `#0F172A`

---

## 3. Tipografía

| Rol | Familia Tipográfica | Pesos | Uso |
|---|---|---|---|
| **Headings & UI Base** | `Inter`, system-ui, sans-serif | 500 (Medium), 600 (SemiBold), 700 (Bold) | Títulos de dashboards, navegación, modales, etiquetas |
| **Data & Financial Metrics** | `JetBrains Mono`, `Roboto Mono`, monospace | 500 (Medium), 600 (SemiBold) | Tabular figures para ingresos ($/h), CCV, duración de streams, timestamps |

### Escala de Texto:
- **Display / Big KPI:** `2.25rem (36px)` / Leading `2.5rem` / Bold
- **H1 (Page Titles):** `1.75rem (28px)` / Leading `2.25rem` / SemiBold
- **H2 (Section Titles):** `1.25rem (20px)` / Leading `1.75rem` / SemiBold
- **H3 (Card Headers):** `1.00rem (16px)` / Leading `1.5rem` / Medium
- **Body Regular:** `0.875rem (14px)` / Leading `1.25rem` / Regular
- **Caption / Meta / Badges:** `0.75rem (12px)` / Leading `1rem` / Medium
- **Micro / Subtext:** `0.6875rem (11px)` / Leading `0.875rem`

---

## 4. Estructura y Layout (App Shell Architecture)

La arquitectura de pantalla está pensada para pantallas de escritorio (Desktop First, con soporte responsive).

```
+-----------------------------------------------------------------------------------------------+
| TOPBAR: Selector de Workspace (Agencia / Tenant) | Quick Search | Live Notifications | Perfil |
+-----------------------+-----------------------------------------------------------------------+
| SIDEBAR               | MAIN CONTENT AREA                                                     |
| - Logo & Branding     | +-------------------------------------------------------------------+ |
| - Resumen Ejecutivo   | | Breadcrumb & Page Header + Date Range Filter + Action Buttons     | |
| - Roster de Creadores | +-------------------------------------------------------------------+ |
| - Importador CSV/XLSX | | Row de KPI Stat Cards (Ingresos, Horas, CCV Medio, Alertas/Strikes)| |
| - Analítica Detallada | +-------------------------------------------------------------------+ |
| - Configuración & RLS | | Grid de Visualizaciones (Gráficos interactivos & Series temporales)| |
|                       | +-------------------------------------------------------------------+ |
|                       | | Tabla Dinámica de Alto Rendimiento (Creators / Streams / Alerts)   | |
|                       | +-------------------------------------------------------------------+ |
+-----------------------+-----------------------------------------------------------------------+
```

---

## 5. Componentes de UI Clave

### 5.1 KPI Metric Card
- **Fondo:** `#111827` con borde de `1px` sólido en `#1F2937` y hover sutil `border-indigo-500/40`.
- **Estructura:**
  1. Icono temático en contenedor circular suave (`bg-indigo-500/10 text-indigo-400`).
  2. Etiqueta pequeña en mayúsculas (`text-xs text-gray-400 font-medium tracking-wide`).
  3. Cifra principal en fuente monoespaciada de alta legibilidad (`text-2xl font-bold text-white font-mono`).
  4. Badge de tendencia porcentual con flecha (`↑ +14.8% vs mes anterior` en verde o `↓ -3.2%` en rojo).

### 5.2 Selector de Tenant / Switcher de Roster
- Permite cambiar entre la vista de **Agencia (Todo el Roster)** y **Creador Específico (ej. @Ibai, @Rivers, @IlloJuan)**.
- Muestra avatar del creador, badge de plataforma (Twitch / YouTube) y estado en vivo (punto verde intermitente).

### 5.3 Smart CSV/Excel Import Wizard
- **Paso 1: Drag & Drop:** Dropzone con soporte para drag & drop de archivos `.csv`, `.xlsx`.
- **Paso 2: Validación en Cliente (Browser Engine):**
  - Mapeo de columnas detectadas vs. requeridas (Fecha, Stream ID, Horas Emitidas, Peak Viewers, Average CCV, Donaciones, Ad Revenue).
  - Chip de estado por fila: `Válido`, `Advertencia: fecha parseada`, `Error: valor nulo`.
- **Paso 3: Preview y Carga Masiva:** Previsualización de las primeras 10 filas normalizadas antes de enviar la transacción a Supabase con RLS.

### 5.4 Tabla de Datos y Roster Analytics
- **Header fijo con sticky position** y opciones de ordenamiento numérico instantáneo.
- **Row Hover:** `bg-gray-800/40` con microtransición suave de `150ms`.
- **Columnas clave:** Creador, Plataforma, Horas Transmitidas, Ingreso Estimado por Hora ($/h), Retención Media, Estado de Sanciones/Alertas.

### 5.5 Sistema de Alertas y Sanciones
- Indicador de strikes y alertas de políticas (Twitch TOS / DMCA).
- Tags semánticos: `Sin Sanciones` (Verde), `Warning Activo` (Amarillo), `Strike Crítico` (Rojo neón).

---

## 6. Principios de Interacción y Micro-animaciones
- **Transiciones:** Duración estándar `150ms - 200ms` con curva `cubic-bezier(0.16, 1, 0.3, 1)`.
- **Tooltips:** Inmediatos para métricas financieras y glosario de streaming (ej. "CCV = Concurrent Viewers").
- **Estados Vacíos (Empty States):** Ilustración técnica sutil + botón de llamada a la acción ("Importar primer reporte CSV").

---

## 7. Directrices de Implementación Frontend
- **Framework UI:** Tailwind CSS v3 / Tailwind v4 con variables CSS semánticas.
- **Iconografía:** Lucide Icons / Heroicons (20px para navegación, 16px para tablas y badges).
- **Procesamiento de Archivos:** PapaParse / SheetJS para ejecución en Web Worker en el cliente sin bloquear la UI principal.
- **Charts:** Apache ECharts optimizado con paleta de gradientes oscuros.
