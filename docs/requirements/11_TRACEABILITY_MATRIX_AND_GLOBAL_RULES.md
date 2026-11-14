# Module 11 — Traceability Matrix & Global Business Rules

## 1. Requirements Traceability Matrix

| Use Case | Title | App(s) | Primary Models | Primary Actors | Related Rules |
|---|---|---|---|---|---|
| **CU-USR-01** | Invite New Member | `members`, `users` | `MemberInvitation`, `User` | Company Admin | RN-SEC-001, RN-SEC-002, RN-SEC-007 |
| **CU-USR-02** | Accept Invitation | `members`, `users` | `MemberInvitation`, `User`, `Group` | Invitee | RN-SEC-001, RN-SEC-002, RN-SEC-003 |
| **CU-USR-03** | Assign / Revoke Roles | `permissions`, `users` | `RoleGroupProfile`, `User`, `Group` | Company Admin | RN-SEC-003, RN-SEC-006, RN-SEC-007 |
| **CU-USR-04** | Manage Creator Team | `members`, `creators` | `CreatorTeamAssignment`, `Creator` | Admin, Manager | RN-SEC-005, RN-CRE-001 |
| **CU-USR-05** | Update User Profile | `users` | `User` | All Users | RN-SEC-001 |
| **CU-USR-06** | Deactivate User | `users`, `audit` | `User`, `AuditEvent` | Company Admin | RN-SEC-006, RN-SYS-002 |
| **CU-CRE-01** | Onboard Creator | `creators` | `Creator` | Manager, Admin | RN-CRE-001, RN-CRE-002 |
| **CU-CRE-02** | Manage KYC Info | `creators`, `audit` | `CreatorPersonalInfo`, `AuditEvent` | Finance, Admin | RN-CRE-003, RN-SEC-004 |
| **CU-CRE-03** | Link Social Channels | `creators` | `Channel`, `Creator` | Manager, Analyst | RN-CRE-004, RN-CRE-005 |
| **CU-CRE-04** | Record Channel Snapshot | `creators` | `ChannelSnapshot`, `Channel` | Celery, Analyst | RN-CRE-005, RN-DAT-006 |
| **CU-CRE-05** | Draft Contract | `contracts`, `creators` | `Contract`, `Creator` | Admin, Manager | RN-CRE-006, RN-CRE-007, RN-CRE-008 |
| **CU-CRE-06** | Activate Contract | `contracts`, `creators` | `Contract`, `Creator` | Finance, Admin | RN-CRE-006, RN-CRE-008, RN-CRE-009 |
| **CU-CRE-07** | Terminate Contract | `contracts`, `creators` | `Contract`, `Creator` | Company Admin | RN-CRE-006, RN-PAY-003 |
| **CU-CRE-08** | 360° Creator Profile | `creators`, `analytics` | `Creator`, `Channel`, `Contract`, `StreamingSession` | Manager, Analyst, Admin | RN-SEC-004, RN-DAT-005 |
| **CU-STR-01** | Log Stream Manually | `streams` | `StreamingSession`, `Creator`, `Channel` | Manager, Creator | RN-STR-001..004 |
| **CU-STR-02** | Bulk Import Streams | `streams`, `imports` | `StreamingSession`, `ImportBatch` | Analyst | RN-STR-001, RN-DAT-001, RN-DAT-002 |
| **CU-STR-03** | Segment Stream | `streams` | `SessionSegment`, `StreamingSession` | Manager, Analyst | RN-STR-006 |
| **CU-STR-04** | Reconcile Sponsored Stream | `streams`, `campaigns` | `StreamingSession`, `CampaignDeliverable` | Manager, Finance | RN-STR-007, RN-CAM-006 |
| **CU-STR-05** | Category Performance | `streams`, `analytics` | `StreamingSession`, `SessionSegment` | Analyst, Manager | RN-STR-004, RN-DAT-005 |
| **CU-STR-06** | Derive Video from Stream | `streams`, `videos` | `StreamingSession`, `VideoRelation`, `Video` | Editor, Manager | RN-STR-001, RN-VID-008 |
| **CU-SCH-01** | Configure RRULE Pattern | `schedules` | `CreatorSchedulePattern`, `Creator` | Manager, Admin | RN-SCH-003, RN-SCH-008 |
| **CU-SCH-02** | Generate Schedule Slots | `schedules` | `CreatorScheduleSlot`, `CreatorSchedulePattern` | Manager, Analyst | RN-SCH-004, RN-SCH-006 |
| **CU-SCH-03** | Create Ad-hoc Slot | `schedules` | `CreatorScheduleSlot`, `Creator` | Manager | RN-SCH-007, RN-SCH-008 |
| **CU-SCH-04** | Reconcile Streams & Slots | `schedules`, `streams` | `CreatorScheduleSlot`, `StreamingSession` | Celery Beat, Analyst | RN-SCH-001, RN-SCH-002, RN-SCH-005 |
| **CU-SCH-05** | Approve Absence Exception | `schedules` | `ScheduleException`, `CreatorScheduleSlot` | Creator, Manager | RN-SCH-006 |
| **CU-SCH-06** | Monthly Compliance Summary | `schedules`, `contracts` | `CreatorScheduleComplianceSummary`, `Contract` | Analyst, Finance | RN-SCH-006..009 |
| **CU-VID-01** | Create Video Project | `videos` | `Video`, `Creator` | Manager, Creator, Editor | RN-VID-001, RN-VID-002 |
| **CU-VID-02** | Track Production Costs | `videos` | `Video` | Finance, Manager | RN-VID-003, RN-VID-005 |
| **CU-VID-03** | Advance Pipeline Stage | `videos` | `Video` | Manager, Editor, Creator | RN-VID-002 |
| **CU-VID-04** | Register Publication | `videos` | `VideoPublication`, `Video`, `Channel` | Manager, Creator | RN-VID-001, RN-VID-004 |
| **CU-VID-05** | Update Publication Metrics | `videos` | `VideoPublication`, `Video` | Celery, Analyst | RN-VID-006, RN-VID-007, RN-DAT-006 |
| **CU-VID-06** | Link Content Lineage | `videos` | `VideoRelation`, `Video` | Editor, Manager | RN-VID-008 |
| **CU-VID-07** | Profitability & ROI Audit | `videos`, `analytics` | `Video`, `VideoPublication` | Finance, Analyst | RN-VID-004..006 |
| **CU-EDT-01** | Register Editor | `editors` | `Editor`, `User` | Manager, Admin | RN-EDT-001, RN-EDT-002 |
| **CU-EDT-02** | Assign Editor to Creator | `editors`, `creators` | `EditorAssignment`, `Editor`, `Creator` | Manager | RN-EDT-002, RN-EDT-003 |
| **CU-EDT-03** | Create Editing Task | `editors`, `videos` | `EditingTask`, `Video`, `Editor` | Manager, Creator | RN-EDT-002, RN-EDT-004, RN-EDT-008 |
| **CU-EDT-04** | Submit Cut Revision | `editors` | `TaskRevision`, `EditingTask` | Editor | RN-EDT-004, RN-EDT-005 |
| **CU-EDT-05** | Request Cut Changes | `editors` | `TaskRevision`, `EditingTask` | Manager, Creator | RN-EDT-005 |
| **CU-EDT-06** | Approve Task & Allocate Cost | `editors`, `videos` | `EditingTask`, `TaskRevision`, `Video` | Manager, Creator | RN-EDT-006, RN-VID-003 |
| **CU-EDT-07** | Settle Editor Fees | `editors` | `EditingTask`, `Editor` | Finance | RN-EDT-007 |
| **CU-CAM-01** | Create Sponsor Campaign | `campaigns` | `SponsorCampaign` | Manager, Finance | RN-CAM-001, RN-CAM-002 |
| **CU-CAM-02** | Assign Deliverables | `campaigns`, `creators` | `CampaignDeliverable`, `SponsorCampaign` | Manager | RN-CAM-001..003 |
| **CU-CAM-03** | Submit Brand Draft | `campaigns` | `CampaignDeliverable` | Manager, Creator | RN-CAM-004 |
| **CU-CAM-04** | Record Brand Verdict | `campaigns` | `CampaignDeliverable` | Manager | RN-CAM-004 |
| **CU-CAM-05** | Publish Deliverable & Proof | `campaigns`, `streams`, `videos` | `CampaignDeliverable`, `VideoPublication` | Creator, Manager | RN-CAM-004..006 |
| **CU-CAM-06** | Audit & Close Campaign | `campaigns` | `SponsorCampaign`, `CampaignDeliverable` | Analyst, Finance | RN-CAM-002, RN-CAM-005 |
| **CU-ALT-01** | Emit Channel Alert | `alerts`, `creators` | `ChannelAlert`, `Channel` | Celery, Manager | RN-ALT-001, RN-ALT-002, RN-ALT-005 |
| **CU-ALT-02** | Assign & Investigate Alert | `alerts` | `ChannelAlert`, `User` | Manager, Admin | RN-ALT-002, RN-ALT-004 |
| **CU-ALT-03** | Submit Appeal | `alerts` | `ChannelAlert` | Manager, Legal | RN-ALT-004 |
| **CU-ALT-04** | Resolve Alert | `alerts`, `creators` | `ChannelAlert`, `Channel` | Manager, Admin | RN-ALT-003..005 |
| **CU-ALT-05** | Detect CCV Drop | `alerts`, `streams` | `ChannelAlert`, `StreamingSession` | Celery, Analyst | RN-ALT-001, RN-ALT-002 |
| **CU-PAY-01** | Generate Monthly Drafts | `payouts`, `contracts` | `CreatorPayout`, `Contract`, `Creator` | Finance, Celery | RN-PAY-001, RN-PAY-002, RN-CRE-008 |
| **CU-PAY-02** | Apply Payout Adjustments | `payouts` | `CreatorPayout` | Manager, Finance | RN-PAY-002, RN-PAY-003 |
| **CU-PAY-03** | Submit for Approval | `payouts` | `CreatorPayout` | Manager | RN-PAY-004 |
| **CU-PAY-04** | Approve Payout | `payouts`, `creators` | `CreatorPayout`, `CreatorPersonalInfo` | Finance, Admin | RN-PAY-004..006 |
| **CU-PAY-05** | View Creator Statement | `payouts` | `CreatorPayout` | Creator | RN-PAY-004, RN-SEC-004 |
| **CU-PAY-06** | Execute Payout Payment | `payouts` | `CreatorPayout` | Finance | RN-PAY-005, RN-PAY-006 |
| **CU-DAT-01** | Upload Metric Batch | `imports` | `ImportBatch` | Analyst | RN-DAT-001, RN-DAT-002 |
| **CU-DAT-02** | Process Batch Async | `imports`, `streams`, `videos` | `ImportBatch`, `StreamingSession` | Celery Worker | RN-DAT-002, RN-DAT-003, RN-DAT-006 |
| **CU-DAT-03** | Rollback Import Batch | `imports`, `audit` | `ImportBatch`, `AuditEvent` | Admin, Analyst | RN-DAT-003, RN-SYS-002 |
| **CU-DAT-04** | Request Export | `exports` | `ExportJob`, `User` | Analyst, Finance, Manager | RN-DAT-002, RN-DAT-004 |
| **CU-DAT-05** | Download Export | `exports`, `audit` | `ExportJob`, `AuditEvent` | Requester | RN-DAT-004, RN-SYS-002 |
| **CU-DAT-06** | Executive Dashboard | `analytics` | `AnalyticsSnapshot`, ORM aggregations | Admin, Manager | RN-DAT-005, RN-SEC-004 |
| **CU-DAT-07** | Refresh Analytics Cache | `analytics` | Cache backend | Admin | RN-DAT-005, RN-DAT-006 |
| **CU-SYS-01** | Update Company Settings | `core` | `CompanySettings` | Admin | RN-SYS-001, RN-SYS-002 |
| **CU-SYS-02** | Inspect Audit Trail | `audit` | `AuditEvent` | Auditor, Admin | RN-SYS-002, RN-SYS-007 |
| **CU-SYS-03** | Inspect App Logs | `logs` | `ApplicationLogEntry` | Admin | RN-SYS-007 |
| **CU-SYS-04** | Health Diagnostics | `monitor` | `InstanceHealthCheck` | Celery Beat, Admin | RN-SYS-003, RN-SYS-004 |
| **CU-SYS-05** | Execute DB Backup | `backups` | `DatabaseBackup` | Celery Beat, Admin | RN-SYS-005..007 |
| **CU-SYS-06** | Verify/Download Backup | `backups`, `audit` | `DatabaseBackup`, `AuditEvent` | Admin | RN-SYS-005..007 |

---

## 2. Database Concurrency & Persistence Guidelines

- **Production**: PostgreSQL 16+ with `ATOMIC_REQUESTS = True` and `CONN_MAX_AGE = 60`.
- **Local Development & Tests (SQLite WAL)**: Initialize connections with `PRAGMA journal_mode = WAL;`, `PRAGMA busy_timeout = 5000;`, `PRAGMA synchronous = NORMAL;`, and `PRAGMA foreign_keys = ON;`. Keep Celery bulk writes inside short `transaction.atomic()` batches (200–500 rows).

---

## 3. Global Acceptance Criteria

1. **Permission Scoping**: Selectors must enforce `view_all_*` vs `creator__user=user` across both HTML views and DRF APIs.
2. **Financial Accuracy**: Agency commission + creator gross share must equal 100% of gross revenue (`±0.01` decimal rounding tolerance).
3. **Resilient Async Pipelines**: Imports/exports never block web workers and transition cleanly to `failed`/`partial` on worker errors.
4. **Auditability**: Contract changes, KYC access, alert resolutions, and payout approvals emit immutable audit records.
