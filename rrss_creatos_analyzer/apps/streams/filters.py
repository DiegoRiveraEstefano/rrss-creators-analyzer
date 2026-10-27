import django_filters

from .models import SessionSegment
from .models import StreamingSession


class StreamingSessionFilter(django_filters.FilterSet):
    session_title = django_filters.CharFilter(lookup_expr="icontains", label="Título")
    game_or_category = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Categoría/Juego",
    )
    streamed_after = django_filters.DateFilter(
        field_name="streamed_at",
        lookup_expr="date__gte",
        label="Desde",
    )
    streamed_before = django_filters.DateFilter(
        field_name="streamed_at",
        lookup_expr="date__lte",
        label="Hasta",
    )

    class Meta:
        model = StreamingSession
        fields = [
            "creator",
            "platform",
            "game_or_category",
            "is_sponsored",
            "streamed_after",
            "streamed_before",
        ]


class SessionSegmentFilter(django_filters.FilterSet):
    game_or_category = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Categoría/Juego",
    )

    class Meta:
        model = SessionSegment
        fields = ["session", "game_or_category"]
