"""
models/application.py – AVEDAN AI Application Model
=====================================================
Tracks a citizen's journey through discovering, navigating to,
and applying for a government scheme.

TRUTHFUL STATUS POLICY:
  - AVEDAN never claims an application is submitted, paid, or verified
    unless confirmed via an authorized official API.
  - User-reported milestones are explicitly labelled as
    'USER_REPORTED_PENDING_VERIFICATION'.
  - AVEDAN NEVER collects payments; avedan_service_fee is strictly 0.0.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum as SAEnum, func,
)
from sqlalchemy.orm import relationship

from models.database import Base


# ─────────────────────────────────────────────────────────────────────────────
# Status Enums
# ─────────────────────────────────────────────────────────────────────────────

class ApplicationStatus(str, enum.Enum):
    """
    Lifecycle status of an application journey.
    Strictly distinguishes between officially verified states and user reports.
    """
    SAVED = "saved"                                     # Scheme saved to dashboard
    CONTINUED_TO_OFFICIAL_PORTAL = "continued_to_portal" # User clicked verified link to official portal
    IN_PROGRESS = "in_progress"                         # User is completing form on official portal
    USER_REPORTED_SUBMITTED = "user_reported_submitted" # User reported submission; pending govt confirmation
    OFFICIALLY_VERIFIED = "officially_verified"         # Confirmed via official API
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentStatus(str, enum.Enum):
    """
    Payment status reflecting direct government portal payments.
    AVEDAN never processes payments.
    """
    NOT_APPLICABLE = "not_applicable"                   # Free scheme (₹0 fee)
    PENDING_ON_GOVERNMENT_PORTAL = "pending_on_portal"  # Official fee must be paid directly on govt site
    USER_REPORTED_PAID = "user_reported_paid"           # User confirms paying on govt portal (unverified)
    OFFICIALLY_VERIFIED = "officially_verified"         # Verified via official integration


# ─────────────────────────────────────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────────────────────────────────────

class Application(Base):
    """
    Represents a citizen's tracked application for a government scheme.
    """

    __tablename__ = "applications"

    # ── Primary Key ───────────────────────────────────────────────────────────
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )

    # ── Foreign Key ───────────────────────────────────────────────────────────
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Scheme Reference ──────────────────────────────────────────────────────
    scheme_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Scheme slug, e.g. 'pm-kisan'",
    )
    scheme_name = Column(
        String(500),
        nullable=False,
        comment="Official scheme name",
    )
    scheme_state = Column(
        String(100),
        nullable=True,
        default="central",
    )

    # ── Official Application Links & Verification ─────────────────────────────
    official_application_url = Column(
        String(1000),
        nullable=True,
        comment="Verified official government portal application URL",
    )
    application_url_verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ── Status Tracking ───────────────────────────────────────────────────────
    status = Column(
        SAEnum(ApplicationStatus),
        default=ApplicationStatus.SAVED,
        nullable=False,
        index=True,
    )
    status_label = Column(
        String(255),
        default="Saved for Reference",
        nullable=False,
    )
    is_verified_by_official_api = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="False unless confirmed via authorized official API integration",
    )

    # ── Official Acknowledgment Number (User Provided) ───────────────────────
    official_acknowledgment_number = Column(
        String(255),
        nullable=True,
        comment="Application/Registration reference number given by official portal",
    )

    # ── Government Fee & Payment Tracking ─────────────────────────────────────
    official_fee_amount = Column(
        Float,
        default=0.0,
        nullable=False,
        comment="Official government fee in INR (0.0 for free)",
    )
    avedan_service_fee = Column(
        Float,
        default=0.0,
        nullable=False,
        comment="Strictly 0.0 at all times. AVEDAN is 100% free.",
    )
    official_payment_url = Column(
        String(1000),
        nullable=True,
        comment="Direct URL to official government payment portal",
    )
    payment_status = Column(
        SAEnum(PaymentStatus),
        default=PaymentStatus.NOT_APPLICABLE,
        nullable=False,
    )
    payment_status_label = Column(
        String(255),
        default="No Fee Required",
        nullable=False,
    )

    # ── Progress Advisory Message ─────────────────────────────────────────────
    progress_notes = Column(
        Text,
        nullable=True,
        comment="Transparent explanation of current step and official portal instructions",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    user = relationship("User", back_populates="applications")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "scheme_id": self.scheme_id,
            "scheme_name": self.scheme_name,
            "scheme_state": self.scheme_state,
            "official_application_url": self.official_application_url,
            "application_url_verified": self.application_url_verified,
            "status": self.status.value,
            "status_label": self.status_label,
            "is_verified_by_official_api": self.is_verified_by_official_api,
            "official_acknowledgment_number": self.official_acknowledgment_number,
            "official_fee_amount": self.official_fee_amount,
            "avedan_service_fee": self.avedan_service_fee,
            "official_payment_url": self.official_payment_url,
            "payment_status": self.payment_status.value,
            "payment_status_label": self.payment_status_label,
            "progress_notes": self.progress_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Application id={self.id} scheme={self.scheme_id} status={self.status}>"
