from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms

from .models import Video
from .models import VideoPublication
from .models import VideoRelation


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            "creator",
            "assigned_editor",
            "title",
            "internal_code",
            "internal_name",
            "category",
            "content_format",
            "status",
            "duration_seconds",
            "production_cost",
            "editing_cost",
            "thumbnail_cost",
            "target_release_date",
            "master_asset_url",
            "tags",
            "description",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column("creator", css_class="col-md-6"),
                Column("assigned_editor", css_class="col-md-6"),
            ),
            Row(
                Column("title", css_class="col-md-6"),
                Column("internal_code", css_class="col-md-3"),
                Column("internal_name", css_class="col-md-3"),
            ),
            Row(
                Column("category", css_class="col-md-3"),
                Column("content_format", css_class="col-md-3"),
                Column("status", css_class="col-md-3"),
                Column("duration_seconds", css_class="col-md-3"),
            ),
            Row(
                Column("production_cost", css_class="col-md-4"),
                Column("editing_cost", css_class="col-md-4"),
                Column("thumbnail_cost", css_class="col-md-4"),
            ),
            Row(
                Column("target_release_date", css_class="col-md-4"),
                Column("master_asset_url", css_class="col-md-8"),
            ),
            "tags",
            "description",
        )


class VideoPublicationForm(forms.ModelForm):
    class Meta:
        model = VideoPublication
        fields = [
            "video",
            "creator",
            "channel",
            "platform",
            "publication_type",
            "status",
            "published_at",
            "platform_post_id",
            "published_title",
            "post_url",
            "thumbnail_url",
            "views_count",
            "unique_viewers_count",
            "impressions_count",
            "click_through_rate",
            "likes_count",
            "dislikes_count",
            "comments_count",
            "shares_count",
            "saves_count",
            "watch_time_hours",
            "avg_view_duration_seconds",
            "retention_rate_pct",
            "engagement_rate",
            "ad_revenue",
            "sponsorship_revenue",
            "estimated_revenue",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class VideoRelationForm(forms.ModelForm):
    class Meta:
        model = VideoRelation
        fields = [
            "source_video",
            "relation_type",
            "target_video",
            "target_session",
            "timestamp_start_seconds",
            "timestamp_end_seconds",
            "description",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
