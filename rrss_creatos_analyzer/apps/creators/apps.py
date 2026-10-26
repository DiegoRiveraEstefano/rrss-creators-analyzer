from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CreatorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rrss_creatos_analyzer.apps.creators"
    verbose_name = _("Creadores y Canales")
