from __future__ import annotations

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Column
from crispy_forms.layout import Fieldset
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rrss_creatos_analyzer.apps.core.choices import CreatorStatus
from rrss_creatos_analyzer.apps.core.choices import PlatformType

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator
from .models import CreatorPersonalInfo


class CreatorForm(forms.ModelForm):
    # Campos opcionales para Onboarding Ágil del Canal Principal
    link_initial_channel = forms.BooleanField(
        label=_("Vincular canal principal de inmediato"),
        required=False,
        initial=True,
        help_text=_("Permite registrar el canal oficial del creador en el mismo paso."),
    )
    initial_platform = forms.ChoiceField(
        label=_("Plataforma Principal"),
        choices=PlatformType.choices,
        required=False,
        initial=PlatformType.TWITCH,
    )
    initial_channel_id = forms.CharField(
        label=_("ID o Handle en la Red"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ej: ibai, auronplay, elrubius"}),
    )
    initial_channel_url = forms.URLField(
        label=_("URL del Canal"),
        max_length=500,
        required=False,
        widget=forms.URLInput(
            attrs={
                "placeholder": "https://twitch.tv/usuario o https://youtube.com/@usuario"
            }
        ),
    )
    initial_followers_count = forms.IntegerField(
        label=_("Seguidores Iniciales"),
        required=False,
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={"placeholder": "0"}),
    )

    class Meta:
        model = Creator
        fields = [
            "display_name",
            "handle",
            "slug",
            "manager",
            "user",
            "tier",
            "status",
            "main_category",
            "language_code",
            "joined_company_at",
            "left_company_at",
            "avatar_url",
            "banner_url",
            "bio",
            "internal_notes",
            "tags",
        ]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Biografía o descripción artística del talento...",
                }
            ),
            "internal_notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Notas internas privadas para el equipo de managers...",
                }
            ),
            "joined_company_at": forms.DateInput(attrs={"type": "date"}),
            "left_company_at": forms.DateInput(attrs={"type": "date"}),
            "avatar_url": forms.URLInput(
                attrs={"placeholder": "https://... imagen de perfil cuadrada"}
            ),
            "banner_url": forms.URLInput(
                attrs={"placeholder": "https://... cabecera horizontal (16:9 o 3:1)"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["slug"].help_text = _(
            "Se autogenera del handle si se deja en blanco."
        )

        # Si ya estamos editando un creador existente, no mostrar los campos de canal inicial
        is_edit = self.instance and self.instance.pk
        if is_edit:
            self.fields.pop("link_initial_channel", None)
            self.fields.pop("initial_platform", None)
            self.fields.pop("initial_channel_id", None)
            self.fields.pop("initial_channel_url", None)
            self.fields.pop("initial_followers_count", None)

        self.helper = FormHelper()
        self.helper.form_tag = False

        layout_elements = [
            Fieldset(
                _("Identidad Artística y Pública"),
                Row(
                    Column("display_name", css_class="col-md-4"),
                    Column("handle", css_class="col-md-4"),
                    Column("slug", css_class="col-md-4"),
                ),
                Row(
                    Column("main_category", css_class="col-md-4"),
                    Column("language_code", css_class="col-md-4"),
                    Column("avatar_url", css_class="col-md-4"),
                ),
                Row(
                    Column("banner_url", css_class="col-md-12"),
                ),
                "bio",
            ),
            Fieldset(
                _("Gestión Interna y Compañía"),
                Row(
                    Column("tier", css_class="col-md-3"),
                    Column("status", css_class="col-md-3"),
                    Column("manager", css_class="col-md-3"),
                    Column("user", css_class="col-md-3"),
                ),
                Row(
                    Column("joined_company_at", css_class="col-md-6"),
                    Column("left_company_at", css_class="col-md-6"),
                ),
                "tags",
                "internal_notes",
            ),
        ]

        if not is_edit:
            layout_elements.append(
                Fieldset(
                    _("Onboarding Ágil: Canal Principal de Transmisión / Video"),
                    HTML(
                        '<div class="alert alert-info py-2 px-3 small mb-3">'
                        '<i class="bi bi-lightning-charge-fill me-1"></i> '
                        "<strong>Flujo Rápido:</strong> Puedes registrar de una vez su cuenta de Twitch, YouTube o Kick. "
                        "Se configurará automáticamente como su canal principal."
                        "</div>",
                    ),
                    "link_initial_channel",
                    Row(
                        Column("initial_platform", css_class="col-md-3"),
                        Column("initial_channel_id", css_class="col-md-3"),
                        Column("initial_channel_url", css_class="col-md-4"),
                        Column("initial_followers_count", css_class="col-md-2"),
                    ),
                ),
            )

        self.helper.layout = Layout(*layout_elements)

    def clean(self):
        cleaned_data = super().clean()
        handle = cleaned_data.get("handle")
        if handle and handle.startswith("@"):
            cleaned_data["handle"] = handle.lstrip("@").strip()
        return cleaned_data


class CreatorPersonalInfoForm(forms.ModelForm):
    class Meta:
        model = CreatorPersonalInfo
        fields = [
            "legal_full_name",
            "tax_id",
            "contact_email",
            "phone_number",
            "birth_date",
            "country_code",
            "city",
            "address",
            "postal_code",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "bank_name",
            "bank_account_holder",
            "bank_account_iban",
            "bank_swift_bic",
            "notes",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "Notas de compliance, régimen fiscal o acuerdos particulares...",
                }
            ),
            "legal_full_name": forms.TextInput(
                attrs={
                    "placeholder": "Nombre y apellidos según documento oficial de identidad"
                }
            ),
            "tax_id": forms.TextInput(
                attrs={"placeholder": "DNI / CIF / RFC / RUT / Social Security"}
            ),
            "country_code": forms.TextInput(
                attrs={"placeholder": "ES, MX, AR, US, CO, CL..."}
            ),
            "bank_account_iban": forms.TextInput(
                attrs={"placeholder": "IBAN, CLABE interbancaria o Número de cuenta"}
            ),
            "bank_swift_bic": forms.TextInput(
                attrs={"placeholder": "Código SWIFT para giros internacionales"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                _("1. Identificación Legal y Contacto Directo"),
                Row(
                    Column("legal_full_name", css_class="col-md-6"),
                    Column("tax_id", css_class="col-md-6"),
                ),
                Row(
                    Column("contact_email", css_class="col-md-4"),
                    Column("phone_number", css_class="col-md-4"),
                    Column("birth_date", css_class="col-md-4"),
                ),
            ),
            Fieldset(
                _("2. Domicilio y Residencia Fiscal"),
                Row(
                    Column("country_code", css_class="col-md-2"),
                    Column("city", css_class="col-md-4"),
                    Column("postal_code", css_class="col-md-2"),
                    Column("address", css_class="col-md-4"),
                ),
            ),
            Fieldset(
                _("3. Contacto de Emergencia"),
                Row(
                    Column("emergency_contact_name", css_class="col-md-4"),
                    Column("emergency_contact_phone", css_class="col-md-4"),
                    Column("emergency_contact_relationship", css_class="col-md-4"),
                ),
            ),
            Fieldset(
                _("4. Datos Bancarios para Liquidación de Ingresos (Payouts)"),
                Row(
                    Column("bank_name", css_class="col-md-6"),
                    Column("bank_account_holder", css_class="col-md-6"),
                ),
                Row(
                    Column("bank_account_iban", css_class="col-md-8"),
                    Column("bank_swift_bic", css_class="col-md-4"),
                ),
                "notes",
            ),
        )


class CreatorStatusChangeForm(forms.Form):
    status = forms.ChoiceField(
        choices=CreatorStatus.choices,
        label=_("Nuevo Estado Operativo"),
        widget=forms.Select(attrs={"class": "form-select fw-semibold"}),
    )
    reason = forms.CharField(
        label=_("Motivo / Justificación"),
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ej: Renovación contractual, período de vacaciones, suspensión por TOS...",
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = [
            "creator",
            "platform",
            "platform_channel_id",
            "handle",
            "channel_name",
            "channel_url",
            "status",
            "is_primary",
            "is_verified",
            "is_monetized",
            "is_live",
            "followers_count",
            "subscribers_count",
            "paid_subscribers_count",
            "total_views_count",
            "sync_enabled",
        ]
        widgets = {
            "channel_url": forms.URLInput(
                attrs={
                    "placeholder": "https://twitch.tv/usuario o https://youtube.com/@canal"
                }
            ),
            "platform_channel_id": forms.TextInput(
                attrs={"placeholder": "ID en la API o handle oficial"}
            ),
            "channel_name": forms.TextInput(
                attrs={"placeholder": "Nombre visible del canal"}
            ),
            "handle": forms.TextInput(attrs={"placeholder": "Handle público (@)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                _("Configuración del Canal y Plataforma"),
                Row(
                    Column("creator", css_class="col-md-6"),
                    Column("platform", css_class="col-md-6"),
                ),
                Row(
                    Column("platform_channel_id", css_class="col-md-4"),
                    Column("channel_name", css_class="col-md-4"),
                    Column("handle", css_class="col-md-4"),
                ),
                Row(
                    Column("channel_url", css_class="col-md-12"),
                ),
            ),
            Fieldset(
                _("Banderas Operativas y Estado"),
                Row(
                    Column("status", css_class="col-md-3"),
                    Column("is_primary", css_class="col-md-2 mt-4 pt-1"),
                    Column("is_verified", css_class="col-md-2 mt-4 pt-1"),
                    Column("is_monetized", css_class="col-md-2 mt-4 pt-1"),
                    Column("sync_enabled", css_class="col-md-3 mt-4 pt-1"),
                ),
            ),
            Fieldset(
                _("Métricas Actuales de Audiencia"),
                Row(
                    Column("followers_count", css_class="col-md-3"),
                    Column("subscribers_count", css_class="col-md-3"),
                    Column("paid_subscribers_count", css_class="col-md-3"),
                    Column("total_views_count", css_class="col-md-3"),
                ),
            ),
        )

    def clean_handle(self):
        handle = self.cleaned_data.get("handle", "")
        if handle and handle.startswith("@"):
            return handle.lstrip("@").strip()
        return handle


class ChannelSnapshotForm(forms.ModelForm):
    class Meta:
        model = ChannelSnapshot
        fields = [
            "channel",
            "snapshot_date",
            "followers_count",
            "followers_delta",
            "subscribers_count",
            "subscribers_delta",
            "paid_subscribers_count",
            "total_views_count",
            "views_delta",
        ]
        widgets = {
            "snapshot_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get("snapshot_date"):
            self.initial["snapshot_date"] = timezone.localdate()

        self.fields["followers_delta"].required = False
        self.fields["followers_delta"].help_text = _(
            "Se calcula automáticamente respecto al snapshot anterior si se deja en 0."
        )
        self.fields["subscribers_delta"].required = False
        self.fields["views_delta"].required = False

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column("channel", css_class="col-md-8"),
                Column("snapshot_date", css_class="col-md-4"),
            ),
            Fieldset(
                _("Métricas de Audiencia y Variación Delta"),
                Row(
                    Column("followers_count", css_class="col-md-6"),
                    Column("followers_delta", css_class="col-md-6"),
                ),
                Row(
                    Column("subscribers_count", css_class="col-md-4"),
                    Column("subscribers_delta", css_class="col-md-4"),
                    Column("paid_subscribers_count", css_class="col-md-4"),
                ),
                Row(
                    Column("total_views_count", css_class="col-md-6"),
                    Column("views_delta", css_class="col-md-6"),
                ),
            ),
        )
