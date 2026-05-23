<p align="center">
  <img src="Backend/docs/screenshots/header.png" width="100%" alt="Closira Banner"/>
</p>

# Closira: Event-Driven Orchestration & Enquiry Intelligence Engine

Closira is a decoupled, full-stack workflow engine designed to ingest, classify, and orchestrate inbound customer communications with strict consistency guarantees and real-time risk routing.

---

## 📹 Video Walkthrough

> **[Click here to watch the system walkthrough](https://your-video-link-here)**  
> *(Note: Replace with actual video link for judging rounds).*

---

## Table of Contents

1. [Why This System Exists](#1-why-this-system-exists)
2. [System Overview & Visuals](#2-system-overview--visuals)
3. [System Architecture](#3-system-architecture)
4. [Repository Structure](#4-repository-structure)
5. [Quick Start — Backend](#5-quick-start--backend)
6. [Quick Start — Frontend](#6-quick-start--frontend)
7. [Run Tests & Execution Proof](#7-run-tests--execution-proof)
8. [API Reference & Example Payloads](#8-api-reference--example-payloads)
9. [Core Engineering Components](#9-core-engineering-components)
10. [Data Model](#10-data-model)
11. [Scalability Roadmap](#11-scalability-roadmap)
12. [Engineering Tradeoffs](#12-engineering-tradeoffs)

---

## 1. Why This System Exists

Traditional CRUD applications fail when managing complex, asynchronous workflows like customer support escalation. They mutate state destructively and lack telemetry. Closira solves this by treating communication as an immutable stream—prioritizing an auditability layer, bounded concurrency, and workflow orchestration over naive data mutations. It is built to demonstrate production-inspired system design, mimicking the constraints and guarantees of real-world SaaS infrastructure.

---

## 2. System Overview & Visuals

### Mobile App Dashboard
<p align="center">
  <img src="Backend/docs/screenshots/Screenshot_20260523_184230_Frontend.jpg" width="19%" alt="Dashboard Home"/>
  <img src="Backend/docs/screenshots/Screenshot_20260523_184238_Frontend.jpg" width="19%" alt="Leads List"/>
  <img src="Backend/docs/screenshots/Screenshot_20260523_184254_Frontend.jpg" width="19%" alt="Conversation Detail"/>
  <img src="Backend/docs/screenshots/Screenshot_20260523_184303_Frontend.jpg" width="19%" alt="Follow Ups"/>
  <img src="Backend/docs/screenshots/Screenshot_20260523_184310_Frontend.jpg" width="19%" alt="Escalations"/>
</p>

### Architecture & Data Flow
<p align="center">
  <img src="Backend/docs/screenshots/System Architecture.png" width="100%" alt="Closira System Architecture"/>
</p>

### API Interface
<p align="center">
  <img src="Backend/docs/screenshots/swagger.png" width="100%" alt="Swagger API"/>
</p>

---

## 3. System Architecture

The backend strictly adheres to Domain-Driven Design (DDD) principles. The HTTP routing layer acts exclusively as a transport protocol, completely insulated from the domain logic. All state mutations occur strictly within isolated transaction boundaries.


---

## 4. Repository Structure

```text
Closira/
├── Backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── enquiry.py           # HTTP transport layer and endpoints
│   │   │   └── health.py            # Infrastructure health checks
│   │   ├── services/
│   │   │   ├── enquiry_service.py   # Core domain logic and transactions
│   │   │   └── ai_insights_service.py # Deterministic scoring sidecar
│   │   ├── models/
│   │   │   ├── enquiry.py           # Root aggregate ORM
│   │   │   ├── event.py             # Event sourcing timeline ORM
│   │   │   ├── insight.py           # AI Metadata ORM
│   │   │   └── message.py           # Conversation thread ORM
│   │   ├── schemas/
│   │   │   └── enquiry.py           # Pydantic v2 I/O validation
│   │   ├── main.py                  # Application factory and exception handlers
│   │   └── database.py              # SQLAlchemy engine config
│   ├── docs/                        # Architecture diagrams and screenshots
│   ├── verify_backend.py            # Automated E2E integration tests
│   └── requirements.txt
│
├── Frontend/
│   ├── app/
│   │   ├── _layout.tsx              # Root context providers
│   │   └── (tabs)/                  # Expo Router navigation
│   ├── components/
│   │   ├── ui/                      # Reusable atoms (badges, cards)
│   ├── constants/                   # Design system tokens
│   ├── mock/                        # Decoupled JSON data abstraction
│   └── package.json
└── README.md
```

---

## 5. Quick Start — Backend

### Prerequisites
- Python 3.10+
- `pip`

### Setup

```bash
cd Backend

# 1. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
*Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.*

---

## 6. Quick Start — Frontend

### Prerequisites
- Node.js 18+
- `npm`

### Setup

```bash
cd Frontend

# 1. Install dependencies
npm install

# 2. Start the Expo development server
npx expo start
```
*Note: The frontend currently runs on a decoupled mock abstraction layer that exactly mirrors backend API contracts, allowing immediate evaluation without a running API.*

---

## 7. Run Tests & Execution Proof

The backend includes a comprehensive E2E validation script that guarantees lifecycle correctness, HTTP contract validation, and concurrency defense against race conditions.

```bash
cd Backend
python verify_backend.py
```

**Expected Output Proof:**
```text
Running E2E Verification for Closira API...

[PASS] Root endpoint (/)
[PASS] Health check (/health)
[PASS] GET /enquiries/stats
[PASS] POST /enquiry/ (Created ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890)
[PASS] AI sidecar generated (Sentiment: negative, Risk: 85)
[PASS] Initial 'new' event logged in timeline
[PASS] Concurrency Guard: Background worker successfully aborted stale write
[PASS] GET /enquiry/{id} contains full thread and insight metadata

==================== All checks passed successfully ====================
```

---

## 8. API Reference & Example Payloads

> Use `curl` to interact with the API, or utilize the interactive `/docs` UI.

### `POST /enquiry/`
Ingests payload, synchronously computes the AI sidecar, persists the initial timeline event, and delegates SOP matching to a non-blocking background worker.

```bash
curl -X POST http://127.0.0.1:8000/enquiry/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test User",
    "channel": "whatsapp",
    "message": "I need a refund immediately, this is broken."
  }'
```

**200 OK Response:**
```json
{
  "id": "e3b0c442-989b-464c-8650-1234567890ab",
  "customer_name": "Test User",
  "status": "new",
  "ai_insights": {
    "sentiment": "negative",
    "sentiment_score": -0.85,
    "risk_score": 92,
    "priority": "P0",
    "reason": "Priority P0 (risk score: 92/100). Negative sentiment detected; High-risk keywords: refund, broken."
  }
}
```

### `GET /enquiries/stats`
Leverages native SQL aggregations (`COUNT()`) to power dashboard metrics without loading heavy row data into memory.

```bash
curl http://127.0.0.1:8000/enquiries/stats
```

**200 OK Response:**
```json
{
  "totalLeadsToday": 15,
  "missedEnquiries": 2,
  "openEscalations": 4,
  "followUpsDue": 7
}
```

---

## 9. Core Engineering Components

* **BackgroundTasks vs Celery:** FastAPI's native `BackgroundTasks` executes asynchronous I/O within the same process pool. This eliminates the operational overhead of managing Redis and Celery clusters, consciously trading distributed horizontal scalability for rapid deployment simplicity.
* **State Isolation & Event Sourcing:** A rigid finite state machine governs lifecycles. Rather than destructively overwriting status columns, transitions append immutable records to an `events` table, creating a perfect historical audit trail.
* **Bounded Concurrency & Race Guards:** Native background I/O handles automated SOP matching. To maintain integrity, these routines explicitly guard against race conditions, instantly aborting stale database writes if a manual escalation occurs mid-processing.
* **Sidecar Intelligence Engine:** Sentiment and risk classifications utilize an in-memory weighted keyword algorithm. This sidecar pattern isolates metadata from the core domain model while guaranteeing sub-millisecond execution and zero network latency.

---

## 10. Data Model

The database schema utilizes SQLAlchemy declarative mapping, enforced by strict foreign key constraints.

* **Enquiry:** The root aggregate. Maintains the current state snapshot and scalar properties.
* **Event:** Append-only log. Many-to-one relationship with Enquiry.
* **Message:** Individual communication nodes within a thread. Many-to-one relationship with Enquiry.
* **Insight:** 1-to-1 sidecar model linked to Enquiry. Stores computed metadata without contaminating the root aggregate structure.

---

## 11. Scalability Roadmap

While currently optimized for zero-configuration local deployment, the system is designed to evolve across distinct phases:

* **Phase 1: PostgreSQL Migration:** Swap SQLite for Postgres to eliminate write lock contention and enable highly concurrent transaction processing.
* **Phase 2: Redis / Celery Orchestration:** Offload native background tasks to distributed Celery workers to scale I/O heavy SOP matching independently.
* **Phase 3: Kafka Event Streaming:** Transition the internal event sourcing table to a distributed Kafka log for cross-service telemetry and real-time analytics.
* **Phase 4: LLM-Based Intelligence:** Replace the deterministic keyword algorithm with an external LLM call within the existing isolated sidecar boundary.

---

## 12. Engineering Tradeoffs

* **SQLite over PostgreSQL:** Sacrifices high-concurrency write lock management for maximum portability.
* **Native Async over Celery:** Sacrifices distributed workers for single-process operational simplicity.
* **No Pagination:** Current list endpoints assume bounded datasets. Offset/limit cursor pagination is required prior to horizontal scaling.
