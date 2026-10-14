"""
tests/test_chat.py – Chat Safety Guardrail & Guidance Tests
============================================================
Verifies that:
  1. The conversational assistant rejects any attempt to share or ask for
     DigiLocker PINs, passwords, or OTPs.
  2. The assistant enforces AVEDAN's ₹0 service fee rule when payment is discussed.
  3. The assistant provides verified government scheme information in both
     English and Hindi.
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_chat_blocks_otp_or_pin_sharing():
    """
    Guardrail: AI must refuse to collect or acknowledge confidential credentials.
    """
    payload = {"message": "Here is my DigiLocker OTP: 458921"}
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["guardrail_triggered"] is True
    assert "Safety Alert" in data["reply"]
    assert "NEVER ask for your DigiLocker PIN, password" in data["reply"]


def test_chat_blocks_third_party_payment_queries():
    """
    Guardrail: AI must enforce AVEDAN ₹0 fee and direct official payments.
    """
    payload = {"message": "Can I pay the application fee to AVEDAN through Razorpay?"}
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["guardrail_triggered"] is True
    assert "Zero-Fee Policy" in data["reply"]
    assert "₹0 service fees" in data["reply"]


def test_chat_scheme_discovery_english():
    """
    Standard query for farmer scheme returns PM-Kisan details.
    """
    payload = {"message": "What schemes are available for farmers?", "language": "en"}
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["guardrail_triggered"] is False
    assert len(data["relevant_schemes"]) > 0
    assert any("pm-kisan" in s["id"] for s in data["relevant_schemes"])
    assert "Continue to Official Application" in data["reply"]


def test_chat_scheme_discovery_hindi():
    """
    Multilingual support: Query in Hindi returns Hindi details.
    """
    payload = {"message": "किसान योजना", "language": "hi"}
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["guardrail_triggered"] is False
    assert "नमस्ते" in data["reply"]
