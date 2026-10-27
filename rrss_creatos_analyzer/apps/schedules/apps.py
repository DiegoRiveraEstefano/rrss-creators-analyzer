from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SchedulesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rrss_creatos_analyzer.apps.schedules"
    verbose_name = _("Horarios y Cumplimiento")
