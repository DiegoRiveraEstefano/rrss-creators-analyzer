from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StreamsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rrss_creatos_analyzer.apps.streams"
    verbose_name = _("Sesiones de Streaming")
