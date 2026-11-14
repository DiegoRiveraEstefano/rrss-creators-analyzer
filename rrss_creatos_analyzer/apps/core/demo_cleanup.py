from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from allauth.account.models import EmailAddress
from auditlog.models import LogEntry
from captcha.models import CaptchaStore
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework.authtoken.models import Token
from taggit.models import TaggedItem

from rrss_creatos_analyzer.apps.alerts.models import ChannelAlert
from rrss_creatos_analyzer.apps.analytics.models import AnalyticsSnapshot
from rrss_creatos_analyzer.apps.backups.models import DatabaseBackup
from rrss_creatos_analyzer.apps.campaigns.models import CampaignDeliverable
from rrss_creatos_analyzer.apps.campaigns.models import SponsorCampaign
from rrss_creatos_analyzer.apps.contracts.models import Contract
from rrss_creatos_analyzer.apps.creators.models import Channel
from rrss_creatos_analyzer.apps.creators.models import ChannelSnapshot
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.creators.models import CreatorPersonalInfo
from rrss_creatos_analyzer.apps.editors.models import EditingTask
from rrss_creatos_analyzer.apps.editors.models import Editor
from rrss_creatos_analyzer.apps.editors.models import EditorAssignment
from rrss_creatos_analyzer.apps.editors.models import TaskRevision
from rrss_creatos_analyzer.apps.exports.models import ExportJob
from rrss_creatos_analyzer.apps.imports.models import ImportBatch
from rrss_creatos_analyzer.apps.logs.models import ApplicationLogEntry
from rrss_creatos_analyzer.apps.members.models import CreatorTeamAssignment
from rrss_creatos_analyzer.apps.members.models import MemberInvitation
from rrss_creatos_analyzer.apps.monitor.models import InstanceHealthCheck
from rrss_creatos_analyzer.apps.payouts.models import CreatorPayout
from rrss_creatos_analyzer.apps.permissions.models import RoleGroupProfile
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleComplianceSummary
from rrss_creatos_analyzer.apps.schedules.models import CreatorSchedulePattern
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException
from rrss_creatos_analyzer.apps.streams.models import SessionSegment
from rrss_creatos_analyzer.apps.streams.models import StreamingSession
from rrss_creatos_analyzer.apps.videos.models import Video
from rrss_creatos_analyzer.apps.videos.models import VideoPublication
from rrss_creatos_analyzer.apps.videos.models import VideoRelation

from .demo_baseline import BASELINE_USERNAMES
from .demo_baseline import get_baseline_pks
from .models import CompanySettings

if TYPE_CHECKING:
    from datetime import datetime

    from django.db import models

logger = logging.getLogger(__name__)
User = get_user_model()

PURGE_MODEL_ORDER: tuple[type[models.Model], ...] = (
    TaskRevision,
    EditingTask,
    EditorAssignment,
    Editor,
    CampaignDeliverable,
    SponsorCampaign,
    CreatorPayout,
    ChannelAlert,
    VideoRelation,
    VideoPublication,
    Video,
    SessionSegment,
    StreamingSession,
    CreatorScheduleSlot,
    CreatorSchedulePattern,
    ScheduleException,
    CreatorScheduleComplianceSummary,
    Contract,
    ChannelSnapshot,
    Channel,
    CreatorPersonalInfo,
    CreatorTeamAssignment,
    MemberInvitation,
    Creator,
    ImportBatch,
    ExportJob,
    AnalyticsSnapshot,
    ApplicationLogEntry,
    InstanceHealthCheck,
    DatabaseBackup,
    CompanySettings,
)


def _model_label(model: type[models.Model]) -> str:
    return model._meta.label  # noqa: SLF001


def _delete_or_count(
    qs: models.QuerySet[Any],
    model_label: str,
    *,
    dry_run: bool,
) -> int:
    if dry_run:
        return qs.count()
    deleted_total, deleted_map = qs.delete()
    return deleted_map.get(model_label, deleted_total)


