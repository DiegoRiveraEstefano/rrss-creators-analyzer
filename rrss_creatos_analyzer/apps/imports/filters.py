import django_filters

from .models import ImportBatch


class ImportBatchFilter(django_filters.FilterSet):
    filename = django_filters.CharFilter(lookup_expr="icontains", label="Archivo")

    class Meta:
        model = ImportBatch
        fields = ["filename", "batch_type", "source_platform", "status"]
