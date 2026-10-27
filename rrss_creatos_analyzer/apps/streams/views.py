from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from rrss_creatos_analyzer.apps.core.mixins import CrudContextMixin

from .filters import SessionSegmentFilter
from .filters import StreamingSessionFilter
from .forms import SessionSegmentForm
from .forms import StreamingSessionForm
from .models import SessionSegment
from .models import StreamingSession
from .selectors import SessionSegmentSelector
from .selectors import StreamingSessionSelector
from .services import SessionSegmentService
from .services import StreamingSessionService
from .tables import SessionSegmentTable
from .tables import StreamingSessionTable


# ==== STREAMING SESSION CRUD ====
class StreamingSessionListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = StreamingSession
    permission_required = "streams.view_streamingsession"
    table_class = StreamingSessionTable
    filterset_class = StreamingSessionFilter
    template_name = "streams/session_list.html"
    paginate_by = 25
    page_title = "Sesiones de Streaming en Vivo"
    page_subtitle = "Registro de transmisiones, métricas de audiencia e ingresos"
    create_url_name = "streams:session_create"

    def get_queryset(self):
        return StreamingSessionSelector.get_visible_queryset(user=self.request.user)


class StreamingSessionDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = StreamingSession
    permission_required = "streams.view_streamingsession"
    template_name = "streams/session_detail.html"
    page_title = "Detalle de Sesión de Streaming"
    list_url_name = "streams:session_list"
    update_url_name = "streams:session_update"
    delete_url_name = "streams:session_delete"

    def get_queryset(self):
        return StreamingSessionSelector.get_visible_queryset(user=self.request.user)


class StreamingSessionCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = StreamingSession
    permission_required = "streams.add_streamingsession"
    form_class = StreamingSessionForm
    template_name = "streams/session_form.html"
    success_url = reverse_lazy("streams:session_list")
    page_title = "Registrar Sesión de Streaming"
    list_url_name = "streams:session_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        self.object = StreamingSessionService.save_session(tags=tags, **data)
        messages.success(self.request, "Sesión de streaming registrada exitosamente.")
        return redirect(self.success_url)


class StreamingSessionUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = StreamingSession
    permission_required = "streams.change_streamingsession"
    form_class = StreamingSessionForm
    template_name = "streams/session_form.html"
    success_url = reverse_lazy("streams:session_list")
    page_title = "Editar Sesión de Streaming"
    list_url_name = "streams:session_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        self.object = StreamingSessionService.save_session(
            instance=self.get_object(),
            tags=tags,
            **data,
        )
        messages.success(self.request, "Sesión de streaming actualizada exitosamente.")
        return redirect(self.success_url)


class StreamingSessionDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = StreamingSession
    permission_required = "streams.delete_streamingsession"
    template_name = "streams/session_confirm_delete.html"
    success_url = reverse_lazy("streams:session_list")
    list_url_name = "streams:session_list"

    def form_valid(self, form):
        StreamingSessionService.delete_session(instance=self.get_object())
        messages.success(self.request, "Sesión eliminada.")
        return redirect(self.success_url)


# ==== SESSION SEGMENT CRUD ====
class SessionSegmentListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = SessionSegment
    permission_required = "streams.view_sessionsegment"
    table_class = SessionSegmentTable
    filterset_class = SessionSegmentFilter
    template_name = "streams/segment_list.html"
    paginate_by = 25
    page_title = "Segmentos de Categoría por Stream"
    create_url_name = "streams:segment_create"

    def get_queryset(self):
        return SessionSegmentSelector.get_visible_queryset(user=self.request.user)


class SessionSegmentDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = SessionSegment
    permission_required = "streams.view_sessionsegment"
    template_name = "streams/segment_detail.html"
    page_title = "Detalle de Segmento"
    list_url_name = "streams:segment_list"
    update_url_name = "streams:segment_update"
    delete_url_name = "streams:segment_delete"

    def get_queryset(self):
        return SessionSegmentSelector.get_visible_queryset(user=self.request.user)


class SessionSegmentCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = SessionSegment
    permission_required = "streams.add_sessionsegment"
    form_class = SessionSegmentForm
    template_name = "streams/segment_form.html"
    success_url = reverse_lazy("streams:segment_list")
    page_title = "Registrar Segmento de Stream"
    list_url_name = "streams:segment_list"

    def form_valid(self, form):
        self.object = SessionSegmentService.save_segment(**form.cleaned_data)
        messages.success(self.request, "Segmento creado exitosamente.")
        return redirect(self.success_url)


class SessionSegmentUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = SessionSegment
    permission_required = "streams.change_sessionsegment"
    form_class = SessionSegmentForm
    template_name = "streams/segment_form.html"
    success_url = reverse_lazy("streams:segment_list")
    page_title = "Editar Segmento de Stream"
    list_url_name = "streams:segment_list"

    def form_valid(self, form):
        self.object = SessionSegmentService.save_segment(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Segmento actualizado exitosamente.")
        return redirect(self.success_url)


class SessionSegmentDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = SessionSegment
    permission_required = "streams.delete_sessionsegment"
    template_name = "streams/segment_confirm_delete.html"
    success_url = reverse_lazy("streams:segment_list")
    list_url_name = "streams:segment_list"

    def form_valid(self, form):
        SessionSegmentService.delete_segment(instance=self.get_object())
        messages.success(self.request, "Segmento eliminado.")
        return redirect(self.success_url)
