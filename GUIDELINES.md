# Guías de Arquitectura e Ingeniería (GUIDELINES)

Este documento establece los lineamientos técnicos obligatorios para el desarrollo en **RRSS Creators Analyzer**. Estas reglas están adaptadas a partir de [`/.agents/rules/`](file:///home/diego/Proyectos/rrss-creators-analyzer/.agents/rules) para responder específicamente a la naturaleza **single-tenant (única compañía)** del proyecto, sus especificaciones de infraestructura (**PostgreSQL + Redis** en producción, con soporte continuo de **SQLite + DiskCache** en local/tests) y el uso intensivo del ecosistema de **Django 6.0**.

---

## 1. Principios Arquitectónicos y Monolito Modular

### 1.1 Reglas de Modularidad y Capas
1. **Límite de 400 líneas por archivo**: Ningún archivo `.py` debe superar las 400 líneas. Si un módulo crece más allá de este límite, debe dividirse en un paquete (`services/`, `selectors/`, `views/`, `tables/`, `wizards/`).
2. **Separación estricta de responsabilidades**:
   - `models.py`: Definición de campos, `TextChoices`, metadatos, índices, `CheckConstraint`, `UniqueConstraint` y `GeneratedField`. **Cero lógica de negocio o llamadas externas**.
   - `selectors.py`: Toda la lógica de lectura, filtrado por permisos de rol (`creator` vs `manager`/`analyst`), optimización `select_related`/`prefetch_related`, anotaciones (`annotate`) y consultas cacheadas (`cache.get_or_set`). **Cero mutaciones**.
   - `services.py`: Toda la lógica de escritura/mutación, validaciones de reglas de negocio, bloques `@transaction.atomic`, invalidación de caché (`cache`) y registro de eventos/auditoría.
   - `tables.py`: Definición declarativa de tablas con **`django-tables2`**.
   - `filters.py`: Definición declarativa de filtros de búsqueda con **`django-filter`**.
   - `forms.py` / `wizards.py`: Formularios de Django con layouts de **`django-crispy-forms`** (`crispy-bootstrap5`), selectores con `django-autocomplete-light` y pasos de asistentes para **`django-formtools`**.
   - `views.py` (o `views/wizards.py`): Controladores HTTP delgados (Class-Based Views y `SessionWizardView`). Desempaquetan la petición, llaman a un `Selector` o `Service`, e integran `SingleTableMixin` / `FilterView`.

### 1.2 Arquitectura Single-Tenant (Sin `tenant_id`)
- El sistema pertenece a **una única compañía**.
- **Prohibido** añadir campos `tenant_id` u `organization_id` en los modelos o exigir `tenant_id` como primer argumento en `Services` y `Selectors`.
- El aislamiento de datos dentro de la compañía se rige por el rol del usuario autenticado:
  - **`company_admin` y `manager`**: Acceso completo de lectura y escritura según capacidades.
  - **`analyst`**: Acceso completo de lectura y exportación a todas las métricas, sesiones, videos y alertas de la compañía.
  - **`creator`**: Acceso restringido únicamente a sus propios canales, sesiones de streaming, videos, publicaciones y alertas vinculadas a su perfil `Creator`.

---

## 2. Uso Prioritario de Librerías del Ecosistema Django

Es directriz obligatoria exprimir al máximo las capacidades nativas de Django y las librerías estándar instaladas en [`pyproject.toml`](file:///home/diego/Proyectos/rrss-creators-analyzer/pyproject.toml) antes de escribir código manual o JavaScript innecesario:

### 2.1 Tablas con `django-tables2`
- Todo listado de entidades (`Creators`, `StreamingSessions`, `Videos`, `VideoPublications`, `ChannelAlerts`, `ImportBatches`, rankings) **debe** implementarse utilizando `django_tables2.Table` y `SingleTableMixin` (o `MultiTableMixin` en dashboards).
- Configurar `template_name = "django_tables2/bootstrap5.html"` (o plantilla personalizada basada en Bootstrap 5).
- Aprovechar el ordenamiento nativo por columnas (`order_by`), paginación automática y `ExportMixin` (junto con `django-import-export`) para exportar tablas a CSV/XLSX.

```python
import django_tables2 as tables
from .models import StreamingSession


class StreamingSessionTable(tables.Table):
    session_title = tables.Column(linkify=True, verbose_name="Título de Sesión")
    creator = tables.Column(accessor="creator.display_name", verbose_name="Creador")
    hours_streamed = tables.Column(verbose_name="Horas")
    avg_ccv = tables.Column(verbose_name="CCV Promedio")
    total_earnings = tables.Column(verbose_name="Ingresos ($)")

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

### 2.2 Filtrado con `django-filter`
- Nunca construir cadenas manuales de `if request.GET.get(...): queryset = queryset.filter(...)` en las vistas.
- Utilizar siempre `django_filters.FilterSet` en `filters.py` combinado con `FilterView` o `SingleTableMixin`.

```python
import django_filters
from rrss_creatos_analyzer.core.choices import PlatformType
from .models import StreamingSession


class StreamingSessionFilter(django_filters.FilterSet):
    streamed_after = django_filters.DateFilter(
        field_name="streamed_at", lookup_expr="date__gte", label="Desde fecha"
    )
    streamed_before = django_filters.DateFilter(
        field_name="streamed_at", lookup_expr="date__lte", label="Hasta fecha"
    )
    platform = django_filters.ChoiceFilter(choices=PlatformType.choices)
    game_or_category = django_filters.CharFilter(
        lookup_expr="icontains", label="Categoría / Juego"
    )

    class Meta:
        model = StreamingSession
        fields = ["creator", "platform", "game_or_category"]
```

### 2.3 Formularios con `django-crispy-forms` y `django-widget-tweaks`
- **Estructura compleja y layouts**: Usar `FormHelper` y `Layout` (`Row`, `Column`, `Fieldset`, `Submit`, `InputGroup`) de `crispy_forms` con el paquete `crispy-bootstrap5`.
- **Ajustes rápidos en plantillas HTML**: Cuando se rendericen filtros compactos, barras de búsqueda o controles puntuales en un template, usar **`django-widget-tweaks`** (`{% load widget_tweaks %}` y `{% render_field form.field class+="form-control form-control-sm" placeholder="Buscar..." %}`).
- **Selectores relacionales grandes**: Para seleccionar `Creator`, `Channel`, `Video` o `tags` en formularios, emplear `django-autocomplete-light` (`dal.autocomplete`).

### 2.4 Formularios en Múltiples Pasos con `django-formtools` (`SessionWizardView`)
- **Casos de uso obligatorios**: Flujos guiados de creación y configuración secuencial donde presentar todos los campos en una sola página resulta abrumador o donde los pasos posteriores dependen de entidades/decisiones del paso previo:
  1. **Onboarding Integral de Creadores (`creators` / `contracts`)**: Paso 1 (Datos de identidad y perfil), Paso 2 (Canales en Twitch/YouTube/Kick/TikTok), Paso 3 (Contrato inicial, metas mensuales y reparto de ingresos).
  2. **Configuración de Campañas de Patrocinio (`campaigns`)**: Paso 1 (Detalles de marca y presupuesto), Paso 2 (Selección de creadores y canales convocados), Paso 3 (Asignación de entregables y fechas límite).
  3. **Cierre de Liquidaciones Financieras (`payouts`)**: Paso 1 (Selección de periodo y creadores), Paso 2 (Revisión de métricas de ingresos e imputación de costos), Paso 3 (Aprobación y liquidación contable).
  4. **Asistente de Ingesta Masiva Asistida (`imports`)**: Paso 1 (Carga de archivo CSV/XLSX), Paso 2 (Mapeo interactivo de columnas a campos del modelo), Paso 3 (Previsualización de filas válidas/inválidas y confirmación de commit).
- **Reglas de Implementación**:
  - Utilizar **`formtools.wizard.views.SessionWizardView`** para almacenar el estado intermedio de manera transparente y segura en la sesión del servidor (evitar diccionarios temporales ad-hoc en sesión o cookies del lado del cliente).
  - Cada paso debe tener su clase de formulario dedicada en `forms.py` (o `wizards.py`) con sus respectivas validaciones aisladas (`clean()`) y layout con `crispy-bootstrap5`.
  - En la plantilla HTML: incluir obligatoriamente `{{ wizard.management_form }}`, una barra de progreso semántica (`<nav aria-label="Progreso del asistente">` con `.progress`), el formulario actual renderizado vía `{% crispy wizard.form %}` y controles de navegación hacia atrás con `<button name="wizard_goto_step" type="submit" value="{{ wizard.steps.prev }}">`.
  - **Zero lógica de negocio en la vista**: En el método `done(self, form_list, **kwargs)`, la vista únicamente extrae los `cleaned_data` consolidados de cada paso mediante `self.get_cleaned_data_for_step(step_name)` y delega la ejecución de la transacción completa a un único método de la capa `Service` (`@transaction.atomic`).

```python
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView

from .forms import (
    CreatorProfileStepForm,
    CreatorChannelsStepForm,
    CreatorContractStepForm,
)
from .services import CreatorOnboardingService

FORMS = [
    ("profile", CreatorProfileStepForm),
    ("channels", CreatorChannelsStepForm),
    ("contract", CreatorContractStepForm),
]


class CreatorOnboardingWizardView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SessionWizardView,
):
    form_list = FORMS
    permission_required = "creators.add_creator"
    template_name = "creators/wizards/onboarding_wizard.html"

    def done(self, form_list, **kwargs) -> HttpResponse:
        profile_data = self.get_cleaned_data_for_step("profile") or {}
        channels_data = self.get_cleaned_data_for_step("channels") or {}
        contract_data = self.get_cleaned_data_for_step("contract") or {}

        creator = CreatorOnboardingService.onboard_creator(
            user=self.request.user,
            profile_payload=profile_data,
            channels_payload=channels_data.get("channels", []),
            contract_payload=contract_data,
        )

        messages.success(
            self.request,
            f"Creador '{creator.display_name}' incorporado exitosamente.",
        )
        return redirect(reverse_lazy("creators:detail", kwargs={"pk": creator.pk}))
```

---

## 3. Reglas de la Capa de Modelos (`models.py`)

1. **Herencia de Modelos Base**:
   - Todo modelo de dominio debe heredar de `BaseModel` (ubicado en `rrss_creatos_analyzer/core/models.py`), que provee `created_at`, `updated_at` (o `TimeStampedModel` de `django-model-utils`) e identificadores consistentes.
2. **Integridad en Base de Datos (`Constraints`)**:
   - Preferir siempre restricciones a nivel de base de datos (`models.UniqueConstraint`, `models.CheckConstraint`) sobre validaciones puramente en Python.
   - Ejemplo obligatorio en `StreamingSession` y `VideoPublication`: `CheckConstraint` asegurando que conteos (`views_count`, `avg_ccv`, `duration_seconds`) e ingresos sean `>= 0`.
3. **Campos Monetarios y Calculados**:
   - Todos los montos financieros (`ad_revenue`, `subs_revenue`, `donations_revenue`, `total_earnings`, `production_cost`, `estimated_revenue`) deben usar `DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))`. Nunca usar `FloatField` para dinero.
   - Usar `models.GeneratedField` (disponible en Django 5.0+/6.0 y soportado en SQLite 3.31+ y PostgreSQL) para columnas calculadas deterministas como `hours_streamed`.
4. **Auditoría Histórica**:
   - Registrar `history = HistoricalRecords()` de `django-simple-history` en los modelos críticos: `Creator`, `Channel`, `Video`, `VideoPublication` y `ChannelAlert`.

---

## 4. Reglas de la Capa de Selectores (`selectors.py`)

1. **Pureza de Solo Lectura**:
   - Los selectores jamás modifican estados ni escriben en la base de datos.
2. **Control de Visibilidad por Usuario**:
   - Los selectores que listan o recuperan objetos del dominio reciben `user: User` cuando la consulta depende del rol:
     - Si `user.role == UserRole.CREATOR`: filtrar por `creator__user=user`.
     - Si `user.role in (UserRole.COMPANY_ADMIN, UserRole.MANAGER, UserRole.ANALYST)`: retornar el conjunto completo de la compañía.
3. **Prevención de Consultas N+1**:
   - Uso obligatorio de `select_related("creator", "channel")` en sesiones, publicaciones y alertas, y `prefetch_related("tags", "publications")` en videos y creadores.
4. **Integración con Caché (`Redis` / `DiskCache`)**:
   - Los selectores analíticos pesados (rankings, resúmenes mensuales, métricas por plataforma que reemplazan a las antiguas vistas materializadas) deben usar `cache.get_or_set(key, callable, timeout=3600)`.

```python
from django.core.cache import cache
from django.db.models import Avg, Count, F, Max, QuerySet, Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from rrss_creatos_analyzer.creators.models import Creator


