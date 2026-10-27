from django.urls import path

from .views import RoleGroupProfileCreateView
from .views import RoleGroupProfileDeleteView
from .views import RoleGroupProfileDetailView
from .views import RoleGroupProfileListView
from .views import RoleGroupProfileUpdateView

app_name = "permissions"

urlpatterns = [
    path("", RoleGroupProfileListView.as_view(), name="role_list"),
    path("create/", RoleGroupProfileCreateView.as_view(), name="role_create"),
    path("<int:pk>/", RoleGroupProfileDetailView.as_view(), name="role_detail"),
    path("<int:pk>/edit/", RoleGroupProfileUpdateView.as_view(), name="role_update"),
    path("<int:pk>/delete/", RoleGroupProfileDeleteView.as_view(), name="role_delete"),
]
