---
trigger: always_on
---

# RRSS Creators Analyzer: Views & Controllers Guidelines

## Core Principles

1. **Thin Class-Based Views (CBVs) with Native Django Permissions**:
   - Views act strictly as HTTP orchestrators.
   - Responsibilities: validate authentication (`LoginRequiredMixin`) and native Django permissions (`PermissionRequiredMixin`), apply filters (`FilterView`), render tables (`SingleTableMixin`), call `Service` or `Selector`, and return response.
2. **Leverage `django-tables2` and `django-filter`**:
   - List views MUST combine `SingleTableMixin` (from `django_tables2`) and `FilterView` (from `django_filters.views`) rather than implementing manual sorting, pagination, or `request.GET` filtering.
3. **Zero Business Logic in Views**:
   - Never write database mutations directly in `form_valid()` or `post()`.
   - Always delegate mutations to the corresponding `Service` classmethod.

## Canonical CBV Pattern

```python
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .filters import StreamingSessionFilter
from .forms import StreamingSessionForm
from .models import StreamingSession
from .selectors import StreamingSessionSelector
from .services import StreamingSessionService
from .tables import StreamingSessionTable


class StreamingSessionListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SingleTableMixin,
    FilterView,
):
    model = StreamingSession
    permission_required = "streams.view_streamingsession"
    table_class = StreamingSessionTable
    filterset_class = StreamingSessionFilter
    template_name = "streams/session_list.html"
    paginate_by = 25

    def get_queryset(self):
        return StreamingSessionSelector.get_visible_queryset(user=self.request.user)


class StreamingSessionCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    model = StreamingSession
    permission_required = "streams.add_streamingsession"
    form_class = StreamingSessionForm
    template_name = "streams/session_form.html"
    success_url = reverse_lazy("streams:list")

    def form_valid(self, form):
        self.object = StreamingSessionService.record_session(
            creator_id=form.cleaned_data["creator"].id,
            channel_id=form.cleaned_data["channel"].id
            if form.cleaned_data.get("channel")
            else None,
            session_title=form.cleaned_data["session_title"],
            game_or_category=form.cleaned_data["game_or_category"],
            platform=form.cleaned_data["platform"],
            streamed_at=form.cleaned_data["streamed_at"],
            duration_seconds=form.cleaned_data["duration_seconds"],
            peak_viewers=form.cleaned_data["peak_viewers"],
            avg_ccv=form.cleaned_data["avg_ccv"],
            ad_revenue=form.cleaned_data["ad_revenue"],
            subs_revenue=form.cleaned_data["subs_revenue"],
            donations_revenue=form.cleaned_data["donations_revenue"],
        )
        messages.success(self.request, "Sesión de streaming registrada exitosamente.")
        return redirect(self.success_url)
```
