"""
services/payment_service.py – Government Fee & Zero-Fee Payment Compliance
===========================================================================
Enforces AVEDAN AI's strict Zero-Fee & Direct Government Payment Policy:
  1. AVEDAN charges ₹0 service fee (100% free citizen tool).
  2. Fees are displayed ONLY if verified from official government portals.
  3. Directs citizens to the official government payment page (e.g. Bharatkosh,
     State Cyber Treasury, or the portal's integrated gateway).
  4. Never routes money through AVEDAN's bank account or any third-party gateway
     like Razorpay.
  5. Never creates fake QR codes, fake receipts, or fake payment-success states.
  6. Tracks user-reported payments with transparent "Unverified / Pending Official
     Confirmation" labeling.
"""

import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PaymentComplianceError(ValueError):
    """Raised when an action violates AVEDAN's payment and zero-fee policies."""
    pass


class PaymentService:
    """
    Handles official government fee verification and direction to official portals.
    """

    @staticmethod
    def get_fee_summary(scheme: Any) -> dict[str, Any]:
        """
        Extracts verified fee details for a scheme with strict transparency.
        """
        fee_amount = getattr(scheme, "fee_amount", None)
        fee_verified = getattr(scheme, "fee_verified", False)
        fee_source_url = getattr(scheme, "fee_source_url", None)
        fee_verified_at = getattr(scheme, "fee_verified_at", None)
        payment_url = getattr(scheme, "official_payment_page_url", None)
        payment_methods = getattr(scheme, "official_payment_methods", []) or []

        # Verification check
        if not fee_verified or fee_amount is None:
            return {
                "fee_status": "unverified_or_not_disclosed",
                "display_text": "Fee details not verified from official portal",
                "fee_amount": None,
                "currency": "INR",
                "avedan_service_fee": 0.0,
                "is_free": False,
                "official_payment_url": None,
                "verification_notice": "Please check the official scheme portal for exact fee details.",
            }

        is_free = fee_amount == 0.0

        return {
            "fee_status": "free" if is_free else "verified_government_fee",
            "display_text": "Free (No government fee)" if is_free else f"₹{fee_amount:.2f} (Official Government Fee)",
            "fee_amount": fee_amount,
            "currency": "INR",
            "avedan_service_fee": 0.0,  # Always strictly ₹0.0
            "is_free": is_free,
            "fee_source_url": fee_source_url,
            "fee_verified_at": fee_verified_at.isoformat() if fee_verified_at else None,
            "official_payment_url": payment_url,
            "official_payment_methods": payment_methods,
            "payment_instructions": (
                "This scheme is 100% free of charge. No payment is required anywhere."
                if is_free
                else "Pay directly on the official government portal using authorized methods (NetBanking, UPI on govt portal, Treasury challan). AVEDAN does not collect or process any fees."
            ),
        }

    @staticmethod
    def reject_intermediary_payment(payment_request: dict[str, Any]) -> None:
        """
        Strict check: Rejects any attempt to process money or integrate
        a private payment gateway (like Razorpay).
        """
        prohibited_terms = ["razorpay", "stripe", "paytm_gateway", "collect_fee", "wallet_transfer"]
        req_str = str(payment_request).lower()
        if any(term in req_str for term in prohibited_terms):
            logger.error("Security/Compliance Violation: Prohibited payment gateway call detected!")
            raise PaymentComplianceError(
                "AVEDAN AI is prohibited from processing payments or integrating third-party payment gateways. "
                "Citizens must pay directly on the official government portal."
            )
