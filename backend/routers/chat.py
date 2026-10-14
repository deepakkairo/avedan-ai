"""
routers/chat.py – Multilingual Conversational AI Assistant Router
==================================================================
Provides conversational assistance for discovering schemes, understanding
eligibility, required documents, and authentication instructions.

BUILT-IN SAFETY GUARDRAILS:
  1. Never accepts or prompts for OTPs, PINs, passwords, or bank card details.
  2. Enforces AVEDAN's ₹0 service fee policy.
  3. Directs users to verified official application links (.gov.in / .nic.in).
  4. Supports multilingual interactions (English, Hindi, Marathi, etc.).
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config import settings
from models.database import get_db
from models.scheme import Scheme
from services.scheme_service import SchemeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Assistant Chat"])


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "en"  # "en", "hi", "mr", "ta", "bn"
    history: Optional[List[ChatMessage]] = []


SYSTEM_PROMPT = """
You are AVEDAN AI, a helpful, transparent, and citizen-friendly assistant for Indian government schemes.
Your goals:
1. Help citizens discover schemes they are eligible for.
2. Clearly explain required documents (e.g., Aadhaar, Income certificate, Caste certificate).
3. State whether DigiLocker authentication is supported/required on the official government portal.
4. Always emphasize that AVEDAN AI is 100% free (₹0 service fee) and never collects government fees.
5. Emphasize that citizens must only authenticate and pay on verified official government portals (.gov.in / .nic.in).

