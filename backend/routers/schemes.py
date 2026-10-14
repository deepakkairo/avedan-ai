"""
routers/schemes.py – Scheme Discovery & Verified URL Router
============================================================
Provides public endpoints for browsing, searching, and inspecting
government schemes with verified official application links.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.database import get_db
from services.scheme_service import SchemeService

router = APIRouter(prefix="/api/schemes", tags=["Schemes"])


@router.get("")
def list_schemes(
    query: Optional[str] = Query(None, description="Search term for scheme name or description"),
    category: Optional[str] = Query(None, description="Category filter (e.g. agriculture, healthcare)"),
    state: Optional[str] = Query(None, description="State filter (e.g. central, Maharashtra)"),
    digilocker_only: Optional[bool] = Query(None, description="Filter for schemes using DigiLocker on portal"),
    free_only: Optional[bool] = Query(None, description="Filter for schemes with ₹0 fee"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List schemes with search and compliance verification metadata.
    """
    schemes = SchemeService.list_schemes(
        db=db,
        query=query,
        category=category,
        state=state,
        digilocker_only=digilocker_only,
        free_only=free_only,
        limit=limit,
        offset=offset,
    )
    return {
        "count": len(schemes),
        "schemes": schemes,
    }


@router.get("/categories")
def get_categories():
    """
    Returns available scheme categories for filtering.
    """
    return [
        {"id": "all", "label_en": "All Schemes", "label_hi": "सभी योजनाएं", "icon": "Layers"},
        {"id": "agriculture", "label_en": "Agriculture & Farming", "label_hi": "कृषि एवं किसान", "icon": "Sprout"},
        {"id": "healthcare", "label_en": "Healthcare & Insurance", "label_hi": "स्वास्थ्य एवं बीमा", "icon": "HeartPulse"},
        {"id": "education", "label_en": "Education & Scholarships", "label_hi": "शिक्षा एवं छात्रवृत्ति", "icon": "GraduationCap"},
        {"id": "identity", "label_en": "Identity & Essential Cards", "label_hi": "पहचान एवं आवश्यक दस्तावेज", "icon": "CreditCard"},
        {"id": "housing", "label_en": "Housing & Urban", "label_hi": "आवास एवं शहरी", "icon": "Home"},
        {"id": "women", "label_en": "Women & Child Support", "label_hi": "महिला एवं बाल कल्याण", "icon": "Users"},
        {"id": "transport", "label_en": "Transport & Driving", "label_hi": "परिवहन एवं ड्राइविंग", "icon": "Car"},
    ]


@router.get("/{scheme_id}")
def get_scheme(scheme_id: str, db: Session = Depends(get_db)):
    """
    Fetch a scheme by slug with full verification status.
    If application link is unverified, application_url is None and
    application_url_status is 'Official application link not verified'.
    """
    scheme = SchemeService.get_scheme_by_id(db, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme
