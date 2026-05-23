# Closira Architecture Overview

This document outlines the architectural patterns and engineering decisions utilized in the Closira backend.

## 1. Request Lifecycle & Layered Architecture

Closira utilizes a strict 3-tier architecture to separate transport concerns from business rules:

1. **Routers (`app/routers/`):** Thin HTTP controllers. They define the path, validate inputs/outputs via Pydantic schemas, and pass the data directly to the service layer. They do not write SQL or implement business logic.
2. **Services (`app/services/`):** The core business layer. This is where transactions are managed, database sessions are utilized, and domain logic (like scheduling follow-ups or evaluating background states) is executed.
3. **Database (`app/models/`):** SQLAlchemy ORM declarative models mapping Python classes to SQL tables.

## 2. Asynchronous Background Workflow

Customer enquiries (WhatsApp, Email) are often erratic and require expensive processing (like hitting an LLM for classification or running complex SOP matching). 

**The Flow:**
* `POST /enquiries` immediately inserts the enquiry into the database with a `NEW` status and returns a `201 Created` to the client (under 50ms).
* FastAPI's `BackgroundTasks` executes `process_enquiry_background()` asynchronously.
* The background worker updates the status to `PROCESSING`, runs the simulated delay and SOP matcher, and transitions the state to `QUALIFIED` or `ESCALATED`.

### Concurrency Protection (The Race Condition Guard)
Because the background task runs on a separate thread, a human operator could potentially trigger a manual escalation (`POST /enquiries/{id}/escalate`) *while* the background task is still running. 

To prevent the background task from blindly overwriting the human operator's state change, the worker **re-fetches the record from the database** after its delay. It verifies that `status == PROCESSING`. If the status has changed, it logs a warning and cleanly aborts the operation.

## 3. Append-Only Event Timeline (Event Sourcing Pattern)

Instead of only updating the `status` column and losing the history of *when* or *why* it changed, Closira employs an **Append-Only Event Timeline**.

* Every operational action (creation, SOP match, escalation, follow-up) generates an immutable `Event` record.
* These events form a chronological audit log accessible via `GET /enquiries/{id}/history`.
* This design makes the system highly observable and allows for future analytics (e.g., measuring the exact time between an enquiry entering `PROCESSING` and being `QUALIFIED`).

## 4. Structured JSON Logging & Tracing

Standard `print()` statements are insufficient for production debugging. Closira implements **Structured JSON Logging**:
* All logs are emitted as JSON objects, making them instantly parseable by log aggregators (ELK, Datadog).
* **Correlation IDs:** A global HTTP middleware intercepts every request, generates an `X-Correlation-ID`, and stores it in a thread-safe Python `ContextVar`. The custom JSON formatter automatically injects this ID into every log emitted during that request, allowing developers to trace the entire lifecycle of a single HTTP call across hundreds of concurrent users.
* **Traceback Serialization:** Exceptions are fully serialized into the JSON payload (type, message, and formatted traceback stack) preventing silent errors.

## 5. Domain Exceptions vs. HTTP Exceptions

**The Issue:** If a service explicitly raises `fastapi.HTTPException`, it becomes permanently glued to the FastAPI web framework. You couldn't reuse that service in a Kafka consumer, a CLI script, or a Celery worker without causing HTTP errors.

**The Solution:** Services in Closira raise custom domain exceptions (e.g., `EnquiryNotFoundError` defined in `app/utils/exceptions.py`). `app/main.py` utilizes a centralized exception handler (`@app.exception_handler`) to map these domain exceptions to standard HTTP 404/500 JSON responses.

## 6. Scalability Tradeoffs

To keep this project focused on backend engineering patterns rather than infrastructure DevOps, two main tradeoffs were made:

1. **SQLite over PostgreSQL:** SQLite locks the entire database on writes. To mitigate this, database connections are managed properly, transactions are kept exceptionally short, and heavily filtered queries (like `status` and `channel`) are backed by database indexes.
2. **In-Memory BackgroundTasks over Celery/Redis:** FastAPI's `BackgroundTasks` are stored in memory. If the server crashes, the queue is lost. In a real production environment, this would be replaced by a durable message broker (RabbitMQ/Redis) and a distributed worker system (Celery/ARQ), but the Python interface inside the service layer would remain entirely unchanged.
