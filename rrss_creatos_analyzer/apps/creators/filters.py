import django_filters

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator


class CreatorFilter(django_filters.FilterSet):
    display_name = django_filters.CharFilter(lookup_expr="icontains", label="Nombre")
    handle = django_filters.CharFilter(lookup_expr="icontains", label="Handle")

    class Meta:
        model = Creator
        fields = [
            "display_name",
            "handle",
            "primary_platform",
            "tier",
            "status",
            "manager",
        ]


class ChannelFilter(django_filters.FilterSet):
    handle = django_filters.CharFilter(lookup_expr="icontains", label="Handle")

    class Meta:
        model = Channel
        fields = ["creator", "platform", "status", "is_live", "is_monetized"]


class ChannelSnapshotFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter(
        field_name="snapshot_date",
        lookup_expr="gte",
        label="Desde",
    )
    date_before = django_filters.DateFilter(
        field_name="snapshot_date",
        lookup_expr="lte",
        label="Hasta",
    )

    class Meta:
        model = ChannelSnapshot
        fields = ["channel", "date_after", "date_before"]
