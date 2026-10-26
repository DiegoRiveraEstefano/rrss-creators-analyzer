import django_filters

from .models import CreatorTeamAssignment
from .models import MemberInvitation


class MemberInvitationFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr="icontains", label="Email")

    class Meta:
        model = MemberInvitation
        fields = ["email", "target_group", "status"]


class CreatorTeamAssignmentFilter(django_filters.FilterSet):
    class Meta:
        model = CreatorTeamAssignment
        fields = ["creator", "user", "group", "responsibility", "is_primary"]
