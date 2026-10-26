from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PermissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rrss_creatos_analyzer.apps.permissions"
    verbose_name = _("Permisos y Grupos de Acceso")
