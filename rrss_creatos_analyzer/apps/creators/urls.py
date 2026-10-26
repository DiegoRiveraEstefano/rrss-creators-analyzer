from django.urls import path

from .views import ChannelCreateView
from .views import ChannelDeleteView
from .views import ChannelDetailView
from .views import ChannelListView
from .views import ChannelSnapshotCreateView
from .views import ChannelSnapshotDeleteView
from .views import ChannelSnapshotDetailView
from .views import ChannelSnapshotListView
from .views import ChannelSnapshotUpdateView
from .views import ChannelUpdateView
from .views import CreatorCreateView
from .views import CreatorDeleteView
from .views import CreatorDetailView
from .views import CreatorListView
from .views import CreatorUpdateView

app_name = "creators"

urlpatterns = [
    path("", CreatorListView.as_view(), name="creator_list"),
    path("create/", CreatorCreateView.as_view(), name="creator_create"),
    path("<int:pk>/", CreatorDetailView.as_view(), name="creator_detail"),
    path("<int:pk>/edit/", CreatorUpdateView.as_view(), name="creator_update"),
    path("<int:pk>/delete/", CreatorDeleteView.as_view(), name="creator_delete"),
    # Channels
    path("channels/", ChannelListView.as_view(), name="channel_list"),
    path("channels/create/", ChannelCreateView.as_view(), name="channel_create"),
    path("channels/<int:pk>/", ChannelDetailView.as_view(), name="channel_detail"),
    path("channels/<int:pk>/edit/", ChannelUpdateView.as_view(), name="channel_update"),
    path(
        "channels/<int:pk>/delete/",
        ChannelDeleteView.as_view(),
        name="channel_delete",
    ),
    # Channel Snapshots
    path("snapshots/", ChannelSnapshotListView.as_view(), name="snapshot_list"),
    path(
        "snapshots/create/",
        ChannelSnapshotCreateView.as_view(),
        name="snapshot_create",
    ),
    path(
        "snapshots/<int:pk>/",
        ChannelSnapshotDetailView.as_view(),
        name="snapshot_detail",
    ),
    path(
        "snapshots/<int:pk>/edit/",
        ChannelSnapshotUpdateView.as_view(),
        name="snapshot_update",
    ),
    path(
        "snapshots/<int:pk>/delete/",
        ChannelSnapshotDeleteView.as_view(),
        name="snapshot_delete",
    ),
]
