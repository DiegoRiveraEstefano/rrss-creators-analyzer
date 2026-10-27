from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import RoleGroupProfile


@admin.register(RoleGroupProfile)
class RoleGroupProfileAdmin(SimpleHistoryAdmin):
    list_display = ("group", "badge_color", "is_system_role", "updated_at")
    list_filter = ("is_system_role", "badge_color")
    search_fields = ("group__name", "description")
