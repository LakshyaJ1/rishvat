# AI CFO — Architecture

See `backend-architecture.md` for backend details. This file covers the full system architecture.

## System Layers
1. **Frontend** (React + Vite) → Person 3
2. **API** (FastAPI) → Person 1 ✅
3. **Data** (PostgreSQL + Redis) → Person 1 ✅
4. **AI** (Ollama + LangGraph + Qdrant) → Person 2
5. **Guardrails** (Python rules) → Person 1 (Stage 2)
6. **Integrations** (Celery workers) → Person 1 ✅

## Data Flow
```
User → Frontend → FastAPI → LangGraph → Qdrant (RAG) + Metrics → Ollama → Guardrails → Audit Log → Response
```

## Tenant Isolation
- JWT carries tenant_id
- Every query scoped to tenant_id
- PostgreSQL RLS as second layer
- Qdrant: separate collection per tenant
