from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EditorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rrss_creatos_analyzer.apps.editors"
    verbose_name = _("Editores y Postproducción")
