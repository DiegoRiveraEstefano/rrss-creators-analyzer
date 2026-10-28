from django.urls import path

from .views import CategoryPerformanceView
from .views import SessionSegmentCreateView
from .views import SessionSegmentDeleteView
from .views import SessionSegmentDetailView
from .views import SessionSegmentListView
from .views import SessionSegmentUpdateView
from .views import StreamingSessionCreateView
from .views import StreamingSessionDeleteView
from .views import StreamingSessionDetailView
from .views import StreamingSessionListView
from .views import StreamingSessionUpdateView

app_name = "streams"

urlpatterns = [
    path("", StreamingSessionListView.as_view(), name="session_list"),
    path("create/", StreamingSessionCreateView.as_view(), name="session_create"),
    path(
        "category-performance/",
        CategoryPerformanceView.as_view(),
        name="category_performance",
    ),
    path("<int:pk>/", StreamingSessionDetailView.as_view(), name="session_detail"),
    path("<int:pk>/edit/", StreamingSessionUpdateView.as_view(), name="session_update"),
    path(
        "<int:pk>/delete/",
        StreamingSessionDeleteView.as_view(),
        name="session_delete",
    ),
    # Segments
    path("segments/", SessionSegmentListView.as_view(), name="segment_list"),
    path("segments/create/", SessionSegmentCreateView.as_view(), name="segment_create"),
    path(
        "segments/<int:pk>/",
        SessionSegmentDetailView.as_view(),
        name="segment_detail",
    ),
    path(
        "segments/<int:pk>/edit/",
        SessionSegmentUpdateView.as_view(),
        name="segment_update",
    ),
    path(
        "segments/<int:pk>/delete/",
        SessionSegmentDeleteView.as_view(),
        name="segment_delete",
    ),
]
