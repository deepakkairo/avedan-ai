"""
main.py – AVEDAN AI FastAPI Application Entry Point
=====================================================
The central API service for AVEDAN AI.

COMPLIANCE & INTEGRITY ASSURANCES:
  1. Zero Fee Policy: AVEDAN AI charges ₹0 service fees and does not collect
     government fees.
  2. Direct DigiLocker Integration is OPTIONAL and DISABLED by default until
     official partner certification from MeitY is active.
  3. Schemes display verified official links or "Official application link not verified".
  4. Never stores DigiLocker PINs, passwords, or OTPs.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models.database import create_all_tables
from data.seed_schemes import seed_database
from routers import schemes, digilocker, applications, chat

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("avedan_ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler for startup initialization and shutdown cleanup."""
    logger.info("Initializing AVEDAN AI database...")
    create_all_tables()
    # Seed default schemes if database was freshly initialized
    try:
        seed_database()
    except Exception as exc:
        logger.warning("Seed database notice: %s", exc)
    logger.info("AVEDAN AI backend initialized successfully.")
    yield
    logger.info("Shutting down AVEDAN AI backend.")


app = FastAPI(
    title="AVEDAN AI API",
    description=(
        "Citizen-first Government Scheme Assistant with DigiLocker compliance, "
        "verified official portal links, and zero-fee transparency."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows frontend in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register API Routers ──────────────────────────────────────────────────────
app.include_router(schemes.router)
app.include_router(digilocker.router)
app.include_router(applications.router)
app.include_router(chat.router)

# ── Mount Frontend Web Portal ────────────────────────────────────────────────
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/portal", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="portal")

    @app.get("/app", include_in_schema=False)
    def serve_app():
        return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/")
def root():
    """
    Root transparency manifest.
    """
    return {
        "app": "AVEDAN AI",
        "description": "Government Scheme Discovery & Application Guidance Platform",
        "version": settings.app_version,
        "compliance": {
            "service_fee": "₹0.00 (100% Free Public Service)",
            "digilocker_direct_api": "Disabled pending official government partner approval",
            "credential_policy": "Zero retention of passwords, PINs, or OTPs",
            "payment_policy": "Direct payment on official portals only; no intermediary collection",
        },
        "endpoints": {
            "schemes": "/api/schemes",
            "categories": "/api/schemes/categories",
            "digilocker_status": "/api/digilocker/status",
            "digilocker_guidelines": "/api/digilocker/guidelines",
            "applications": "/api/applications",
            "chat": "/api/chat",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health_check():
    """Service health check."""
    return {"status": "healthy", "environment": settings.environment}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
