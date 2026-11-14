from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand

from rrss_creatos_analyzer.apps.core.demo_cleanup import DemoCleanupService


class Command(BaseCommand):
    help = "Purge expired non-baseline demo records and self-registered users."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--days",
            type=int,
            default=int(getattr(settings, "DEMO_DATA_RETENTION_DAYS", 7)),
            help="Retention window in days (default: DEMO_DATA_RETENTION_DAYS).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview expired records without deleting anything.",
        )

    def handle(self, *args, **options) -> None:
        days = int(options["days"])
        dry_run = bool(options["dry_run"])
        summary = DemoCleanupService.purge_expired_data(
            retention_days=days,
            dry_run=dry_run,
        )
        prefix = "[DRY RUN] Would purge" if dry_run else "Purged"
        self.stdout.write(self.style.SUCCESS(f"{prefix}: {summary}"))
