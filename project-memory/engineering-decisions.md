# AI CFO — Engineering Decisions

## ED-001: Async SQLAlchemy with asyncpg
- **Decision**: Use async SQLAlchemy with asyncpg driver
- **Context**: FastAPI is async-native; blocking DB calls degrade performance
- **Chosen Solution**: `create_async_engine` with `asyncpg`
- **Alternatives Rejected**: Sync SQLAlchemy (blocks event loop), raw asyncpg (loses ORM)
- **Reasoning**: Best of both worlds — ORM convenience with async performance
- **Impact**: All DB access is non-blocking; requires async session management
- **Date**: 2026-05-17

## ED-002: Amount storage as BIGINT cents
- **Decision**: Store all financial amounts as BIGINT in smallest currency unit
- **Context**: Floating point arithmetic causes rounding errors in financial calculations
- **Chosen Solution**: `amount_cents` as BIGINT (e.g., $50.00 = 5000)
- **Alternatives Rejected**: DECIMAL (slower), FLOAT (rounding errors), String (unusable for math)
- **Reasoning**: Stripe already uses cents; avoids all float precision issues
- **Impact**: All display logic must divide by 100 (or currency-appropriate factor)
- **Date**: 2026-05-17

## ED-003: Double-layer tenant isolation
- **Decision**: Enforce tenant isolation at both application and database levels
- **Context**: Single application bug could leak data across tenants
- **Chosen Solution**: JWT middleware + PostgreSQL RLS policies
- **Alternatives Rejected**: Application-only (single point of failure), Database-only (no app-level context)
- **Reasoning**: Defense in depth — even if app code has a bug, RLS prevents cross-tenant reads
- **Impact**: Must set `app.current_tenant_id` in every DB session via middleware
- **Date**: 2026-05-17

## ED-004: Fernet encryption for connector credentials
- **Decision**: Use Fernet (AES-256-CBC) for encrypting connector credentials at rest
- **Context**: API keys for Stripe/Plaid must not be stored in plaintext
- **Chosen Solution**: `cryptography.fernet.Fernet` with key from env/secrets manager
- **Alternatives Rejected**: AWS KMS (adds latency, requires AWS), plaintext (unacceptable), custom AES (error-prone)
- **Reasoning**: Fernet is a well-audited, symmetric encryption scheme; key management is separate
- **Impact**: Encryption key must be managed via Secrets Manager in production
- **Date**: 2026-05-17

## ED-005: Audit log immutability via database trigger
- **Decision**: Enforce append-only audit log with a PostgreSQL trigger
- **Context**: Audit logs must be tamper-proof for compliance
- **Chosen Solution**: `BEFORE UPDATE OR DELETE` trigger that raises an exception
- **Alternatives Rejected**: Application-only enforcement (bypassable), separate audit database (overkill for Stage 1)
- **Reasoning**: Database trigger is the strongest guarantee; cannot be bypassed by application bugs
- **Impact**: Audit log corrections require a new append entry, not an update
- **Date**: 2026-05-17

## ED-006: Celery with ack-late for reliability
- **Decision**: Configure Celery with `task_acks_late=True`
- **Context**: Sync tasks fetch external API data; failure mid-task loses work
- **Chosen Solution**: Ack after task completion + 3 retries with 60s delay
- **Alternatives Rejected**: Default ack (data loss on worker crash), no retries (brittle)
- **Reasoning**: Financial data sync must be reliable; ack-late ensures tasks re-run on failure
- **Impact**: Tasks must be idempotent (handled via upsert pattern)
- **Date**: 2026-05-17
