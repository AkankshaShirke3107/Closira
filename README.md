# Closira

Event-driven customer relationship management and automated workflow engine.

Closira is a full-stack system designed to process, classify, and track inbound customer communications. It implements a decoupled service architecture, append-only event sourcing for state transitions, and a deterministic insight engine for real-time risk scoring and priority routing.

## Architecture

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

The backend follows a strict domain-driven design. The HTTP transport layer (routers) is decoupled from the business logic (services). All state changes are executed within atomic database transactions and synchronously emit timeline events.

## System Design Decisions

**SQLite Usage**
SQLite is used for local zero-config deployment. To mitigate lock contention from concurrent writes, the system minimizes transaction windows and handles race conditions explicitly in the application layer.

**BackgroundTasks over Celery**
FastAPI's native `BackgroundTasks` executes operations within the same process thread pool. This avoids the infrastructure complexity of Redis and Celery, trading horizontal scalability for operational simplicity.

**Event Sourcing**
State transitions (e.g., `processing` -> `escalated`) do not simply overwrite the status column. They write immutable records to an `events` table. This guarantees a cryptographic-style audit trail of when and why an enquiry changed state.

**Deterministic AI Layer**
Sentiment and risk scoring rely on an in-memory weighted keyword engine rather than external LLM APIs. This ensures sub-millisecond execution, zero network latency, and reproducible test cases.

## Core Features

* Workflow Engine: Strict finite state machine governing enquiry lifecycles (`new`, `processing`, `qualified`, `escalated`).
* SOP Matching Engine: Background processors parse message content against standard operating procedures to generate automated responses.
* Timeline Auditing: Every system action and state mutation is logged immutably.
* AI Risk Scoring: Synchronous sidecar computation assigns priority tiers (P0, P1, P2) based on channel vectors and negative sentiment signals.
* Escalation Logic: Automated interception of high-risk workflows requiring manual operator intervention.

## API Design

The API adheres to REST principles while optimizing for client rendering patterns.

* `POST /enquiry/`: Ingests data, synchronously computes the AI insight sidecar, persists the initial timeline event, and delegates SOP matching to a background worker.
* `GET /enquiry/{id}`: Returns a deeply nested resource containing the enquiry entity, the AI sidecar, and the complete chronologically ordered message thread.
* `GET /enquiries/stats`: Uses native SQL aggregation (`COUNT()`) to compute dashboard metrics without pulling row data into application memory.
* `GET /enquiry/{id}/history`: Exposes the immutable event stream for audit trails.

## Data Model

The schema uses SQLAlchemy declarative mapping with strict foreign key constraints.

* **Enquiry**: The root aggregate. Maintains the current state snapshot and scalar properties (channel, customer name).
* **Event**: Append-only log. Many-to-one relationship with Enquiry.
* **Message**: Represents individual communication nodes in a conversation thread. Many-to-one relationship with Enquiry.
* **Insight**: 1-to-1 sidecar model linked to Enquiry. Stores computed metadata (sentiment, priority) without mutating the root aggregate structure.

## Frontend

The mobile application is a React Native (Expo) thin client. 

* Navigation: Bottom tab and stack navigation structure.
* UI Architecture: Component-based rendering decoupling layout from state.
* Data Abstraction: Currently driven by a local mock JSON layer designed to mirror the backend API contracts, allowing immediate swap to `fetch` calls.
* Views: Dashboard metrics, Lead processing queues, and Conversation timelines mapping directly to the backend entities.

## Testing & Reliability

* E2E Verification: An automated integration script (`verify_backend.py`) executes full HTTP lifecycles against a live server.
* Concurrency Defense: Tests simulate race conditions by firing manual escalations during async sleep windows to ensure background workers abort stale writes.
* Domain Exceptions: `EnquiryNotFoundError` prevents business logic from coupling to `HTTPException(404)`.

## Tradeoffs

* **No PostgreSQL**: Sacrifices high-concurrency write locks for portability.
* **No Redis / Celery**: Sacrifices distributed background workers for single-process simplicity.
* **No Authentication Layer**: Sacrifices identity verification to focus entirely on the workflow engine mechanics.
* **No Pagination**: Current list endpoints assume bounded datasets. Offset/limit cursor pagination must be implemented before horizontal scaling.

## Run Instructions

**Backend Setup**
```bash
cd Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend Setup**
```bash
cd Frontend
npm install
npx expo start
```
*Note: EAS build profiles are configured in `eas.json` for internal preview distributions.*

## Why this system is production-relevant

Closira models the architectural realities of modern SaaS backend engineering. The separation of transport from business logic allows the API layer to be swapped entirely. The choice to use event sourcing provides the foundational telemetry required for compliance and observability in real-world deployments. By explicitly handling race conditions in background workers and preventing dirty database writes, the system demonstrates maturity beyond standard CRUD applications.
