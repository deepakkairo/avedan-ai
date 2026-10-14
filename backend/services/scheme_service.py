"""
services/scheme_service.py – Scheme Query & Verification Service
================================================================
Handles querying schemes from SQLite/PostgreSQL with strict URL verification:
  - If an official application URL cannot be verified, sets
    application_url_verified=False and ensures UI displays:
    "Official application link not verified".
  - Validates official domains against known government TLDs (.gov.in, .nic.in).
"""

import logging
import urllib.parse
from typing import Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from models.scheme import Scheme

logger = logging.getLogger(__name__)

# Recognized official Indian government domains
OFFICIAL_GOVT_DOMAIN_SUFFIXES = (
    ".gov.in",
    ".nic.in",
    ".ac.in",
    "digitallocker.gov.in",
    "meripehchaan.gov.in",
    "pmkisan.gov.in",
    "pmjay.gov.in",
    "scholarships.gov.in",
    "parivahan.gov.in",
    "incometax.gov.in",
)


def is_official_government_url(url: Optional[str]) -> bool:
    """
    Checks if a URL has a valid official government hostname.
    """
    if not url:
        return False
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        # Strip port if present
        if ":" in netloc:
            netloc = netloc.split(":")[0]
        return any(netloc.endswith(suffix) or netloc == suffix for suffix in OFFICIAL_GOVT_DOMAIN_SUFFIXES)
    except Exception as exc:
        logger.warning("Failed to parse URL %s: %s", url, exc)
        return False


class SchemeService:
    """
    Query, search, and URL verification service for schemes.
    """

    @staticmethod
    def list_schemes(
        db: Session,
        query: Optional[str] = None,
        category: Optional[str] = None,
        state: Optional[str] = None,
        digilocker_only: Optional[bool] = None,
        free_only: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        List schemes with optional filters.
        """
        q = db.query(Scheme)

        if category and category != "all":
            q = q.filter(Scheme.category == category)

        if state and state != "all":
            normalized_state = state.strip().lower()
            if normalized_state == "central":
                q = q.filter(Scheme.state == "central")
            else:
                q = q.filter(or_(Scheme.state == state, Scheme.state == "central"))

        if digilocker_only is True:
            q = q.filter(Scheme.digilocker_supported_on_portal == True)

        if free_only is True:
            q = q.filter(Scheme.fee_amount == 0.0)

        if query and query.strip():
            raw_text = query.strip().lower()
            stop_words = {"what", "which", "where", "how", "who", "when", "scheme", "schemes", "available", "show", "tell", "need", "for", "the", "are", "any", "and", "can", "get", "with", "from", "about"}
            tokens = [t.strip("?,.!") for t in raw_text.split() if len(t.strip("?,.!")) >= 3 and t.strip("?,.!") not in stop_words]
            
            # Match whole phrase or any significant keyword
            conditions = [
                Scheme.name.ilike(f"%{raw_text}%"),
                Scheme.name_hi.ilike(f"%{raw_text}%"),
                Scheme.description.ilike(f"%{raw_text}%"),
                Scheme.eligibility.ilike(f"%{raw_text}%"),
            ]
            for tok in tokens:
                # Also handle singular / plural e.g. farmers -> farmer
                singular = tok.rstrip("s") if tok.endswith("s") and len(tok) > 4 else tok
                conditions.extend([
                    Scheme.name.ilike(f"%{singular}%"),
                    Scheme.name_hi.ilike(f"%{singular}%"),
                    Scheme.description.ilike(f"%{singular}%"),
                    Scheme.eligibility.ilike(f"%{singular}%"),
                    Scheme.category.ilike(f"%{singular}%"),
                ])
            q = q.filter(or_(*conditions))

        schemes = q.offset(offset).limit(limit).all()
        return [SchemeService.format_scheme_response(s) for s in schemes]

    @staticmethod
    def get_scheme_by_id(db: Session, scheme_id: str) -> Optional[dict[str, Any]]:
        """
        Fetch a scheme by ID and return formatted dict with verification flags.
        """
        scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
        if not scheme:
            return None
        return SchemeService.format_scheme_response(scheme)

    @staticmethod
    def format_scheme_response(scheme: Scheme) -> dict[str, Any]:
        """
        Formats a scheme object into an API dictionary, rigorously enforcing:
          - If application_url is None or not verified, application_url_status
            is explicitly 'Official application link not verified'.
        """
        data = scheme.to_dict()

        # Strict link verification check
        has_verified_url = bool(
            scheme.application_url
            and scheme.application_url_verified
            and is_official_government_url(scheme.application_url)
        )

        data["application_url_verified"] = has_verified_url
        if not has_verified_url:
            data["application_url"] = None
            data["application_url_status"] = "Official application link not verified"
        else:
            data["application_url_status"] = "Verified Official Application Portal"

        # Verification of main official URL
        data["official_url_verified"] = is_official_government_url(scheme.official_url)

        return data
