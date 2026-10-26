from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ImportsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rrss_creatos_analyzer.apps.imports"
    verbose_name = _("Importaciones de Datos")
