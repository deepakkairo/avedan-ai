"""
models/user.py – AVEDAN AI User Model
======================================
Stores basic user identity data with strict privacy controls:
  - digilocker_id is optional and nullable.
  - Zero Credential Storage: AVEDAN NEVER stores DigiLocker passwords,
    security PINs, or OTPs.
  - Aadhaar: Only the last 4 digits are stored if explicitly provided;
    full Aadhaar numbers are NEVER stored.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship

from models.database import Base


class User(Base):
    """
    Represents an AVEDAN AI user.
    """

    __tablename__ = "users"

    # ── Primary Key (string UUID for universal SQLite / Postgres support) ──────
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="Internal AVEDAN user ID",
    )

    # ── DigiLocker Identity (Optional & Nullable) ─────────────────────────────
    digilocker_id = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="DigiLocker unique user identifier (populated only if officially authenticated via partner OAuth)",
    )

    # ── User Details ──────────────────────────────────────────────────────────
    name = Column(
        String(255),
        nullable=True,
        comment="Name of citizen",
    )
    mobile = Column(
        String(15),
        nullable=True,
        comment="Contact number",
    )
    dob = Column(
        String(20),
        nullable=True,
        comment="Date of birth in DD-MM-YYYY format",
    )
    gender = Column(
        String(10),
        nullable=True,
        comment="Gender: M / F / T / Other",
    )

    # ── Masked Aadhaar (Last 4 only - NEVER store full Aadhaar) ───────────────
    aadhaar_last4 = Column(
        String(4),
        nullable=True,
        comment="Last 4 digits of Aadhaar only",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    applications = relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "digilocker_linked": bool(self.digilocker_id),
            "aadhaar_last4": self.aadhaar_last4,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r}>"
