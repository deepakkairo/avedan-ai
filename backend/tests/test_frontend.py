"""
tests/test_frontend.py – Frontend Serving & Access Tests
=========================================================
Verifies that the multilingual, accessible frontend is properly served.
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_frontend_portal_accessible():
    """
    Verifies that the web interface is accessible at /app.
    """
    response = client.get("/app")
    assert response.status_code == 200
    assert "AVEDAN AI" in response.text
    assert "Zero Credential Policy" in response.text
    assert "₹0 Service Fee" in response.text
    assert "Continue to Official Application" in response.text
