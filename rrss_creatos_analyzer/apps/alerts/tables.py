import django_tables2 as tables

from .models import ChannelAlert


class ChannelAlertTable(tables.Table):
    title = tables.Column(linkify=True)
    strike_points = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    actions = tables.TemplateColumn(
        template_name="alerts/includes/alert_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = ChannelAlert
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "occurred_at",
            "creator",
            "channel",
            "alert_type",
            "severity",
            "status",
            "title",
            "strike_points",
            "assigned_to",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
