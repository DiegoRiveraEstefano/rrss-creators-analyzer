from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Fieldset
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms
from django.utils.translation import gettext_lazy as _

from rrss_creatos_analyzer.apps.core.choices import CreatorStatus

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator
from .models import CreatorPersonalInfo


class CreatorForm(forms.ModelForm):
    class Meta:
        model = Creator
        fields = [
            "display_name",
            "handle",
            "slug",
            "user",
            "manager",
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
            "bio": forms.Textarea(attrs={"rows": 3}),
            "internal_notes": forms.Textarea(attrs={"rows": 3}),
            "joined_company_at": forms.DateInput(attrs={"type": "date"}),
            "left_company_at": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
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
        )


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
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                _("Datos de Identidad y Contacto"),
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
                _("Dirección y Residencia Fiscal"),
                Row(
                    Column("country_code", css_class="col-md-3"),
                    Column("city", css_class="col-md-3"),
                    Column("postal_code", css_class="col-md-2"),
                    Column("address", css_class="col-md-4"),
                ),
            ),
            Fieldset(
                _("Contacto de Emergencia"),
                Row(
                    Column("emergency_contact_name", css_class="col-md-4"),
                    Column("emergency_contact_phone", css_class="col-md-4"),
                    Column("emergency_contact_relationship", css_class="col-md-4"),
                ),
            ),
            Fieldset(
                _("Información Bancaria para Liquidaciones"),
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
    status = (
        forms.ChoiceFilter
        if False
        else forms.ChoiceField(
            choices=CreatorStatus.choices,
            label=_("Nuevo Estado"),
        )
    )
    reason = forms.CharField(
        label=_("Motivo / Justificación"),
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Ej: Renovación de contrato, pausa solicitada..."},
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
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
            Row(
                Column("status", css_class="col-md-3"),
                Column("is_primary", css_class="col-md-2 mt-4"),
                Column("is_verified", css_class="col-md-2 mt-4"),
                Column("is_monetized", css_class="col-md-2 mt-4"),
                Column("sync_enabled", css_class="col-md-3 mt-4"),
            ),
            Row(
                Column("followers_count", css_class="col-md-3"),
                Column("subscribers_count", css_class="col-md-3"),
                Column("paid_subscribers_count", css_class="col-md-3"),
                Column("total_views_count", css_class="col-md-3"),
            ),
        )


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
        self.helper = FormHelper()
        self.helper.form_tag = False
