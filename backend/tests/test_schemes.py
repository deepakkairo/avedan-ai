"""
tests/test_schemes.py – Scheme Verification & URL Integrity Tests
==================================================================
Verifies that:
  1. Schemes with verified URLs return valid .gov.in or .nic.in domains.
  2. Unverified application URLs return application_url_verified=False
     and status 'Official application link not verified'.
  3. Authentication instructions match the official portal process and
     do not assume DigiLocker for all schemes.
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_verified_scheme_application_url():
    """
    Requirement 2: Every verified scheme provides its official application URL.
    """
    resp = client.get("/api/schemes/pm-kisan")
    assert resp.status_code == 200
    data = resp.json()
    assert data["application_url_verified"] is True
    assert data["application_url"] == "https://pmkisan.gov.in/RegistrationFormNew.aspx"
    assert data["application_url_status"] == "Verified Official Application Portal"


def test_unverified_scheme_displays_exact_warning():
    """
    Requirement 8: If an official application URL cannot be verified,
    display 'Official application link not verified' and do not invent a URL.
    """
    resp = client.get("/api/schemes/rural-artisan-grant-unverified")
    assert resp.status_code == 200
    data = resp.json()
    assert data["application_url_verified"] is False
    assert data["application_url"] is None
    assert data["application_url_status"] == "Official application link not verified"


def test_auth_types_do_not_assume_digilocker_for_all():
    """
    Requirement 4: Do not assume every scheme requires DigiLocker.
    Display authentication instructions according to verified scheme process.
    """
    # PM-Kisan does not use DigiLocker
    resp_kisan = client.get("/api/schemes/pm-kisan")
    assert resp_kisan.json()["digilocker_supported_on_portal"] is False
    assert resp_kisan.json()["auth_type"] == "aadhaar_otp"

    # Ayushman Bharat uses DigiLocker / MeriPehchaan
    resp_ayushman = client.get("/api/schemes/ayushman-bharat")
    assert resp_ayushman.json()["digilocker_supported_on_portal"] is True
    assert resp_ayushman.json()["auth_type"] == "digilocker_sso"


def test_search_and_filters():
    """
    Verifies category and search filters work accurately.
    """
    # Filter by category: healthcare
    resp = client.get("/api/schemes?category=healthcare")
    assert resp.status_code == 200
    schemes = resp.json()["schemes"]
    assert any(s["id"] == "ayushman-bharat" for s in schemes)

    # Search for 'farmer'
    resp_search = client.get("/api/schemes?query=farmer")
    assert resp_search.status_code == 200
    search_schemes = resp_search.json()["schemes"]
    assert any("pm-kisan" in s["id"] for s in search_schemes)
