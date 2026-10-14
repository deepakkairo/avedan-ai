# AVEDAN AI (आवेदन एआई)
### Citizen Government Schemes & Welfare Assistant

AVEDAN AI is an accessible, citizen-first platform that helps Indian citizens discover, understand, and apply for central and state government schemes with complete transparency, verified official application links, zero service fees, and strict privacy compliance.

---

## Key Compliance Policies Implemented

### 1. DigiLocker Support & Zero-Credential Policy
- **No Fake Login Forms:** AVEDAN never renders a simulated DigiLocker login screen or asks for passwords, security PINs, or OTPs.
- **Official Government Authentication:** If a scheme uses DigiLocker, citizens authenticate directly on official government portals (via MeriPehchaan SSO / DigiLocker).
- **Accurate Authentication Requirements:** AVEDAN does not assume every scheme uses DigiLocker; it accurately categorizes portals (DigiLocker SSO, Aadhaar OTP, State portal login, in-person CSC).
- **Direct Partner Integration Disabled by Default:** Direct API integration is optional and inactive until official partner approval and certification from Digital India Corporation / MeitY.
- **Zero Credential Storage:** AVEDAN never stores DigiLocker credentials or OTPs in any database, logs, analytics, or browser storage.

### 2. Verified Application URLs
- Every scheme card features a verified official application URL and a prominent **“Continue to Official Application”** button opening `.gov.in` or `.nic.in` portals in a new tab.
- If an official application URL cannot be verified, AVEDAN displays **“Official application link not verified”** and strictly does not invent any URL.

### 3. Government Fee Payment Transparency
- **₹0 AVEDAN Service Fee:** AVEDAN AI is 100% free of charge. No service fees or platform charges are ever assessed.
- **Verified Government Fees Only:** Official fees (e.g. ₹200 for Driving Licence on Sarathi Parivahan, ₹0 for PM-Kisan) are shown only with official portal verification source links.
- **Direct Portal Payment:** Citizens pay fees directly on the official government payment page (e.g., Bharatkosh, State Cyber Treasury, Sarathi gateway).
- **No Intermediary Gateways:** AVEDAN never routes money through its own bank account or private gateways (no Razorpay).
- **Honest Status Tracking:** AVEDAN never claims an application is submitted or paid unless verified by an official API. User-reported progress is labelled: `User Reported (Pending Official Verification)`.

---

## Project Structure

```
avedan-ai/
├── backend/
│   ├── config.py                 # Safe Pydantic settings with disabled-by-default DigiLocker integration
│   ├── main.py                   # FastAPI app with CORS, health check, and static frontend mount
│   ├── models/
│   │   ├── database.py           # SQLite (dev/test) & PostgreSQL (prod) database session engine
│   │   ├── scheme.py             # Scheme schema with verified links, auth requirements, fee metadata
│   │   ├── user.py               # Privacy-first User schema (zero credentials, nullable digilocker_id)
│   │   └── application.py        # Application model with honest status labels & no fake claims
│   ├── services/
│   │   ├── digilocker_service.py # DigiLocker compliance checks, citizen guidelines, and safe redirects
│   │   ├── payment_service.py    # Zero-fee verification and direct govt payment routing
│   │   └── scheme_service.py     # Scheme search & official government domain (.gov.in/.nic.in) verification
│   ├── routers/
│   │   ├── schemes.py            # Endpoints: list, categories, detailed scheme with verification badges
│   │   ├── digilocker.py         # Endpoints: partner status, citizen guidelines, compliance validation
│   │   ├── applications.py       # Endpoints: citizen journey tracker and unverified status labels
│   │   └── chat.py               # Multilingual conversational assistant with credential safety guardrails
│   ├── data/
│   │   └── seed_schemes.py       # Authentic scheme seed dataset (PM-Kisan, Ayushman Bharat, NSP, etc.)
│   └── tests/
│       ├── test_digilocker.py    # Unit tests for DigiLocker safety & zero-credential rejection
│       ├── test_payments.py      # Unit tests for ₹0 service fee & direct govt payments
│       ├── test_schemes.py       # Unit tests for URL verification & auth type accuracy
│       ├── test_applications.py  # Unit tests for truthful application tracking
│       ├── test_chat.py          # Unit tests for AI assistant safety guardrails
│       └── test_frontend.py      # Unit tests for frontend serving
└── frontend/
    ├── index.html                # Responsive, accessible, multilingual web application
    └── package.json              # Web client package metadata
```

---

## How to Run & Test

### 1. Run Automated Tests
```bash
cd backend
.\venv\Scripts\python -m pytest tests/ -v
```
All 22 unit tests verify URL verification, DigiLocker safety, zero-fee enforcement, and truthful reporting.

### 2. Start the Backend & Web Portal
```bash
cd backend
.\venv\Scripts\uvicorn main:app --reload --port 8000
```
- Web Application: [http://localhost:8000/app](http://localhost:8000/app) or [http://localhost:8000/portal](http://localhost:8000/portal)
- API Documentation (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
- System Manifest: [http://localhost:8000/](http://localhost:8000/)
