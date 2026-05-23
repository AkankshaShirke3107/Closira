<p align="center">
  <img src="Backend/docs/screenshots/header.png" width="100%" alt="Closira Banner"/>
</p>

# Closira: Event-Driven Enquiry Intelligence Engine

Closira is a production-grade full-stack system designed to ingest, classify, and orchestrate inbound customer communications. It implements a decoupled service architecture, append-only event sourcing for state transitions, and a deterministic AI engine for real-time risk scoring and priority routing.

---

## ⚡ Quick System Flow

1. **Ingest:** Client submits `POST /enquiry/` via transport layer.
2. **Compute:** Synchronous sidecar assigns deterministic risk and sentiment scores.
3. **Persist:** Root aggregate and initial timeline events commit via atomic transaction.
4. **Delegate:** Native background workers execute SOP string-matching for automated replies.
5. **Serve:** Read-optimized SQL aggregations power real-time dashboard metrics.

---

## 🎯 Why This System Matters

Closira models the architectural realities of enterprise SaaS development. By enforcing strict separation of transport from business logic, explicitly handling background race conditions, and writing immutable cryptographic-style audit trails (event sourcing), the system prioritizes telemetry, compliance, and observability. It demonstrates engineering maturity far beyond standard CRUD applications.

---

## 📸 System Overview

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
  <img src="Backend/docs/screenshots/architecture_v2.png" width="100%" alt="Closira Architecture and Workflow"/>
</p>

### API Interface
<p align="center">
  <img src="Backend/docs/screenshots/swagger.png" width="100%" alt="Swagger API"/>
</p>

---

## 🏗 System Architecture

The backend adheres strictly to Domain-Driven Design (DDD) principles. The HTTP routing layer acts exclusively as a transport protocol, completely decoupled from the service logic. All state mutations occur within isolated transaction boundaries.

```text
[ React Native Thin Client ]
             │
             ▼
[ FastAPI Routing Layer ] -> Domain Validation & Transport
             │
             ▼
[ Core Service Layer ] -> Transaction Management & Business Logic
             │
      ┌──────┴──────┐
      ▼             ▼
[ SQLite DB ]  [ Background Workers ]
   (ORM)         (SOP matching, async I/O)
      │
      ▼
[ Deterministic AI Sidecar ]
```

---

## 🧠 System Design Decisions

* **SQLite Usage:** Selected for zero-configuration, standalone deployment. To mitigate lock contention from concurrent writes, the system minimizes transaction lifetimes and explicitly guards against race conditions in the application layer.
* **BackgroundTasks over Celery:** FastAPI's native `BackgroundTasks` executes asynchronous I/O within the same process pool. This eliminates the operational overhead of managing Redis and Celery clusters, consciously trading distributed horizontal scalability for deployment simplicity.
* **Event Sourcing:** State transitions (e.g., `processing` -> `escalated`) do not simply overwrite status columns. They append immutable records to an `events` table, guaranteeing a perfect audit trail of system history.
* **Deterministic AI Layer:** Sentiment and risk classifications utilize an in-memory weighted keyword engine rather than external LLM APIs. This guarantees sub-millisecond execution, zero network latency, and 100% reproducible test suites.

---

## ⚙️ Core Engineering Features

* **Workflow Engine:** A rigid finite state machine governs enquiry lifecycles (`new`, `processing`, `qualified`, `escalated`).
* **SOP Matching Engine:** Background thread workers parse inbound message content against standard operating procedures to orchestrate automated responses.
* **Timeline Auditing:** Every system action, manual intervention, and state mutation is logged immutably.
* **AI Risk Scoring:** Synchronous sidecar computations assign priority tiers (P0, P1, P2) using channel vectors and negative sentiment multipliers.
* **Escalation Logic:** Automated interception algorithms reroute high-risk workflows requiring immediate operator intervention.

---

## 🔌 API Design

The API adheres to REST semantics while optimizing payload structures for client rendering.

* `POST /enquiry/`: Ingests data, synchronously computes the AI insight sidecar, persists the initial timeline event, and delegates SOP matching to a background worker.
* `GET /enquiry/{id}`: Returns a deeply nested resource containing the root enquiry entity, the AI sidecar, and the chronologically ordered message thread.
* `GET /enquiries/stats`: Uses native SQL aggregations (`COUNT()`) to compute dashboard metrics without loading row data into application memory.
* `GET /enquiry/{id}/history`: Exposes the immutable event stream for audit and telemetry.

---

## 🗄 Data Model

The database schema utilizes SQLAlchemy declarative mapping enforced by strict foreign key constraints.

* **Enquiry:** The root aggregate. Maintains the current state snapshot and scalar properties.
* **Event:** Append-only log. Many-to-one relationship with Enquiry.
* **Message:** Individual communication nodes within a thread. Many-to-one relationship with Enquiry.
* **Insight:** 1-to-1 sidecar model linked to Enquiry. Stores computed metadata (sentiment, priority) without contaminating the root aggregate structure.

---

## 📱 Frontend Client

The mobile application is a React Native (Expo) thin client.

* **Navigation:** Bottom tab and stack navigation structure.
* **UI Architecture:** Component-based rendering decoupling layout from state.
* **Data Abstraction:** Driven by a local mock JSON layer designed to perfectly mirror backend API contracts, allowing an immediate drop-in replacement to HTTP `fetch` calls.
* **Views:** Dashboard metrics, Lead processing queues, and Conversation timelines directly mapping to backend domain entities.

---

## 📂 Project Structure

```text
Closira/
├── Frontend/                 # React Native Mobile Dashboard (Expo)
│   ├── components/           # Reusable UI cards and badges
│   ├── constants/            # Design system tokens (colors, typography)
│   ├── mock/                 # Local JSON abstraction layer
│   ├── navigation/           # Tab and stack routing
│   └── screens/              # Dashboard, Leads, Escalations views
├── Backend/                  # FastAPI Application Core
│   ├── app/                  # ORM models, routers, and domain services
│   ├── docs/                 # Architecture documentation
│   └── verify_backend.py     # End-to-End automated validation script
└── README.md
```

---

## 🧪 Testing & Reliability

* **E2E Verification:** An automated integration script (`verify_backend.py`) executes full HTTP lifecycles against a live server.
* **Concurrency Defense:** Test suites intentionally simulate race conditions by firing manual escalations during async worker sleep windows, verifying that workers correctly abort stale database writes.
* **Domain Exceptions:** `EnquiryNotFoundError` prevents business logic from coupling to HTTP transport layers, keeping services framework-agnostic.

---

## ⚖️ Engineering Tradeoffs

* **No PostgreSQL:** Sacrifices high-concurrency write lock management for maximum portability.
* **No Redis / Celery:** Sacrifices distributed background workers for single-process operational simplicity.
* **No Authentication Layer:** Sacrifices identity verification to focus computational complexity entirely on workflow engine mechanics.
* **No Pagination:** Current list endpoints assume bounded datasets. Offset/limit cursor pagination must be implemented prior to horizontal scaling.

---

## 🚀 Run Instructions

### API Server (Backend)

**Prerequisites:** Python 3.10+

```bash
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
*Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.*

### Mobile App (Frontend)

```bash
cd Frontend
npm install
npx expo start
```
*Note: EAS build profiles are configured in `eas.json` for internal preview distributions.*
