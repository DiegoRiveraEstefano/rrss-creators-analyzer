import pytest
from django.db import IntegrityError

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.creators.tests.factories import ChannelFactory
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.creators.tests.factories import (
    CreatorPersonalInfoFactory,
)

pytestmark = pytest.mark.django_db


def test_creator_creation_normalized():
    creator = CreatorFactory(display_name="Ibai Llanos", handle="ibai")
    assert str(creator) == "Ibai Llanos (@ibai)"
    assert hasattr(creator, "display_name")
    assert hasattr(creator, "handle")
    # Los campos de canal y personales ya no residen en Creator
    assert not hasattr(Creator, "primary_platform") or isinstance(
        Creator.primary_platform,
        property,
    )
    assert not hasattr(Creator, "legal_full_name")


def test_creator_personal_info_relation():
    creator = CreatorFactory(display_name="AuronPlay", handle="auron")
    personal_info = CreatorPersonalInfoFactory(
        creator=creator,
        legal_full_name="Raúl Álvarez Genes",
        tax_id="ES12345678Z",
        contact_email="auron@example.com",
    )
    creator.refresh_from_db()
    assert creator.personal_info == personal_info
    assert creator.personal_info.legal_full_name == "Raúl Álvarez Genes"
    assert "AuronPlay" in str(personal_info)


def test_creator_primary_channel_and_platform_property():
    creator = CreatorFactory()
    assert creator.primary_channel is None
    assert creator.primary_platform == ""

    ch_twitch = ChannelFactory(
        creator=creator,
        platform=PlatformType.TWITCH,
        is_primary=True,
    )
    ChannelFactory(
        creator=creator,
        platform=PlatformType.YOUTUBE,
        is_primary=False,
    )

    creator.refresh_from_db()
    assert creator.primary_channel == ch_twitch
    assert creator.primary_platform == PlatformType.TWITCH


def test_channel_single_primary_constraint():
    creator = CreatorFactory()
    ChannelFactory(creator=creator, platform=PlatformType.TWITCH, is_primary=True)

    with pytest.raises(IntegrityError):
        ChannelFactory(creator=creator, platform=PlatformType.YOUTUBE, is_primary=True)
