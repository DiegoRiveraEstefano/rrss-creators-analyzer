import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator


class CreatorTable(tables.Table):
    display_name = tables.TemplateColumn(
        template_name="creators/includes/creator_column_name.html",
        verbose_name=_("Talento / Creador"),
    )
    platforms = tables.TemplateColumn(
        template_name="creators/includes/creator_column_platforms.html",
        verbose_name=_("Plataformas"),
        orderable=False,
    )
    tier = tables.TemplateColumn(
        template_name="creators/includes/creator_column_tier.html",
        verbose_name=_("Tier"),
    )
    status = tables.TemplateColumn(
        template_name="creators/includes/creator_column_status.html",
        verbose_name=_("Estado"),
    )
    total_followers = tables.Column(
        accessor="total_followers_count",
        verbose_name=_("Audiencia Total"),
        attrs={"td": {"class": "text-end font-monospace fw-semibold"}},
    )
    actions = tables.TemplateColumn(
        template_name="creators/includes/creator_actions.html",
        verbose_name=_("Acciones"),
        orderable=False,
    )

    class Meta:
        model = Creator
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "display_name",
            "platforms",
            "tier",
            "status",
            "manager",
            "total_followers",
            "joined_company_at",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}


class ChannelTable(tables.Table):
    platform_channel_id = tables.Column(linkify=True, verbose_name=_("ID Canal"))
    platform = tables.TemplateColumn(
        template_name="creators/includes/channel_column_platform.html",
        verbose_name=_("Plataforma"),
    )
    followers_count = tables.Column(
        verbose_name=_("Seguidores"),
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    subscribers_count = tables.Column(
        verbose_name=_("Suscriptores"),
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    total_views_count = tables.Column(
        verbose_name=_("Vistas"),
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    is_live = tables.TemplateColumn(
        template_code=(
            "{% if record.is_live %}"
            '<span class="badge text-bg-danger animate-pulse">'
            '<i class="bi bi-broadcast me-1"></i>EN VIVO</span>'
            "{% else %}"
            '<span class="badge text-bg-light text-muted border">Offline</span>'
            "{% endif %}"
        ),
        verbose_name=_("Transmisión"),
    )
    actions = tables.TemplateColumn(
        template_name="creators/includes/channel_actions.html",
        verbose_name=_("Acciones"),
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
    snapshot_date = tables.Column(linkify=True, verbose_name=_("Fecha"))
    followers_count = tables.Column(
        verbose_name=_("Seguidores"),
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    followers_delta = tables.TemplateColumn(
        template_code=(
            "{% if record.followers_delta > 0 %}"
            '<span class="text-success fw-bold font-monospace">+{{ record.followers_delta }}</span>'
            "{% elif record.followers_delta < 0 %}"
            '<span class="text-danger fw-bold font-monospace">{{ record.followers_delta }}</span>'
            "{% else %}"
            '<span class="text-muted font-monospace">0</span>'
            "{% endif %}"
        ),
        verbose_name=_("Δ Seguidores"),
        attrs={"td": {"class": "text-end"}},
    )
    subscribers_count = tables.Column(
        verbose_name=_("Suscriptores"),
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    total_views_count = tables.Column(
        verbose_name=_("Total Vistas"),
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    views_delta = tables.TemplateColumn(
        template_code=(
            "{% if record.views_delta > 0 %}"
            '<span class="text-success font-monospace">+{{ record.views_delta }}</span>'
            "{% elif record.views_delta < 0 %}"
            '<span class="text-danger font-monospace">{{ record.views_delta }}</span>'
            "{% else %}"
            '<span class="text-muted font-monospace">0</span>'
            "{% endif %}"
        ),
        verbose_name=_("Δ Vistas"),
        attrs={"td": {"class": "text-end"}},
    )
    actions = tables.TemplateColumn(
        template_name="creators/includes/snapshot_actions.html",
        verbose_name=_("Acciones"),
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
            "views_delta",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
