"""
tests/test_payments.py – Government Fee & Zero-Fee Compliance Tests
=====================================================================
Verifies that:
  1. AVEDAN charges ₹0 service fee across all endpoints and models.
  2. Government fee is shown only when verified from official portal.
  3. No Razorpay or intermediary payment gateway routes exist.
  4. Intermediary payment attempts are rejected.
  5. Unverified payment statuses are clearly labelled.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from services.payment_service import PaymentService, PaymentComplianceError

client = TestClient(app)


def test_avedan_service_fee_always_zero():
    """
    Core Policy: AVEDAN must not charge any service fee.
    """
    response = client.get("/api/schemes")
    assert response.status_code == 200
    schemes = response.json()["schemes"]
    for s in schemes:
        assert s["avedan_service_fee"] == 0.0


def test_verified_fee_display():
    """
    Requirement 1: Show the government fee only when verified from official portal.
    """
    # PM Kisan is verified free
    resp = client.get("/api/schemes/pm-kisan")
    assert resp.status_code == 200
    data = resp.json()
    assert data["fee_verified"] is True
    assert data["fee_amount"] == 0.0

    # Sarathi Driving Licence has verified government fee
    resp_dl = client.get("/api/schemes/parivahan-driving-licence")
    assert resp_dl.status_code == 200
    dl_data = resp_dl.json()
    assert dl_data["fee_verified"] is True
    assert dl_data["fee_amount"] == 200.0
    assert "parivahan.gov.in" in dl_data["fee_source_url"]


def test_unverified_fee_handling():
    """
    Requirement 1 & 8: Unverified schemes must not display invented fees.
    """
    resp = client.get("/api/schemes/rural-artisan-grant-unverified")
    assert resp.status_code == 200
    data = resp.json()
    assert data["fee_verified"] is False
    assert data["fee_amount"] is None


def test_reject_intermediary_payment_processing():
    """
    Requirement 4 & 8: Never route fees through AVEDAN and never integrate Razorpay.
    """
    with pytest.raises(PaymentComplianceError):
        PaymentService.reject_intermediary_payment({"gateway": "razorpay", "amount": 200})

    with pytest.raises(PaymentComplianceError):
        PaymentService.reject_intermediary_payment({"action": "collect_fee", "amount": 50})


def test_root_manifest_confirms_zero_fee_and_direct_payment():
    """
    Transparency: The API manifest explicitly commits to ₹0 fee and direct portal payment.
    """
    resp = client.get("/")
    assert resp.status_code == 200
    compliance = resp.json()["compliance"]
    assert "₹0.00" in compliance["service_fee"]
    assert "Direct payment on official portals only" in compliance["payment_policy"]
