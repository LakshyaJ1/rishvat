# AI CFO - Tasks

## Active Tasks

### T-003: Stage 1 Stripe Validation
- **Priority**: P0
- **Status**: Complete via test-only mock
- **Owner**: Person 1
- **Description**: Real Stripe validation is blocked by approval/access. Implemented mocked Stripe E2E test that validates register -> connect Stripe -> sync -> financial records -> burn metrics -> audit.
- **Dependencies**: T-001, T-002

### T-004: Financial Computation Functions
- **Priority**: P1
- **Status**: Complete for Stage 2
- **Owner**: Person 1
- **Description**: Implemented burn, runway, MRR, ARR, CAC, and explicit insufficient-data contracts for churn/NRR.
- **Remaining**: Rich churn/NRR needs account-level subscription movement data.

### T-005: Data Normalization Pipeline
- **Priority**: P1
- **Status**: Complete for Stage 2
- **Owner**: Person 1
- **Description**: Shared sync upsert service now handles inserted/updated/skipped records and audit logging. Richer provider-specific normalization remains.

### T-006: Guardrails Engine
- **Priority**: P1
- **Status**: Complete for Stage 2
- **Owner**: Person 1
- **Description**: Stable typed action contracts, deterministic validation, authenticated validation endpoint, thresholds, reversibility, jurisdiction rules, autopilot config lookup, approval creation, and audit logging are implemented.
- **Remaining**: Person 2 AI endpoints must call `/guardrails/validate` before returning action/recommendation outputs.

### T-007: Financial Snapshot Endpoint
- **Priority**: P1
- **Status**: Complete for Stage 2
- **Owner**: Person 1
- **Description**: Snapshot endpoint includes burn, optional runway, MRR, ARR, and record count.
- **Remaining**: Cache strategy and richer cash/account data.

### T-008: Stage 2 Approval Inbox
- **Priority**: P1
- **Status**: Complete
- **Owner**: Person 1
- **Description**: ApprovalAction model, migration, list endpoint, approve endpoint, reject endpoint, tenant scoping, and audit logging are implemented.

### T-009: Stage 2 Notifications
- **Priority**: P1
- **Status**: Complete
- **Owner**: Person 1
- **Description**: Notification model, migration, list endpoint, read endpoint, dismiss endpoint, tenant scoping, and audit logging are implemented.

## Completed
- T-001: Docker Compose startup validated
- T-002: Alembic migration validated

## Backlog
- QuickBooks connector
- Xero connector
- Razorpay connector
- Autopilot execution engine
- Approvals inbox backend
- Compliance calendar
- Vendor intelligence
- Load testing
- Terraform deployment config
