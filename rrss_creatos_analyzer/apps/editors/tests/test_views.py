from http import HTTPStatus

import pytest
from django.urls import reverse

from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory

from .factories import EditingTaskFactory
from .factories import EditorFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def superuser(client):
    user = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(user)
    return user


class TestEditorViews:
    def test_editor_list_view(self, client, superuser):
        EditorFactory(name="Editor One")
        url = reverse("editors:editor_list")
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert "Editor One" in response.content.decode()

    def test_editor_detail_view(self, client, superuser):
        editor = EditorFactory(name="Editor Two", slug="editor-two")
        url = reverse("editors:editor_detail", kwargs={"slug": editor.slug})
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert "Editor Two" in response.content.decode()

    def test_editor_create_view(self, client, superuser):
        url = reverse("editors:editor_create")
        data = {
            "name": "Jane Editor",
            "handle": "jane_ed",
            "slug": "jane-ed",
            "status": "active",
            "editor_type": "freelancer",
            "primary_specialty": "long_form",
            "rate_model": "per_video",
            "base_video_rate": "120.00",
            "base_short_rate": "35.00",
            "hourly_rate": "20.00",
            "monthly_retainer": "0.00",
            "max_active_tasks": 3,
        }
        response = client.post(url, data=data)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse("editors:editor_list")


class TestEditingTaskViews:
    def test_task_list_view(self, client, superuser):
        EditingTaskFactory(title="Video Gameplay Task")
        url = reverse("editors:task_list")
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert "Video Gameplay Task" in response.content.decode()

    def test_task_detail_view(self, client, superuser):
        task = EditingTaskFactory(title="Task Specific Detail")
        url = reverse("editors:task_detail", kwargs={"pk": task.pk})
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert "Task Specific Detail" in response.content.decode()
