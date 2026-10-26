import django_filters

from .models import AnalyticsSnapshot


class AnalyticsSnapshotFilter(django_filters.FilterSet):
    class Meta:
        model = AnalyticsSnapshot
        fields = ["report_type", "period_label"]
