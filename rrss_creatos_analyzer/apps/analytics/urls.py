from django.urls import path

from .views import AnalyticsSnapshotCreateView
from .views import AnalyticsSnapshotDeleteView
from .views import AnalyticsSnapshotDetailView
from .views import AnalyticsSnapshotListView
from .views import AnalyticsSnapshotUpdateView

app_name = "analytics"

urlpatterns = [
    path("", AnalyticsSnapshotListView.as_view(), name="snapshot_list"),
    path("create/", AnalyticsSnapshotCreateView.as_view(), name="snapshot_create"),
    path("<int:pk>/", AnalyticsSnapshotDetailView.as_view(), name="snapshot_detail"),
    path(
        "<int:pk>/edit/",
        AnalyticsSnapshotUpdateView.as_view(),
        name="snapshot_update",
    ),
    path(
        "<int:pk>/delete/",
        AnalyticsSnapshotDeleteView.as_view(),
        name="snapshot_delete",
    ),
]
