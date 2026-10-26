from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import CreatorTeamAssignment
from .models import MemberInvitation


@admin.register(MemberInvitation)
class MemberInvitationAdmin(SimpleHistoryAdmin):
    list_display = (
        "email",
        "full_name",
        "target_group",
        "status",
        "invited_by",
        "expires_at",
        "created_at",
    )
    list_filter = ("status", "target_group")
    search_fields = ("email", "full_name", "token")


@admin.register(CreatorTeamAssignment)
class CreatorTeamAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "creator",
        "user",
        "group",
        "responsibility",
        "is_primary",
        "created_at",
    )
    list_filter = ("responsibility", "is_primary", "group")
    search_fields = ("creator__display_name", "user__username", "user__email")
