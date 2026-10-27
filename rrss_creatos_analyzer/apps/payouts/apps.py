from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PayoutsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rrss_creatos_analyzer.apps.payouts"
    verbose_name = _("Liquidaciones y Pagos")
