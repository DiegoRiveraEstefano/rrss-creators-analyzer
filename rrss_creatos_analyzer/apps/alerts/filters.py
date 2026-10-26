import django_filters

from .models import ChannelAlert


class ChannelAlertFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains", label="Título")

    class Meta:
        model = ChannelAlert
        fields = [
            "creator",
            "channel",
            "alert_type",
            "severity",
            "status",
            "assigned_to",
        ]
