import django_filters

from .models import CreatorPayout


class CreatorPayoutFilter(django_filters.FilterSet):
    class Meta:
        model = CreatorPayout
        fields = ["creator", "period_year", "period_month", "status"]
