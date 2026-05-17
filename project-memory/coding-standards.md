# AI CFO — Coding Standards

## Naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- API routes: `kebab-case` (`/audit-log`, not `/audit_log`)

## API Standards
- All endpoints under `/api/v1/`
- Standard error envelope: `{ "error": { "code", "message", "details" } }`
- Pagination: `page` + `per_page` query params
- Response envelope: `{ "items", "total", "page", "per_page", "total_pages" }`

## Error Handling
- Use `HTTPException` with structured error detail
- Log errors with `exc_info=True`
- Never expose internal errors to clients in production

## Logging
- Use Python `logging` module
- Logger per module: `logging.getLogger(__name__)`
- Format: `%(asctime)s | %(name)s | %(levelname)s | %(message)s`
- Always log: tenant_id, action, outcome

## Testing
- pytest + pytest-asyncio
- Each test gets a fresh database (create/drop tables per function)
- Use fixtures from conftest.py
- Test files: `test_*.py`

## Database
- All tables have UUID primary keys
- All tenant-scoped tables include `tenant_id` FK
- Amounts in BIGINT cents
- Timestamps in UTC with timezone
