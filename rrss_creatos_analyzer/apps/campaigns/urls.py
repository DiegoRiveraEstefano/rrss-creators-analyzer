from django.urls import path

from .views import CampaignDeliverableCreateView
from .views import CampaignDeliverableDeleteView
from .views import CampaignDeliverableDetailView
from .views import CampaignDeliverableListView
from .views import CampaignDeliverableUpdateView
from .views import SponsorCampaignCreateView
from .views import SponsorCampaignDeleteView
from .views import SponsorCampaignDetailView
from .views import SponsorCampaignListView
from .views import SponsorCampaignUpdateView

app_name = "campaigns"

urlpatterns = [
    path("", SponsorCampaignListView.as_view(), name="campaign_list"),
    path("create/", SponsorCampaignCreateView.as_view(), name="campaign_create"),
    path("<int:pk>/", SponsorCampaignDetailView.as_view(), name="campaign_detail"),
    path("<int:pk>/edit/", SponsorCampaignUpdateView.as_view(), name="campaign_update"),
    path(
        "<int:pk>/delete/",
        SponsorCampaignDeleteView.as_view(),
        name="campaign_delete",
    ),
    # Deliverables
    path(
        "deliverables/",
        CampaignDeliverableListView.as_view(),
        name="deliverable_list",
    ),
    path(
        "deliverables/create/",
        CampaignDeliverableCreateView.as_view(),
        name="deliverable_create",
    ),
    path(
        "deliverables/<int:pk>/",
        CampaignDeliverableDetailView.as_view(),
        name="deliverable_detail",
    ),
    path(
        "deliverables/<int:pk>/edit/",
        CampaignDeliverableUpdateView.as_view(),
        name="deliverable_update",
    ),
    path(
        "deliverables/<int:pk>/delete/",
        CampaignDeliverableDeleteView.as_view(),
        name="deliverable_delete",
    ),
]
