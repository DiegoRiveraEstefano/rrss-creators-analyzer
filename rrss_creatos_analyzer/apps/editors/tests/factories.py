from __future__ import annotations

from decimal import Decimal

import factory
from django.utils import timezone
from factory import Faker
from factory.django import DjangoModelFactory
from slugify import slugify

from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.editors.choices import AssignmentStatus
from rrss_creatos_analyzer.apps.editors.choices import EditorAssignmentRole
from rrss_creatos_analyzer.apps.editors.choices import EditorSpecialty
from rrss_creatos_analyzer.apps.editors.choices import EditorStatus
from rrss_creatos_analyzer.apps.editors.choices import EditorType
from rrss_creatos_analyzer.apps.editors.choices import RateModel
from rrss_creatos_analyzer.apps.editors.choices import RevisionStatus
from rrss_creatos_analyzer.apps.editors.choices import TaskPriority
from rrss_creatos_analyzer.apps.editors.choices import TaskStatus
from rrss_creatos_analyzer.apps.editors.choices import TaskType
from rrss_creatos_analyzer.apps.editors.models import EditingTask
from rrss_creatos_analyzer.apps.editors.models import Editor
from rrss_creatos_analyzer.apps.editors.models import EditorAssignment
from rrss_creatos_analyzer.apps.editors.models import TaskRevision
from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory


class EditorFactory(DjangoModelFactory[Editor]):
    user = factory.SubFactory(UserFactory)
    name = Faker("name")
    handle = factory.Sequence(lambda n: f"editor_{n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.handle))
    email = Faker("email")
    status = EditorStatus.ACTIVE
    editor_type = EditorType.FREELANCER
    primary_specialty = EditorSpecialty.LONG_FORM
    rate_model = RateModel.PER_VIDEO
    base_video_rate = Decimal("150.00")
    base_short_rate = Decimal("40.00")
    hourly_rate = Decimal("25.00")
    monthly_retainer = Decimal("0.00")
    max_active_tasks = 4

    class Meta:
        model = Editor


class EditorAssignmentFactory(DjangoModelFactory[EditorAssignment]):
    editor = factory.SubFactory(EditorFactory)
    creator = factory.SubFactory(CreatorFactory)
    role = EditorAssignmentRole.LEAD_EDITOR
    status = AssignmentStatus.ACTIVE
    is_primary = True
    agreed_video_rate = Decimal("160.00")
    agreed_short_rate = Decimal("45.00")
    start_date = Faker("date_object")

    class Meta:
        model = EditorAssignment


class EditingTaskFactory(DjangoModelFactory[EditingTask]):
    title = factory.Sequence(lambda n: f"Edición Video Episodio {n}")
    creator = factory.SubFactory(CreatorFactory)
    editor = factory.SubFactory(EditorFactory)
    status = TaskStatus.ASSIGNED
    priority = TaskPriority.MEDIUM
    task_type = TaskType.LONG_FORM_EDIT
    assigned_date = Faker("date_object")
    deadline = factory.LazyAttribute(lambda o: o.assigned_date)
    agreed_cost = Decimal("150.00")

    class Meta:
        model = EditingTask


class TaskRevisionFactory(DjangoModelFactory[TaskRevision]):
    task = factory.SubFactory(EditingTaskFactory)
    revision_number = 1
    render_url = "https://example.com/renders/v1.mp4"
    status = RevisionStatus.PENDING_REVIEW
    submitted_at = factory.LazyFunction(timezone.now)

    class Meta:
        model = TaskRevision
