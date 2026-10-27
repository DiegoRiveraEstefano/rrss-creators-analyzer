import django_filters

from .models import Video
from .models import VideoPublication
from .models import VideoRelation


class VideoFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains", label="Título")
    category = django_filters.CharFilter(lookup_expr="icontains", label="Categoría")

    class Meta:
        model = Video
        fields = ["title", "creator", "content_format", "status", "category"]


class VideoPublicationFilter(django_filters.FilterSet):
    published_after = django_filters.DateFilter(
        field_name="published_at",
        lookup_expr="date__gte",
        label="Desde",
    )
    published_before = django_filters.DateFilter(
        field_name="published_at",
        lookup_expr="date__lte",
        label="Hasta",
    )

    class Meta:
        model = VideoPublication
        fields = [
            "creator",
            "video",
            "platform",
            "publication_type",
            "status",
            "published_after",
            "published_before",
        ]


class VideoRelationFilter(django_filters.FilterSet):
    class Meta:
        model = VideoRelation
        fields = ["source_video", "relation_type", "target_video", "target_session"]
