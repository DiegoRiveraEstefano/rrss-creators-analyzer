from http import HTTPStatus

import pytest
from django.urls import reverse

from rrss_creatos_analyzer.apps.core.choices import CreatorStatus
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.creators.tests.factories import ChannelFactory
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.creators.tests.factories import (
    CreatorPersonalInfoFactory,
)
from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_creator_list_view_renders_kpis_and_table(client):
    admin = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(admin)

    c1 = CreatorFactory(display_name="Ibai Llanos")
    ChannelFactory(creator=c1, platform=PlatformType.TWITCH, followers_count=12000000)

    res = client.get(reverse("creators:creator_list"))
    assert res.status_code == HTTPStatus.OK
    assert "kpis" in res.context
    assert b"Ibai Llanos" in res.content
    assert b"Directorio de Creadores" in res.content


def test_creator_detail_view_renders_dashboard(client):
    admin = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(admin)

    creator = CreatorFactory(display_name="IlloJuan", handle="illojuan")
    ChannelFactory(
        creator=creator,
        platform=PlatformType.TWITCH,
        followers_count=1000000,
        is_primary=True,
    )
    CreatorPersonalInfoFactory(
        creator=creator,
        legal_full_name="Juan Alberto García",
        tax_id="ES11223344K",
        city="Málaga",
    )

    res = client.get(reverse("creators:creator_detail", kwargs={"pk": creator.pk}))
    assert res.status_code == HTTPStatus.OK
    assert b"IlloJuan" in res.content
    assert b"Juan Alberto Garc" in res.content
    assert b"M\xc3\xa1laga" in res.content
    assert b"Twitch" in res.content


def test_creator_create_view_with_initial_channel(client):
    admin = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(admin)

    url = reverse("creators:creator_create")
    res_post = client.post(
        url,
        data={
            "display_name": "Rivers GG",
            "handle": "rivers_gg",
            "tier": "partner",
            "status": "active",
            "main_category": "Gaming & Just Chatting",
            "language_code": "es",
            "link_initial_channel": True,
            "initial_platform": PlatformType.TWITCH,
            "initial_channel_id": "rivers_gg",
            "initial_channel_url": "https://twitch.tv/rivers_gg",
            "initial_followers_count": 6500000,
        },
    )
    assert res_post.status_code == HTTPStatus.FOUND
    creator = Creator.objects.get(handle="rivers_gg")
    assert creator.display_name == "Rivers GG"
    assert creator.channels.count() == 1
    ch = creator.channels.first()
    assert ch.platform == PlatformType.TWITCH
    assert ch.is_primary is True
    assert ch.followers_count == 6500000


def test_creator_personal_info_update_view(client):
    admin = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(admin)

    creator = CreatorFactory(display_name="TheGrefg", handle="thegrefg")
    url = reverse("creators:creator_personal_info", kwargs={"creator_pk": creator.pk})

    res_get = client.get(url)
    assert res_get.status_code == HTTPStatus.OK

    res_post = client.post(
        url,
        data={
            "legal_full_name": "David Cánovas Martínez",
            "tax_id": "AD-123456-X",
            "contact_email": "grefg@example.com",
            "country_code": "AD",
            "city": "Andorra la Vella",
            "address": "Av. Meritxell 10",
            "postal_code": "AD500",
            "phone_number": "+376123456",
            "bank_name": "Andbank",
            "bank_account_holder": "David Cánovas",
            "bank_account_iban": "AD1200010001000123456789",
            "bank_swift_bic": "ANDBAD",
        },
    )
    assert res_post.status_code == HTTPStatus.FOUND
    creator.refresh_from_db()
    assert creator.personal_info.legal_full_name == "David Cánovas Martínez"
    assert creator.personal_info.city == "Andorra la Vella"


def test_creator_status_change_view(client):
    admin = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(admin)

    creator = CreatorFactory(status=CreatorStatus.ACTIVE)
    url = reverse("creators:creator_change_status", kwargs={"pk": creator.pk})

    res = client.post(
        url,
        data={
            "status": CreatorStatus.ON_LEAVE,
            "reason": "Vacaciones de temporada",
        },
    )
    assert res.status_code == HTTPStatus.FOUND
    creator.refresh_from_db()
    assert creator.status == CreatorStatus.ON_LEAVE
    assert "Vacaciones de temporada" in creator.internal_notes


def test_channel_set_primary_view(client):
    admin = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(admin)

    creator = CreatorFactory()
    ch1 = ChannelFactory(creator=creator, platform=PlatformType.TWITCH, is_primary=True)
    ch2 = ChannelFactory(
        creator=creator,
        platform=PlatformType.YOUTUBE,
        is_primary=False,
    )

    url = reverse("creators:channel_set_primary", kwargs={"pk": ch2.pk})
    res = client.post(url)
    assert res.status_code == HTTPStatus.FOUND

    ch1.refresh_from_db()
    ch2.refresh_from_db()
    assert ch2.is_primary is True
    assert ch1.is_primary is False


def test_channel_toggle_sync_view(client):
    admin = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(admin)

    ch = ChannelFactory(sync_enabled=True)
    url = reverse("creators:channel_toggle_sync", kwargs={"pk": ch.pk})

    res = client.post(url)
    assert res.status_code == HTTPStatus.FOUND
    ch.refresh_from_db()
    assert ch.sync_enabled is False
