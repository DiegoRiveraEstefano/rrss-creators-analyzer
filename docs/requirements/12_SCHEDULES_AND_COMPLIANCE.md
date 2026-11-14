# Module 12 — Broadcast Schedules & Compliance Tracking

## 1. Scope & Data Models

Manages recurring broadcast schedules, calendar slot generation, live-stream reconciliation, justified absences, and monthly schedule compliance summaries using **RFC 5545 `RRULE`** recurrence rules (`python-dateutil`).

- [`CreatorSchedulePattern`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/schedules/models/pattern.py) (`schedules_creator_schedule_pattern`): Recurring schedule defined by an RFC 5545 `rrule` string (e.g., `FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=1`), time window (`start_time`, `end_time`), and effective dates (`CreatorWeeklySchedule` alias preserved).
- [`CreatorScheduleSlot`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/schedules/models/slot.py) (`schedules_creator_schedule_slot`): Dated broadcast slot tracking planned vs actual hours, `start_delay_minutes`, compliance percentage, status, and optional 1:1 link to [`StreamingSession`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/streams/models.py).
- [`ScheduleException`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/schedules/models/exception.py) (`schedules_schedule_exception`): Approved medical leave, vacation, or technical outage exemptions.
- [`CreatorScheduleComplianceSummary`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/schedules/models/compliance.py) (`schedules_creator_compliance_summary`): Monthly rollup of stipulated vs completed days/hours and punctuality rates for contract/payout evaluation.

---

## 2. Business Rules (`RN-SCH`)

- **RN-SCH-001 (Punctuality Grace Period)**: Starts within `[scheduled_start_time, scheduled_start_time + 15 min]` are on time (`start_delay_minutes <= 15`); later starts are marked `LATE` (or `PARTIAL` if below duration threshold).
- **RN-SCH-002 (Slot Status Classification)**:
  - `SCHEDULED`: Future/unreconciled slot.
  - `COMPLETED`: `compliance_rate_pct >= 90.00` and within grace window.
  - `PARTIAL`: `0.00 < compliance_rate_pct < 90.00`.
  - `LATE`: `compliance_rate_pct >= 90.00` with `start_delay_minutes > 15`.
  - `MISSED`: Past deadline with `0.00` actual hours and no approved exception.
  - `JUSTIFIED_ABSENCE`: Covered by an approved `ScheduleException`.
  - `CANCELLED` / `RESCHEDULED`: Mutually cancelled or moved.
- **RN-SCH-003 (RRULE Validation & Overlap Guard)**: Patterns must validate via `dateutil.rrule.rrulestr` and must not overlap active patterns for the same creator within shared time windows.
- **RN-SCH-004 (Idempotent Slot Generation)**: `rrulestr(pattern.rrule).between(start, end)` skips existing `(creator, scheduled_date, scheduled_start_time)` slots without duplicating or overwriting reconciled data.
- **RN-SCH-005 (Stream Reconciliation)**: Matches `StreamingSession` to the closest slot by `creator`, `scheduled_date`, optional `channel`/`platform`, and `streamed_at` within `scheduled_start_time ± 120 min`, computing `compliance_rate_pct = min(100.00, (actual_hours / planned_hours) * 100.00)`.
- **RN-SCH-006 (Justified Absence Exclusion)**: Approved `ScheduleException` ranges transition matching slots to `JUSTIFIED_ABSENCE` and exclude them from denominator penalties:

  $$\text{days\_compliance\_rate\_pct} = \frac{\text{completed\_days} + \text{late\_days}}{\text{stipulated\_days} - \text{justified\_days}} \times 100$$

- **RN-SCH-007 (Time Invariants)**: `planned_duration_minutes > 0`, `end_time > start_time`, `effective_until >= effective_from`.
- **RN-SCH-008 (Monthly Compliance Threshold)**: `is_compliant = True` when `hours_compliance_rate_pct >= 90.00` and `days_compliance_rate_pct >= 85.00`.
- **RN-SCH-009 (Visual RRULE Builder + Raw Input)**: UI offers frequency/day toggles synced bidirectionally with an expandable RFC 5545 `RRULE` input.
- **RN-SCH-010 (RBAC Scoping)**: Creators see only their own schedules; managers/admins manage all creators and approve exceptions.

---

## 3. Use Cases

- **CU-SCH-01 — Configure Recurring Pattern (`ACT-MGR`, `ACT-ADM`)**: Builds or pastes `RRULE`, checks overlaps (`RN-SCH-003`), saves `CreatorSchedulePattern`.
- **CU-SCH-02 — Generate Calendar Slots (`ACT-MGR`, `ACT-ANA`)**: Projects slots for a date range idempotently (`RN-SCH-004`), honoring approved exceptions.
- **CU-SCH-03 — Create Ad-hoc Slot (`ACT-MGR`)**: Adds one-off streams (tournaments, marathons) to the monthly schedule.
- **CU-SCH-04 — Reconcile Live Sessions (`Celery Beat` / Staff)**: Links `StreamingSession` within `±120 min`, computes delay and compliance status.
- **CU-SCH-05 — Submit & Approve Absence (`ACT-TAL`, `ACT-MGR`)**: Approves `ScheduleException` and cascades `JUSTIFIED_ABSENCE` to covered slots.
- **CU-SCH-06 — Compute Monthly Compliance Summary (`ACT-ANA`, `ACT-FIN`)**: Persists `CreatorScheduleComplianceSummary` for contracts and payouts.
