from typing import TYPE_CHECKING

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator

if TYPE_CHECKING:
    from django.db.models import QuerySet


class CreatorSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[Creator]:
        qs = Creator.objects.select_related("user", "manager").prefetch_related(
            "tags",
            "channels",
        )
        if user.is_superuser or user.has_perm("creators.view_all_creators"):
            return qs
        return qs.filter(user=user)


class ChannelSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[Channel]:
        qs = Channel.objects.select_related("creator")
        if user.is_superuser or user.has_perm("creators.view_all_creators"):
            return qs
        return qs.filter(creator__user=user)


class ChannelSnapshotSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[ChannelSnapshot]:
        qs = ChannelSnapshot.objects.select_related("channel", "channel__creator")
        if user.is_superuser or user.has_perm("creators.view_all_creators"):
            return qs
        return qs.filter(channel__creator__user=user)
