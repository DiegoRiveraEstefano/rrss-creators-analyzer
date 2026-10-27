import datetime

import pytest
from django.utils import timezone

from rrss_creatos_analyzer.apps.core.choices import CreatorStatus
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.creators.services import ChannelService
from rrss_creatos_analyzer.apps.creators.services import ChannelSnapshotService
from rrss_creatos_analyzer.apps.creators.services import CreatorService
from rrss_creatos_analyzer.apps.creators.tests.factories import ChannelFactory
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory

pytestmark = pytest.mark.django_db


def test_save_creator_with_auto_slug_and_dates():
    creator = CreatorService.save_creator(
        display_name="El Rubius",
        handle="Rubius",
        status=CreatorStatus.ACTIVE,
    )
    assert creator.slug == "rubius"
    assert creator.joined_company_at == timezone.localdate()
    assert creator.left_company_at is None


def test_save_creator_with_personal_info():
    creator = CreatorService.save_creator(
        display_name="Vegetta777",
        handle="vegetta777",
        status=CreatorStatus.ACTIVE,
        personal_info_data={
            "legal_full_name": "Samuel de Luque",
            "tax_id": "ES99988877A",
            "contact_email": "samuel@example.com",
            "city": "Madrid",
        },
    )
    assert hasattr(creator, "personal_info")
    assert creator.personal_info.legal_full_name == "Samuel de Luque"
    assert creator.personal_info.city == "Madrid"


def test_save_creator_with_initial_channel_onboarding():
    creator = CreatorService.save_creator(
        display_name="AuronPlay",
        handle="auronplay",
        status=CreatorStatus.ACTIVE,
        initial_channel_data={
            "platform": PlatformType.TWITCH,
            "platform_channel_id": "auronplay",
            "channel_url": "https://twitch.tv/auronplay",
            "followers_count": 15000000,
        },
    )
    assert creator.channels.count() == 1
    channel = creator.channels.first()
    assert channel.platform == PlatformType.TWITCH
    assert channel.is_primary is True
    assert channel.followers_count == 15000000


def test_change_creator_status():
    creator = CreatorFactory(status=CreatorStatus.ACTIVE)
    updated = CreatorService.change_status(
        creator=creator,
        new_status=CreatorStatus.INACTIVE,
        reason="Fin de contrato pactado",
    )
    assert updated.status == CreatorStatus.INACTIVE
    assert updated.left_company_at == timezone.localdate()
    assert "Fin de contrato pactado" in updated.internal_notes

    with pytest.raises(BusinessLogicError):
        CreatorService.change_status(creator=creator, new_status="invalid_status")


def test_channel_save_first_channel_is_primary_automatically():
    creator = CreatorFactory()
    channel = ChannelService.save_channel(
        creator=creator,
        platform=PlatformType.TWITCH,
        platform_channel_id="twitch_123",
        is_primary=False,
    )
    assert channel.is_primary is True


def test_channel_set_primary_switches_others():
    creator = CreatorFactory()
    ch1 = ChannelFactory(creator=creator, platform=PlatformType.TWITCH, is_primary=True)
    ch2 = ChannelFactory(
        creator=creator,
        platform=PlatformType.YOUTUBE,
        is_primary=False,
    )

    ChannelService.set_primary_channel(channel=ch2)
    ch1.refresh_from_db()
    ch2.refresh_from_db()

    assert ch2.is_primary is True
    assert ch1.is_primary is False


def test_channel_save_negative_counts_raises_error():
    creator = CreatorFactory()
    with pytest.raises(BusinessLogicError):
        ChannelService.save_channel(
            creator=creator,
            platform=PlatformType.KICK,
            platform_channel_id="kick_abc",
            followers_count=-10,
        )


def test_channel_toggle_sync():
    channel = ChannelFactory(sync_enabled=True)
    ChannelService.toggle_sync(channel=channel)
    channel.refresh_from_db()
    assert channel.sync_enabled is False

    ChannelService.toggle_sync(channel=channel)
    channel.refresh_from_db()
    assert channel.sync_enabled is True


def test_delete_channel_promotes_next_if_was_primary():
    creator = CreatorFactory()
    ch1 = ChannelFactory(creator=creator, platform=PlatformType.TWITCH, is_primary=True)
    ch2 = ChannelFactory(
        creator=creator,
        platform=PlatformType.YOUTUBE,
        is_primary=False,
    )

    ChannelService.delete_channel(instance=ch1)
    ch2.refresh_from_db()
    assert ch2.is_primary is True


def test_snapshot_auto_delta_calculation_and_channel_update():
    channel = ChannelFactory(
        followers_count=1000,
        subscribers_count=50,
        total_views_count=10000,
    )
    d1 = datetime.date(2026, 10, 1)
    d2 = datetime.date(2026, 10, 2)

    # Primer snapshot
    s1 = ChannelSnapshotService.save_snapshot(
        channel=channel,
        snapshot_date=d1,
        followers_count=1000,
        subscribers_count=50,
        total_views_count=10000,
    )
    assert s1.followers_delta == 0

    # Segundo snapshot con crecimiento
    s2 = ChannelSnapshotService.save_snapshot(
        channel=channel,
        snapshot_date=d2,
        followers_count=1200,
        subscribers_count=60,
        total_views_count=12500,
    )
    assert s2.followers_delta == 200
    assert s2.subscribers_delta == 10
    assert s2.views_delta == 2500

    channel.refresh_from_db()
    assert channel.followers_count == 1200
    assert channel.subscribers_count == 60
    assert channel.total_views_count == 12500
