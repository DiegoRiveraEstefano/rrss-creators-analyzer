from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms
from django.utils.translation import gettext_lazy as _

from rrss_creatos_analyzer.apps.core.choices import PublicationStatus
from rrss_creatos_analyzer.apps.core.choices import VideoStatus

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

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        if status == VideoStatus.PUBLISHED:
            if (
                not self.instance.pk
                or not self.instance.publications.filter(
                    status=PublicationStatus.PUBLISHED,
                ).exists()
            ):
                self.add_error(
                    "status",
                    _(
                        "Un video no puede marcarse en estado 'published' "
                        "a menos que exista al menos una publicación vinculada "
                        "en estado 'published'.",
                    ),
                )
        return cleaned_data


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

    def clean(self):
        cleaned_data = super().clean()
        source_video = cleaned_data.get("source_video")
        target_video = cleaned_data.get("target_video")
        target_session = cleaned_data.get("target_session")

        if not target_video and not target_session:
            self.add_error(
                None,
                _(
                    "Debe seleccionar al menos un Video Relacionado "
                    "o una Sesión de Streaming de destino.",
                ),
            )

        if source_video and target_video and source_video == target_video:
            self.add_error(
                "target_video",
                _("Un video no puede relacionarse consigo mismo."),
            )

        start = cleaned_data.get("timestamp_start_seconds")
        end = cleaned_data.get("timestamp_end_seconds")
        if start is not None and end is not None and start > end:
            self.add_error(
                "timestamp_end_seconds",
                _("El segundo de fin no puede ser menor al segundo de inicio."),
            )
        return cleaned_data
