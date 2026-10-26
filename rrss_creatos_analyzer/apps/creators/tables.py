import django_tables2 as tables

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator


class CreatorTable(tables.Table):
    display_name = tables.Column(linkify=True, verbose_name="Creador")
    actions = tables.TemplateColumn(
        template_name="creators/includes/creator_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = Creator
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "display_name",
            "handle",
            "primary_platform",
            "tier",
            "status",
            "manager",
            "joined_company_at",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}


class ChannelTable(tables.Table):
    platform_channel_id = tables.Column(linkify=True, verbose_name="ID Canal")
    followers_count = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    subscribers_count = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    total_views_count = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    actions = tables.TemplateColumn(
        template_name="creators/includes/channel_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = Channel
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "creator",
            "platform",
            "platform_channel_id",
            "followers_count",
            "subscribers_count",
            "total_views_count",
            "is_live",
            "status",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}


class ChannelSnapshotTable(tables.Table):
    snapshot_date = tables.Column(linkify=True)
    followers_count = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    followers_delta = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    subscribers_count = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    total_views_count = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    actions = tables.TemplateColumn(
        template_name="creators/includes/snapshot_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = ChannelSnapshot
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "channel",
            "snapshot_date",
            "followers_count",
            "followers_delta",
            "subscribers_count",
            "total_views_count",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
