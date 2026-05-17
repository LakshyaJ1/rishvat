"""
AI CFO — FastAPI Application

Main application factory and startup configuration.
All routes are registered here under the /api/v1 prefix.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.middleware.logging import RequestLoggingMiddleware

settings = get_settings()

# ── Logging Configuration ────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.is_development else logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("aicfo")


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"AI CFO Backend v{settings.app_version} starting...")
    logger.info(f"Environment: {settings.app_env}")

    # Initialize Sentry if configured
    if settings.sentry_dsn:
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=settings.sentry_dsn,
                environment=settings.app_env,
                traces_sample_rate=0.1,
            )
            logger.info("Sentry initialized")
        except Exception as e:
            logger.warning(f"Sentry initialization failed: {e}")

    yield

    logger.info("AI CFO Backend shutting down...")


# ── Application Factory ──────────────────────────────────────────────────────

app = FastAPI(
    title="AI CFO API",
    description=(
        "AI-native financial operating system for startups. "
        "Privacy-first, human-in-the-loop, fully auditable."
    ),
    version=settings.app_version,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging
app.add_middleware(RequestLoggingMiddleware)

# ── Routes ────────────────────────────────────────────────────────────────────

from app.auth.router import router as auth_router
from app.routers.health import router as health_router
from app.routers.integrations import router as integrations_router
from app.routers.audit import router as audit_router
from app.routers.financials import router as financials_router
from app.routers.guardrails import router as guardrails_router
from app.routers.notifications import router as notifications_router
from app.routers.approvals import router as approvals_router
from app.routers.autopilot import router as autopilot_router

# Health endpoints (no prefix — accessible at /api/v1/health)
app.include_router(health_router, prefix=settings.api_prefix)

# Auth endpoints
app.include_router(auth_router, prefix=settings.api_prefix)

# Integration endpoints
app.include_router(integrations_router, prefix=settings.api_prefix)

# Audit log endpoints
app.include_router(audit_router, prefix=settings.api_prefix)

# Deterministic financial metric endpoints
app.include_router(financials_router, prefix=settings.api_prefix)

# Guardrails validation endpoints
app.include_router(guardrails_router, prefix=settings.api_prefix)

# Notification endpoints
app.include_router(notifications_router, prefix=settings.api_prefix)

# Approval inbox endpoints
app.include_router(approvals_router, prefix=settings.api_prefix)

# Autopilot configuration endpoints
app.include_router(autopilot_router, prefix=settings.api_prefix)


# ── Root Endpoint ─────────────────────────────────────────────────────────────

@app.get("/", tags=["root"])
async def root():
    """Root endpoint — confirms the API is running."""
    return {
        "name": "AI CFO API",
        "version": settings.app_version,
        "docs": "/docs" if settings.is_development else None,
    }
