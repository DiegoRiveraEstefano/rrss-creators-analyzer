from django.urls import path

from .views import ExportJobCreateView
from .views import ExportJobDeleteView
from .views import ExportJobDetailView
from .views import ExportJobListView
from .views import ExportJobUpdateView

app_name = "exports"

urlpatterns = [
    path("", ExportJobListView.as_view(), name="export_list"),
    path("create/", ExportJobCreateView.as_view(), name="export_create"),
    path("<int:pk>/", ExportJobDetailView.as_view(), name="export_detail"),
    path("<int:pk>/edit/", ExportJobUpdateView.as_view(), name="export_update"),
    path("<int:pk>/delete/", ExportJobDeleteView.as_view(), name="export_delete"),
]