CRITICAL COMPLIANCE RULES:
- NEVER ask for or accept a citizen's DigiLocker password, security PIN, Aadhaar OTP, or bank card details.
- If a user attempts to share an OTP or PIN, immediately tell them to keep it safe and never share it.
- NEVER claim to automatically submit or pay without verified official integration.
- If a scheme's official link is not verified, explicitly state: "Official application link not verified".
"""


def detect_security_flags(message: str) -> Optional[str]:
    """
    Scans for sensitive credential keywords and returns a safety advisory.
    """
    lower = message.lower()
    if any(k in lower for k in ["otp", "pin", "password", "cvv", "card number", "debit card", "credit card"]):
        return (
            "⚠️ Safety Alert: AVEDAN AI will NEVER ask for your DigiLocker PIN, password, bank card, or OTP. "
            "Please never share your confidential credentials with any AI tool, website, or person. "
            "Always enter credentials only on official government portals ending in .gov.in or .nic.in."
        )
    if any(k in lower for k in ["pay you", "pay avedan", "send money", "service charge", "razorpay"]):
        return (
            "ℹ️ AVEDAN AI Zero-Fee Policy: AVEDAN AI charges ₹0 service fees and does not collect or process money. "
            "Any official government fee must be paid directly on the verified official portal using government-approved methods."
        )
    return None


@router.post("")
def chat_with_assistant(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Chat endpoint for citizen scheme guidance.
    """
    user_msg = payload.message.strip()

    # Step 1: Check security guardrails
    security_flag = detect_security_flags(user_msg)
    if security_flag:
        return {
            "reply": security_flag,
            "relevant_schemes": [],
            "guardrail_triggered": True,
        }

    # Step 2: Search relevant schemes from database
    search_results = SchemeService.list_schemes(db, query=user_msg, limit=3)

    # Step 3: Check if OpenAI is configured
    if settings.openai_api_key and settings.openai_api_key.startswith("sk-"):
        try:
            import httpx
            context = "\n\n".join(
                [
                    f"Scheme: {s['name']}\nMinistry: {s['ministry']}\nFee: ₹{s['fee_amount'] or 0} (AVEDAN fee: ₹0)\nOfficial URL: {s['application_url'] or 'Official application link not verified'}\nAuth Method: {s['auth_instructions']}"
                    for s in search_results
                ]
            )
            prompt = f"Citizen Question: {user_msg}\nPreferred Language: {payload.language}\nRelevant Schemes:\n{context}"

            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                },
                timeout=15.0,
            )
            if response.status_code == 200:
                reply_text = response.json()["choices"][0]["message"]["content"]
                return {
                    "reply": reply_text,
                    "relevant_schemes": search_results,
                    "guardrail_triggered": False,
                }
        except Exception as exc:
            logger.warning("OpenAI API call failed, falling back to intelligent response engine: %s", exc)

    # Step 4: Built-in contextual response engine (Multilingual & Deterministic)
    if search_results:
        top_scheme = search_results[0]
        name = top_scheme["name_hi"] if payload.language == "hi" and top_scheme.get("name_hi") else top_scheme["name"]
        fee_info = (
            "निःशुल्क (₹0 सरकारी शुल्क)"
            if payload.language == "hi" and (top_scheme["fee_amount"] == 0 or top_scheme["fee_amount"] is None)
            else f"₹{top_scheme['fee_amount']} (सरकारी शुल्क)"
            if payload.language == "hi"
            else "Free (₹0 government fee)"
            if (top_scheme["fee_amount"] == 0 or top_scheme["fee_amount"] is None)
            else f"₹{top_scheme['fee_amount']} (Government Fee)"
        )
        url_info = (
            top_scheme["application_url"]
            if top_scheme["application_url_verified"]
            else "Official application link not verified"
        )
        digilocker_info = (
            "डिजीलॉकर आधिकारिक पोर्टल पर समर्थित है।"
            if payload.language == "hi" and top_scheme["digilocker_supported_on_portal"]
            else "आधार / पोर्टल लॉगिन आवश्यक है।"
            if payload.language == "hi"
            else "DigiLocker is supported directly on the official portal."
            if top_scheme["digilocker_supported_on_portal"]
            else "Standard Aadhaar / Portal login is required."
        )

        if payload.language == "hi":
            reply = (
                f"नमस्ते! आपके प्रश्न के आधार पर, सबसे प्रासंगिक योजना है: **{name}**।\n\n"
                f"• **विवरण:** {top_scheme.get('description_hi') or top_scheme['description']}\n"
                f"• **पात्रता:** {top_scheme.get('eligibility_hi') or top_scheme['eligibility']}\n"
                f"• **आवश्यक दस्तावेज:** {', '.join(top_scheme['documents_required'])}\n"
                f"• **शुल्क:** {fee_info} | आवेदन एआई सेवा शुल्क: ₹0.00\n"
                f"• **प्रमाणीकरण:** {digilocker_info}\n"
                f"• **आधिकारिक आवेदन लिंक:** {url_info}\n\n"
                f"कृपया आधिकारिक पोर्टल पर सीधे आवेदन करने के लिए नीचे दिए गए 'Continue to Official Application' बटन का उपयोग करें।"
            )
        else:
            reply = (
                f"Hello! Based on your query, the most relevant scheme is: **{name}**.\n\n"
                f"• **Description:** {top_scheme['description']}\n"
                f"• **Eligibility:** {top_scheme['eligibility']}\n"
                f"• **Required Documents:** {', '.join(top_scheme['documents_required'])}\n"
                f"• **Government Fee:** {fee_info} | AVEDAN AI Service Fee: ₹0.00 (Free)\n"
                f"• **Authentication:** {digilocker_info}\n"
                f"• **Official Application Portal:** {url_info}\n\n"
                f"You can review the full scheme card below and click 'Continue to Official Application' to proceed safely on the government website."
            )
    else:
        if payload.language == "hi":
            reply = (
                "नमस्ते! मैं आवेदन एआई (AVEDAN AI) हूँ। आप केंद्र या राज्य सरकार की किसी भी योजना (जैसे पीएम-किसान, आयुष्मान भारत, छात्रवृत्ति) के बारे में पूछ सकते हैं। "
                "कृपया ध्यान दें कि हम कभी भी आपका डिजीलॉकर पिन या ओटीपी नहीं मांगते हैं, और हमारी सेवा पूर्णतः निःशुल्क (₹0) है।"
            )
        else:
            reply = (
                "Hello! I am AVEDAN AI, your government schemes assistant. You can ask me about any central or state government scheme "
                "(such as PM-Kisan, Ayushman Bharat, National Scholarships, or Driving Licences). "
                "Please note: AVEDAN never asks for your DigiLocker PIN or OTP, and our assistance is 100% free (₹0 service fee)."
            )

    return {
        "reply": reply,
        "relevant_schemes": search_results,
        "guardrail_triggered": False,
    }
