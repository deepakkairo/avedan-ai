"""
models/database.py – SQLAlchemy Database Setup
===============================================
Provides Base, engine, SessionLocal, and the get_db dependency
used across all routers for database access. Supports SQLite
for lightweight local development/tests and PostgreSQL for production.
"""

import logging
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool

from config import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Engine Configuration
# ─────────────────────────────────────────────────────────────────────────────

if settings.database_url.startswith("sqlite"):
    # SQLite configuration for dev/testing
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        poolclass=StaticPool,
        echo=False,
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,
    )

# ─────────────────────────────────────────────────────────────────────────────
# Session Factory
# ─────────────────────────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# ─────────────────────────────────────────────────────────────────────────────
# Declarative Base
# ─────────────────────────────────────────────────────────────────────────────

Base = declarative_base()


# ─────────────────────────────────────────────────────────────────────────────
# Database Dependency & Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:
        logger.error("Database session error: %s", exc)
        db.rollback()
        raise
    finally:
        db.close()


def create_all_tables() -> None:
    """
    Create all tables defined in ORM models.
    Safe to call multiple times.
    """
    from models import user, application, scheme  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("All database tables created / verified.")
