from django.urls import path

from .views import CreatorTeamAssignmentCreateView
from .views import CreatorTeamAssignmentDeleteView
from .views import CreatorTeamAssignmentDetailView
from .views import CreatorTeamAssignmentListView
from .views import CreatorTeamAssignmentUpdateView
from .views import MemberInvitationCreateView
from .views import MemberInvitationDeleteView
from .views import MemberInvitationDetailView
from .views import MemberInvitationListView
from .views import MemberInvitationUpdateView

app_name = "members"

urlpatterns = [
    path("", MemberInvitationListView.as_view(), name="invitation_list"),
    path("create/", MemberInvitationCreateView.as_view(), name="invitation_create"),
    path("<int:pk>/", MemberInvitationDetailView.as_view(), name="invitation_detail"),
    path(
        "<int:pk>/edit/",
        MemberInvitationUpdateView.as_view(),
        name="invitation_update",
    ),
    path(
        "<int:pk>/delete/",
        MemberInvitationDeleteView.as_view(),
        name="invitation_delete",
    ),
    # Team Assignments
    path(
        "assignments/",
        CreatorTeamAssignmentListView.as_view(),
        name="assignment_list",
    ),
    path(
        "assignments/create/",
        CreatorTeamAssignmentCreateView.as_view(),
        name="assignment_create",
    ),
    path(
        "assignments/<int:pk>/",
        CreatorTeamAssignmentDetailView.as_view(),
        name="assignment_detail",
    ),
    path(
        "assignments/<int:pk>/edit/",
        CreatorTeamAssignmentUpdateView.as_view(),
        name="assignment_update",
    ),
    path(
        "assignments/<int:pk>/delete/",
        CreatorTeamAssignmentDeleteView.as_view(),
        name="assignment_delete",
    ),
]
