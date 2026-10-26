from django.urls import path

from .views import CompanySettingsCreateView
from .views import CompanySettingsDeleteView
from .views import CompanySettingsDetailView
from .views import CompanySettingsListView
from .views import CompanySettingsUpdateView

app_name = "core"

urlpatterns = [
    path("settings/", CompanySettingsListView.as_view(), name="settings_list"),
    path(
        "settings/create/",
        CompanySettingsCreateView.as_view(),
        name="settings_create",
    ),
    path(
        "settings/<int:pk>/",
        CompanySettingsDetailView.as_view(),
        name="settings_detail",
    ),
    path(
        "settings/<int:pk>/edit/",
        CompanySettingsUpdateView.as_view(),
        name="settings_update",
    ),
    path(
        "settings/<int:pk>/delete/",
        CompanySettingsDeleteView.as_view(),
        name="settings_delete",
    ),
]
