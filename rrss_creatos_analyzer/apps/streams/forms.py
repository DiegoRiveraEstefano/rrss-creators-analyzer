from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms

from .models import SessionSegment
from .models import StreamingSession


class StreamingSessionForm(forms.ModelForm):
    class Meta:
        model = StreamingSession
        fields = [
            "creator",
            "channel",
            "platform",
            "session_title",
            "game_or_category",
            "streamed_at",
            "ended_at",
            "duration_seconds",
            "peak_viewers",
            "avg_ccv",
            "unique_viewers",
            "live_views_count",
            "chat_messages_count",
            "unique_chatters_count",
            "new_followers",
            "new_subscriptions",
            "gifted_subscriptions",
            "raids_received",
            "ad_revenue",
            "subs_revenue",
            "donations_revenue",
            "bits_or_gifts_revenue",
            "sponsorship_revenue",
            "is_sponsored",
            "stream_url",
            "vod_url",
            "tags",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column("creator", css_class="col-md-4"),
                Column("channel", css_class="col-md-4"),
                Column("platform", css_class="col-md-4"),
            ),
            Row(
                Column("session_title", css_class="col-md-8"),
                Column("game_or_category", css_class="col-md-4"),
            ),
            Row(
                Column("streamed_at", css_class="col-md-4"),
                Column("ended_at", css_class="col-md-4"),
                Column("duration_seconds", css_class="col-md-4"),
            ),
            Row(
                Column("avg_ccv", css_class="col-md-3"),
                Column("peak_viewers", css_class="col-md-3"),
                Column("unique_viewers", css_class="col-md-3"),
                Column("live_views_count", css_class="col-md-3"),
            ),
            Row(
                Column("chat_messages_count", css_class="col-md-4"),
                Column("unique_chatters_count", css_class="col-md-4"),
                Column("new_followers", css_class="col-md-4"),
            ),
            Row(
                Column("new_subscriptions", css_class="col-md-4"),
                Column("gifted_subscriptions", css_class="col-md-4"),
                Column("raids_received", css_class="col-md-4"),
            ),
            Row(
                Column("ad_revenue", css_class="col-md-4"),
                Column("subs_revenue", css_class="col-md-4"),
                Column("donations_revenue", css_class="col-md-4"),
            ),
            Row(
                Column("bits_or_gifts_revenue", css_class="col-md-6"),
                Column("sponsorship_revenue", css_class="col-md-6"),
            ),
            Row(
                Column("stream_url", css_class="col-md-6"),
                Column("vod_url", css_class="col-md-6"),
            ),
            "is_sponsored",
            "tags",
            "notes",
        )


class SessionSegmentForm(forms.ModelForm):
    class Meta:
        model = SessionSegment
        fields = [
            "session",
            "game_or_category",
            "start_offset_seconds",
            "duration_seconds",
            "avg_ccv",
            "peak_viewers",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
