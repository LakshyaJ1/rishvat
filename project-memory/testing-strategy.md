# AI CFO - Testing Strategy

## Unit Tests
- Connector normalization logic (Stripe, Plaid)
- Financial computation functions
- Guardrails validation contracts
- Encryption/decryption

## Integration Tests
- Auth endpoints: register, login, refresh
- Health endpoints
- Connector endpoints: connect, status, sync
- Audit log endpoints
- Financial endpoints
- Tenant isolation and cross-tenant access prevention
- Autopilot config endpoints
- Guardrails to approval-action flow
- Approval inbox endpoints
- Notification list/read/dismiss endpoints

## Test Infrastructure
- pytest + pytest-asyncio
- Separate test database: `aicfo_test`
- Fresh tables per test function
- Fixtures: db_session, client, test_tenant, test_user, auth_headers
- Local run requires PostgreSQL and Redis from Docker Compose
- Current validated command: `backend/.venv/Scripts/python.exe -m pytest -q`

## Current Status
- 59 tests passing as of 2026-05-17
- Stage 1 Stripe validation is covered by test-only mocked Stripe data
- Mocked Stripe E2E validates register -> connect -> sync service -> financial records -> metrics -> audit
- Stage 2 Person 1 tests validate autopilot-configured guardrails, jurisdiction escalation, threshold blocking, approval review, notification lifecycle, and audit writes
- Known cleanup: remove incorrect async marks from sync connector normalization tests
- Known cleanup: replace custom `event_loop` fixture with pytest-asyncio fixture scope config

## Coverage Target
- Critical paths: 90%+ coverage
- Financial computations: 100% coverage
- Connector normalization: 100% coverage
