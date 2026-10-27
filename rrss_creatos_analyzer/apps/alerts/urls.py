from django.urls import path

from .views import ChannelAlertCreateView
from .views import ChannelAlertDeleteView
from .views import ChannelAlertDetailView
from .views import ChannelAlertListView
from .views import ChannelAlertUpdateView

app_name = "alerts"

urlpatterns = [
    path("", ChannelAlertListView.as_view(), name="alert_list"),
    path("create/", ChannelAlertCreateView.as_view(), name="alert_create"),
    path("<int:pk>/", ChannelAlertDetailView.as_view(), name="alert_detail"),
    path("<int:pk>/edit/", ChannelAlertUpdateView.as_view(), name="alert_update"),
    path("<int:pk>/delete/", ChannelAlertDeleteView.as_view(), name="alert_delete"),
]
