from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator


class CreatorForm(forms.ModelForm):
    class Meta:
        model = Creator
        fields = [
            "display_name",
            "handle",
            "slug",
            "user",
            "manager",
            "primary_platform",
            "tier",
            "status",
            "main_category",
            "legal_full_name",
            "contact_email",
            "country_code",
            "language_code",
            "joined_company_at",
            "left_company_at",
            "avatar_url",
            "banner_url",
            "bio",
            "internal_notes",
            "tags",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column("display_name", css_class="col-md-4"),
                Column("handle", css_class="col-md-4"),
                Column("slug", css_class="col-md-4"),
            ),
            Row(
                Column("primary_platform", css_class="col-md-4"),
                Column("tier", css_class="col-md-4"),
                Column("status", css_class="col-md-4"),
            ),
            Row(
                Column("user", css_class="col-md-4"),
                Column("manager", css_class="col-md-4"),
                Column("main_category", css_class="col-md-4"),
            ),
            Row(
                Column("legal_full_name", css_class="col-md-6"),
                Column("contact_email", css_class="col-md-6"),
            ),
            Row(
                Column("country_code", css_class="col-md-3"),
                Column("language_code", css_class="col-md-3"),
                Column("joined_company_at", css_class="col-md-3"),
                Column("left_company_at", css_class="col-md-3"),
            ),
            Row(
                Column("avatar_url", css_class="col-md-6"),
                Column("banner_url", css_class="col-md-6"),
            ),
            "tags",
            "bio",
            "internal_notes",
        )


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
