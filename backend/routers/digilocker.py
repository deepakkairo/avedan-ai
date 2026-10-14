"""
routers/digilocker.py – DigiLocker Compliance & Status Router
==============================================================
Exposes endpoints for checking DigiLocker integration status, citizen safety
guidelines, and official OAuth authorization (when officially enabled).

STRICT COMPLIANCE:
  - Direct integration is disabled by default until partner approval.
  - Rejects any endpoint attempting to take passwords, PINs, or OTPs.
  - Provides guidance on using DigiLocker directly on official government portals.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from services.digilocker_service import DigiLockerService, DigiLockerComplianceError

router = APIRouter(prefix="/api/digilocker", tags=["DigiLocker"])


class SafetyCheckPayload(BaseModel):
    data: Dict[str, Any]


@router.get("/status")
def get_digilocker_status():
    """
    Returns the official status of DigiLocker integration in AVEDAN AI.
    Confirms direct API is optional/disabled until official government partner approval.
    """
    return DigiLockerService.get_status()


@router.get("/guidelines")
def get_guidelines():
    """
    Citizen guidelines for authenticating safely with DigiLocker on official government sites.
    """
    return {
        "title": "Official Guidelines for Using DigiLocker for Government Schemes",
        "guidelines": DigiLockerService.get_citizen_guidelines(),
        "portal_verification_tip": "Always check that the website domain ends in .gov.in or .nic.in before signing in.",
    }


@router.get("/auth-url")
def get_auth_url(state: str = Query("default_state", description="CSRF prevention state token")):
    """
    Provides the official OAuth authorization URL if partner integration is enabled.
    Returns 403 Forbidden with explanatory guidance if direct integration is inactive.
    """
    result = DigiLockerService.get_official_oauth_url(state)
    if not result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": result["reason"],
                "advisory": result["advisory"],
                "action": "Please proceed to the scheme's verified official portal to authenticate directly.",
            },
        )
    return result


@router.post("/validate-compliance")
def validate_compliance(payload: SafetyCheckPayload):
    """
    Compliance validation check: Ensures no credentials or OTPs enter AVEDAN AI.
    Raises 400 Bad Request if any sensitive credential is provided.
    """
    try:
        DigiLockerService.sanitize_and_audit(payload.data)
        return {"status": "compliant", "message": "No sensitive credentials detected."}
    except DigiLockerComplianceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
