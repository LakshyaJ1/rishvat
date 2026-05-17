# AI CFO - Changelog

## 2026-05-17

### Stage 1 Foundation - Initial Implementation
- Created backend project structure with FastAPI, SQLAlchemy, Alembic, Celery, and Docker
- Implemented database models: Tenant, User, FinancialRecord, ConnectorConfig, AuditLog
- Created initial Alembic migration with RLS policies and audit immutability trigger
- Built JWT auth system: register, login, refresh
- Implemented tenant scoping middleware and request logging
- Built connector contract plus Stripe and Plaid connector skeletons
- Added credential encryption for connector configuration
- Created health, metrics, integration, and audit-log endpoints
- Configured Celery worker and beat task skeletons
- Added tests for auth, health, tenant isolation, and connectors
- Created project memory system

### Stage 1 Hardening + First Milestone Backend Surface
- Added deterministic financial calculations in `app/financials/calculations.py`
- Added financial contracts for burn rate, runway, MRR, ARR, CAC, churn, NRR, and snapshot
- Added tenant-scoped financial endpoints: `/api/v1/financials/burn`, `/runway`, `/snapshot`
- Added deterministic guardrails contracts and initial validation engine
- Bound authenticated DB sessions to PostgreSQL RLS tenant context using `set_config`
- Corrected financial record uniqueness to include `tenant_id`
- Made timezone-aware datetime columns explicit in SQLAlchemy models
- Added missing dependencies: `email-validator`, `bcrypt==4.0.1`
- Hardened test database fixture by dropping tables before each test run
- Added tests for financial calculations, financial endpoint tenant scoping, and guardrails
- Local validation: `30 passed` with PostgreSQL and Redis running through Docker Compose
- Alembic migration validated against local dev PostgreSQL
- Full Docker Compose stack started successfully
- Health endpoint validated: DB, Redis, and Celery all returned `ok`
- Added backend-local `.dockerignore`; Docker build context dropped from 176 MB to about 25 KB
- Cleaned Dockerfile stage casing and removed obsolete Compose `version` key

### Stage 1 Mock Validation + Stage 2 Backend Contracts
- Added shared connector sync service used by Celery and tests
- Added sync result accounting for inserted, updated, and skipped records
- Added connector sync audit logging
- Added test-only mocked Stripe E2E validation for development without real Stripe access
- Documented that Stripe is not a locked product dependency and remains replaceable
- Added financial endpoints for MRR, ARR, CAC, churn, and NRR contracts
- Added authenticated guardrails validation endpoint with audit logging
- Expanded tests from 30 to 54 passing tests

### Stage 2 Person 1 Completion
- Added Stage 2 database models and migration coverage for autopilot configs, notifications, and approval actions
- Added autopilot config endpoints for category-level autonomy, financial thresholds, revenue floors, and founder locks
- Expanded guardrails with typed action contracts for pricing, payment, report, and alert actions
- Wired guardrails to tenant autopilot config, current MRR context, tenant jurisdiction, threshold rules, reversibility rules, and jurisdiction rules
- Added automatic pending approval creation for outputs that are display-safe but require human review
- Added approval inbox endpoints for list, approve, and reject flows with audit logging
- Added notification endpoints for list, read, and dismiss flows with audit logging
- Updated Alembic environment imports for Stage 2 models and aligned financial record category indexing
- Added Stage 2 Person 1 integration tests
- Local validation: `59 passed` with PostgreSQL test database
