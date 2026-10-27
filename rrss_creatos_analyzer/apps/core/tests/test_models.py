import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import connection
from django.db import models
from django.utils import timezone

from rrss_creatos_analyzer.apps.core.base_models import ActiveBaseModel
from rrss_creatos_analyzer.apps.core.base_models import ArchivableModelMixin
from rrss_creatos_analyzer.apps.core.base_models import BaseModel
from rrss_creatos_analyzer.apps.core.base_models import DateRangeModelMixin
from rrss_creatos_analyzer.apps.core.base_models import MetadataModelMixin
from rrss_creatos_analyzer.apps.core.base_models import MonetaryModelMixin
from rrss_creatos_analyzer.apps.core.base_models import NameSlugDescriptionModel
from rrss_creatos_analyzer.apps.core.base_models import SoftDeleteBaseModel
from rrss_creatos_analyzer.apps.core.base_models import StandardModel
from rrss_creatos_analyzer.apps.core.base_models import StandardUUIDModel
from rrss_creatos_analyzer.apps.core.base_models import TitleSlugDescriptionModel
from rrss_creatos_analyzer.apps.core.base_models import UserTrackingModelMixin
from rrss_creatos_analyzer.apps.core.base_models import UUIDBaseModel
from rrss_creatos_analyzer.apps.core.models import CompanySettings

User = get_user_model()
pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_test_model():
    created_models = []

    def _create(model_cls):
        with connection.schema_editor() as editor:
            editor.create_model(model_cls)
        created_models.append(model_cls)
        return model_cls

    yield _create

    for model_cls in reversed(created_models):
        with connection.schema_editor() as editor:
            editor.delete_model(model_cls)


def test_company_settings_defaults_and_str():
    settings = CompanySettings.objects.create(
        company_name="Alpha Creators",
        legal_name="Alpha Creators LLC",
    )
    assert str(settings) == "Alpha Creators"
    assert settings.get_absolute_url() == f"/core/settings/{settings.pk}/"
    assert settings.default_currency == "USD"
    assert settings.default_agency_split_pct == Decimal("20.00")
    assert settings.default_creator_split_pct == Decimal("80.00")


def test_company_settings_splits_sum_constraint():
    with pytest.raises(IntegrityError):
        CompanySettings.objects.create(
            company_name="Bad Split",
            default_agency_split_pct=Decimal("30.00"),
            default_creator_split_pct=Decimal("80.00"),
        )


def test_active_model_mixin(create_test_model):
    class ItemActive(ActiveBaseModel):
        name = models.CharField(max_length=50)

        class Meta:
            app_label = "core"

    create_test_model(ItemActive)

    item1 = ItemActive.objects.create(name="One", is_active=True)
    item2 = ItemActive.objects.create(name="Two", is_active=False)

    assert list(ItemActive.objects.active()) == [item1]
    assert list(ItemActive.objects.inactive()) == [item2]

    item2.activate()
    assert item2.is_active is True
    assert ItemActive.objects.active().count() == 2  # noqa: PLR2004

    item1.deactivate()
    assert item1.is_active is False
    assert ItemActive.objects.active().count() == 1

    item1.toggle_active()
    assert item1.is_active is True


def test_soft_deletable_model_mixin(create_test_model):
    class ItemSoftDelete(SoftDeleteBaseModel):
        title = models.CharField(max_length=50)

        class Meta:
            app_label = "core"

    create_test_model(ItemSoftDelete)

    item1 = ItemSoftDelete.objects.create(title="Post 1")
    item2 = ItemSoftDelete.objects.create(title="Post 2")

    assert ItemSoftDelete.objects.count() == 2  # noqa: PLR2004

    # Soft delete item1
    item1.delete()
    item1.refresh_from_db()
    assert item1.is_deleted is True
    assert item1.deleted_at is not None

    # Manager filters out soft-deleted
    assert list(ItemSoftDelete.objects.all()) == [item2]
    assert list(ItemSoftDelete.objects.deleted()) == [item1]
    assert ItemSoftDelete.objects.with_deleted().count() == 2  # noqa: PLR2004
    assert ItemSoftDelete.all_objects.count() == 2  # noqa: PLR2004

    # Restore item1
    item1.restore()
    assert item1.is_deleted is False
    assert item1.deleted_at is None
    assert ItemSoftDelete.objects.count() == 2  # noqa: PLR2004

    # Hard delete
    item1.hard_delete()
    assert ItemSoftDelete.all_objects.count() == 1


def test_soft_delete_queryset_delete_and_restore(create_test_model):
    class Article(SoftDeleteBaseModel):
        headline = models.CharField(max_length=100)

        class Meta:
            app_label = "core"

    create_test_model(Article)

    Article.objects.create(headline="Art 1")
    Article.objects.create(headline="Art 2")

    # Bulk soft delete
    Article.objects.all().delete()
    assert Article.objects.count() == 0
    assert Article.objects.deleted().count() == 2  # noqa: PLR2004

    # Bulk restore
    Article.objects.deleted().restore()
    assert Article.objects.count() == 2  # noqa: PLR2004


def test_slugged_model_mixin(create_test_model):
    class Category(TitleSlugDescriptionModel):
        class Meta:
            app_label = "core"

    create_test_model(Category)

    cat1 = Category.objects.create(title="Gaming Highlights")
    assert cat1.slug == "gaming-highlights"
    assert str(cat1) == "Gaming Highlights"

    # Collision test: same title produces unique slug with suffix
    cat2 = Category.objects.create(title="Gaming Highlights")
    assert cat2.slug == "gaming-highlights-2"

    # Custom slug is respected
    cat3 = Category.objects.create(title="Gaming", slug="custom-slug")
    assert cat3.slug == "custom-slug"


def test_name_slug_description_model(create_test_model):
    class Tag(NameSlugDescriptionModel):
        class Meta:
            app_label = "core"

    create_test_model(Tag)

    tag = Tag.objects.create(name="Fortnite Pro")
    assert tag.slug == "fortnite-pro"
    assert str(tag) == "Fortnite Pro"


def test_metadata_model_mixin(create_test_model):
    expected_limit = 100

    class ServiceConfig(BaseModel, MetadataModelMixin):
        class Meta:
            app_label = "core"

    create_test_model(ServiceConfig)

    cfg = ServiceConfig.objects.create()
    assert cfg.get_metadata("missing", default="empty") == "empty"

    cfg.set_metadata("rate_limit", expected_limit, commit=True)
    cfg.refresh_from_db()
    assert cfg.get_metadata("rate_limit") == expected_limit

    cfg.remove_metadata("rate_limit", commit=True)
    cfg.refresh_from_db()
    assert cfg.get_metadata("rate_limit") is None


def test_date_range_model_mixin(create_test_model):
    class Event(BaseModel, DateRangeModelMixin):
        class Meta:
            app_label = "core"

    create_test_model(Event)

    today = timezone.localdate()
    current_event = Event(
        start_date=today - timedelta(days=2),
        end_date=today + timedelta(days=2),
    )
    assert current_event.is_currently_active is True

    past_event = Event(
        start_date=today - timedelta(days=5),
        end_date=today - timedelta(days=1),
    )
    assert past_event.is_currently_active is False

    invalid_event = Event(
        start_date=today + timedelta(days=5),
        end_date=today + timedelta(days=1),
    )
    with pytest.raises(ValidationError):
        invalid_event.clean()


def test_monetary_model_mixin(create_test_model):
    class Budget(BaseModel, MonetaryModelMixin):
        class Meta(MonetaryModelMixin.Meta):
            app_label = "core"

    create_test_model(Budget)

    valid_budget = Budget.objects.create(amount=Decimal("150.50"), currency="EUR")
    assert valid_budget.amount == Decimal("150.50")
    assert valid_budget.currency == "EUR"

    invalid_budget = Budget(amount=Decimal("-10.00"))
    with pytest.raises(ValidationError):
        invalid_budget.clean()

    with pytest.raises(IntegrityError):
        Budget.objects.create(amount=Decimal("-10.00"))


def test_archivable_model_mixin(create_test_model):
    class Document(BaseModel, ArchivableModelMixin):
        class Meta:
            app_label = "core"

    create_test_model(Document)

    doc = Document.objects.create()
    assert doc.is_archived is False
    assert Document.objects.not_archived().count() == 1
    assert Document.objects.archived().count() == 0

    doc.archive()
    assert doc.is_archived is True
    assert doc.archived_at is not None
    assert Document.objects.archived().count() == 1
    assert Document.objects.not_archived().count() == 0

    doc.unarchive()
    assert doc.is_archived is False
    assert doc.archived_at is None


def test_user_tracking_model_mixin(create_test_model):
    class Note(BaseModel, UserTrackingModelMixin):
        class Meta:
            app_label = "core"

    create_test_model(Note)

    user1 = User.objects.create_user(username="creator_admin")
    user2 = User.objects.create_user(username="editor_user")

    note = Note()
    note.set_user_tracking(user1)
    note.save()
    assert note.created_by == user1
    assert note.updated_by == user1

    note.set_user_tracking(user2)
    note.save()
    assert note.created_by == user1
    assert note.updated_by == user2


def test_uuid_base_model(create_test_model):
    class Resource(UUIDBaseModel):
        class Meta:
            app_label = "core"

    create_test_model(Resource)

    res = Resource.objects.create()
    assert isinstance(res.uuid, uuid.UUID)
    assert res.created_at is not None
    assert res.updated_at is not None


def test_standard_model_and_standard_uuid_model(create_test_model):
    class Entity(StandardModel):
        class Meta:
            app_label = "core"

    class SecuredEntity(StandardUUIDModel):
        class Meta:
            app_label = "core"

    create_test_model(Entity)
    create_test_model(SecuredEntity)

    e = Entity.objects.create()
    assert e.is_active is True
    assert e.metadata == {}

    se = SecuredEntity.objects.create()
    assert isinstance(se.uuid, uuid.UUID)
    assert se.is_active is True
    assert se.metadata == {}
