from django.urls import path

from .views import CreatorPayoutCreateView
from .views import CreatorPayoutDeleteView
from .views import CreatorPayoutDetailView
from .views import CreatorPayoutListView
from .views import CreatorPayoutUpdateView

app_name = "payouts"

urlpatterns = [
    path("", CreatorPayoutListView.as_view(), name="payout_list"),
    path("create/", CreatorPayoutCreateView.as_view(), name="payout_create"),
    path("<int:pk>/", CreatorPayoutDetailView.as_view(), name="payout_detail"),
    path("<int:pk>/edit/", CreatorPayoutUpdateView.as_view(), name="payout_update"),
    path("<int:pk>/delete/", CreatorPayoutDeleteView.as_view(), name="payout_delete"),
]
