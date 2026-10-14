"""
models/scheme.py – AVEDAN AI Scheme Model
==========================================
Relational storage for government schemes with strict compliance rules:
  1. verified official application URL tracking. If unverified, application_url
     must be None or flagged so UI displays "Official application link not verified".
  2. auth_type & auth_instructions reflect the real government portal process.
     Never assumes every scheme uses DigiLocker.
  3. fee_amount is sourced ONLY from official government portals.
  4. official_payment_page_url directs users directly to the government portal.
     AVEDAN never collects fees.
"""

from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Float, String, Text, JSON, func,
)

from models.database import Base


class Scheme(Base):
    """
    Represents a verified or monitored central or state government scheme.
    """

    __tablename__ = "schemes"

    # ── Primary Key (slug) ────────────────────────────────────────────────────
    id = Column(
        String(255),
        primary_key=True,
        comment="URL-safe slug, e.g. 'pm-kisan', 'ayushman-bharat'",
    )

    # ── Basic Info & Multilingual Names ───────────────────────────────────────
    name = Column(String(500), nullable=False, comment="Full official scheme name in English")
    name_hi = Column(String(500), nullable=True, comment="Official scheme name in Hindi")
    category = Column(
        String(100),
        nullable=False,
        default="general",
        index=True,
        comment="Category: agriculture, healthcare, education, identity, housing, women, transport",
    )
    ministry = Column(
        String(300),
        nullable=True,
        comment="Ministry / Department responsible",
    )
    state = Column(
        String(100),
        nullable=False,
        default="central",
        index=True,
        comment="'central' for national schemes, or state name e.g. 'Maharashtra'",
    )

    # ── Description & Eligibility ─────────────────────────────────────────────
    description = Column(Text, nullable=False, comment="What the scheme provides")
    description_hi = Column(Text, nullable=True, comment="Hindi translation of description")
    eligibility = Column(Text, nullable=False, comment="Eligibility criteria in plain text")
    eligibility_hi = Column(Text, nullable=True, comment="Hindi eligibility criteria")

    # ── Documents Required ────────────────────────────────────────────────────
    documents_required = Column(
        JSON,
        nullable=True,
        default=list,
        comment="List of documents needed by citizen before applying",
    )

    # ── Official Application URLs & Verification Status ───────────────────────
    official_url = Column(
        String(1000),
        nullable=False,
        comment="Main informational website on official .gov.in or .nic.in domain",
    )
    application_url = Column(
        String(1000),
        nullable=True,
        comment="Direct verified online application link on official portal. None if unverified.",
    )
    application_url_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="If False or application_url is None, UI MUST display 'Official application link not verified'",
    )

    # ── Authentication Requirements on Government Portal ──────────────────────
    auth_type = Column(
        String(100),
        nullable=False,
        default="aadhaar_otp",
        comment="Mode: 'digilocker_sso' | 'aadhaar_otp' | 'state_portal_login' | 'in_person_csc' | 'none_offline' | 'unverified'",
    )
    auth_instructions = Column(
        Text,
        nullable=False,
        comment="Citizen instructions for authenticating safely on the official portal",
    )
    digilocker_supported_on_portal = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True if the official government portal allows login/e-KYC via DigiLocker / MeriPehchaan",
    )
    digilocker_notes = Column(
        Text,
        nullable=True,
        comment="Advisory on how DigiLocker is used on the official portal (e.g. document fetching vs login)",
    )

    # ── Official Government Fee Information ───────────────────────────────────
    fee_amount = Column(
        Float,
        nullable=True,
        comment="Application fee in INR as verified from official portal. 0.0 means free.",
    )
    fee_currency = Column(
        String(10),
        nullable=False,
        default="INR",
    )
    fee_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True ONLY if verified from official government circular or portal",
    )
    fee_verified_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when fee was last officially confirmed",
    )
    fee_source_url = Column(
        String(1000),
        nullable=True,
        comment="Official URL where fee was verified",
    )
    official_payment_page_url = Column(
        String(1000),
        nullable=True,
        comment="Official government portal payment URL. Citizen pays directly on govt site.",
    )
    official_payment_methods = Column(
        JSON,
        nullable=True,
        default=list,
        comment="Payment methods supported directly on the government portal (e.g. Bharatkosh, NetBanking, UPI on portal)",
    )

    # ── API Integration Status ────────────────────────────────────────────────
    has_api = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True ONLY if AVEDAN has an authorized official API integration",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict:
        """Serialize model for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "name_hi": self.name_hi,
            "category": self.category,
            "ministry": self.ministry,
            "state": self.state,
            "description": self.description,
            "description_hi": self.description_hi,
            "eligibility": self.eligibility,
            "eligibility_hi": self.eligibility_hi,
            "documents_required": self.documents_required or [],
            "official_url": self.official_url,
            "application_url": self.application_url,
            "application_url_verified": bool(self.application_url_verified and self.application_url),
            "auth_type": self.auth_type,
            "auth_instructions": self.auth_instructions,
            "digilocker_supported_on_portal": self.digilocker_supported_on_portal,
            "digilocker_notes": self.digilocker_notes,
            "fee_amount": self.fee_amount,
            "fee_currency": self.fee_currency,
            "fee_verified": self.fee_verified,
            "fee_verified_at": self.fee_verified_at.isoformat() if self.fee_verified_at else None,
            "fee_source_url": self.fee_source_url,
            "official_payment_page_url": self.official_payment_page_url,
            "official_payment_methods": self.official_payment_methods or [],
            "has_api": self.has_api,
            "avedan_service_fee": 0.0,  # Always ₹0
        }

    def __repr__(self) -> str:
        return f"<Scheme id={self.id!r} name={self.name!r} verified={self.application_url_verified}>"
