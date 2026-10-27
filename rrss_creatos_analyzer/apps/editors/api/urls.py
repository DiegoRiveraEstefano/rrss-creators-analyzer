from rest_framework.routers import DefaultRouter

from .views import EditingTaskViewSet
from .views import EditorAssignmentViewSet
from .views import EditorViewSet
from .views import TaskRevisionViewSet

router = DefaultRouter()
router.register("editors", EditorViewSet, basename="editor")
router.register("assignments", EditorAssignmentViewSet, basename="editor-assignment")
router.register("tasks", EditingTaskViewSet, basename="editing-task")
router.register("revisions", TaskRevisionViewSet, basename="task-revision")

urlpatterns = router.urls
