# Closira — Step 6: Finalization, Hardening, and Submission Polish

This plan outlines the final consolidation and polish of the Closira backend to prepare it for recruiter review, GitHub submission, and walk-through readiness. We will fully implement all missing operational endpoints (Step 4), apply production-grade hardening, exception handling, and observability patterns (Step 5), and provide full automated verification, architecture docs, and a polished README.md (Step 6).

## User Review Required
> [!IMPORTANT]
> - **Zero Infrastructure additions:** Per your constraints, we use only FastAPI BackgroundTasks and local SQLite, keeping the runtime fully self-contained.
> - **Unified Error Format:** All API routes (including validation and internal server errors) will consistently output `{ success: false, error: { type, message } }`.
> - **Consolidated Execution:** We will implement all required logic across schemas, services, routers, middleware, enums, exception handlers, and banners in a single vertical slice to deliver a complete, fully functional backend.

---

## Proposed Changes

We will group our planned edits by layer:

---

### 1. Database & Domain Models

#### [MODIFY] [models/event.py](file:///c:/Users/Akanksha Shirke/OneDrive/Documents/Projects/Closira/backend/app/models/event.py)
*   Define a centralized `EventType(str, enum.Enum)`:
    *   `ENQUIRY_CREATED = "enquiry_created"`
    *   `STATUS_UPDATED = "status_updated"`
    *   `SOP_MATCHED = "sop_matched"`
    *   `ESCALATION_TRIGGERED = "escalation_triggered"`
    *   `FOLLOW_UP_SCHEDULED = "follow_up_scheduled"`
*   Update the `Event.event_type` column to use `Enum(EventType)` to enforce database-level validation.
*   Enforce chronological order in relationships.

---

### 2. Interface layer (Pydantic Schemas)

#### [MODIFY] [schemas/enquiry.py](file:///c:/Users/Akanksha Shirke/OneDrive/Documents/Projects/Closira/backend/app/schemas/enquiry.py)
*   Add `EnquiryFollowUpRequest` (accepts `delay_minutes` $> 0$ and optional `message_template`).
*   Add `EnquiryEscalateRequest` (accepts non-empty `reason`).
*   Add `EventResponse` (to map timeline events).
*   Add `EnquiryHistoryResponse` (to map the chronological `timeline: list[EventResponse]`).
*   Ensure all models define full descriptions, summaries, and complete request/response examples for a flawless Swagger UI experience.

---

### 3. Business Logic Layer (Services)

#### [MODIFY] [services/enquiry_service.py](file:///c:/Users/Akanksha Shirke/OneDrive/Documents/Projects/Closira/backend/app/services/enquiry_service.py)
*   Refactor existing methods (`create_enquiry()`, `create_event()`, `process_enquiry_background()`) to use the new `EventType` enum.
*   Implement `schedule_follow_up(db, enquiry_id, delay_minutes, message_template)`:
    *   Verifies enquiry, raises HTTP 404 if missing.
    *   Updates status to `follow_up_scheduled`.
    *   Appends `status_updated` and `follow_up_scheduled` timeline events.
*   Implement `escalate_enquiry_manual(db, enquiry_id, reason)`:
    *   Verifies enquiry, raises HTTP 404 if missing.
    *   Updates status to `escalated`.
    *   Appends `status_updated` and `escalation_triggered` events.
*   Implement `get_enquiry_history(db, enquiry_id)`:
    *   Builds the chronological timeline payload.
*   Implement `list_enquiries(db, status, channel, limit)`:
    *   Returns filtered, newest-first ordered list of enquiries.

---

### 4. API Routers

#### [MODIFY] [routers/enquiry.py](file:///c:/Users/Akanksha Shirke/OneDrive/Documents/Projects/Closira/backend/app/routers/enquiry.py)
*   Add operational routes to `router` (singular):
    *   `POST /enquiry/{id}/follow-up` $\rightarrow$ schedule follow-up
    *   `POST /enquiry/{id}/escalate` $\rightarrow$ trigger manual escalation
    *   `GET /enquiry/{id}/history` $\rightarrow$ chronological timeline logs
*   Add `router_plural = APIRouter(prefix="/enquiries", tags=["Enquiries"])` with:
    *   `GET /` $\rightarrow$ filter-supported query list.

---

### 5. Application Entry Point, Logger, & Middleware

#### [MODIFY] [logging/config.py](file:///c:/Users/Akanksha Shirke/OneDrive/Documents/Projects/Closira/backend/app/logging/config.py)
*   Define a context variable `request_correlation_id: ContextVar[str]`.
*   Update `JSONFormatter` to append `correlation_id` to log outputs if active.

#### [MODIFY] [main.py](file:///c:/Users/Akanksha Shirke/OneDrive/Documents/Projects/Closira/backend/app/main.py)
*   Register both `health` and new plural/singular routers.
*   Implement a high-quality HTTP logging middleware mapping request durations and correlation IDs.
*   Register global exception handlers for `RequestValidationError`, `HTTPException`, and general `Exception` mapping to standard unified JSON error blocks.
*   Implement a beautiful startup ASCII banner displaying version, env, and docs location.
*   Implement root endpoint `GET /` returning basic service metadata.

---

## Verification Plan

### Automated Run
1.  Start the FastAPI Uvicorn server: `.\venv\Scripts\uvicorn app.main:app --reload`
2.  Run `.\venv\Scripts\python verify_backend.py` from the `backend/` directory.
3.  Confirm that all scenarios print `[PASS]` and output the full chronological history trace successfully.
