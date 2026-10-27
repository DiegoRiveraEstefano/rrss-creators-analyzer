from rrss_creatos_analyzer.apps.schedules.services.compliance_service import (
    ComplianceService,
)
from rrss_creatos_analyzer.apps.schedules.services.pattern_service import PatternService
from rrss_creatos_analyzer.apps.schedules.services.reconciliation_service import (
    ReconciliationService,
)


class ScheduleService:
    """Fachada unificada para patrones, conciliación y cumplimiento."""

    # Delegación de PatternService
    save_schedule_pattern = PatternService.save_schedule_pattern
    save_weekly_schedule = PatternService.save_weekly_schedule
    generate_slots_for_period = PatternService.generate_slots_for_period

    # Delegación de ReconciliationService
    reconcile_slot = ReconciliationService.reconcile_slot
    reconcile_creator_period = ReconciliationService.reconcile_creator_period

    # Delegación de ComplianceService
    register_exception = ComplianceService.register_exception
    approve_exception = ComplianceService.approve_exception
    calculate_monthly_compliance_summary = (
        ComplianceService.calculate_monthly_compliance_summary
    )


__all__ = [
    "ComplianceService",
    "PatternService",
    "ReconciliationService",
    "ScheduleService",
]