def _record_deleted(
    summary: dict[str, int],
    model: type[models.Model],
    qs: models.QuerySet[Any],
    *,
    dry_run: bool,
) -> None:
    label = _model_label(model)
    count = _delete_or_count(qs, label, dry_run=dry_run)
    if count:
        summary[label] = count


def _purge_domain_models(*, cutoff: datetime, dry_run: bool) -> dict[str, int]:
    summary: dict[str, int] = {}
    for model in PURGE_MODEL_ORDER:
        baseline_pks = get_baseline_pks(model)
        qs = cast("Any", model).objects.filter(created_at__lt=cutoff)
        if baseline_pks:
            qs = qs.exclude(pk__in=baseline_pks)
        _record_deleted(summary, model, qs, dry_run=dry_run)

    baseline_role_pks = get_baseline_pks(RoleGroupProfile)
    role_qs = RoleGroupProfile.objects.filter(
        created_at__lt=cutoff,
        is_system_role=False,
    )
    if baseline_role_pks:
        role_qs = role_qs.exclude(pk__in=baseline_role_pks)
    _record_deleted(summary, RoleGroupProfile, role_qs, dry_run=dry_run)
    return summary


def _purge_expired_users(*, cutoff: datetime, dry_run: bool) -> dict[str, int]:
    summary: dict[str, int] = {}
    baseline_user_pks = get_baseline_pks(User)
    expired_users = User.objects.filter(
        date_joined__lt=cutoff,
        is_superuser=False,
    ).exclude(username__in=BASELINE_USERNAMES)
    if baseline_user_pks:
        expired_users = expired_users.exclude(pk__in=baseline_user_pks)
    expired_user_ids = list(expired_users.values_list("pk", flat=True))

    if not expired_user_ids:
        return summary

    _record_deleted(
        summary,
        EmailAddress,
        EmailAddress.objects.filter(user_id__in=expired_user_ids),
        dry_run=dry_run,
    )
    _record_deleted(
        summary,
        Token,
        Token.objects.filter(user_id__in=expired_user_ids),
        dry_run=dry_run,
    )
    _record_deleted(
        summary,
        User,
        User.objects.filter(pk__in=expired_user_ids),
        dry_run=dry_run,
    )
    return summary


def _purge_auxiliary(
    *,
    now: datetime,
    cutoff: datetime,
    dry_run: bool,
) -> dict[str, int]:
    summary: dict[str, int] = {}
    _record_deleted(
        summary,
        LogEntry,
        LogEntry.objects.filter(timestamp__lt=cutoff),
        dry_run=dry_run,
    )
    _record_deleted(
        summary,
        Session,
        Session.objects.filter(expire_date__lt=now),
        dry_run=dry_run,
    )
    _record_deleted(
        summary,
        TaggedItem,
        TaggedItem.objects.filter(object_id__isnull=True),
        dry_run=dry_run,
    )
    return summary


class DemoCleanupService:
    """Purge non-baseline data and self-registered accounts past retention window."""

    @classmethod
    @transaction.atomic
    def purge_expired_data(
        cls,
        *,
        retention_days: int = 7,
        dry_run: bool = False,
    ) -> dict[str, int]:
        """Delete expired non-baseline records and return deleted counts per model."""
        if retention_days < 1:
            msg = "retention_days must be at least 1."
            raise ValueError(msg)

        now = timezone.now()
        cutoff = now - timedelta(days=retention_days)
        summary: dict[str, int] = {}
        summary.update(_purge_domain_models(cutoff=cutoff, dry_run=dry_run))
        summary.update(_purge_expired_users(cutoff=cutoff, dry_run=dry_run))
        summary.update(_purge_auxiliary(now=now, cutoff=cutoff, dry_run=dry_run))

        if not dry_run:
            CaptchaStore.remove_expired()
            transaction.on_commit(cache.clear)

        logger.info(
            "demo_cleanup_completed",
            extra={
                "retention_days": retention_days,
                "dry_run": dry_run,
                "summary": summary,
            },
        )
        return summary
