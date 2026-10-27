from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CampaignsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rrss_creatos_analyzer.apps.campaigns"
    verbose_name = _("Campañas y Patrocinios")
