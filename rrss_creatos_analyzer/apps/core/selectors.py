from typing import TYPE_CHECKING
from typing import Any

from rrss_creatos_analyzer.apps.alerts.models import ChannelAlert
from rrss_creatos_analyzer.apps.campaigns.models import SponsorCampaign
from rrss_creatos_analyzer.apps.contracts.models import Contract
from rrss_creatos_analyzer.apps.creators.models import Channel
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.payouts.models import CreatorPayout
from rrss_creatos_analyzer.apps.streams.models import StreamingSession
from rrss_creatos_analyzer.apps.videos.models import Video

from .choices import AlertStatus
from .choices import CampaignStatus
from .choices import CreatorStatus
from .models import CompanySettings

if TYPE_CHECKING:
    from django.db.models import QuerySet


class CompanySettingsSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[CompanySettings]:
        return CompanySettings.objects.all().order_by("-updated_at")

    @classmethod
    def get_current(cls) -> CompanySettings | None:
        return CompanySettings.objects.first()

    @classmethod
    def get_dashboard_summary(cls) -> dict[str, Any]:
        return {
            "company_settings": cls.get_current(),
            "creators_total": Creator.objects.count(),
            "creators_active": Creator.objects.filter(
                status=CreatorStatus.ACTIVE,
            ).count(),
            "channels_total": Channel.objects.count(),
            "channels_live": Channel.objects.filter(is_live=True).count(),
            "contracts_total": Contract.objects.count(),
            "sessions_total": StreamingSession.objects.count(),
            "videos_total": Video.objects.count(),
            "campaigns_active": SponsorCampaign.objects.filter(
                status=CampaignStatus.ACTIVE,
            ).count(),
            "alerts_open": ChannelAlert.objects.filter(
                status=AlertStatus.ACTIVE,
            ).count(),
            "payouts_total": CreatorPayout.objects.count(),
            "recent_creators": Creator.objects.select_related("manager").order_by(
                "-created_at",
            )[:5],
            "recent_sessions": StreamingSession.objects.select_related(
                "creator",
                "channel",
            ).order_by("-streamed_at")[:5],
            "recent_alerts": ChannelAlert.objects.select_related(
                "creator",
                "channel",
            ).order_by("-occurred_at")[:5],
        }
