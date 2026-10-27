from typing import TYPE_CHECKING

from .models import Video
from .models import VideoPublication
from .models import VideoRelation

if TYPE_CHECKING:
    from django.db.models import QuerySet


class VideoSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[Video]:
        qs = Video.objects.select_related(
            "creator",
            "assigned_editor",
        ).prefetch_related("tags", "publications")
        if user.is_superuser or user.has_perm("videos.view_all_videos"):
            return qs
        return qs.filter(creator__user=user)


class VideoPublicationSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[VideoPublication]:
        qs = VideoPublication.objects.select_related(
            "video",
            "creator",
            "channel",
            "import_batch",
        )
        if user.is_superuser or user.has_perm("videos.view_all_videos"):
            return qs
        return qs.filter(creator__user=user)


class VideoRelationSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[VideoRelation]:
        qs = VideoRelation.objects.select_related(
            "source_video",
            "target_video",
            "target_session",
        )
        if user.is_superuser or user.has_perm("videos.view_all_videos"):
            return qs
        return qs.filter(source_video__creator__user=user)
