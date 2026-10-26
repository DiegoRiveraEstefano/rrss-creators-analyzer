from django.urls import path

from .views import ImportBatchCreateView
from .views import ImportBatchDeleteView
from .views import ImportBatchDetailView
from .views import ImportBatchListView
from .views import ImportBatchUpdateView

app_name = "imports"

urlpatterns = [
    path("", ImportBatchListView.as_view(), name="batch_list"),
    path("create/", ImportBatchCreateView.as_view(), name="batch_create"),
    path("<int:pk>/", ImportBatchDetailView.as_view(), name="batch_detail"),
    path("<int:pk>/edit/", ImportBatchUpdateView.as_view(), name="batch_update"),
    path("<int:pk>/delete/", ImportBatchDeleteView.as_view(), name="batch_delete"),
]
