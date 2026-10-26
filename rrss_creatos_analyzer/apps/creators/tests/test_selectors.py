import pytest

from rrss_creatos_analyzer.apps.core.choices import CreatorStatus
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.creators.selectors import ChannelSelector
from rrss_creatos_analyzer.apps.creators.selectors import CreatorSelector
from rrss_creatos_analyzer.apps.creators.tests.factories import ChannelFactory
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_creator_selector_visibility_superuser_vs_creator():
    superuser = UserFactory(is_superuser=True)
    creator_user = UserFactory(is_superuser=False)

    c1 = CreatorFactory(user=creator_user, status=CreatorStatus.ACTIVE)
    CreatorFactory(status=CreatorStatus.ACTIVE)

    qs_admin = CreatorSelector.get_visible_queryset(user=superuser)
    expected_min_count = 2
    assert qs_admin.count() >= expected_min_count

    qs_creator = CreatorSelector.get_visible_queryset(user=creator_user)
    assert qs_creator.count() == 1
    assert qs_creator.first() == c1


def test_creator_selector_annotations():
    admin = UserFactory(is_superuser=True)
    creator = CreatorFactory()
    ChannelFactory(creator=creator, platform=PlatformType.TWITCH, followers_count=3000)
    ChannelFactory(creator=creator, platform=PlatformType.YOUTUBE, followers_count=5000)

    item = CreatorSelector.get_visible_queryset(user=admin).get(pk=creator.pk)
    expected_channels = 2
    expected_followers = 8000
    assert item.channels_count == expected_channels
    assert item.total_followers_count == expected_followers


def test_creator_kpis():
    admin = UserFactory(is_superuser=True)
    CreatorFactory(status=CreatorStatus.ACTIVE)
    c2 = CreatorFactory(status=CreatorStatus.INACTIVE)
    ChannelFactory(creator=c2, is_live=True)

    kpis = CreatorSelector.get_kpis(user=admin)
    min_creators = 2
    assert kpis["total_creators"] >= min_creators
    assert kpis["active_creators"] >= 1
    assert kpis["live_now_creators"] >= 1


def test_channel_selector_order_primary_first():
    admin = UserFactory(is_superuser=True)
    creator = CreatorFactory()
    ch1 = ChannelFactory(
        creator=creator,
        platform=PlatformType.YOUTUBE,
        is_primary=False,
    )
    ch2 = ChannelFactory(
        creator=creator,
        platform=PlatformType.TWITCH,
        is_primary=True,
    )

    channels = list(ChannelSelector.get_for_creator(creator_id=creator.id, user=admin))
    assert channels[0] == ch2
    assert channels[1] == ch1
