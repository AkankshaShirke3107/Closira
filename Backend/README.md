# Closira Backend

Closira Backend is a lightweight, deterministic processing engine for customer enquiry management. It routes inbound communications, computes priority classifications, and tracks lifecycle state transitions via an append-only event log.

The system is designed to provide immediate insight into customer sentiment and escalation risk without introducing the latency or non-determinism of external language models.

## Architecture

```text
  [HTTP Client]
       │
       ▼
  +---------+      +-------------------+      +------------------+
  | Router  | ---> |  Service Layer    | ---> | SQLite Database  |
  +---------+      +-------------------+      +------------------+
                             │
                             ▼
                   [ Background Task ]
                   (SOP Classification)
```

## Tech Stack

* Python 3.10+
* FastAPI
* SQLAlchemy (Core & ORM)
* Uvicorn
* SQLite

## Repository Structure

```text
Backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── routers/
│   │   ├── health.py
│   │   └── enquiry.py
│   ├── schemas/
│   │   └── enquiry.py
│   ├── models/
│   │   ├── enquiry.py
│   │   ├── event.py
│   │   ├── insight.py
│   │   └── message.py
│   └── services/
│       ├── enquiry_service.py
│       └── ai_insights_service.py
├── verify_backend.py
└── requirements.txt
```

## Core Features

* Strict lifecycle state machine (`new` -> `processing` -> `qualified` -> `follow_up_scheduled` -> `escalated`).
* Synchronous sidecar insight generation (sentiment scoring, risk weighting, priority tiering).
* Append-only timeline logging for all state transitions and background actions.
* Background thread isolation for SOP processing with race-condition guards.
* Plural endpoint aggregation via native SQL `COUNT` queries.

## API Endpoints

### Create Enquiry
`POST /enquiry/`

**Request:**
```json
{
  "customer_name": "Test User",
  "channel": "whatsapp",
  "message": "I have a complaint about my refund."
}
```

**Response:**
```json
{
  "id": "e3b0c442-989b-464c-8650-1234567890ab",
  "customer_name": "Test User",
  "status": "new",
  "ai_insights": {
    "sentiment": "negative",
    "sentiment_score": -0.67,
    "risk_score": 85,
    "priority": "P0",
    "reason": "Priority P0 (risk score: 85/100). Negative sentiment detected; High-risk keywords: complaint, refund; Channel weight (whatsapp): +8."
  }
}
```

### Get Dashboard Stats
`GET /enquiries/stats`

**Response:**
```json
{
  "totalLeadsToday": 15,
  "missedEnquiries": 2,
  "openEscalations": 4,
  "followUpsDue": 7
}
```

## Getting Started

1. Clone the repository and navigate to the backend directory.
2. Initialize and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
5. Access interactive API documentation at `http://127.0.0.1:8000/docs`.

## Common Issues

**WinError 10048 / Address already in use**
If you encounter `[WinError 10048] Only one usage of each socket address is permitted` on Windows, a background process is binding port 8000.

To resolve:
```powershell
netstat -ano | findstr :8000
taskkill /PID <ProcessID> /F
```

## Design Philosophy

* **Thin Routers**: HTTP layer handles transport and validation. Domain logic lives in the service layer.
* **Sidecar Models**: The `EnquiryInsight` model maintains a 1:1 relationship with `Enquiry` to prevent core table bloating and complex migrations.
* **Deterministic Scoring**: Risk and sentiment logic rely on pure Python dictionaries and weighting heuristics to guarantee high throughput and sub-millisecond execution times.
* **Defensive Concurrency**: Background tasks verify database state post-sleep before writing to avoid overwriting newer manual escalations.

## Future Improvements

* [ ] Migrate from SQLite to PostgreSQL for concurrent write capabilities.
* [ ] Implement Alembic for declarative schema migrations.
* [ ] Extract magic strings/weights in `ai_insights_service.py` to environment variables.
* [ ] Add Redis-backed rate limiting on public creation endpoints.
