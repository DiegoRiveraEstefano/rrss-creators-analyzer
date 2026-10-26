from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rrss_creatos_analyzer.apps.analytics"
    verbose_name = _("Analítica y Reportes Cacheados")
