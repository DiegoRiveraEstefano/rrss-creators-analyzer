from django.urls import path

from .views import ChannelCreateView
from .views import ChannelDeleteView
from .views import ChannelDetailView
from .views import ChannelListView
from .views import ChannelSetPrimaryView
from .views import ChannelSnapshotCreateView
from .views import ChannelSnapshotDeleteView
from .views import ChannelSnapshotDetailView
from .views import ChannelSnapshotListView
from .views import ChannelSnapshotUpdateView
from .views import ChannelToggleSyncView
from .views import ChannelUpdateView
from .views import CreatorCreateView
from .views import CreatorDeleteView
from .views import CreatorDetailView
from .views import CreatorListView
from .views import CreatorPersonalInfoUpdateView
from .views import CreatorStatusChangeView
from .views import CreatorUpdateView

app_name = "creators"

urlpatterns = [
    path("", CreatorListView.as_view(), name="creator_list"),
    path("create/", CreatorCreateView.as_view(), name="creator_create"),
    path("<int:pk>/", CreatorDetailView.as_view(), name="creator_detail"),
    path("<int:pk>/edit/", CreatorUpdateView.as_view(), name="creator_update"),
    path("<int:pk>/delete/", CreatorDeleteView.as_view(), name="creator_delete"),
    path(
        "<int:pk>/change-status/",
        CreatorStatusChangeView.as_view(),
        name="creator_change_status",
    ),
    path(
        "<int:creator_pk>/personal-info/",
        CreatorPersonalInfoUpdateView.as_view(),
        name="creator_personal_info",
    ),
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
    path(
        "channels/<int:pk>/set-primary/",
        ChannelSetPrimaryView.as_view(),
        name="channel_set_primary",
    ),
    path(
        "channels/<int:pk>/toggle-sync/",
        ChannelToggleSyncView.as_view(),
        name="channel_toggle_sync",
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
