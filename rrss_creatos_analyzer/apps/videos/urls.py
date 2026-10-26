from django.urls import path

from .views import VideoCreateView
from .views import VideoDeleteView
from .views import VideoDetailView
from .views import VideoListView
from .views import VideoPublicationCreateView
from .views import VideoPublicationDeleteView
from .views import VideoPublicationDetailView
from .views import VideoPublicationListView
from .views import VideoPublicationUpdateView
from .views import VideoRelationCreateView
from .views import VideoRelationDeleteView
from .views import VideoRelationDetailView
from .views import VideoRelationListView
from .views import VideoRelationUpdateView
from .views import VideoUpdateView

app_name = "videos"

urlpatterns = [
    path("", VideoListView.as_view(), name="video_list"),
    path("create/", VideoCreateView.as_view(), name="video_create"),
    path("<int:pk>/", VideoDetailView.as_view(), name="video_detail"),
    path("<int:pk>/edit/", VideoUpdateView.as_view(), name="video_update"),
    path("<int:pk>/delete/", VideoDeleteView.as_view(), name="video_delete"),
    # Publications
    path("publications/", VideoPublicationListView.as_view(), name="publication_list"),
    path(
        "publications/create/",
        VideoPublicationCreateView.as_view(),
        name="publication_create",
    ),
    path(
        "publications/<int:pk>/",
        VideoPublicationDetailView.as_view(),
        name="publication_detail",
    ),
    path(
        "publications/<int:pk>/edit/",
        VideoPublicationUpdateView.as_view(),
        name="publication_update",
    ),
    path(
        "publications/<int:pk>/delete/",
        VideoPublicationDeleteView.as_view(),
        name="publication_delete",
    ),
    # Relations
    path("relations/", VideoRelationListView.as_view(), name="relation_list"),
    path(
        "relations/create/",
        VideoRelationCreateView.as_view(),
        name="relation_create",
    ),
    path(
        "relations/<int:pk>/",
        VideoRelationDetailView.as_view(),
        name="relation_detail",
    ),
    path(
        "relations/<int:pk>/edit/",
        VideoRelationUpdateView.as_view(),
        name="relation_update",
    ),
    path(
        "relations/<int:pk>/delete/",
        VideoRelationDeleteView.as_view(),
        name="relation_delete",
    ),
]
