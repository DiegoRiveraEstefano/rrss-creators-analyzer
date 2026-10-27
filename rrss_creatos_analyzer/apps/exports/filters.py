import django_filters

from .models import ExportJob


class ExportJobFilter(django_filters.FilterSet):
    class Meta:
        model = ExportJob
        fields = ["report_type", "export_format", "status"]
