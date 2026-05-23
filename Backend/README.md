# Closira — AI-Powered Customer Communication Platform Backend

Closira is a highly polished, production-grade backend service designed to help small and medium businesses (SMBs) seamlessly manage customer enquiries from multiple communication channels (WhatsApp, Email, Calls). 

It automatically classifies incoming customer queries using an intelligent, rule-based **SOP (Standard Operating Procedure) Matching Engine**, generates context-aware suggested template responses, records an append-only historical audit timeline, and supports critical operational customer workflows (follow-up scheduling and manual escalations).

---

## 🌟 Key Features

*   **FastAPI Asynchronous Ingestion:** Instantly accepts incoming enquiries and returns a `201 Created` status with unique tracking UUIDs, processing the SOP logic in the background without blocking the client.
*   **Modular SOP Matching Engine:** A structured, keyword-driven rule engine supporting five default business categories:
    *   *Booking enquiry* (triggered by keywords like *book, schedule, reserve*)
    *   *Pricing enquiry* (triggered by keywords like *pricing, price, quote, rate, cost*)
    *   *Complaint* (triggered by keywords like *unhappy, complaint, bad, worst, terrible*)
    *   *Support request* (triggered by keywords like *help, support, issue, broken, error*)
    *   *After-hours message* (triggered by keywords like *hours, open, close, holiday*)
*   **Operational Lifecycle Workflows:** Full-featured business logic endpoints supporting:
    *   `POST /enquiry/{id}/follow-up` - Transition status to `follow_up_scheduled` and log delay constraints.
    *   `POST /enquiry/{id}/escalate` - Transition status to `escalated` and attach manual comments.
    *   `GET /enquiry/{id}/history` - Retrieve a detailed, sorted chronological audit timeline log.
    *   `GET /enquiries/` - Query and filter all enquiries by status or channel with limit-bound parameters.
*   **Production Observability:** Injecting trace-aggregating correlation IDs (`X-Correlation-ID`) across async task boundaries, logged in structured JSON formatting.
*   **Standardized Error Infrastructure:** Consolidated catch-all exception filters formatting validation (`422`), HTTP (`404`), and internal server (`500`) failures into a unified contract: `{ success: false, error: { type, message } }`.
*   **Premium Interactive API Documentation:** Beautiful, descriptive Swagger UI documentation complete with request/response schemas, field descriptions, and interactive examples.

---

## 🛠️ Technology Stack

*   **FastAPI** — High-performance async web framework
*   **SQLAlchemy** — Standard Python Object-Relational Mapper (ORM)
*   **SQLite** — Lightweight, serverless local SQL database
*   **Pydantic v2** — Data parsing and schema level validation
*   **Uvicorn** — Lightning-fast ASGI web server implementation

---

## 📂 Project Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point, middleware, & global handlers
│   ├── config.py               # Centralized configuration (Pydantic BaseSettings loading .env)
│   ├── database.py             # SQLite connection engine and session factory
│   ├── logging/
│   │   ├── __init__.py
│   │   └── config.py           # Thread-safe ContextVar correlation ID and JSON Formatter
│   ├── mock_sops/
│   │   ├── __init__.py         # Package interface re-exports
│   │   ├── matcher.py          # SOP classification and response suggestion pure-logic
│   │   ├── rules.py            # Hardcoded business category keyword rules
│   │   └── templates.py        # suggested response message templates
│   ├── models/
│   │   ├── __init__.py         # Models registry imports
│   │   ├── enquiry.py          # Enquiry database SQLAlchemy Model & Enums
│   │   └── event.py            # Chronological Event database SQLAlchemy Model & Enums
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── enquiry.py          # Strict Pydantic operational validation schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py           # Health check endpoints verifying API + DB state
│   │   └── enquiry.py          # Operational routers (singular & plural routes)
│   └── utils/
│       └── __init__.py
├── docs/
│   └── architecture.md         # Detailed architectural documentation & sequence flows
├── tests/
│   └── __init__.py
├── closira.db                  # Local SQLite database (auto-generated)
├── requirements.txt            # Pinned dependencies
├── .env                        # Local environment parameters
├── README.md                   # This overview file
└── verify_backend.py           # Comprehensive automated E2E workflow verification suite
```

---

## 🚀 Setup & Installation

### 1. Prerequisite
Ensure you have **Python 3.11+** installed on your system.

### 2. Navigate to the backend directory
```bash
cd Backend
```

### 3. Initialize Virtual Environment
Create and activate a isolated python virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environments
Create a `.env` file inside the `Backend/` directory (or use the preconfigured one):
```env
APP_NAME="Closira API"
DATABASE_URL="sqlite:///./closira.db"
DEBUG=True
```

### 6. Run the Application Server
Start the Uvicorn ASGI production-ready reload server:
```bash
uvicorn app.main:app --reload
```
Upon launching, a beautiful ASCII Closira banner will display confirming database synchronization:
```
   _____ _                 _             
  / ____| |               (_)            
 | |    | | ___  ___ _ __ _  __ _       
 | |    | |/ _ \/ __| '__| |/ _` |      
 | |____| | (_) \__ \ |  | | (_| |      
  \_____|_|\___/|___/_|  |_|\__,_|      
                                         
AI-Powered Customer Communication Platform
===========================================
Version: 1.0.0
Environment: Development / Debug
Docs: http://127.0.0.1:8000/docs
===========================================
```

---

## 🔍 API Observability & Documentation

Once the server has successfully booted, access the self-documenting interface endpoints at:
*   **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Includes descriptive field guides and prefilled request examples)
*   **ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Running Automated E2E Verification Tests

Closira features a comprehensive automated integration and workflow suite mapping E2E lifecycles, timing, validations, filtering, and history.

To execute the verification suite:
1. Make sure your local Uvicorn development server is active on `http://127.0.0.1:8000`.
2. Open a separate terminal window and execute:
```bash
.\venv\Scripts\python verify_backend.py
```

### What is tested:
*   **Test 1 (Root & Health Check):** Verifies the server is operational and the SQLite engine is actively connected.
*   **Test 2 (Unified Exception Infrastructure):** Triggers a 422 schema violation (empty names), an invalid channel value injection, and a 404 UUID lookup, verifying they conform to standard JSON error patterns.
*   **Test 3 (E2E Enquiry Lifecycle):** Generates a customer pricing query, waits for the asynchronous BackgroundTask thread to match the SOP and qualify, schedules an operational follow-up window, triggers manual escalation, and audits the chronological event order of all 8 lifecycle events.
*   **Test 4 (Query Listings & Filtering):** Creates concurrent queries and validates status filters (`status=escalated`, `status=qualified`), channel sorting, chronological newest-first outputs, and boundary limit parameters.
