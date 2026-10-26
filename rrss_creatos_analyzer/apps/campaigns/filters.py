import django_filters

from .models import CampaignDeliverable
from .models import SponsorCampaign


class SponsorCampaignFilter(django_filters.FilterSet):
    brand_name = django_filters.CharFilter(lookup_expr="icontains", label="Marca")
    campaign_name = django_filters.CharFilter(lookup_expr="icontains", label="Campaña")

    class Meta:
        model = SponsorCampaign
        fields = ["brand_name", "campaign_name", "status", "account_manager"]


class CampaignDeliverableFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains", label="Entregable")

    class Meta:
        model = CampaignDeliverable
        fields = ["campaign", "creator", "deliverable_type", "platform", "status"]
