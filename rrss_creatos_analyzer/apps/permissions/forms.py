from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.models import Permission

from .models import RoleGroupProfile


class RoleGroupProfileForm(forms.ModelForm):
    group_name = forms.CharField(label="Nombre del Grupo de Django", max_length=150)
    permissions = forms.ModelMultipleChoiceField(
        label="Permisos Asignados al Grupo",
        queryset=Permission.objects.select_related("content_type").all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": "12"}),
    )

    class Meta:
        model = RoleGroupProfile
        fields = [
            "group_name",
            "description",
            "badge_color",
            "is_system_role",
            "permissions",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["group_name"].initial = self.instance.group.name
            self.fields["permissions"].initial = self.instance.group.permissions.all()
        self.helper = FormHelper()
        self.helper.form_tag = False
