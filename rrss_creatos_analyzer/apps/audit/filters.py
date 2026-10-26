import django_filters

from .models import AuditEvent


class AuditEventFilter(django_filters.FilterSet):
    class Meta:
        model = AuditEvent
        fields = ["event_action", "target_model", "actor"]
