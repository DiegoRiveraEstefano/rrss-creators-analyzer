import django_filters

from .models import RoleGroupProfile


class RoleGroupProfileFilter(django_filters.FilterSet):
    group__name = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Nombre de Grupo",
    )

    class Meta:
        model = RoleGroupProfile
        fields = ["group__name", "is_system_role"]
