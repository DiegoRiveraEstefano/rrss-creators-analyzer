import django_filters
from django.utils.translation import gettext_lazy as _

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleExceptionReason
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleComplianceSummary
from rrss_creatos_analyzer.apps.schedules.models import CreatorSchedulePattern
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException


class CreatorSchedulePatternFilter(django_filters.FilterSet):
    platform = django_filters.ChoiceFilter(
        choices=PlatformType.choices,
        label=_("Plataforma"),
    )
    is_active = django_filters.BooleanFilter(label=_("Solo Activos"))
    is_mandatory = django_filters.BooleanFilter(label=_("Cómputo Obligatorio"))

    class Meta:
        model = CreatorSchedulePattern
        fields = ["creator", "platform", "is_active", "is_mandatory"]


# Alias para retrocompatibilidad
CreatorWeeklyScheduleFilter = CreatorSchedulePatternFilter


class CreatorScheduleSlotFilter(django_filters.FilterSet):
    scheduled_after = django_filters.DateFilter(
        field_name="scheduled_date",
        lookup_expr="gte",
        label=_("Desde Fecha"),
    )
    scheduled_before = django_filters.DateFilter(
        field_name="scheduled_date",
        lookup_expr="lte",
        label=_("Hasta Fecha"),
    )
    status = django_filters.ChoiceFilter(
        choices=ScheduleSlotStatus.choices,
        label=_("Estado de Cumplimiento"),
    )

    class Meta:
        model = CreatorScheduleSlot
        fields = ["creator", "status", "scheduled_after", "scheduled_before"]


class ScheduleExceptionFilter(django_filters.FilterSet):
    reason_type = django_filters.ChoiceFilter(
        choices=ScheduleExceptionReason.choices,
        label=_("Tipo de Excepción"),
    )
    is_approved = django_filters.BooleanFilter(label=_("Aprobadas"))

    class Meta:
        model = ScheduleException
        fields = ["creator", "reason_type", "is_approved"]


class CreatorScheduleComplianceSummaryFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(label=_("Año"))
    month = django_filters.NumberFilter(label=_("Mes"))
    is_compliant = django_filters.BooleanFilter(
        label=_("Solo Períodos Cumplidos"),
    )

    class Meta:
        model = CreatorScheduleComplianceSummary
        fields = ["creator", "year", "month", "is_compliant"]
