"""
tests/test_digilocker.py – DigiLocker Compliance Tests
========================================================
Verifies that:
  1. Direct DigiLocker API integration is optional and disabled by default.
  2. AVEDAN AI never accepts, prompts for, or stores PINs, passwords, or OTPs.
  3. Attempting to pass credentials triggers 400 Bad Request.
  4. The User database model has no credential/OTP columns.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from models.user import User

client = TestClient(app)


def test_digilocker_disabled_by_default():
    """
    Requirement 6: Direct DigiLocker API integration must be optional
    and disabled until official partner approval.
    """
    response = client.get("/api/digilocker/status")
    assert response.status_code == 200
    data = response.json()
    assert data["integration_enabled"] is False
    assert data["partner_status"] == "pending_approval"
    assert data["compliance_policy"]["zero_credential_storage"] is True
    assert data["compliance_policy"]["no_fake_login_forms"] is True


def test_auth_url_blocked_when_disabled():
    """
    Accessing the auth redirect when partner integration is disabled
    must return HTTP 403 with guidance to use the official portal.
    """
    response = client.get("/api/digilocker/auth-url")
    assert response.status_code == 403
    error_detail = response.json()["detail"]
    assert "Official partner credentials are not configured" in error_detail["message"]


def test_zero_credential_storage_rejection():
    """
    Requirement 1 & 7: Never accept or store DigiLocker password, PIN, or OTP.
    """
    forbidden_payloads = [
        {"data": {"otp": "123456"}},
        {"data": {"security_pin": "9999"}},
        {"data": {"password": "secret_password"}},
        {"data": {"cvv": "123"}},
    ]

    for payload in forbidden_payloads:
        response = client.post("/api/digilocker/validate-compliance", json=payload)
        assert response.status_code == 400
        assert "does not accept or store" in response.json()["detail"]


def test_safe_guidelines_endpoint():
    """
    Requirement 3 & 4: Provide citizens with authentic instructions on how
    to authenticate safely on official government portals.
    """
    response = client.get("/api/digilocker/guidelines")
    assert response.status_code == 200
    data = response.json()
    assert "guidelines" in data
    assert len(data["guidelines"]) >= 4
    # Check that warning against sharing PIN exists in guidelines
    assert any("PIN or OTP" in g["title"] or "PIN" in g["detail"] for g in data["guidelines"])


def test_user_model_has_no_credential_fields():
    """
    Requirement 7: Verify User table schema strictly avoids passwords, PINs, OTPs.
    """
    columns = [c.name for c in User.__table__.columns]
    assert "password" not in columns
    assert "pin" not in columns
    assert "otp" not in columns
    assert "security_pin" not in columns
    assert "aadhaar_full" not in columns
    assert "aadhaar_last4" in columns  # Only masked last 4 allowed
