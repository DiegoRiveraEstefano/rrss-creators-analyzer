from decimal import Decimal

from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager

from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.core.models import SluggedModelMixin
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.videos.models import Video

from .choices import AssignmentStatus
from .choices import EditorAssignmentRole
from .choices import EditorSpecialty
from .choices import EditorStatus
from .choices import EditorType
from .choices import RateModel
from .choices import RevisionStatus
from .choices import TaskPriority
from .choices import TaskStatus
from .choices import TaskType


@auditlog.register()
class Editor(BaseModel, SluggedModelMixin):
    slug_source_field = "handle"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="editor_profile",
        verbose_name=_("Cuenta de Usuario"),
    )
    name = models.CharField(_("Nombre Completo / Estudio"), max_length=150)
    handle = models.CharField(
        _("Handle (@)"),
        max_length=100,
        unique=True,
        db_index=True,
    )
    slug = models.SlugField(_("Slug"), max_length=120, unique=True)
    email = models.EmailField(_("Correo Electrónico"), blank=True)
    phone = models.CharField(_("Teléfono / WhatsApp"), max_length=30, blank=True)
    discord_handle = models.CharField(
        _("Usuario de Discord"),
        max_length=60,
        blank=True,
    )
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=EditorStatus.choices,
        default=EditorStatus.ACTIVE,
        db_index=True,
    )
    editor_type = models.CharField(
        _("Modalidad"),
        max_length=20,
        choices=EditorType.choices,
        default=EditorType.FREELANCER,
    )
    primary_specialty = models.CharField(
        _("Especialidad Principal"),
        max_length=30,
        choices=EditorSpecialty.choices,
        default=EditorSpecialty.LONG_FORM,
    )
    software_stack = models.CharField(
        _("Software / Herramientas"),
        max_length=255,
        blank=True,
        default="Adobe Premiere Pro, After Effects",
    )
    rate_model = models.CharField(
        _("Modelo de Tarifa Base"),
        max_length=30,
        choices=RateModel.choices,
        default=RateModel.PER_VIDEO,
    )
    base_video_rate = models.DecimalField(
        _("Tarifa Base Video Largo ($)"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    base_short_rate = models.DecimalField(
        _("Tarifa Base Short/Reel ($)"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    hourly_rate = models.DecimalField(
        _("Tarifa por Hora ($)"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    monthly_retainer = models.DecimalField(
        _("Retainer Mensual ($)"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    max_active_tasks = models.PositiveIntegerField(
        _("Capacidad Máxima de Tareas Simultáneas"),
        default=3,
    )
    portfolio_url = models.URLField(_("URL del Portafolio"), max_length=500, blank=True)
    reel_url = models.URLField(_("URL del Showreel / Demo"), max_length=500, blank=True)
    notes = models.TextField(_("Notas Internas"), blank=True)

    tags = TaggableManager(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Editor")
        verbose_name_plural = _("Editores")
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(base_video_rate__gte=0)
                    & Q(base_short_rate__gte=0)
                    & Q(hourly_rate__gte=0)
                    & Q(monthly_retainer__gte=0)
                    & Q(max_active_tasks__gte=1)
                ),
                name="chk_editor_rates_and_capacity_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} (@{self.handle})"

    def get_absolute_url(self) -> str:
        return reverse("editors:editor_detail", kwargs={"slug": self.slug})


@auditlog.register()
class EditorAssignment(BaseModel):
    editor = models.ForeignKey(
        Editor,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name=_("Editor"),
    )
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="editor_assignments",
        verbose_name=_("Creador"),
    )
    role = models.CharField(
        _("Rol Asignado"),
        max_length=30,
        choices=EditorAssignmentRole.choices,
        default=EditorAssignmentRole.LEAD_EDITOR,
    )
    status = models.CharField(
        _("Estado de la Asignación"),
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.ACTIVE,
        db_index=True,
    )
    is_primary = models.BooleanField(_("Editor Principal para este Rol"), default=False)
    agreed_video_rate = models.DecimalField(
        _("Tarifa Acordada Video Largo ($)"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    agreed_short_rate = models.DecimalField(
        _("Tarifa Acordada Short/Reel ($)"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    start_date = models.DateField(_("Fecha de Inicio"))
    end_date = models.DateField(_("Fecha de Fin"), null=True, blank=True)
    notes = models.TextField(_("Condiciones / Notas de la Asignación"), blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Asignación de Editor a Creador")
        verbose_name_plural = _("Asignaciones de Editores a Creadores")
        ordering = ["creator", "-is_primary", "role"]
        constraints = [
            models.UniqueConstraint(
                fields=["editor", "creator", "role"],
                name="uq_editor_creator_role",
            ),
        ]

    def __str__(self) -> str:
        role_label = self.get_role_display()
        return f"{self.editor.name} -> {self.creator.display_name} ({role_label})"

    def get_absolute_url(self) -> str:
        return reverse("editors:assignment_detail", kwargs={"pk": self.pk})


@auditlog.register()
class EditingTask(BaseModel):
    title = models.CharField(_("Título de la Tarea / Proyecto"), max_length=255)
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="editing_tasks",
        verbose_name=_("Creador"),
    )
    editor = models.ForeignKey(
        Editor,
        on_delete=models.CASCADE,
        related_name="editing_tasks",
        verbose_name=_("Editor"),
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="editing_tasks",
        verbose_name=_("Video Asociado"),
    )
    status = models.CharField(
        _("Estado de la Tarea"),
        max_length=25,
        choices=TaskStatus.choices,
        default=TaskStatus.ASSIGNED,
        db_index=True,
    )
    priority = models.CharField(
        _("Prioridad"),
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
    )
    task_type = models.CharField(
        _("Tipo de Edición"),
        max_length=30,
        choices=TaskType.choices,
        default=TaskType.LONG_FORM_EDIT,
    )
    brief = models.TextField(_("Brief / Instrucciones de Edición"), blank=True)
    raw_footage_url = models.URLField(
        _("URL Material en Bruto (Drive/Dropbox/Frame.io)"),
        max_length=500,
        blank=True,
    )
    preview_render_url = models.URLField(
        _("URL Previsualización (Corte Actual)"),
        max_length=500,
        blank=True,
    )
    final_render_url = models.URLField(
        _("URL Render Final / Master"),
        max_length=500,
        blank=True,
    )
    assigned_date = models.DateField(_("Fecha de Asignación"))
    deadline = models.DateField(_("Fecha Límite (Deadline)"), db_index=True)
    delivered_at = models.DateTimeField(_("Entregado el"), null=True, blank=True)
    approved_at = models.DateTimeField(_("Aprobado el"), null=True, blank=True)
    revision_count = models.PositiveIntegerField(
        _("Número de Revisiones Solicitadas"),
        default=0,
    )
    agreed_cost = models.DecimalField(
        _("Costo Acordado de Edición ($)"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    is_paid = models.BooleanField(_("Liquidado / Pagado al Editor"), default=False)
    paid_at = models.DateTimeField(_("Fecha de Liquidación"), null=True, blank=True)
    estimated_duration_seconds = models.PositiveIntegerField(
        _("Duración Estimada (Segundos)"),
        default=0,
    )
    actual_duration_seconds = models.PositiveIntegerField(
        _("Duración Final (Segundos)"),
        default=0,
    )

    tags = TaggableManager(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Tarea de Edición")
        verbose_name_plural = _("Tareas de Edición")
        ordering = ["-deadline", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(agreed_cost__gte=0),
                name="chk_task_agreed_cost_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} - {self.editor.name} ({self.get_status_display()})"

    def get_absolute_url(self) -> str:
        return reverse("editors:task_detail", kwargs={"pk": self.pk})


@auditlog.register()
class TaskRevision(BaseModel):
    task = models.ForeignKey(
        EditingTask,
        on_delete=models.CASCADE,
        related_name="revisions",
        verbose_name=_("Tarea de Edición"),
    )
    revision_number = models.PositiveIntegerField(_("Número de Versión"))
    render_url = models.URLField(_("URL del Corte / Render"), max_length=500)
    change_summary = models.TextField(
        _("Resumen de Cambios del Editor"),
        blank=True,
    )
    feedback_notes = models.TextField(
        _("Feedback del Creador / Manager"),
        blank=True,
    )
    status = models.CharField(
        _("Estado de Revisión"),
        max_length=25,
        choices=RevisionStatus.choices,
        default=RevisionStatus.PENDING_REVIEW,
    )
    submitted_at = models.DateTimeField(_("Enviado a Revisión"))
    reviewed_at = models.DateTimeField(_("Revisado el"), null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Revisión de Tarea")
        verbose_name_plural = _("Revisiones de Tareas")
        ordering = ["task", "-revision_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["task", "revision_number"],
                name="uq_task_revision_number",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.task.title} - v{self.revision_number} ({self.get_status_display()})"
        )

    def get_absolute_url(self) -> str:
        return reverse("editors:revision_detail", kwargs={"pk": self.pk})
