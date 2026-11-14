# Architecture & Engineering Guidelines

Mandatory engineering standards for **RRSS Creators Analyzer** (Django 6.0, Python 3.14, single-tenant architecture, PostgreSQL/Redis in production, SQLite WAL/DiskCache locally).

---

## 1. Modularity & Layered Architecture

### 1.1 File & Layer Boundaries
1. **400-Line Limit**: No `.py` file may exceed 400 lines. Split growing modules into packages (`services/`, `selectors/`, `views/`, `tables/`, `wizards/`).
2. **Responsibility Separation**:
   - `models.py`: Fields, `TextChoices`, indexes, `UniqueConstraint`, `CheckConstraint`, `GeneratedField`, `HistoricalRecords()`. Zero business logic or external I/O.
   - `selectors.py`: Read-only `QuerySet`s, permission-based scoping, `select_related`/`prefetch_related`, `annotate`, `Window`, and `cache.get_or_set(...)`. Zero mutations.
   - `services.py`: Write logic, business validation, `@transaction.atomic`, explicit cache invalidation (`transaction.on_commit`), and structured logging.
   - `tables.py`: Declarative `django_tables2.Table` definitions.
   - `filters.py`: Declarative `django_filters.FilterSet` definitions.
   - `forms.py` / `wizards.py`: `crispy-bootstrap5` layouts, `django-autocomplete-light` selectors, and `django-formtools` step forms.
   - `views.py`: Thin CBVs (`SingleTableMixin`, `FilterView`, `SessionWizardView`).

### 1.2 Single-Tenant Rule
- Never add `tenant_id` or `organization_id` columns or pass tenant identifiers to services/selectors.
- Data scoping inside the agency uses `user.has_perm(...)` (`view_all_*` vs `creator__user=user`).

---

## 2. Django Ecosystem Standards

### 2.1 Tables (`django-tables2`)
- Every entity listing uses `django_tables2.Table` with `SingleTableMixin` and `template_name = "django_tables2/bootstrap5.html"`.

```python
import django_tables2 as tables
from .models import StreamingSession


class StreamingSessionTable(tables.Table):
    session_title = tables.Column(linkify=True, verbose_name="Session Title")
    creator = tables.Column(accessor="creator.display_name", verbose_name="Creator")
    hours_streamed = tables.Column(verbose_name="Hours")
    avg_ccv = tables.Column(verbose_name="Avg CCV")
    total_earnings = tables.Column(verbose_name="Earnings ($)")

    class Meta:
        model = StreamingSession
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "streamed_at",
            "creator",
            "platform",
            "session_title",
            "game_or_category",
            "hours_streamed",
            "avg_ccv",
            "peak_viewers",
            "total_earnings",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
```

### 2.2 Filtering (`django-filter`)
- Never write manual `if request.GET.get(...)` filter chains in views. Always use `django_filters.FilterSet` in `filters.py`.

### 2.3 Forms (`django-crispy-forms` & `django-widget-tweaks`)
- Use `FormHelper` + `Layout` (`crispy-bootstrap5`) for create/update forms.
- Use `{% render_field %}` from `django-widget-tweaks` for compact inline filter bars.
- Use `django-autocomplete-light` (`dal.autocomplete`) for large relational selects (`Creator`, `Channel`, `Video`).

### 2.4 Multi-Step Wizards (`django-formtools`)
- Use `formtools.wizard.views.SessionWizardView` for sequential workflows (creator onboarding, campaign setup, payout approval, import column mapping).
- Templates must include `{{ wizard.management_form }}`, a semantic progress indicator, `{% crispy wizard.form %}`, and back navigation via `<button name="wizard_goto_step" type="submit" value="{{ wizard.steps.prev }}">`.
- `done(self, form_list, **kwargs)` must remain free of business logic and delegate a single consolidated payload to an atomic `Service` method.

---

## 3. Models (`models.py`)

1. Inherit from `BaseModel` ([`rrss_creatos_analyzer/apps/core/base_models/common.py`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/core/base_models/common.py)) so `created_at` (indexed) and `updated_at` are consistent across all domain models.
2. Enforce invariants at the database level via `UniqueConstraint` and `CheckConstraint` (e.g., non-negative counts/amounts).
3. Store currency values in `DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))`—never `FloatField`.
4. Use `models.GeneratedField` for deterministic derived columns (`hours_streamed`).
5. Attach `history = HistoricalRecords()` and `@auditlog.register()` to audited entities.

---

## 4. Selectors (`selectors.py`)

1. **Read-Only**: Never mutate state inside selectors.
2. **Permission Scoping**: Accept `user: User` and filter by `creator__user=user` unless `user.has_perm("<app>.view_all_<models>")` is `True`.
3. **N+1 Prevention**: Always apply `select_related(...)` and `prefetch_related(...)`.
4. **Caching**: Cache heavy analytical aggregations with `cache.get_or_set(key, callable, timeout=3600)`.

---

## 5. Services (`services.py`)

1. **Stateless `@classmethod` Classes**: Never instantiate `Service()`.
2. **HTTP-Agnostic**: Never pass `HttpRequest`, `HttpResponse`, `Form`, or `WizardView` to services.
3. **Short Atomic Transactions**: Decorate write methods with `@transaction.atomic`. Keep external HTTP calls and heavy file parsing outside open transactions.
4. **Explicit Cache Invalidation**: Schedule cache invalidation with `transaction.on_commit(...)`.
5. **Fail-Fast Guards**: Validate preconditions up front and raise `BusinessLogicError`.

---

## 6. Strict Django Signals Policy

> [!WARNING]
> **No Business Logic in Signals**: Do NOT use `post_save`, `pre_save`, `m2m_changed`, or `post_delete` to recalculate metrics, mutate related records, send emails, or enqueue background tasks.

**Allowed uses**:
- Internal hooks of audited libraries (`django-simple-history`, `django-auditlog`).
- Setting SQLite connection `PRAGMA`s on `connection_created`.

---

## 7. Views (`views.py`), Logging & TDD

- **Views**: Use Django CBVs + `LoginRequiredMixin` + `PermissionRequiredMixin`. Never call `Model.objects.create(...)` directly in views—delegate to `Service`.
- **Logging**: Use `logger = logging.getLogger(__name__)` with static `snake_case` event strings (no f-strings) and structured `extra={...}` dicts.
- **TDD (`pytest` + `factory-boy`)**:
  - Test role isolation (`Creator` cannot access other creators' records -> `403` or empty queryset).
  - Guard list views/selectors against `N+1` queries with `django_assert_max_num_queries`.
  - Test every `Service` method for happy path, `BusinessLogicError` guard clauses, and cache invalidation.
  - Test `SessionWizardView` step validation, back navigation (`wizard_goto_step`), and `done()` delegation.
