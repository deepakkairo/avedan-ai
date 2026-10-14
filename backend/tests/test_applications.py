"""
tests/test_applications.py – Truthful Application Tracking Tests
==================================================================
Verifies that:
  1. Citizens can track their progress without false automation claims.
  2. Submissions reported by users are labelled 'Pending Official Verification'.
  3. No automatic submission or payment is claimed without official integration.
  4. AVEDAN service fee remains 0.0.
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_application_journey():
    """
    Test creating a tracked application journey for PM-Kisan.
    """
    payload = {
        "user_name": "Ramesh Kumar",
        "scheme_id": "pm-kisan",
    }
    resp = client.post("/api/applications", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["scheme_id"] == "pm-kisan"
    assert data["avedan_service_fee"] == 0.0
    assert data["is_verified_by_official_api"] is False
    assert data["status"] == "saved"


def test_user_reported_submission_labeled_pending_verification():
    """
    Requirement 5 & 7: Do not claim AVEDAN submitted or completed an application.
    User reports must be clearly labelled as unverified.
    """
    # Create application first
    create_resp = client.post("/api/applications", json={"scheme_id": "ayushman-bharat"})
    app_id = create_resp.json()["id"]

    # Update to user-reported submitted
    update_payload = {
        "status": "user_reported_submitted",
        "official_acknowledgment_number": "AB-PMJAY-2026-987654",
    }
    resp = client.patch(f"/api/applications/{app_id}/progress", json=update_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "user_reported_submitted"
    assert "Pending Official Verification" in data["status_label"]
    assert data["is_verified_by_official_api"] is False
    assert data["official_acknowledgment_number"] == "AB-PMJAY-2026-987654"


def test_direct_payment_user_report_labeled_unverified():
    """
    Payment Requirement 6: After payment, clearly label any unverified status.
    """
    create_resp = client.post("/api/applications", json={"scheme_id": "parivahan-driving-licence"})
    app_id = create_resp.json()["id"]

    # User reports they paid the official ₹200 on Sarathi portal
    update_payload = {
        "user_reported_payment_done": True,
    }
    resp = client.patch(f"/api/applications/{app_id}/progress", json=update_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["payment_status"] == "user_reported_paid"
    assert "Pending Official Treasury Verification" in data["payment_status_label"]
