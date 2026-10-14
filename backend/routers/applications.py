"""
routers/applications.py – Application Journey & Status Tracking Router
======================================================================
Allows citizens to save schemes, record their journey, and log
official acknowledgment references from government portals.

TRUTHFUL REPORTING:
  - Any milestone logged by the user is clearly marked as
    'USER_REPORTED_PENDING_VERIFICATION'.
  - AVEDAN never claims an application is submitted or paid unless verified
    by an official government API.
  - Zero Payment collection: avedan_service_fee is always 0.0.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models.database import get_db
from models.user import User
from models.scheme import Scheme
from models.application import Application, ApplicationStatus, PaymentStatus
from services.scheme_service import SchemeService

router = APIRouter(prefix="/api/applications", tags=["Applications"])


class CreateApplicationRequest(BaseModel):
    user_id: Optional[str] = None
    user_name: Optional[str] = "Citizen"
    scheme_id: str


class UpdateProgressRequest(BaseModel):
    status: Optional[str] = Field(None, description="Reported status (e.g. continued_to_portal, user_reported_submitted)")
    official_acknowledgment_number: Optional[str] = Field(None, description="Official registration number from govt portal")
    user_reported_payment_done: Optional[bool] = Field(None, description="Whether user completed direct payment on official portal")
    notes: Optional[str] = None


@router.get("")
def list_applications(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    List tracked applications for a citizen.
    """
    q = db.query(Application)
    if user_id:
        q = q.filter(Application.user_id == user_id)
    apps = q.order_by(Application.created_at.desc()).all()
    return {"count": len(apps), "applications": [a.to_dict() for a in apps]}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_application(payload: CreateApplicationRequest, db: Session = Depends(get_db)):
    """
    Start tracking a scheme application journey.
    """
    scheme = SchemeService.get_scheme_by_id(db, payload.scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Get or create user
    user = None
    if payload.user_id:
        user = db.query(User).filter(User.id == payload.user_id).first()

    if not user:
        user = User(name=payload.user_name or "Citizen")
        db.add(user)
        db.commit()
        db.refresh(user)

    is_free = scheme.get("fee_amount") == 0.0 or scheme.get("fee_amount") is None

    app_entry = Application(
        user_id=user.id,
        scheme_id=scheme["id"],
        scheme_name=scheme["name"],
        scheme_state=scheme["state"],
        official_application_url=scheme["application_url"],
        application_url_verified=scheme["application_url_verified"],
        status=ApplicationStatus.SAVED,
        status_label="Saved to Tracker (Not yet applied)",
        is_verified_by_official_api=False,
        official_fee_amount=scheme["fee_amount"] or 0.0,
        avedan_service_fee=0.0,  # Always ₹0
        official_payment_url=scheme.get("official_payment_page_url"),
        payment_status=PaymentStatus.NOT_APPLICABLE if is_free else PaymentStatus.PENDING_ON_GOVERNMENT_PORTAL,
        payment_status_label="Free (No fee)" if is_free else "Official fee to be paid directly on government portal",
        progress_notes="Citizen started tracking this scheme.",
    )

    db.add(app_entry)
    db.commit()
    db.refresh(app_entry)

    return app_entry.to_dict()


@router.patch("/{app_id}/progress")
def update_progress(app_id: str, payload: UpdateProgressRequest, db: Session = Depends(get_db)):
    """
    Update citizen progress. Strictly distinguishes user reports from official verification.
    """
    app_entry = db.query(Application).filter(Application.id == app_id).first()
    if not app_entry:
        raise HTTPException(status_code=404, detail="Application not found")

    if payload.official_acknowledgment_number:
        app_entry.official_acknowledgment_number = payload.official_acknowledgment_number.strip()

    if payload.status == "continued_to_portal":
        app_entry.status = ApplicationStatus.CONTINUED_TO_OFFICIAL_PORTAL
        app_entry.status_label = "Redirected to Official Government Portal"
        app_entry.progress_notes = "Citizen clicked 'Continue to Official Application' to proceed on government portal."

    elif payload.status == "user_reported_submitted":
        app_entry.status = ApplicationStatus.USER_REPORTED_SUBMITTED
        app_entry.status_label = "User Reported Submitted (Pending Official Verification)"
        app_entry.is_verified_by_official_api = False
        app_entry.progress_notes = (
            f"Citizen reported submitting on official portal with reference #{app_entry.official_acknowledgment_number or 'Not provided'}. "
            "Awaiting official government verification."
        )

    if payload.user_reported_payment_done is True:
        if app_entry.official_fee_amount > 0:
            app_entry.payment_status = PaymentStatus.USER_REPORTED_PAID
            app_entry.payment_status_label = "User Reported Paid at Govt Portal (Pending Official Treasury Verification)"

    if payload.notes:
        app_entry.progress_notes = payload.notes

    db.commit()
    db.refresh(app_entry)
    return app_entry.to_dict()
