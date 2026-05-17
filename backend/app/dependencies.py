"""
AI CFO — Dependency Injection

Central location for all FastAPI dependencies.
Avoids circular imports by importing from specific modules.
"""

from app.db.session import get_db
from app.middleware.tenant import get_current_user, require_tenant

__all__ = [
    "get_db",
    "get_current_user",
    "require_tenant",
]
