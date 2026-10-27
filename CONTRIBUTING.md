# Guía de Contribución (CONTRIBUTING)

¡Gracias por contribuir a **RRSS Creators Analyzer**! Este documento detalla el flujo de trabajo con Git, las convenciones de commits, el entorno de desarrollo local y la lista de verificación requerida antes de enviar un Pull Request.

---

## 1. Flujo de Trabajo y Ramas (Git Branching)

No se permite realizar commits directamente sobre la rama `main`. Todo cambio debe desarrollarse en una rama dedicada siguiendo esta nomenclatura:

- **Nuevas funcionalidades**: `feature/<scope>-<descripcion-corta>` (ej. `feature/streams-session-table`, `feature/videos-roi-selector`)
- **Corrección de errores**: `bugfix/<scope>-<descripcion-corta>` (ej. `bugfix/alerts-status-filter`)
- **Parches críticos en producción**: `hotfix/<descripcion-corta>`
- **Documentación o mantenimiento**: `chore/<scope>-<descripcion-corta>` o `docs/<descripcion-corta>`

---

## 2. Estándar de Mensajes de Commit (Conventional Commits)

Todos los mensajes de commit deben seguir el formato **Conventional Commits**:

```text
<type>(<scope>): <descripción corta en modo imperativo>

- Detalle técnico explicando el qué y el porqué del cambio
- Referencia a modelos, servicios o reglas actualizadas
```

### Tipos Permitidos (`<type>`)
- `feat`: Nueva funcionalidad para el usuario o el sistema.
- `fix`: Corrección de un bug.
- `docs`: Cambios exclusivos en documentación (`*.md`, `/docs`).
- `style`: Cambios de formato, estilos Bootstrap 5, CSS o linting sin cambios de lógica.
- `refactor`: Refactorización de código sin alterar el comportamiento funcional.
- `perf`: Mejoras de rendimiento (optimización de queries ORM, índices SQLite, caché en `DiskCache`).
- `test`: Adición o corrección de pruebas con `pytest` y `factory-boy`.
- `chore`: Actualización de dependencias (`pyproject.toml`, `uv.lock`), configuración o scripts.

### Ámbitos Permitidos (`<scope>`)
- `users`: Autenticación, perfiles y roles de la compañía.
- `creators`: Modelos, vistas y servicios de creadores y canales.
- `streams`: Sesiones de streaming en vivo y métricas CCV/ingresos.
- `videos`: Videos, publicaciones por plataforma y relaciones entre contenidos.
- `alerts`: Sistema de alertas, advertencias TOS y strikes DMCA.
- `imports`: Procesamiento de lotes CSV/XLSX (`django-import-export`).
- `analytics`: Dashboards, rankings, agregaciones y caché en `DiskCache`.
- `core`: Utilidades transversales, modelos base, configuración de SQLite/DiskCache.
- `ui`: Plantillas HTML5, tablas (`django-tables2`), filtros (`django-filter`), formularios (`crispy-forms`) y Web Components.
- `docs`: Documentación del repositorio.

---

## 3. Reglas de Ingeniería Obligatorias

Antes de escribir código, asegúrate de revisar [`GUIDELINES.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/GUIDELINES.md) y [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/STYLE_GUIDE.md):

1. **Arquitectura Single-Tenant**: No agregues `tenant_id` ni `organization_id`. El sistema es exclusivo para una única compañía.
2. **Separación en Capas**:
   - Lecturas complejas y filtros por rol en `selectors.py`.
   - Mutaciones y transacciones (`@transaction.atomic`) en `services.py`.
   - Cero lógica de negocio en `models.py`, `views.py` o `signals`.
3. **Uso del Ecosistema Django**:
   - Usa **`django-tables2`** para tablas de datos.
   - Usa **`django-filter`** para búsquedas y filtros.
   - Usa **`django-crispy-forms`** (`crispy-bootstrap5`) y **`django-widget-tweaks`** para formularios.
4. **Frontend Limpio**:
   - HTML5 semántico + Bootstrap 5 + JS Vanilla / Web Components nativos.

---

## 4. Verificación de Calidad Previa al Pull Request

Ejecuta siempre los siguientes comandos localmente antes de abrir un Pull Request:

```bash
# 1. Linting y formato de Python con Ruff
uv run ruff check .
uv run ruff format --check .

# 2. Verificación estática de tipos con Mypy
uv run mypy rrss_creatos_analyzer

# 3. Linting de plantillas HTML5/Django con djLint
uv run djlint rrss_creatos_analyzer/templates --lint

# 4. Ejecución de pruebas automatizadas con Pytest
uv run pytest
```

### Lista de Verificación (PR Checklist)
- [ ] El código respeta el límite de **400 líneas por archivo**.
- [ ] Los nuevos servicios tienen cobertura de pruebas unitarias (caso exitoso, error de validación e invalidación de `DiskCache`).
- [ ] Las vistas de listado y selectores están protegidos contra consultas `N+1` (`select_related` / `prefetch_related`).
- [ ] Si se modificó algún modelo, servicio o regla de arquitectura, se actualizaron sincrónicamente [`DOCS.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/DOCS.md) y [`CHANGELOG.md`](file:///home/diego/Proyectos/rrss-creators-analyzer/CHANGELOG.md).