class CreatorAnalyticsSelector:
    CACHE_KEY_PERF_SUMMARY = "analytics:creator_performance_summary:v1"

    @classmethod
    def get_performance_summary(cls) -> list[dict]:
        def _compute() -> list[dict]:
            qs = Creator.objects.annotate(
                total_streams=Count("streaming_sessions", distinct=True),
                total_stream_seconds=Coalesce(
                    Sum("streaming_sessions__duration_seconds"), 0
                ),
                overall_avg_ccv=Coalesce(Avg("streaming_sessions__avg_ccv"), 0.0),
                max_peak_viewers=Coalesce(Max("streaming_sessions__peak_viewers"), 0),
                total_stream_earnings=Coalesce(
                    Sum("streaming_sessions__total_earnings"),
                    Value(
                        0, output_field=DecimalField(max_digits=12, decimal_places=2)
                    ),
                ),
                total_videos=Count("videos", distinct=True),
                total_publications=Count("video_publications", distinct=True),
                total_video_views=Coalesce(Sum("video_publications__views_count"), 0),
                total_video_earnings=Coalesce(
                    Sum("video_publications__estimated_revenue"),
                    Value(
                        0, output_field=DecimalField(max_digits=12, decimal_places=2)
                    ),
                ),
            ).annotate(
                total_combined_revenue=F("total_stream_earnings")
                + F("total_video_earnings")
            )
            return list(
                qs.values(
                    "id",
                    "display_name",
                    "handle",
                    "primary_platform",
                    "status",
                    "total_streams",
                    "overall_avg_ccv",
                    "max_peak_viewers",
                    "total_stream_earnings",
                    "total_videos",
                    "total_publications",
                    "total_video_views",
                    "total_video_earnings",
                    "total_combined_revenue",
                )
            )

        return cache.get_or_set(cls.CACHE_KEY_PERF_SUMMARY, _compute, timeout=3600)
