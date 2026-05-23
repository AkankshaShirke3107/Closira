<p align="center">
  <img src="Backend/docs/screenshots/header.png" width="100%" alt="Closira Banner"/>
</p>

# Closira

An event-driven AI-powered CRM that transforms raw customer enquiries into structured, prioritized, and auditable workflows in real time.

Built with:
- Deterministic AI scoring (no LLM dependency)
- Event-sourced architecture
- Background workflow orchestration
- Mobile-first operations dashboard

---

## System Overview

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

## Why This System Matters

Closira models the architectural realities of enterprise SaaS development. Rather than acting as a simple CRUD wrapper, it enforces strict separation of transport protocols from domain logic. By explicitly handling background race conditions and persisting immutable, cryptographic-style audit trails via event sourcing, the system prioritizes telemetry, compliance, and runtime observability over naive data mutation.

---

## Request Lifecycle

1. **Ingest:** Client submits HTTP `POST /enquiry/` via the FastAPI transport boundary.
2. **Compute:** A synchronous sidecar assigns deterministic risk and sentiment vectors.
3. **Persist:** The root aggregate and its initial timeline event commit within a single atomic database transaction.
4. **Delegate:** Native background workers take over, executing SOP string-matching to dispatch automated replies.
5. **Serve:** Read-optimized SQL aggregations power real-time frontend dashboard metrics without memory-heavy application joins.

---

## System Architecture

The backend strictly adheres to Domain-Driven Design (DDD) principles. The HTTP routing layer acts exclusively as a transport protocol, completely insulated from the service logic. All domain mutations occur strictly within isolated transaction boundaries.

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

## Core Engineering Components

### 1. Workflow Engine & Event Sourcing
A rigid finite state machine governs enquiry lifecycles (`new`, `processing`, `qualified`, `escalated`). State transitions do not destructively overwrite status columns; they append immutable records to an `events` table, guaranteeing a perfect historical audit trail of system behavior.

### 2. Deterministic AI Sidecar
Sentiment and risk classifications utilize an in-memory weighted keyword engine rather than external LLM APIs. This sidecar pattern isolates AI metadata from the core domain model while guaranteeing sub-millisecond execution, zero network latency, and 100% reproducible test suites.

### 3. Background Processing & Race Condition Guards
FastAPI's native `BackgroundTasks` executes asynchronous I/O within the same process pool, avoiding the infrastructure overhead of Redis/Celery. To maintain integrity, these background routines explicitly guard against database race conditions, aborting stale writes if a manual escalation occurs mid-processing.

### 4. Automated Escalation Logic
Automated interception algorithms constantly evaluate incoming workflow states, rerouting high-risk or negatively scored communications into queues requiring immediate operator intervention.

---

## API Design

The API adheres to REST semantics while optimizing payload structures for efficient client rendering.

* `POST /enquiry/`: Ingests data, synchronously computes the AI insight sidecar, persists the initial timeline event, and delegates SOP matching to a background worker.
* `GET /enquiry/{id}`: Returns a deeply nested resource encompassing the root enquiry entity, the AI sidecar, and the chronologically ordered message thread.
* `GET /enquiries/stats`: Uses native SQL aggregations (`COUNT()`) to compute dashboard metrics, bypassing the need to load row data into application memory.
* `GET /enquiry/{id}/history`: Exposes the immutable event stream for audit and telemetry integration.

---

## Data Model

The database schema utilizes SQLAlchemy declarative mapping, enforced by strict foreign key constraints.

* **Enquiry:** The root aggregate. Maintains the current state snapshot and scalar properties.
* **Event:** Append-only log. Many-to-one relationship with Enquiry.
* **Message:** Individual communication nodes within a thread. Many-to-one relationship with Enquiry.
* **Insight:** 1-to-1 sidecar model linked to Enquiry. Stores computed metadata without contaminating the root aggregate structure.

---

## Frontend Contract

The mobile application operates as a React Native (Expo) thin client, completely decoupled from backend persistence.

* **Navigation:** Tab and stack routing hierarchies.
* **UI Architecture:** Component-based rendering decoupling visual layout from application state.
* **Data Abstraction:** Driven by a local mock JSON layer designed to perfectly mirror backend API contracts, allowing an immediate, zero-friction drop-in replacement to HTTP `fetch` calls.
* **Views:** Dashboard metrics, Lead processing queues, and Conversation timelines directly map to backend domain entities.

---

## Testing & Reliability

* **E2E Verification:** An automated integration script (`verify_backend.py`) executes full HTTP lifecycles against a live server.
* **Concurrency Defense:** Test suites intentionally simulate race conditions by firing manual escalations during async worker sleep windows, verifying that workers correctly abort stale database writes.
* **Domain Exceptions:** `EnquiryNotFoundError` prevents business logic from coupling to HTTP transport layers, keeping services framework-agnostic.

---

## Engineering Tradeoffs

* **SQLite over PostgreSQL:** Selected for zero-configuration, standalone deployment. Sacrifices high-concurrency write lock management for maximum portability.
* **Native Async over Celery:** Sacrifices distributed background workers for single-process operational simplicity.
* **No Authentication Layer:** Sacrifices identity verification to focus computational complexity entirely on workflow engine mechanics.
* **No Pagination:** Current list endpoints assume bounded datasets. Offset/limit cursor pagination must be implemented prior to horizontal scaling.

---

## Project Structure

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

## Run Instructions

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
