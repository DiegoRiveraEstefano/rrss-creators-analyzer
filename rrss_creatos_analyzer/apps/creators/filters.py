import django_filters
from django.utils.translation import gettext_lazy as _

from rrss_creatos_analyzer.apps.core.choices import PlatformType

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator


class CreatorFilter(django_filters.FilterSet):
    display_name = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Nombre"),
    )
    handle = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Handle (@)"),
    )
    main_category = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Categoría"),
    )
    platform = django_filters.ChoiceFilter(
        field_name="channels__platform",
        choices=PlatformType.choices,
        label=_("Plataforma Activa"),
        distinct=True,
    )
    has_live_channel = django_filters.BooleanFilter(
        field_name="channels__is_live",
        label=_("Transmitiendo En Vivo"),
        distinct=True,
    )

    class Meta:
        model = Creator
        fields = [
            "display_name",
            "handle",
            "platform",
            "tier",
            "status",
            "manager",
            "main_category",
            "has_live_channel",
        ]


class ChannelFilter(django_filters.FilterSet):
    handle = django_filters.CharFilter(lookup_expr="icontains", label=_("Handle"))
    channel_name = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Nombre del Canal"),
    )

    class Meta:
        model = Channel
        fields = [
            "creator",
            "platform",
            "status",
            "is_primary",
            "is_live",
            "is_monetized",
            "sync_enabled",
        ]


class ChannelSnapshotFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter(
        field_name="snapshot_date",
        lookup_expr="gte",
        label=_("Desde"),
    )
    date_before = django_filters.DateFilter(
        field_name="snapshot_date",
        lookup_expr="lte",
        label=_("Hasta"),
    )

    class Meta:
        model = ChannelSnapshot
        fields = ["channel", "date_after", "date_before"]
