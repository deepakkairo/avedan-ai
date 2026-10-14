"""
data/seed_schemes.py – Seed Data with Real Verified Government Schemes
========================================================================
Populates the database with real, verified Indian government schemes,
explicit authentication requirements, verified fee data, and an
unverified scheme to demonstrate strict adherence to compliance rules.
"""

import os
import sys
from pathlib import Path

# Ensure backend root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.database import SessionLocal, create_all_tables
from models.scheme import Scheme


SCHEMES_DATA = [
    {
        "id": "pm-kisan",
        "name": "PM Kisan Samman Nidhi",
        "name_hi": "प्रधानमंत्री किसान सम्मान निधि",
        "category": "agriculture",
        "ministry": "Ministry of Agriculture and Farmers Welfare",
        "state": "central",
        "description": "Income support of ₹6,000 per year in three equal installments to all eligible landholding farmer families across India.",
        "description_hi": "सभी पात्र भूमिधारक किसान परिवारों को प्रति वर्ष ₹6,000 की वित्तीय सहायता तीन समान किस्तों में प्रदान की जाती है।",
        "eligibility": "Small and marginal farmers owning cultivable land in their name. Exclusion criteria apply to institutional landholders and income tax payees.",
        "eligibility_hi": "कृषि योग्य भूमि रखने वाले छोटे और सीमांत किसान। आयकर दाता और संस्थागत भूमिधारक पात्र नहीं हैं।",
        "documents_required": [
            "Aadhaar Card",
            "Land ownership records (Khatoni/Khasra)",
            "Active Bank Account with Aadhaar seeding",
            "Mobile number linked to Aadhaar",
        ],
        "official_url": "https://pmkisan.gov.in",
        "application_url": "https://pmkisan.gov.in/RegistrationFormNew.aspx",
        "application_url_verified": True,
        "auth_type": "aadhaar_otp",
        "auth_instructions": "Online registration requires Aadhaar e-KYC using OTP sent to your Aadhaar-linked mobile number, or biometric authentication at a local CSC center.",
        "digilocker_supported_on_portal": False,
        "digilocker_notes": "DigiLocker is not directly required for the PM-Kisan registration form. Farmers authenticate directly via Aadhaar OTP on pmkisan.gov.in.",
        "fee_amount": 0.0,
        "fee_currency": "INR",
        "fee_verified": True,
        "fee_verified_at": datetime.now(timezone.utc),
        "fee_source_url": "https://pmkisan.gov.in",
        "official_payment_page_url": None,
        "official_payment_methods": [],
        "has_api": False,
    },
    {
        "id": "ayushman-bharat",
        "name": "Ayushman Bharat PM-JAY",
        "name_hi": "आयुष्मान भारत प्रधानमंत्री जन आरोग्य योजना (PM-JAY)",
        "category": "healthcare",
        "ministry": "National Health Authority / MoHFW",
        "state": "central",
        "description": "Cashless health cover of up to ₹5,00,000 per family per year for secondary and tertiary care hospitalization in empaneled public and private hospitals.",
        "description_hi": "पात्र परिवारों को सरकारी और सूचीबद्ध निजी अस्पतालों में द्वितीयक और तृतीयक देखभाल के लिए प्रति वर्ष ₹5,00,000 तक का कैशलेस स्वास्थ्य कवर।",
        "eligibility": "Households identified under SECC 2011 criteria or state-specific priority ration card lists, and all senior citizens aged 70+ irrespective of income.",
        "eligibility_hi": "सामाजिक आर्थिक जाति जनगणना (SECC 2011) के तहत पहचाने गए ग्रामीण और शहरी परिवार, तथा 70 वर्ष से अधिक आयु के सभी वरिष्ठ नागरिक।",
        "documents_required": [
            "Aadhaar Card",
            "Ration Card / Family ID",
            "Aadhaar-linked Mobile Number",
        ],
        "official_url": "https://pmjay.gov.in",
        "application_url": "https://beneficiary.nha.gov.in",
        "application_url_verified": True,
        "auth_type": "digilocker_sso",
        "auth_instructions": "Citizens authenticate directly on the official NHA Beneficiary portal using MeriPehchaan SSO / DigiLocker, Aadhaar OTP, or Face Authentication.",
        "digilocker_supported_on_portal": True,
        "digilocker_notes": "The official beneficiary.nha.gov.in portal provides direct login through MeriPehchaan / DigiLocker for instant family e-KYC.",
        "fee_amount": 0.0,
        "fee_currency": "INR",
        "fee_verified": True,
        "fee_verified_at": datetime.now(timezone.utc),
        "fee_source_url": "https://beneficiary.nha.gov.in",
        "official_payment_page_url": None,
        "official_payment_methods": [],
        "has_api": False,
    },
    {
        "id": "national-scholarship-portal",
        "name": "National Scholarship Portal (NSP)",
        "name_hi": "राष्ट्रीय छात्रवृत्ति पोर्टल (NSP)",
        "category": "education",
        "ministry": "Ministry of Electronics and Information Technology (MeitY)",
        "state": "central",
        "description": "Unified platform offering over 100+ scholarships from central ministries and state governments for Pre-Matric, Post-Matric, Higher Education, and Minorities.",
        "description_hi": "विभिन्न मंत्रालयों द्वारा पूर्व-मैट्रिक, उत्तर-मैट्रिक, उच्च शिक्षा और अल्पसंख्यक छात्रों के लिए 100 से अधिक छात्रवृत्तियों का एकीकृत राष्ट्रीय पोर्टल।",
        "eligibility": "Students enrolled in recognized schools/colleges meeting income criteria (usually under ₹2.5 Lakhs annually) and merit cutoffs.",
        "eligibility_hi": "मान्यता प्राप्त संस्थानों में अध्ययनरत छात्र जो वार्षिक आय और मेरिट शर्तों को पूरा करते हैं।",
        "documents_required": [
            "Aadhaar Card",
            "DigiLocker Account (for academic certificates / OTR)",
            "Income Certificate",
            "Caste Certificate (if applicable)",
            "Bank Account linked to Aadhaar (NPCI mapped)",
            "Previous Year Academic Marksheet",
        ],
        "official_url": "https://scholarships.gov.in",
        "application_url": "https://scholarships.gov.in",
        "application_url_verified": True,
        "auth_type": "digilocker_sso",
        "auth_instructions": "NSP mandates One-Time Registration (OTR). Students can use DigiLocker to auto-verify their identity and fetch verified board marksheets without physical upload.",
        "digilocker_supported_on_portal": True,
        "digilocker_notes": "Official NSP portal integrates directly with DigiLocker for seamless verification of caste, income, and educational certificates.",
        "fee_amount": 0.0,
        "fee_currency": "INR",
        "fee_verified": True,
        "fee_verified_at": datetime.now(timezone.utc),
        "fee_source_url": "https://scholarships.gov.in",
        "official_payment_page_url": None,
        "official_payment_methods": [],
        "has_api": False,
    },
    {
        "id": "parivahan-driving-licence",
        "name": "Sarathi Parivahan - Driving & Learner Licence",
        "name_hi": "सारथी परिवहन - लर्नर एवं ड्राइविंग लाइसेंस",
        "category": "transport",
        "ministry": "Ministry of Road Transport and Highways (MoRTH)",
        "state": "central",
        "description": "Online application service for Learner's Licence and Driving Licence issuance and renewal across all Indian States and Union Territories.",
        "description_hi": "सभी राज्यों और केंद्र शासित प्रदेशों में ऑनलाइन लर्नर और स्थायी ड्राइविंग लाइसेंस आवेदन और नवीनीकरण सेवा।",
        "eligibility": "Citizens aged 18+ (or 16+ for gearless 50cc two-wheelers) residing in the applying RTO jurisdiction.",
        "eligibility_hi": "18 वर्ष या उससे अधिक आयु के नागरिक (गियरलेस दोपहिया के लिए 16 वर्ष) जो संबंधित आरटीओ क्षेत्र में रहते हैं।",
        "documents_required": [
            "Aadhaar Card (for contactless online test)",
            "Age Proof (10th Marksheet or Birth Certificate)",
            "Address Proof",
            "Passport Size Photograph",
            "Medical Certificate (Form 1A if required)",
        ],
        "official_url": "https://parivahan.gov.in",
        "application_url": "https://sarathi.parivahan.gov.in/sarathiservice/stateSelection.do",
        "application_url_verified": True,
        "auth_type": "digilocker_sso",
        "auth_instructions": "Applicants can authenticate via Aadhaar e-KYC or link documents via DigiLocker on Sarathi Parivahan to take the online LL test from home without visiting the RTO.",
        "digilocker_supported_on_portal": True,
        "digilocker_notes": "DigiLocker is natively integrated into Sarathi Parivahan for fetching educational certificates and identity proof.",
        "fee_amount": 200.0,
        "fee_currency": "INR",
        "fee_verified": True,
        "fee_verified_at": datetime.now(timezone.utc),
        "fee_source_url": "https://parivahan.gov.in/parivahan/en/content/licensing-related-fees-and-charges",
        "official_payment_page_url": "https://sarathi.parivahan.gov.in/sarathiservice/stateSelection.do",
        "official_payment_methods": [
            "State Cyber Treasury (Gras)",
            "Bharatkosh",
            "NetBanking on Sarathi portal",
            "UPI directly on Sarathi payment gateway",
        ],
        "has_api": False,
    },
    {
        "id": "instant-e-pan",
        "name": "Instant e-PAN (Income Tax Department)",
        "name_hi": "तत्काल ई-पैन (आयकर विभाग)",
        "category": "identity",
        "ministry": "Ministry of Finance - Central Board of Direct Taxes",
        "state": "central",
        "description": "Paperless and instant allotment of Permanent Account Number (e-PAN) in digital PDF format within 10 minutes based on Aadhaar e-KYC.",
        "description_hi": "आधार ई-केवाईसी के आधार पर 10 मिनट के भीतर डिजिटल पीडीएफ प्रारूप में तत्काल और निःशुल्क ई-पैन आवंटन।",
        "eligibility": "Individual applicants who have never been allotted a PAN, possess an active Aadhaar card with mobile linked, and are not minors.",
        "eligibility_hi": "ऐसे भारतीय नागरिक जिनके पास पहले से पैन नहीं है, और जिनका आधार मोबाइल नंबर से जुड़ा हुआ है।",
        "documents_required": [
            "Aadhaar Card with active mobile linkage",
        ],
        "official_url": "https://www.incometax.gov.in",
        "application_url": "https://eportal.incometax.gov.in/iec/foservices/#/pre-login/instant-e-pan",
        "application_url_verified": True,
        "auth_type": "aadhaar_otp",
        "auth_instructions": "Applicant enters Aadhaar number on the official Income Tax e-filing portal and verifies via OTP sent to Aadhaar-linked mobile. No physical documents required.",
        "digilocker_supported_on_portal": True,
        "digilocker_notes": "Once allotted, the digital PAN can be permanently imported into your DigiLocker account as an official verified document.",
        "fee_amount": 0.0,
        "fee_currency": "INR",
        "fee_verified": True,
        "fee_verified_at": datetime.now(timezone.utc),
        "fee_source_url": "https://www.incometax.gov.in",
        "official_payment_page_url": None,
        "official_payment_methods": [],
        "has_api": False,
    },
    {
        "id": "pm-awas-urban",
        "name": "Pradhan Mantri Awas Yojana - Urban (PMAY-U 2.0)",
        "name_hi": "प्रधानमंत्री आवास योजना - शहरी (PMAY-U 2.0)",
        "category": "housing",
        "ministry": "Ministry of Housing and Urban Affairs",
        "state": "central",
        "description": "Central interest subsidy and financial assistance to urban poor families (EWS, LIG, and Middle Income) for constructing or purchasing their first pucca house.",
        "description_hi": "शहरी गरीब और मध्यम आय वर्ग के परिवारों को अपना पहला पक्का घर बनाने या खरीदने के लिए ब्याज सब्सिडी और वित्तीय सहायता।",
        "eligibility": "Urban families not owning a pucca house anywhere in India. Annual household income categories: EWS (up to ₹3 Lakhs), LIG (₹3 to ₹6 Lakhs), MIG (₹6 to ₹9 Lakhs).",
        "eligibility_hi": "ऐसे परिवार जिनके पास भारत में कहीं भी पक्का मकान नहीं है और जो ईडब्ल्यूएस या एलआईजी आय सीमा में आते हैं।",
        "documents_required": [
            "Aadhaar Card of all family members",
            "Income Certificate / ITR",
            "Bank Passbook / Cancelled Cheque",
            "Proof of Residence",
            "Land title / Sale deed (if constructing)",
        ],
        "official_url": "https://pmay-urban.gov.in",
        "application_url": "https://pmay-urban.gov.in",
        "application_url_verified": True,
        "auth_type": "aadhaar_otp",
        "auth_instructions": "Online registration requires Aadhaar OTP verification of the head of the family on the official PMAY-U portal.",
        "digilocker_supported_on_portal": False,
        "digilocker_notes": "DigiLocker is not directly mandated on the PMAY-U registration portal; documents are uploaded directly during online application.",
        "fee_amount": 0.0,
        "fee_currency": "INR",
        "fee_verified": True,
        "fee_verified_at": datetime.now(timezone.utc),
        "fee_source_url": "https://pmay-urban.gov.in",
        "official_payment_page_url": None,
        "official_payment_methods": [],
        "has_api": False,
    },
    {
        "id": "rural-artisan-grant-unverified",
        "name": "Rural Traditional Artisan Welfare Grant",
        "name_hi": "ग्रामीण पारंपरिक कारीगर कल्याण अनुदान (अपुष्ट लिंक)",
        "category": "agriculture",
        "ministry": "Department of Rural Development",
        "state": "Uttar Pradesh",
        "description": "Proposed state welfare initiative for traditional village artisans and craftspeople. Portal migration in progress.",
        "description_hi": "पारंपरिक ग्रामीण कारीगरों के लिए प्रस्तावित राज्य कल्याणकारी योजना। पोर्टल आधुनिकीकरण प्रगति पर है।",
        "eligibility": "Rural artisans holding traditional craft trade certification.",
        "eligibility_hi": "पारंपरिक शिल्प कौशल प्रमाण पत्र रखने वाले ग्रामीण कारीगर।",
        "documents_required": [
            "Aadhaar Card",
            "Artisan Registration Certificate",
            "Local Gram Panchayat Recommendation",
        ],
        "official_url": "http://rd.up.gov.in",
        "application_url": None,              # DELIBERATELY NONE
        "application_url_verified": False,     # DELIBERATELY FALSE
        "auth_type": "unverified",
        "auth_instructions": "Online application portal is currently undergoing maintenance and upgrade. Citizens should visit the local District Rural Development Agency (DRDA) office.",
        "digilocker_supported_on_portal": False,
        "digilocker_notes": "Portal integration status is currently unverified.",
        "fee_amount": None,                   # Fee unverified
        "fee_currency": "INR",
        "fee_verified": False,
        "fee_verified_at": None,
        "fee_source_url": None,
        "official_payment_page_url": None,
        "official_payment_methods": [],
        "has_api": False,
    },
]


def seed_database():
    """
    Populates SQLite or PostgreSQL with seed schemes.
    """
    create_all_tables()
    db: Session = SessionLocal()
    try:
        count = 0
        for data in SCHEMES_DATA:
            existing = db.query(Scheme).filter(Scheme.id == data["id"]).first()
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
            else:
                scheme = Scheme(**data)
                db.add(scheme)
            count += 1
        db.commit()
        print(f"Successfully seeded {count} government schemes.")
    except Exception as exc:
        db.rollback()
        print(f"Error seeding database: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
