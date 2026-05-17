# AI CFO — Infrastructure & Deployment

## Docker Architecture
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| postgres | postgres:16-alpine | 5432 | Primary database |
| redis | redis:7-alpine | 6379 | Cache + Celery broker |
| backend | custom (Python 3.11) | 8000 | FastAPI API |
| celery-worker | same as backend | — | Background tasks |
| celery-beat | same as backend | — | Task scheduler |

## Environments
- **Development**: docker-compose with hot reload
- **Production**: Multi-worker, non-root user, no docs endpoint

## Secrets Management
- Dev: `.env` file (gitignored)
- Prod: AWS/GCP Secrets Manager

## Health Checks
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- Backend: `GET /api/v1/health`