```

---

## 5. Reglas de la Capa de Servicios (`services.py`)

1. **Clases Stateless con `@classmethod`**:
   - Todos los servicios se implementan como clases sin estado con métodos `@classmethod`. No instanciar servicios (`Service()`).
2. **Desacoplamiento de HTTP**:
   - Un servicio **nunca** recibe `HttpRequest`, `HttpResponse`, instancias de `Form` ni `WizardView`. Recibe tipos primitivos (`int`, `str`, `Decimal`, `datetime`), dataclasses o instancias de modelos.
3. **Atomicidad y Compatibilidad de Base de Datos (PostgreSQL / SQLite)**:
   - Decorar todos los métodos de escritura con `@transaction.atomic`.
   - En PostgreSQL y SQLite, mantener las transacciones lo más limpias y rápidas posible (no hacer peticiones HTTP externas ni procesamientos pesados de archivos dentro del bloque `transaction.atomic` antes de persistir).
   - Registrar la invalidación de caché usando `transaction.on_commit(AnalyticsCacheService.invalidate_all)`.
4. **Cláusulas de Guarda (Fail-Fast)**:
   - Validar todas las precondiciones al inicio del método y lanzar `BusinessLogicError` (o `ValidationError` de dominio) si no se cumplen.

```python
import logging
from decimal import Decimal
from django.db import transaction
from rrss_creatos_analyzer.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.analytics.services import AnalyticsCacheService
from .models import StreamingSession

