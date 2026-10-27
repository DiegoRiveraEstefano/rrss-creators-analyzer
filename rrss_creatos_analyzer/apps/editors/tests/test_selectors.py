from decimal import Decimal

import pytest

from rrss_creatos_analyzer.apps.editors.choices import TaskStatus
from rrss_creatos_analyzer.apps.editors.selectors import EditingTaskSelector
from rrss_creatos_analyzer.apps.editors.selectors import EditorSelector
from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory

from .factories import EditingTaskFactory
from .factories import EditorFactory

pytestmark = pytest.mark.django_db


class TestEditorSelector:
    def test_get_visible_queryset_superuser(self):
        admin = UserFactory(is_superuser=True)
        EditorFactory(handle="ed1")
        EditorFactory(handle="ed2")

        qs = EditorSelector.get_visible_queryset(user=admin)
        assert qs.count() >= 2  # noqa: PLR2004

    def test_get_editor_metrics(self):
        editor = EditorFactory()
        EditingTaskFactory(
            editor=editor,
            status=TaskStatus.COMPLETED,
            agreed_cost=Decimal("150.00"),
            revision_count=2,
        )
        EditingTaskFactory(
            editor=editor,
            status=TaskStatus.COMPLETED,
            agreed_cost=Decimal("200.00"),
            revision_count=1,
        )
        EditingTaskFactory(
            editor=editor,
            status=TaskStatus.IN_PROGRESS,
            agreed_cost=Decimal("100.00"),
        )

        metrics = EditorSelector.get_editor_metrics(editor_id=editor.id)
        assert metrics["total_tasks"] == 3  # noqa: PLR2004
        assert metrics["completed_tasks"] == 2  # noqa: PLR2004
        assert metrics["active_tasks"] == 1
        assert metrics["total_earnings"] == Decimal("350.00")
        assert metrics["avg_revisions"] == 1.5  # noqa: PLR2004


class TestEditingTaskSelector:
    def test_get_pending_reviews(self):
        admin = UserFactory(is_superuser=True)
        task_review = EditingTaskFactory(status=TaskStatus.IN_REVIEW)
        task_done = EditingTaskFactory(status=TaskStatus.COMPLETED)

        pending = EditingTaskSelector.get_pending_reviews(user=admin)
        assert task_review in pending
        assert task_done not in pending
