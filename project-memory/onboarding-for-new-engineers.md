# AI CFO — Onboarding for New Engineers

## Prerequisites
- Python 3.11+
- Docker + Docker Compose
- Git

## Quick Start
```bash
# Clone the repo
git clone <repo-url>
cd rishvat

# Start all services
docker-compose up --build

# The API is available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Architecture Overview
Read `project-memory/` docs in this order:
1. `project-overview.md`
2. `backend-architecture.md`
3. `database-schema.md`
4. `api-contracts.md`
5. `coding-standards.md`

## Running Tests
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## Key Conventions
- All amounts in BIGINT cents
- All times in UTC
- All tables have tenant_id (except tenants itself)
- Audit log is append-only
- Connectors are read-only by default
