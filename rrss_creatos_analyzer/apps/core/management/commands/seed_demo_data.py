from __future__ import annotations

from django.core.management.base import BaseCommand

from rrss_creatos_analyzer.apps.core.demo_services import DemoSeedService


class Command(BaseCommand):
    help = "Seed baseline RBAC roles, demo accounts, and realistic dataset."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset existing baseline demo records before seeding.",
        )
        parser.add_argument(
            "--if-empty",
            action="store_true",
            help="Only seed if baseline demo data is not yet present.",
        )

    def handle(self, *args, **options) -> None:
        if options["if_empty"] and DemoSeedService.is_seeded():
            self.stdout.write(
                self.style.NOTICE("Demo baseline already present; skipping seed."),
            )
            return

        summary = DemoSeedService.seed_all(reset=bool(options["reset"]))
        self.stdout.write(
            self.style.SUCCESS(f"Demo data seeded successfully: {summary}"),
        )
