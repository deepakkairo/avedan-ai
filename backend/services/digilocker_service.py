"""
services/digilocker_service.py – DigiLocker Compliance & Integration Service
=============================================================================
Manages DigiLocker integration state in strict compliance with safety rules:
  1. Direct DigiLocker API integration is OPTIONAL and DISABLED by default until
     official partner approval, credentials, consent handling, and secure backend
     implementation are verified.
  2. Zero Credential Interception: NEVER requests, accepts, or stores DigiLocker
     passwords, security PINs, or OTPs.
  3. Directs citizens to authenticate on official government portals (MeriPehchaan/DigiLocker).
"""

import logging
import urllib.parse
from typing import Any, Optional

from config import settings

logger = logging.getLogger(__name__)

# List of forbidden keys that must never be handled by AVEDAN
FORBIDDEN_CREDENTIAL_KEYS = {
    "password", "pin", "security_pin", "otp", "one_time_password",
    "cvv", "card_number", "mpin", "tpin"
}


class DigiLockerComplianceError(ValueError):
    """Raised when a request violates DigiLocker credential security policies."""
    pass


class DigiLockerService:
    """
    Manages official DigiLocker partner status, citizen safety guidance,
    and official OAuth authorization flow when authorized.
    """

    @staticmethod
    def get_status() -> dict[str, Any]:
        """
        Returns the current DigiLocker integration status for AVEDAN AI.
        Direct API is disabled by default until official partner credentials exist.
        """
        is_enabled = settings.digilocker_integration_enabled and bool(
            settings.digilocker_client_id and settings.digilocker_client_secret
        )

        return {
            "integration_enabled": is_enabled,
            "partner_status": settings.digilocker_partner_status,
            "compliance_policy": {
                "zero_credential_storage": True,
                "no_fake_login_forms": True,
                "no_third_party_otp_handling": True,
                "dpdp_act_compliant": True,
            },
            "status_message": (
                "Official DigiLocker direct API integration is currently pending government partner certification. "
                "Citizens should authenticate directly on official scheme portals via MeriPehchaan / DigiLocker."
                if not is_enabled
                else "DigiLocker official partner integration is active."
            ),
            "official_portal_guidance": DigiLockerService.get_citizen_guidelines(),
        }

    @staticmethod
    def get_citizen_guidelines() -> list[dict[str, str]]:
        """
        Advisory instructions for Indian citizens on authenticating safely via DigiLocker.
        """
        return [
            {
                "title": "Always verify official government domains",
                "detail": "Only authenticate DigiLocker on portals ending with .gov.in, .nic.in, or official SSO (meripehchaan.gov.in). Never enter your credentials on private websites.",
            },
            {
                "title": "Never share your 6-digit DigiLocker PIN or OTP",
                "detail": "AVEDAN AI and government officials will never ask for your DigiLocker PIN, Aadhaar OTP, or login password. Do not share them with anyone or any AI tool.",
            },
            {
                "title": "Individual Document Consent",
                "detail": "When an official government portal asks to fetch a document from DigiLocker, it will clearly list the exact document requested (e.g. Caste Certificate or Marksheet) and require your explicit consent.",
            },
            {
                "title": "DigiLocker is Free",
                "detail": "DigiLocker is a free digital public infrastructure provided by the Government of India. There are no fees to view, link, or download your verified digital documents.",
            },
        ]

    @staticmethod
    def sanitize_and_audit(payload: dict[str, Any]) -> None:
        """
        Guarantees that no passwords, PINs, or OTPs enter AVEDAN's system.
        Raises DigiLockerComplianceError if any forbidden credential is detected.
        """
        for key in payload.keys():
            normalized = key.lower().replace("-", "_").replace(" ", "_")
            if any(forbidden in normalized for forbidden in FORBIDDEN_CREDENTIAL_KEYS):
                logger.warning(
                    "Security Violation: Attempted to submit sensitive credential key '%s'", key
                )
                raise DigiLockerComplianceError(
                    f"AVEDAN AI does not accept or store '{key}'. "
                    "Authentication must occur directly on official government portals."
                )

    @staticmethod
    def get_official_oauth_url(state: str) -> dict[str, Any]:
        """
        Generates the official OAuth authorization redirect URL.
        Only allowed if direct partner integration is officially enabled and configured.
        """
        if not (settings.digilocker_integration_enabled and settings.digilocker_client_id):
            return {
                "allowed": False,
                "reason": "Official partner credentials are not configured or direct integration is disabled.",
                "redirect_url": None,
                "advisory": "Please authenticate directly on the scheme's verified official portal.",
            }

        params = {
            "response_type": "code",
            "client_id": settings.digilocker_client_id,
            "redirect_uri": settings.digilocker_redirect_uri,
            "state": state,
        }
        url = f"{settings.digilocker_auth_url}?{urllib.parse.urlencode(params)}"
        return {
            "allowed": True,
            "reason": "Authorized partner flow",
            "redirect_url": url,
            "advisory": "You will be redirected to the official Digital India portal (api.digitallocker.gov.in).",
        }
