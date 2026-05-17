# AI CFO - API Contracts

## Base URL
`/api/v1`

## Authentication
All endpoints except `/health`, `/metrics`, and `/auth/*` require a Bearer JWT token. Tenant scope is always derived from JWT, not client-supplied tenant IDs.

## Auth Endpoints
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

## Health Endpoints
- `GET /api/v1/health`
- `GET /api/v1/metrics`

## Integration Endpoints
- `POST /api/v1/integrations/connect`
  - Request: `{ provider: "stripe"|"plaid", credentials: {...} }`
  - Response: `{ id, provider, status, permissions, last_synced_at, sync_error }`
- `GET /api/v1/integrations/status`
- `POST /api/v1/integrations/{connector_id}/sync`
  - Response: `{ task_id, status: "queued" }`

## Audit Log Endpoint
- `GET /api/v1/audit-log`
  - Query: `page`, `per_page`, `action_type`
  - Response: `{ items, total, page, per_page, total_pages }`

## Financial Endpoints
- `GET /api/v1/financials/snapshot`
  - Query: `cash_balance_cents?`, `period_months=3`
  - Response: `{ burn_rate, runway, mrr, arr, record_count }`
- `GET /api/v1/financials/burn`
- `GET /api/v1/financials/runway`
  - Query: `cash_balance_cents`, `period_months=3`
- `GET /api/v1/financials/mrr`
- `GET /api/v1/financials/arr`
- `GET /api/v1/financials/cac`
  - Query: `new_customers`
- `GET /api/v1/financials/churn`
  - Returns explicit `insufficient_data=true` until customer lifecycle data exists
- `GET /api/v1/financials/nrr`
  - Returns explicit `insufficient_data=true` until account-level subscription movement exists

## Guardrails Endpoint
- `POST /api/v1/guardrails/validate`
  - Request: `{ action_type, ai_output, data_sources, confidence, reversible?, requested_autonomy_level?, category?, reasoning?, expected_outcome? }`
  - Response: `{ approved, modified_output, violations, warnings, requires_human_approval, reason, approval_action_id? }`
  - Applies typed action contracts, tenant autopilot config, thresholds, reversibility, and jurisdiction rules
  - Creates an approval action when output is display-safe but requires human review
  - Writes `guardrail.validate` audit entries

## Autopilot Endpoints
- `GET /api/v1/autopilot/config`
  - Response: `[{ id, category, autonomy_level, max_amount_cents, revenue_floor_cents, locked }]`
- `POST /api/v1/autopilot/configure`
  - Request: `{ category, autonomy_level, max_amount_cents?, revenue_floor_cents?, locked? }`
  - Response: `{ id, category, autonomy_level, max_amount_cents, revenue_floor_cents, locked }`
  - Valid categories: `payment`, `pricing`, `reporting`, `categorization`, `alerts`
  - Valid levels: `advisory`, `semi_auto`, `full_auto`

## Approval Endpoints
- `GET /api/v1/approvals`
  - Query: `status?`, `limit=50`, `offset=0`
  - Response: pending/approved/rejected approval actions for the authenticated tenant
- `POST /api/v1/approvals/{id}/approve`
- `POST /api/v1/approvals/{id}/reject`
  - Reject request: `{ reason }`
  - Approval and rejection write audit entries

## Notification Endpoints
- `GET /api/v1/notifications`
  - Query: `type?`, `severity?`, `unread_only=false`, `limit=50`, `offset=0`
- `POST /api/v1/notifications/{id}/read`
- `POST /api/v1/notifications/{id}/dismiss`
  - Read and dismiss operations write audit entries

## Planned Endpoints
- `POST /api/v1/ai/ask` - owned by later Person 2 integration
- `POST /api/v1/ai/scenario` - owned by later Person 2 integration
- `GET /api/v1/ai/anomalies` - owned by later Person 2 integration
