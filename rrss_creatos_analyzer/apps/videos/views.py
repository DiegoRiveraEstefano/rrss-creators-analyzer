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

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.core.mixins import CrudContextMixin

from .filters import VideoFilter
from .filters import VideoPublicationFilter
from .filters import VideoRelationFilter
from .forms import VideoForm
from .forms import VideoPublicationForm
from .forms import VideoRelationForm
from .models import Video
from .models import VideoPublication
from .models import VideoRelation
from .selectors import VideoPublicationSelector
from .selectors import VideoRelationSelector
from .selectors import VideoSelector
from .services import VideoPublicationService
from .services import VideoRelationService
from .services import VideoService
from .tables import VideoPublicationTable
from .tables import VideoRelationTable
from .tables import VideoTable


# ==== VIDEO CRUD ====
class VideoListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = Video
    permission_required = "videos.view_video"
    table_class = VideoTable
    filterset_class = VideoFilter
    template_name = "videos/video_list.html"
    paginate_by = 25
    page_title = "Activos de Video (Catálogo Maestro)"
    page_subtitle = "Control de producción, costos y estado editorial"
    create_url_name = "videos:video_create"

    def get_queryset(self):
        return VideoSelector.get_visible_queryset(user=self.request.user)


class VideoDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = Video
    permission_required = "videos.view_video"
    template_name = "videos/video_detail.html"
    page_title = "Detalle de Video"
    list_url_name = "videos:video_list"
    update_url_name = "videos:video_update"
    delete_url_name = "videos:video_delete"

    def get_queryset(self):
        return VideoSelector.get_visible_queryset(user=self.request.user)


class VideoCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = Video
    permission_required = "videos.add_video"
    form_class = VideoForm
    template_name = "videos/video_form.html"
    success_url = reverse_lazy("videos:video_list")
    page_title = "Nuevo Video Maestro"
    list_url_name = "videos:video_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        self.object = VideoService.save_video(tags=tags, **data)
        messages.success(self.request, "Video registrado exitosamente.")
        return redirect(self.success_url)


class VideoUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = Video
    permission_required = "videos.change_video"
    form_class = VideoForm
    template_name = "videos/video_form.html"
    success_url = reverse_lazy("videos:video_list")
    page_title = "Editar Video Maestro"
    list_url_name = "videos:video_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        self.object = VideoService.save_video(
            instance=self.get_object(),
            tags=tags,
            **data,
        )
        messages.success(self.request, "Video actualizado exitosamente.")
        return redirect(self.success_url)


class VideoDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = Video
    permission_required = "videos.delete_video"
    template_name = "videos/video_confirm_delete.html"
    success_url = reverse_lazy("videos:video_list")
    list_url_name = "videos:video_list"

    def form_valid(self, form):
        VideoService.delete_video(instance=self.get_object())
        messages.success(self.request, "Video eliminado.")
        return redirect(self.success_url)


# ==== VIDEO PUBLICATION CRUD ====
class VideoPublicationListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = VideoPublication
    permission_required = "videos.view_videopublication"
    table_class = VideoPublicationTable
    filterset_class = VideoPublicationFilter
    template_name = "videos/publication_list.html"
    paginate_by = 25
    page_title = "Publicaciones por Plataforma"
    page_subtitle = "Rendimiento en YouTube, TikTok, Reels, Shorts y VODs"
    create_url_name = "videos:publication_create"

    def get_queryset(self):
        return VideoPublicationSelector.get_visible_queryset(user=self.request.user)


class VideoPublicationDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = VideoPublication
    permission_required = "videos.view_videopublication"
    template_name = "videos/publication_detail.html"
    page_title = "Detalle de Publicación"
    list_url_name = "videos:publication_list"
    update_url_name = "videos:publication_update"
    delete_url_name = "videos:publication_delete"

    def get_queryset(self):
        return VideoPublicationSelector.get_visible_queryset(user=self.request.user)


class VideoPublicationCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = VideoPublication
    permission_required = "videos.add_videopublication"
    form_class = VideoPublicationForm
    template_name = "videos/publication_form.html"
    success_url = reverse_lazy("videos:publication_list")
    page_title = "Registrar Publicación de Video"
    list_url_name = "videos:publication_list"

    def form_valid(self, form):
        self.object = VideoPublicationService.save_publication(**form.cleaned_data)
        messages.success(self.request, "Publicación creada exitosamente.")
        return redirect(self.success_url)


class VideoPublicationUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = VideoPublication
    permission_required = "videos.change_videopublication"
    form_class = VideoPublicationForm
    template_name = "videos/publication_form.html"
    success_url = reverse_lazy("videos:publication_list")
    page_title = "Editar Publicación de Video"
    list_url_name = "videos:publication_list"

    def form_valid(self, form):
        self.object = VideoPublicationService.save_publication(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Publicación actualizada exitosamente.")
        return redirect(self.success_url)


class VideoPublicationDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = VideoPublication
    permission_required = "videos.delete_videopublication"
    template_name = "videos/publication_confirm_delete.html"
    success_url = reverse_lazy("videos:publication_list")
    list_url_name = "videos:publication_list"

    def form_valid(self, form):
        VideoPublicationService.delete_publication(instance=self.get_object())
        messages.success(self.request, "Publicación eliminada.")
        return redirect(self.success_url)


# ==== VIDEO RELATION CRUD ====
class VideoRelationListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = VideoRelation
    permission_required = "videos.view_videorelation"
    table_class = VideoRelationTable
    filterset_class = VideoRelationFilter
    template_name = "videos/relation_list.html"
    paginate_by = 25
    page_title = "Relaciones entre Videos y Streams"
    page_subtitle = (
        "Trazabilidad de clips, secuelas y contenido derivado de transmisiones en vivo"
    )
    create_url_name = "videos:relation_create"

    def get_queryset(self):
        return VideoRelationSelector.get_visible_queryset(user=self.request.user)


class VideoRelationDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = VideoRelation
    permission_required = "videos.view_videorelation"
    template_name = "videos/relation_detail.html"
    page_title = "Detalle de Relación de Contenido"
    list_url_name = "videos:relation_list"
    update_url_name = "videos:relation_update"
    delete_url_name = "videos:relation_delete"

    def get_queryset(self):
        return VideoRelationSelector.get_visible_queryset(user=self.request.user)


class VideoRelationCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = VideoRelation
    permission_required = "videos.add_videorelation"
    form_class = VideoRelationForm
    template_name = "videos/relation_form.html"
    success_url = reverse_lazy("videos:relation_list")
    page_title = "Nueva Relación de Video"
    list_url_name = "videos:relation_list"

    def form_valid(self, form):
        try:
            self.object = VideoRelationService.save_relation(**form.cleaned_data)
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Relación creada exitosamente.")
        return redirect(self.success_url)


class VideoRelationUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = VideoRelation
    permission_required = "videos.change_videorelation"
    form_class = VideoRelationForm
    template_name = "videos/relation_form.html"
    success_url = reverse_lazy("videos:relation_list")
    page_title = "Editar Relación de Video"
    list_url_name = "videos:relation_list"

    def form_valid(self, form):
        try:
            self.object = VideoRelationService.save_relation(
                instance=self.get_object(),
                **form.cleaned_data,
            )
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Relación actualizada exitosamente.")
        return redirect(self.success_url)


class VideoRelationDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = VideoRelation
    permission_required = "videos.delete_videorelation"
    template_name = "videos/relation_confirm_delete.html"
    success_url = reverse_lazy("videos:relation_list")
    list_url_name = "videos:relation_list"

    def form_valid(self, form):
        VideoRelationService.delete_relation(instance=self.get_object())
        messages.success(self.request, "Relación eliminada.")
        return redirect(self.success_url)
