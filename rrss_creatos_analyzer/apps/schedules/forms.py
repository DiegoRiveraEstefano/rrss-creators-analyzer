from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Fieldset
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.schedules.models import CreatorSchedulePattern
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException
from rrss_creatos_analyzer.apps.schedules.rrule_utils import build_rrule_from_components
from rrss_creatos_analyzer.apps.schedules.rrule_utils import parse_rrule_components
from rrss_creatos_analyzer.apps.schedules.rrule_utils import validate_rrule


class CreatorSchedulePatternForm(forms.ModelForm):
    recurrence_freq = forms.ChoiceField(
        required=False,
        choices=[
            ("WEEKLY", _("Semanal")),
            ("DAILY", _("Diaria")),
            ("MONTHLY", _("Mensual")),
        ],
        initial="WEEKLY",
        label=_("Frecuencia"),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_recurrence_freq"}),
    )
    recurrence_interval = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        label=_("Repetir cada"),
        widget=forms.NumberInput(
            attrs={"class": "form-control", "id": "id_recurrence_interval", "min": "1"},
        ),
    )
    recurrence_days = forms.MultipleChoiceField(
        choices=[
            ("MO", _("Lunes")),
            ("TU", _("Martes")),
            ("WE", _("Miércoles")),
            ("TH", _("Jueves")),
            ("FR", _("Viernes")),
            ("SA", _("Sábado")),
            ("SU", _("Domingo")),
        ],
        required=False,
        label=_("Días de la semana"),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "btn-check"}),
    )

    class Meta:
        model = CreatorSchedulePattern
        fields = [
            "creator",
            "title",
            "channel",
            "platform",
            "start_time",
            "end_time",
            "planned_duration_minutes",
            "category_or_game",
            "is_mandatory",
            "effective_from",
            "effective_until",
            "is_active",
            "rrule",
            "notes",
        ]
        widgets = {
            "start_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"},
            ),
            "end_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"},
            ),
            "effective_from": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
            ),
            "effective_until": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
            ),
            "rrule": forms.TextInput(
                attrs={
                    "class": "form-control font-monospace",
                    "id": "id_rrule_input",
                    "placeholder": "FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=1",
                },
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rrule"].required = False
        if self.instance and self.instance.pk and self.instance.rrule:
            comp = parse_rrule_components(self.instance.rrule)
            self.fields["recurrence_freq"].initial = comp.get("freq", "WEEKLY")
            self.fields["recurrence_interval"].initial = comp.get("interval", 1)
            self.fields["recurrence_days"].initial = comp.get("byday", [])

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                _("Identificación y Plataforma"),
                Row(
                    Column("creator", css_class="col-md-6 mb-3"),
                    Column("title", css_class="col-md-6 mb-3"),
                ),
                Row(
                    Column("channel", css_class="col-md-6 mb-3"),
                    Column("platform", css_class="col-md-3 mb-3"),
                    Column("category_or_game", css_class="col-md-3 mb-3"),
                ),
            ),
            Fieldset(
                _("Horario y Duración"),
                Row(
                    Column("start_time", css_class="col-md-4 mb-3"),
                    Column("end_time", css_class="col-md-4 mb-3"),
                    Column("planned_duration_minutes", css_class="col-md-4 mb-3"),
                ),
                Row(
                    Column("is_mandatory", css_class="col-md-12 mb-3"),
                ),
            ),
            Fieldset(
                _("Vigencia y Estado"),
                Row(
                    Column("effective_from", css_class="col-md-6 mb-3"),
                    Column("effective_until", css_class="col-md-6 mb-3"),
                ),
                Row(
                    Column("is_active", css_class="col-md-12 mb-3"),
                ),
                "notes",
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        rrule_str = (cleaned_data.get("rrule") or "").strip()
        freq = cleaned_data.get("recurrence_freq", "WEEKLY")
        interval = cleaned_data.get("recurrence_interval") or 1
        days = cleaned_data.get("recurrence_days") or []

        if not rrule_str:
            rrule_str = build_rrule_from_components(
                freq=freq,
                interval=interval,
                byday=days,
            )
            cleaned_data["rrule"] = rrule_str

        try:
            validate_rrule(rrule_str)
        except ValidationError as exc:
            self.add_error("rrule", exc)

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and end_time <= start_time:
            self.add_error(
                "end_time", _("La hora de fin debe ser posterior a la de inicio."),
            )

        eff_from = cleaned_data.get("effective_from")
        eff_until = cleaned_data.get("effective_until")
        if eff_from and eff_until and eff_until < eff_from:
            self.add_error(
                "effective_until",
                _("La fecha de fin de vigencia no puede ser anterior a la de inicio."),
            )

        return cleaned_data


# Alias para retrocompatibilidad
CreatorWeeklyScheduleForm = CreatorSchedulePatternForm


class CreatorScheduleSlotForm(forms.ModelForm):
    class Meta:
        model = CreatorScheduleSlot
        fields = [
            "creator",
            "channel",
            "schedule_pattern",
            "scheduled_date",
            "scheduled_start_time",
            "scheduled_end_time",
            "planned_duration_minutes",
            "planned_hours",
            "title",
            "category_or_game",
            "status",
            "is_mandatory",
            "notes",
        ]
        widgets = {
            "scheduled_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
            ),
            "scheduled_start_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"},
            ),
            "scheduled_end_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"},
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class ScheduleExceptionForm(forms.ModelForm):
    class Meta:
        model = ScheduleException
        fields = [
            "creator",
            "reason_type",
            "title",
            "description",
            "start_date",
            "end_date",
            "document_url",
        ]
        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
            ),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class GenerateSlotsBatchForm(forms.Form):
    creator = forms.ModelChoiceField(
        queryset=Creator.objects.all(),
        required=False,
        empty_label=_("Todos los Creadores Activos"),
        label=_("Creador"),
    )
    start_date = forms.DateField(
        label=_("Fecha de Inicio"),
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        initial=timezone.localdate,
    )
    end_date = forms.DateField(
        label=_("Fecha de Fin"),
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit(
                "submit",
                _("Generar Slots desde Pautas"),
                css_class="btn-primary w-100",
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        if start and end and end < start:
            self.add_error(
                "end_date",
                _("La fecha de fin debe ser posterior o igual a la de inicio."),
            )
        return cleaned_data


class RecalculateMonthlyComplianceForm(forms.Form):
    creator = forms.ModelChoiceField(
        queryset=Creator.objects.all(),
        label=_("Creador"),
    )
    year = forms.IntegerField(
        label=_("Año"),
        min_value=2020,
        max_value=2100,
        initial=lambda: timezone.localdate().year,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    month = forms.IntegerField(
        label=_("Mes"),
        min_value=1,
        max_value=12,
        initial=lambda: timezone.localdate().month,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit(
                "submit",
                _("Calcular y Guardar Auditoría"),
                css_class="btn-primary w-100",
            ),
        )

ComplianceRecalculateForm = RecalculateMonthlyComplianceForm
GenerateSlotsForm = GenerateSlotsBatchForm
