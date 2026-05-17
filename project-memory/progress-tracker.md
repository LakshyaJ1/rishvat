# AI CFO - Progress Tracker

## Stage 1 - Foundation

### Completed
- [x] Project structure, backend dependencies, Dockerfile, and docker-compose.yml
- [x] FastAPI app, config, request logging, JWT auth, and tenant-scoped dependencies
- [x] PostgreSQL models and Alembic migration for Tenant, User, FinancialRecord, ConnectorConfig, AuditLog
- [x] PostgreSQL RLS tenant context bound per authenticated DB session
- [x] Redis and Celery worker/beat foundation
- [x] Connector contract plus Stripe and Plaid read-only connector skeletons
- [x] Credential encryption for connector configuration
- [x] Health, metrics, integration, audit-log, and financial endpoints
- [x] Deterministic financial calculations: burn, runway, MRR, ARR, CAC, churn/NRR insufficient-data contracts
- [x] Guardrails contracts and deterministic validation skeleton
- [x] Alembic migration validated against local dev PostgreSQL
- [x] Docker Compose stack validated: backend, PostgreSQL, Redis, Celery worker, Celery beat
- [x] Health endpoint validated at `http://localhost:8000/api/v1/health`
- [x] Stage 1 Stripe flow validated with test-only mocked Stripe data
- [x] Local backend validation: 59 tests passing

### Stripe Validation Note
- Real Stripe account/API validation is blocked by current developer/location approval constraints.
- Stripe is not a locked product dependency. It remains one provider behind a replaceable connector interface.
- Stage 1 uses a test-only mocked Stripe sync path; no production mock provider is exposed.

## Stage 2 - Core Product

### Person 1 Completed
- [x] Financial metric endpoints expanded for MRR, ARR, CAC, churn, and NRR contracts
- [x] Guardrails validation endpoint added for later local AI integration
- [x] Connector sync upsert logic extracted into a shared service used by Celery and tests
- [x] Connector sync audit logging added for success/failure/skipped outcomes
- [x] Stage 2 schema added for autopilot configs, notifications, and approval actions
- [x] Autopilot configuration endpoints added for per-category autonomy, limits, floors, and locks
- [x] Guardrails now apply typed action contracts, threshold rules, reversibility rules, tenant jurisdiction rules, and tenant autopilot config
- [x] Guardrails create pending approval actions whenever an approved output still requires human review
- [x] Approval inbox endpoints added for list, approve, and reject flows with audit logging
- [x] Notification endpoints added for list, read, and dismiss flows with audit logging

### Remaining Backend Dependencies
- [ ] Add richer Stripe/Plaid subscription/account normalization once real data access is available
- [ ] Add financial snapshot caching after endpoint contracts stabilize
- [ ] Add Sentry integration test
- [ ] Add basic load test for auth, financial snapshot, and connector status endpoints

## Stage 3 - Autopilot + Onboarding
Not started.

## Stage 4 - Polish + Launch
Not started.

## Current Sprint
Sprint 2: Stage 1 mock validation completed; Stage 2 Person 1 backend contracts completed and validated.

## Milestones
| Milestone | Status | Date |
|-----------|--------|------|
| Stage 1 backend foundation | Complete | 2026-05-17 |
| Stage 1 Stripe validation | Complete via test-only mock; real Stripe pending approval/access | 2026-05-17 |
| Stage 2 Person 1 backend | Complete | 2026-05-17 |
| First milestone with Person 2/3 | Pending later integration | TBD |
