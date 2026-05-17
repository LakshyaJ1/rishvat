# AI CFO — Security Model

## Authentication
- JWT (HS256) with access (30min) + refresh (7d) tokens
- bcrypt password hashing via passlib
- Token payload: user_id, tenant_id, role, type, exp

## Tenant Isolation (Defense in Depth)
1. **Application layer**: JWT middleware extracts tenant_id, all queries scoped
2. **Database layer**: PostgreSQL RLS policies on all tenant-scoped tables
3. **Qdrant layer**: Separate collection per tenant (Stage 2)

## Encryption
- Connector credentials: AES-256 (Fernet) at rest
- Production: keys from AWS/GCP Secrets Manager

## Audit
- Append-only audit_logs table
- Database trigger prevents UPDATE/DELETE
- Every action logged: auth, connector ops, guardrail decisions, approval decisions, notification state changes, AI recommendations

## Permissions
- All integrations read-only by default
- Write access requires explicit grant per provider
- Shadow mode: 30 days before any autonomous execution
- Stage 2 guardrails enforce per-category autopilot settings before an AI recommendation/action can proceed.
- Non-reversible, jurisdiction-sensitive, warning-bearing, or threshold-exceeding outputs are escalated to founder approval.

## Secrets
- Never in code or .env in production
- AWS Secrets Manager / GCP Secret Manager pattern
