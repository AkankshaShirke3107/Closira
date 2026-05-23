# API Demo Walkthrough

This guide provides a step-by-step sequence for demoing the Closira backend to recruiters, interviewers, or clients using the built-in Swagger UI.

## 1. Start the Server

Open your terminal in the `Backend` directory and start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
Once running, open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

---

## 2. Demo Sequence

### A. Health Check
*   **Endpoint:** `GET /health`
*   **Action:** Click **Try it out** -> **Execute**.
*   **Explain:** "This is a standard production practice. The health endpoint pings the SQLite database (`SELECT 1`). If the DB is down, it returns a `503 Service Unavailable`, allowing load balancers to safely route traffic away from broken instances."

### B. Create an Enquiry (SOP Match Success)
*   **Endpoint:** `POST /enquiries/`
*   **Action:** Click **Try it out**, edit the JSON body, and click **Execute**.
    ```json
    {
      "customer_name": "Priya",
      "channel": "whatsapp",
      "message": "Can you send me your pricing details?"
    }
    ```
*   **Explain:** "Notice how we get a `201 Created` response instantly with the status `new`. The system doesn't make the user wait while we run our SOP classification. It spun up an asynchronous background task."

### C. Verify the Background Classification
*   **Endpoint:** `GET /enquiries/{id}/history`
*   **Action:** Copy the `id` from Priya's response in Step B, paste it here, and execute.
*   **Explain:** "Look at the `timeline` array. You can see a chronological append-only audit log:
    1. `enquiry_created`
    2. `status_updated` (to processing)
    3. `sop_matched` (it detected 'pricing' and generated a response)
    4. `status_updated` (to qualified)
    This Event Sourcing pattern is exactly how highly compliant systems track state changes."

### D. Schedule a Follow-up
*   **Endpoint:** `POST /enquiries/{id}/follow-up`
*   **Action:** Paste Priya's `id`, set `delay_minutes` to 60, and execute.
*   **Explain:** "We simulate an agent reviewing the SOP match and scheduling an automated follow-up. Check the history endpoint again — you'll see a new `follow_up_scheduled` event cleanly appended to the timeline."

### E. Demonstrate the Concurrency Race-Condition Guard
This is your strongest backend talking point.
*   **Endpoint:** `POST /enquiries/`
*   **Action:** Create a new enquiry for "John".
    ```json
    {
      "customer_name": "John",
      "channel": "email",
      "message": "I want to book an appointment."
    }
    ```
*   **Action:** As soon as you hit execute, *immediately* copy John's ID, go to `POST /enquiries/{id}/escalate`, paste the ID, and execute it within 1.5 seconds.
*   **Explain:** "In a naive system, the background task would wake up after its processing delay and blindly overwrite John's manual escalation back to 'qualified'. However, check John's history. The status is `escalated`. The background task includes a strict concurrency guard—it re-fetches the database record, sees the state was changed externally, and aborts safely to protect data integrity."

### F. Terminal Logs
*   **Action:** Show your terminal running the `uvicorn` server.
*   **Explain:** "Instead of messy print statements, all logs are emitted in structured JSON. Every log line contains an `X-Correlation-ID`. In a distributed microservices environment, this exact JSON payload gets piped into Datadog or ELK, allowing engineers to trace a single user's request across the entire system."