logger = logging.getLogger(__name__)


class StreamingSessionService:
    @classmethod
    @transaction.atomic
    def record_session(
        cls,
        *,
        creator_id: int,
        channel_id: int | None,
        session_title: str,
        game_or_category: str,
        platform: str,
        streamed_at,
        duration_seconds: int,
        peak_viewers: int = 0,
        avg_ccv: int = 0,
        ad_revenue: Decimal = Decimal("0.00"),
        subs_revenue: Decimal = Decimal("0.00"),
        donations_revenue: Decimal = Decimal("0.00"),
    ) -> StreamingSession:
        if duration_seconds < 0:
            raise BusinessLogicError("La duración de la sesión no puede ser negativa.")

        total_earnings = ad_revenue + subs_revenue + donations_revenue
        hours = (
            Decimal(duration_seconds) / Decimal(3600)
            if duration_seconds > 0
            else Decimal(0)
        )
        earnings_per_hour = (
            (total_earnings / hours).quantize(Decimal("0.01"))
            if hours > 0
            else Decimal("0.00")
        )

        session = StreamingSession.objects.create(
            creator_id=creator_id,
            channel_id=channel_id,
            session_title=session_title,
            game_or_category=game_or_category,
            platform=platform,
            streamed_at=streamed_at,
            duration_seconds=duration_seconds,
            peak_viewers=peak_viewers,
            avg_ccv=avg_ccv,
            ad_revenue=ad_revenue,
            subs_revenue=subs_revenue,
            donations_revenue=donations_revenue,
            total_earnings=total_earnings,
            earnings_per_hour=earnings_per_hour,
        )

        transaction.on_commit(AnalyticsCacheService.invalidate_creator_metrics)
        logger.info(
            "streaming_session_recorded",
            extra={
                "session_id": session.id,
                "creator_id": creator_id,
                "platform": platform,
            },
        )
        return session
