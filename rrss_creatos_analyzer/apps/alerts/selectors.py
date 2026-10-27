from typing import TYPE_CHECKING

from .models import ChannelAlert

if TYPE_CHECKING:
    from django.db.models import QuerySet


class ChannelAlertSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[ChannelAlert]:
        qs = ChannelAlert.objects.select_related(
            "creator",
            "channel",
            "related_session",
            "related_publication",
            "assigned_to",
            "resolved_by",
        )
        if user.is_superuser or user.has_perm("alerts.view_all_alerts"):
            return qs
        return qs.filter(creator__user=user)
