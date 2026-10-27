import django_filters

from .models import CompanySettings


class CompanySettingsFilter(django_filters.FilterSet):
    company_name = django_filters.CharFilter(lookup_expr="icontains", label="Compañía")
    default_currency = django_filters.CharFilter(lookup_expr="iexact", label="Moneda")

    class Meta:
        model = CompanySettings
        fields = ["company_name", "default_currency"]
