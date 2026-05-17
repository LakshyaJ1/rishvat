# AI CFO — Skills & Capabilities

## Established Capabilities

### Infrastructure
- ✅ FastAPI project structure with modular architecture
- ✅ Docker Compose multi-service orchestration
- ✅ Multi-stage Dockerfile (dev/prod)
- ✅ Async SQLAlchemy with connection pooling

### Security
- ✅ JWT authentication (access + refresh tokens)
- ✅ bcrypt password hashing
- ✅ PostgreSQL Row-Level Security (RLS) for tenant isolation
- ✅ AES-256 credential encryption (Fernet)
- ✅ Audit log immutability trigger

### Data
- ✅ Multi-tenant database schema with UUID primary keys
- ✅ Alembic migrations with RLS policies
- ✅ Canonical financial record schema (BIGINT cents)
- ✅ Append-only audit log

### Integrations
- ✅ Abstract connector pattern (BaseConnector)
- ✅ Stripe connector (charges + refunds normalization)
- ✅ Plaid connector (transactions with sign inversion)
- ✅ Encrypted credential storage
- ✅ Read-only default permissions

### Background Processing
- ✅ Celery with Redis broker
- ✅ Periodic task scheduling (Celery Beat)
- ✅ Retry orchestration (3 retries, 60s delay, ack-late)
- ✅ Connector sync pipeline (fetch → normalize → upsert)

### Testing
- ✅ pytest-asyncio test infrastructure
- ✅ Test fixtures (db session, client, tenant, user, auth headers)
- ✅ Auth endpoint tests
- ✅ Tenant isolation tests
- ✅ Connector normalization tests
