from decimal import Decimal

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms
from django.utils.translation import gettext_lazy as _

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

    def clean(self):
        cleaned_data = super().clean()
        streamed_at = cleaned_data.get("streamed_at")
        ended_at = cleaned_data.get("ended_at")
        if streamed_at and ended_at and ended_at < streamed_at:
            self.add_error(
                "ended_at",
                _("La fecha/hora de fin no puede ser anterior a la de inicio."),
            )

        avg_ccv = cleaned_data.get("avg_ccv") or 0
        peak_viewers = cleaned_data.get("peak_viewers") or 0
        if avg_ccv > peak_viewers:
            self.add_error(
                "peak_viewers",
                _(
                    "El pico de espectadores debe ser mayor o igual "
                    "a la media de espectadores (CCV).",
                ),
            )

        is_sponsored = cleaned_data.get("is_sponsored")
        sponsorship_revenue = cleaned_data.get("sponsorship_revenue") or Decimal("0.00")
        if is_sponsored and sponsorship_revenue <= Decimal("0.00"):
            self.add_error(
                "sponsorship_revenue",
                _(
                    "Una sesión marcada como patrocinada debe contar con "
                    "un ingreso de patrocinio mayor a cero.",
                ),
            )
        return cleaned_data


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

    def clean(self):
        cleaned_data = super().clean()
        avg_ccv = cleaned_data.get("avg_ccv") or 0
        peak_viewers = cleaned_data.get("peak_viewers") or 0
        if avg_ccv > peak_viewers:
            self.add_error(
                "peak_viewers",
                _("El pico de espectadores debe ser mayor o igual al CCV promedio."),
            )

        session = cleaned_data.get("session")
        start_offset = cleaned_data.get("start_offset_seconds") or 0
        duration = cleaned_data.get("duration_seconds") or 0
        if session and session.duration_seconds > 0:
            if start_offset + duration > session.duration_seconds:
                self.add_error(
                    "duration_seconds",
                    _(
                        "El rango del segmento no puede exceder "
                        "la duración total del stream.",
                    ),
                )
        return cleaned_data
