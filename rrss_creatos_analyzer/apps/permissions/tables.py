import django_tables2 as tables

from .models import RoleGroupProfile


class RoleGroupProfileTable(tables.Table):
    group = tables.Column(linkify=True, verbose_name="Grupo / Rol")
    actions = tables.TemplateColumn(
        template_name="permissions/includes/role_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = RoleGroupProfile
        template_name = "django_tables2/bootstrap5.html"
        fields = ("group", "description", "badge_color", "is_system_role", "updated_at")
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