```

---

## 6. Política Estricta sobre Signals de Django

> [!WARNING]
> **Prohibición de Signals para Lógica de Negocio**:
> Está **estrictamente prohibido** usar `post_save`, `pre_save`, `m2m_changed` o `post_delete` para:
> - Calcular o mutar modelos relacionados (ej. recalcular ingresos del creador en un signal).
> - Enviar correos electrónicos o notificaciones externas.
> - Disparar tareas asíncronas sin control transaccional.

**Usos permitidos**:
- Hooks internos de librerías auditadas como `django-simple-history`.
- Configuración de `PRAGMA` en la señal `connection_created` cuando el motor sea SQLite.
- Toda invalidación de caché o efecto secundario de negocio debe invocarse **explícitamente** dentro del método del `Service` mediante `transaction.on_commit(...)`.

---

## 7. Reglas de Vistas (`views.py`)

- Utilizar **Class-Based Views (CBVs)** nativas de Django (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`, `TemplateView`) y **`SessionWizardView`** para flujos secuenciales multi-paso, combinadas con `LoginRequiredMixin`, mixins de permisos por rol (`PermissionRequiredMixin` / `RoleRequiredMixin`), `SingleTableMixin` (`django-tables2`) y `FilterView` (`django-filter`).
- Ninguna vista debe realizar llamadas `Model.objects.create(...)` o `form.save()` con lógica de negocio; en `form_valid()` o en el método `done()` del wizard se debe delegar siempre al método correspondiente de la capa `Service`.

---

## 8. Estándares de Logging y Observabilidad

1. **Solo `logging` estándar de Python**:
   - Usar `import logging; logger = logging.getLogger(__name__)`.
   - No introducir librerías externas de logging no estándar.
2. **Identificadores de evento estáticos (`snake_case`)**:
   - El mensaje principal del log debe ser una cadena estática descriptiva (ej. `"creator_created"`, `"import_batch_failed"`, `"alert_resolved"`).
   - Prohibido interpolar variables con f-strings en el mensaje principal.
3. **Metadatos estructurados en `extra`**:
   - Pasar siempre los identificadores de contexto en el diccionario `extra`:
     ```python
     logger.info(
         "channel_alert_resolved",
         extra={"alert_id": alert.id, "creator_id": alert.creator_id, "user_id": user.id},
     )
     ```

---

## 9. Desarrollo Guiado por Pruebas (TDD)

1. **Ejecución con `pytest` y `pytest-django`**:
   - Configuración de pruebas en `config.settings.test`.
2. **Fixtures con `factory-boy`**:
   - Crear fábricas deterministas (`CreatorFactory`, `ChannelFactory`, `StreamingSessionFactory`, `VideoFactory`, `VideoPublicationFactory`, `ChannelAlertFactory`) en `tests/factories.py` de cada app.
3. **Pruebas de Permisos por Rol**:
   - Verificar siempre que un usuario con rol `creator` no pueda acceder ni filtrar registros de otro creador (`403 Forbidden` o queryset filtrado vacío), mientras que un `manager` o `analyst` sí visualiza todos los creadores de la compañía.
4. **Prevención de N+1 en Tests**:
   - Utilizar `django_assert_max_num_queries` en las pruebas de selectores y vistas con `django-tables2`.
5. **Cobertura de Servicios**:
   - Cada método de `Service` debe contar con tests para:
     1. Caso exitoso (*happy path*) y persistencia correcta.
     2. Violación de cláusulas de guarda (`pytest.raises(BusinessLogicError)`).
     3. Invalidación o actualización efectiva de las claves en caché (`cache`).
6. **Pruebas de Asistentes en Múltiples Pasos (`django-formtools`)**:
   - Testear individualmente la validación de cada formulario de paso (`test_forms.py`).
   - Testear la navegación del wizard con el cliente de pruebas de Django: simulación de envío de pasos con `management_form` (`<wizard_name>-current_step`), navegación hacia atrás (`wizard_goto_step`), persistencia de sesión entre pasos y verificación de que el método `done()` delega los datos al `Service` esperado.
