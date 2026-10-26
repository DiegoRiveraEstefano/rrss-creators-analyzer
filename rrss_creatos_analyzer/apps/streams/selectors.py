from typing import TYPE_CHECKING

from .models import SessionSegment
from .models import StreamingSession

if TYPE_CHECKING:
    from django.db.models import QuerySet


class StreamingSessionSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[StreamingSession]:
        qs = StreamingSession.objects.select_related(
            "creator",
            "channel",
            "import_batch",
        ).prefetch_related("tags")
        if user.is_superuser or user.has_perm("streams.view_all_sessions"):
            return qs
        return qs.filter(creator__user=user)


class SessionSegmentSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[SessionSegment]:
        qs = SessionSegment.objects.select_related("session", "session__creator")
        if user.is_superuser or user.has_perm("streams.view_all_sessions"):
            return qs
        return qs.filter(session__creator__user=user)
