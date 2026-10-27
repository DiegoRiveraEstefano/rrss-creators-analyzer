import django_filters

from .models import Contract


class ContractFilter(django_filters.FilterSet):
    contract_code = django_filters.CharFilter(lookup_expr="icontains", label="Código")

    class Meta:
        model = Contract
        fields = ["contract_code", "creator", "status", "auto_renew"]
