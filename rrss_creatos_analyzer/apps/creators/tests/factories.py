from __future__ import annotations

import factory
from factory import Faker
from factory.django import DjangoModelFactory
from slugify import slugify

from rrss_creatos_analyzer.apps.core.choices import CreatorStatus
from rrss_creatos_analyzer.apps.core.choices import CreatorTier
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.creators.models import Channel
from rrss_creatos_analyzer.apps.creators.models import ChannelSnapshot
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.creators.models import CreatorPersonalInfo
from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory


class CreatorFactory(DjangoModelFactory[Creator]):
    user = factory.SubFactory(UserFactory)
    manager = factory.SubFactory(UserFactory)
    display_name = Faker("name")
    handle = factory.Sequence(lambda n: f"creator_{n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.handle))
    main_category = "Gaming"
    tier = CreatorTier.STANDARD
    status = CreatorStatus.ACTIVE

    class Meta:
        model = Creator
        django_get_or_create = ["handle"]


class CreatorPersonalInfoFactory(DjangoModelFactory[CreatorPersonalInfo]):
    creator = factory.SubFactory(CreatorFactory)
    legal_full_name = Faker("name")
    tax_id = factory.Sequence(lambda n: f"ID-{n:06d}")
    contact_email = Faker("email")
    phone_number = Faker("phone_number")
    country_code = "ES"
    city = "Madrid"
    address = Faker("street_address")
    postal_code = "28001"

    class Meta:
        model = CreatorPersonalInfo
        django_get_or_create = ["creator"]


class ChannelFactory(DjangoModelFactory[Channel]):
    creator = factory.SubFactory(CreatorFactory)
    platform = PlatformType.TWITCH
    platform_channel_id = factory.Sequence(lambda n: f"channel_{n}")
    handle = factory.Sequence(lambda n: f"chan_handle_{n}")
    channel_name = factory.Sequence(lambda n: f"Channel {n}")
    followers_count = 5000
    subscribers_count = 250
    total_views_count = 20000
    is_primary = False
    is_live = False

    class Meta:
        model = Channel


class ChannelSnapshotFactory(DjangoModelFactory[ChannelSnapshot]):
    channel = factory.SubFactory(ChannelFactory)
    snapshot_date = Faker("date_object")
    followers_count = 5000
    followers_delta = 100
    subscribers_count = 250
    subscribers_delta = 10
    total_views_count = 20000
    views_delta = 500

    class Meta:
        model = ChannelSnapshot
