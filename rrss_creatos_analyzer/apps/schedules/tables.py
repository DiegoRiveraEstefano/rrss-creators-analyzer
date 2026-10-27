import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleComplianceSummary
from rrss_creatos_analyzer.apps.schedules.models import CreatorSchedulePattern
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException


class CreatorSchedulePatternTable(tables.Table):
    creator = tables.Column(
        accessor="creator__display_name",
        verbose_name=_("Creador"),
        linkify=lambda record: record.get_absolute_url(),
    )
    recurrence = tables.Column(
        empty_values=(),
        verbose_name=_("Recurrencia"),
    )
    time_window = tables.Column(empty_values=(), verbose_name=_("Horario Estipulado"))
    is_active = tables.Column(verbose_name=_("Estado"))
    actions = tables.TemplateColumn(
        template_name="schedules/includes/weekly_actions.html",
        orderable=False,
        verbose_name=_("Acciones"),
    )

    class Meta:
        model = CreatorSchedulePattern
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "creator",
            "recurrence",
            "time_window",
            "platform",
            "planned_duration_minutes",
            "category_or_game",
            "effective_from",
            "is_active",
            "actions",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}

    def render_recurrence(self, record) -> str:
        label = record.title or record.human_recurrence
        badge_tpl = (
            '<span class="badge bg-light text-dark font-monospace border ms-1" '
            'title="{}">RRULE</span>'
        )
        return format_html(f"{{}} {badge_tpl}", label, record.rrule)

    def render_time_window(self, record) -> str:
        s = record.start_time.strftime("%H:%M")
        e = record.end_time.strftime("%H:%M")
        return f"{s} - {e}"

    def render_is_active(self, value: bool) -> str:  # noqa: FBT001
        if value:
            return format_html(
                '<span class="badge bg-{}">{}</span>',
                "success",
                "Activo",
            )
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            "secondary",
            "Inactivo",
        )


# Alias para retrocompatibilidad
CreatorWeeklyScheduleTable = CreatorSchedulePatternTable


class CreatorScheduleSlotTable(tables.Table):
    creator = tables.Column(
        accessor="creator__display_name",
        verbose_name=_("Creador"),
        linkify=lambda record: record.get_absolute_url(),
    )
    scheduled_date = tables.DateColumn(
        format="Y-m-d",
        verbose_name=_("Fecha Programada"),
    )
    scheduled_time = tables.Column(empty_values=(), verbose_name=_("Horario Pactado"))
    status = tables.Column(verbose_name=_("Estado"))
    hours_comparison = tables.Column(
        empty_values=(),
        verbose_name=_("Horas (Real / Pactadas)"),
    )
    compliance_rate_pct = tables.Column(verbose_name=_("Cumplimiento"))
    actions = tables.TemplateColumn(
        template_name="schedules/includes/slot_actions.html",
        orderable=False,
        verbose_name=_("Acciones"),
    )

    class Meta:
        model = CreatorScheduleSlot
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "scheduled_date",
            "creator",
            "title",
            "scheduled_time",
            "hours_comparison",
            "compliance_rate_pct",
            "status",
            "actions",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}

    def render_scheduled_time(self, record) -> str:
        s = record.scheduled_start_time.strftime("%H:%M")
        e = record.scheduled_end_time.strftime("%H:%M")
        return f"{s} - {e}"

    def render_hours_comparison(self, record) -> str:
        return f"{record.actual_hours}h / {record.planned_hours}h"

    def render_status(self, value: str) -> str:
        colors = {
            ScheduleSlotStatus.SCHEDULED: "secondary",
            ScheduleSlotStatus.COMPLETED: "success",
            ScheduleSlotStatus.LATE: "warning text-dark",
            ScheduleSlotStatus.PARTIAL: "info text-dark",
            ScheduleSlotStatus.MISSED: "danger",
            ScheduleSlotStatus.JUSTIFIED_ABSENCE: "primary",
            ScheduleSlotStatus.CANCELLED: "dark",
        }
        color = colors.get(value, "secondary")
        slot_obj = CreatorScheduleSlot(status=value)
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            slot_obj.get_status_display(),
        )

    def render_compliance_rate_pct(self, value) -> str:
        if value >= 90:  # noqa: PLR2004
            badge_class = "success"
        elif value >= 50:  # noqa: PLR2004
            badge_class = "warning text-dark"
        else:
            badge_class = "danger"
        return format_html('<span class="badge bg-{}">{}%</span>', badge_class, value)


class ScheduleExceptionTable(tables.Table):
    creator = tables.Column(
        accessor="creator__display_name",
        verbose_name=_("Creador"),
        linkify=lambda record: record.get_absolute_url(),
    )
    date_range = tables.Column(empty_values=(), verbose_name=_("Período"))
    is_approved = tables.Column(verbose_name=_("Estado de Aprobación"))
    actions = tables.TemplateColumn(
        template_name="schedules/includes/exception_actions.html",
        orderable=False,
        verbose_name=_("Acciones"),
    )

    class Meta:
        model = ScheduleException
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "creator",
            "title",
            "reason_type",
            "date_range",
            "is_approved",
            "approved_by",
            "actions",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}

    def render_date_range(self, record) -> str:
        return f"{record.start_date} al {record.end_date}"

    def render_is_approved(self, value: bool) -> str:  # noqa: FBT001
        if value:
            return format_html(
                '<span class="badge bg-{}">{}</span>',
                "success",
                "Aprobada",
            )
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            "warning text-dark",
            "Pendiente",
        )


class CreatorScheduleComplianceSummaryTable(tables.Table):
    creator = tables.Column(
        accessor="creator__display_name",
        verbose_name=_("Creador"),
        linkify=lambda record: record.get_absolute_url(),
    )
    period = tables.Column(empty_values=(), verbose_name=_("Período"))
    days_ratio = tables.Column(
        empty_values=(),
        verbose_name=_("Días Cumplidos / Estipulados"),
    )
    hours_ratio = tables.Column(
        empty_values=(),
        verbose_name=_("Horas Efectivas / Estipuladas"),
    )
    punctuality_rate_pct = tables.Column(verbose_name=_("Puntualidad"))
    is_compliant = tables.Column(verbose_name=_("Cumplimiento Contractual"))
    actions = tables.TemplateColumn(
        template_name="schedules/includes/compliance_actions.html",
        orderable=False,
        verbose_name=_("Acciones"),
    )

    class Meta:
        model = CreatorScheduleComplianceSummary
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "period",
            "creator",
            "days_ratio",
            "hours_ratio",
            "punctuality_rate_pct",
            "is_compliant",
            "actions",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}

    def render_period(self, record) -> str:
        return f"{record.month:02d}/{record.year}"

    def render_days_ratio(self, record) -> str:
        done = record.completed_days_count + record.late_days_count
        pct = record.days_compliance_rate_pct
        return f"{done} / {record.stipulated_days_count} ({pct}%)"

    def render_hours_ratio(self, record) -> str:
        return f"{record.actual_hours}h / {record.stipulated_hours}h"

    def render_punctuality_rate_pct(self, value) -> str:
        return format_html('<span class="badge bg-info text-dark">{}%</span>', value)

    def render_is_compliant(self, value: bool) -> str:  # noqa: FBT001
        if value:
            return format_html(
                '<span class="badge bg-{}">{}</span>',
                "success",
                "Cumplido",
            )
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            "danger",
            "Incumplido",
        )
