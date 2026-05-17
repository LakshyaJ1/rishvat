# AI CFO - Backend Architecture

## FastAPI Structure
```
backend/app/
├── main.py              # App factory, middleware, router registration
├── config.py            # pydantic-settings configuration
├── dependencies.py      # Dependency injection
├── auth/                # JWT auth
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic request/response contracts
├── middleware/          # Tenant scoping, request logging
├── services/            # Business logic and sync service
├── connectors/          # External integrations
├── financials/          # Deterministic financial calculations
├── guardrails/          # Deterministic AI/action validation
├── routers/             # API route handlers
├── tasks/               # Celery background tasks
└── utils/               # Encryption and helpers
```

## Auth And Tenant Isolation
- JWT contains `user_id`, `tenant_id`, `role`, `type`, and expiry.
- Protected endpoints use `get_current_user`.
- Tenant scope is derived from JWT, never request body tenant IDs.
- PostgreSQL RLS context is set through `set_config('app.current_tenant_id', ...)`.

## Celery And Sync
- Redis DB 1 is the Celery broker; Redis DB 2 is the result backend.
- Celery Beat schedules health checks and connector syncs.
- Celery calls the shared connector sync service so tests and workers use the same upsert/audit behavior.
- Connector sync returns inserted, updated, skipped, status, provider, and error data when applicable.
- Sync success/failure/skipped outcomes are written to the append-only audit log.

## Connector Architecture
- All providers implement `BaseConnector.fetch()` and `normalize()`.
- Credentials are encrypted at rest.
- Integrations are read-only by default.
- Pipeline: fetch -> normalize -> shared sync upsert -> audit.
- Stripe is not a locked dependency; provider alternatives must fit the same connector contract.
- Real Stripe validation can be unavailable during development, so tests use monkeypatched Stripe fetch data instead of a production mock provider.

## Financial Computation Architecture
- Deterministic functions compute burn, runway, MRR, ARR, CAC, churn, and NRR contracts.
- Churn and NRR return explicit insufficient-data responses until account/customer lifecycle data exists.
- Money is stored and returned in integer minor units.
- Financial endpoints are tenant scoped and include source record IDs where records support the metric.

## Guardrails Architecture
- Guardrails are deterministic Python validation, not AI.
- API endpoint: `POST /api/v1/guardrails/validate`.
- Authenticated endpoint derives tenant from JWT and writes audit entries.
- The API maps each action to a product category and loads the tenant's `AutopilotConfig` for autonomy level, max amount, revenue floor, and lock state.
- Current checks cover source requirements, typed action payload validation, low confidence review, unsupported autonomy, founder locks, thresholds, reversibility, and jurisdiction rules.
- If output is approved for display but not approved for autonomous execution, the endpoint creates a pending `ApprovalAction` and returns `approval_action_id`.

## Stage 2 Action Workflow
- Person 2 AI output should call `/guardrails/validate` before returning any recommendation or action to the frontend.
- Guardrails either block the output, approve it for display only with a pending approval, or approve it for autonomous execution within the configured category limits.
- Approval review is handled through `/api/v1/approvals`, and approve/reject decisions are written to audit logs.
- Notifications are tenant-scoped records used for anomalies, runway warnings, compliance reminders, and sync errors.

## Redis Usage
- DB 0: application cache
- DB 1: Celery broker
- DB 2: Celery result backend
