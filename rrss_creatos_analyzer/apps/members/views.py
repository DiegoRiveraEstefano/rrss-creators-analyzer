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

from .filters import CreatorTeamAssignmentFilter
from .filters import MemberInvitationFilter
from .forms import CreatorTeamAssignmentForm
from .forms import MemberInvitationForm
from .models import CreatorTeamAssignment
from .models import MemberInvitation
from .selectors import CreatorTeamAssignmentSelector
from .selectors import MemberInvitationSelector
from .services import CreatorTeamAssignmentService
from .services import MemberInvitationService
from .tables import CreatorTeamAssignmentTable
from .tables import MemberInvitationTable


class MemberInvitationListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = MemberInvitation
    permission_required = "members.view_memberinvitation"
    table_class = MemberInvitationTable
    filterset_class = MemberInvitationFilter
    template_name = "members/invitation_list.html"
    paginate_by = 25
    page_title = "Invitaciones a la Plataforma"
    page_subtitle = (
        "Invitación de nuevos miembros con asignación automática de grupo de permisos"
    )
    create_url_name = "members:invitation_create"

    def get_queryset(self):
        return MemberInvitationSelector.get_queryset()


class MemberInvitationDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = MemberInvitation
    permission_required = "members.view_memberinvitation"
    template_name = "members/invitation_detail.html"
    page_title = "Detalle de Invitación"
    list_url_name = "members:invitation_list"
    update_url_name = "members:invitation_update"
    delete_url_name = "members:invitation_delete"


class MemberInvitationCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = MemberInvitation
    permission_required = "members.add_memberinvitation"
    form_class = MemberInvitationForm
    template_name = "members/invitation_form.html"
    success_url = reverse_lazy("members:invitation_list")
    page_title = "Nueva Invitación"
    list_url_name = "members:invitation_list"

    def form_valid(self, form):
        self.object = MemberInvitationService.save_invitation(
            invited_by=self.request.user,
            **form.cleaned_data,
        )
        messages.success(self.request, "Invitación creada exitosamente.")
        return redirect(self.success_url)


class MemberInvitationUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = MemberInvitation
    permission_required = "members.change_memberinvitation"
    form_class = MemberInvitationForm
    template_name = "members/invitation_form.html"
    success_url = reverse_lazy("members:invitation_list")
    page_title = "Editar Invitación"
    list_url_name = "members:invitation_list"

    def form_valid(self, form):
        self.object = MemberInvitationService.save_invitation(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Invitación actualizada exitosamente.")
        return redirect(self.success_url)


class MemberInvitationDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = MemberInvitation
    permission_required = "members.delete_memberinvitation"
    template_name = "members/invitation_confirm_delete.html"
    success_url = reverse_lazy("members:invitation_list")
    list_url_name = "members:invitation_list"

    def form_valid(self, form):
        MemberInvitationService.delete_invitation(instance=self.get_object())
        messages.success(self.request, "Invitación eliminada.")
        return redirect(self.success_url)


# ==== TEAM ASSIGNMENT CRUD ====
class CreatorTeamAssignmentListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = CreatorTeamAssignment
    permission_required = "members.view_creatorteamassignment"
    table_class = CreatorTeamAssignmentTable
    filterset_class = CreatorTeamAssignmentFilter
    template_name = "members/assignment_list.html"
    paginate_by = 25
    page_title = "Asignaciones de Equipo por Creador"
    create_url_name = "members:assignment_create"

    def get_queryset(self):
        return CreatorTeamAssignmentSelector.get_queryset()


class CreatorTeamAssignmentDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = CreatorTeamAssignment
    permission_required = "members.view_creatorteamassignment"
    template_name = "members/assignment_detail.html"
    page_title = "Detalle de Asignación"
    list_url_name = "members:assignment_list"
    update_url_name = "members:assignment_update"
    delete_url_name = "members:assignment_delete"


class CreatorTeamAssignmentCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = CreatorTeamAssignment
    permission_required = "members.add_creatorteamassignment"
    form_class = CreatorTeamAssignmentForm
    template_name = "members/assignment_form.html"
    success_url = reverse_lazy("members:assignment_list")
    page_title = "Asignar Miembro a Creador"
    list_url_name = "members:assignment_list"

    def form_valid(self, form):
        self.object = CreatorTeamAssignmentService.save_assignment(**form.cleaned_data)
        messages.success(self.request, "Asignación creada exitosamente.")
        return redirect(self.success_url)


class CreatorTeamAssignmentUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = CreatorTeamAssignment
    permission_required = "members.change_creatorteamassignment"
    form_class = CreatorTeamAssignmentForm
    template_name = "members/assignment_form.html"
    success_url = reverse_lazy("members:assignment_list")
    page_title = "Editar Asignación"
    list_url_name = "members:assignment_list"

    def form_valid(self, form):
        self.object = CreatorTeamAssignmentService.save_assignment(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Asignación actualizada exitosamente.")
        return redirect(self.success_url)


class CreatorTeamAssignmentDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = CreatorTeamAssignment
    permission_required = "members.delete_creatorteamassignment"
    template_name = "members/assignment_confirm_delete.html"
    success_url = reverse_lazy("members:assignment_list")
    list_url_name = "members:assignment_list"

    def form_valid(self, form):
        CreatorTeamAssignmentService.delete_assignment(instance=self.get_object())
        messages.success(self.request, "Asignación eliminada.")
        return redirect(self.success_url)
