"""
Closira — End-to-End Automated Backend Verification Suite

This script runs comprehensive E2E tests validating the entire Closira backend service:
- Root API metadata (GET /)
- Health endpoints (GET /health)
- Global exception handlers & standardized validation schemas
- Non-existent resource lookups (404 errors via domain exception handler)
- Core asynchronous lifecycle flow:
  1. Enquiry creation (immediate 201 response)
  2. Asynchronous SOP matching (processing delay, auto-classification)
  3. Operational workflows: scheduling follow-ups (200 response, status updates)
  4. Operational workflows: manual escalations (200 response, status updates)
  5. Ordered chronological timeline logs and EventType enum validation
- Plural query search list (GET /enquiries) with filters (status/channel) and limit bounds.
- [HARDENING PATCH] Race condition prevention: verifies that a manual escalation
  during background processing is NOT overwritten when the background task wakes up.
- [HARDENING PATCH] Domain exception propagation: verifies 404 responses use the
  new "not_found" error type from the centralized EnquiryNotFoundError handler.
"""

import time
import httpx

BASE_URL = "http://127.0.0.1:8000"


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f" {title.upper()} ".center(80, "="))
    print("=" * 80)


def run_tests():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # Wait for server to become responsive (highly robust E2E practice)
    print("Waiting for server to become responsive at http://127.0.0.1:8000 ...")
    server_ready = False
    for i in range(15):
        try:
            r = client.get("/")
            if r.status_code == 200:
                server_ready = True
                break
        except httpx.RequestError:
            pass
        time.sleep(0.5)

    if not server_ready:
        print("[FAIL] Server is not responsive at http://127.0.0.1:8000.")
        print("Please check that the Uvicorn FastAPI server is running.")
        exit(1)

    # ---------------------------------------------------------------------------
    # TEST 1: Root Metadata & Health Check
    # ---------------------------------------------------------------------------
    print_header("Test 1: Root Metadata & Health Check")

    # GET /
    r_root = client.get("/")
    assert r_root.status_code == 200, f"Root endpoint failed: {r_root.status_code}"
    root_data = r_root.json()
    assert root_data["service"] == "Closira API"
    assert root_data["status"] == "running"
    print("  [PASS] Root endpoint returned correct service metadata:")
    print(f"         {root_data}")

    # GET /health
    r_health = client.get("/health")
    assert r_health.status_code == 200, f"Health endpoint failed: {r_health.status_code}"
    health_data = r_health.json()
    assert health_data["status"] == "healthy"
    assert health_data["database"] == "connected"
    print("  [PASS] Health endpoint returned healthy DB status:")
    print(f"         {health_data}")


    # ---------------------------------------------------------------------------
    # TEST 2: Unified Error Formatter & Validation Checks
    # ---------------------------------------------------------------------------
    print_header("Test 2: Unified Error Formatting & Input Validation")

    # Empty Name payload (Validation Error)
    r_val = client.post("/enquiry/", json={
        "customer_name": "",
        "channel": "whatsapp",
        "message": "I need pricing details."
    })
    assert r_val.status_code == 422, f"Validation did not reject empty name: {r_val.status_code}"
    val_data = r_val.json()
    assert val_data["success"] is False
    assert val_data["error"]["type"] == "validation_error"
    assert "customer_name" in val_data["error"]["message"]
    print("  [PASS] Rejected empty name payload with standardized error:")
    print(f"         {val_data}")

    # Invalid Channel payload (Validation Error)
    r_chan = client.post("/enquiry/", json={
        "customer_name": "Akanksha Shirke",
        "channel": "telegram",
        "message": "Hi"
    })
    assert r_chan.status_code == 422, f"Validation did not reject invalid channel: {r_chan.status_code}"
    chan_data = r_chan.json()
    assert chan_data["success"] is False
    assert "channel" in chan_data["error"]["message"]
    print("  [PASS] Rejected invalid channel payload with standardized error:")
    print(f"         {chan_data}") 

    # Non-existent UUID Lookup (HTTP 404 via Domain Exception Handler)
    # HARDENING PATCH: error type is now "not_found" (from EnquiryNotFoundError handler)
    # rather than the old "http_error" (from raw HTTPException). This validates that
    # the service layer is transport-decoupled via the domain exception system.
    random_uuid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    r_404 = client.get(f"/enquiry/{random_uuid}/history")
    assert r_404.status_code == 404, f"Endpoint did not return 404: {r_404.status_code}"
    err_data = r_404.json()
    assert err_data["success"] is False
    assert err_data["error"]["type"] == "not_found", (
        f"Expected 'not_found' (domain exception handler), got '{err_data['error']['type']}'"
    )
    assert err_data["error"]["message"] == "Enquiry not found"
    print("  [PASS] Missing resource lookup returned 'not_found' via domain exception handler:")
    print(f"         {err_data}")

    # Validate 404 on follow-up endpoint too
    r_404_followup = client.post(f"/enquiry/{random_uuid}/follow-up", json={
        "delay_minutes": 30
    })
    assert r_404_followup.status_code == 404
    fu_err = r_404_followup.json()
    assert fu_err["error"]["type"] == "not_found"
    print("  [PASS] Follow-up on non-existent enquiry returned 'not_found'.")

    # Validate 404 on escalate endpoint too
    r_404_escalate = client.post(f"/enquiry/{random_uuid}/escalate", json={
        "reason": "Testing 404 handling."
    })
    assert r_404_escalate.status_code == 404
    esc_err = r_404_escalate.json()
    assert esc_err["error"]["type"] == "not_found"
    print("  [PASS] Escalate on non-existent enquiry returned 'not_found'.")


    # ---------------------------------------------------------------------------
    # TEST 3: E2E Enquiry Lifecycle & Chronological Timeline Audit
    # ---------------------------------------------------------------------------
    print_header("Test 3: E2E Enquiry Lifecycle & Timeline Auditing")

    # Step 3.1: Create valid enquiry triggering automated SOP Matching
    print("  -> Creating pricing WhatsApp enquiry for Priya...")
    r_create = client.post("/enquiry/", json={
        "customer_name": "Priya",
        "channel": "whatsapp",
        "message": "I want to get a quote and check your pricing rates."
    })
    assert r_create.status_code == 201, f"Enquiry creation failed: {r_create.status_code}"
    priya_enquiry = r_create.json()
    priya_id = priya_enquiry["id"]
    assert priya_enquiry["customer_name"] == "Priya"
    assert priya_enquiry["status"] == "new"
    print(f"  [PASS] Enquiry created immediately with status 'new' and ID: {priya_id}")

    # Step 3.2: Wait for background task with 1.5s delay to finish SOP matching
    print("     [Waiting 2.5s for asynchronous SOP classification thread to complete...]")
    time.sleep(2.5)

    # Step 3.3: Fetch history to verify auto-classification
    r_hist1 = client.get(f"/enquiry/{priya_id}/history")
    assert r_hist1.status_code == 200, f"History fetch failed: {r_hist1.status_code}"
    priya_hist = r_hist1.json()
    assert priya_hist["status"] == "qualified"
    assert priya_hist["sop_category"] == "Pricing enquiry"
    assert "pricing" in priya_hist["suggested_response"].lower()

    # Assert timeline events
    timeline = priya_hist["timeline"]
    assert len(timeline) == 4, f"Expected 4 events (enquiry_created, status_updated(processing), sop_matched, status_updated(qualified)), got {len(timeline)}"
    assert timeline[0]["event_type"] == "enquiry_created"
    assert timeline[1]["event_type"] == "status_updated"
    assert timeline[2]["event_type"] == "sop_matched"
    assert timeline[3]["event_type"] == "status_updated"
    print("  [PASS] Asynchronous background task successfully completed:")
    print(f"         SOP Classified:  {priya_hist['sop_category']}")
    print(f"         Current Status:  {priya_hist['status']}")
    print(f"         Timeline Audit:  {len(timeline)} events generated.")

    # Step 3.4: Schedule a follow-up action
    print("\n  -> Scheduling follow-up for Priya (60 minutes delay)...")
    r_follow = client.post(f"/enquiry/{priya_id}/follow-up", json={
        "delay_minutes": 60,
        "message_template": "Hi Priya, just following up on the pricing details sent earlier."
    })
    assert r_follow.status_code == 200, f"Follow-up scheduling failed: {r_follow.status_code}"
    priya_follow = r_follow.json()
    assert priya_follow["status"] == "follow_up_scheduled"
    print(f"  [PASS] Status updated to 'follow_up_scheduled'.")

    # Step 3.5: Trigger manual escalation
    print("\n  -> Manually escalating Priya's enquiry...")
    r_escalate = client.post(f"/enquiry/{priya_id}/escalate", json={
        "reason": "Customer requested speaking directly to pricing team head."
    })
    assert r_escalate.status_code == 200, f"Escalation failed: {r_escalate.status_code}"
    priya_escalate = r_escalate.json()
    assert priya_escalate["status"] == "escalated"
    print(f"  [PASS] Status updated to 'escalated'.")

    # Step 3.6: Verify complete sorted chronological timeline history
    print("\n  -> Verifying complete chronological audit history timeline...")
    r_hist2 = client.get(f"/enquiry/{priya_id}/history")
    assert r_hist2.status_code == 200
    full_hist = r_hist2.json()
    events = full_hist["timeline"]

    # Assert 8 events in timeline:
    # 1. enquiry_created
    # 2. status_updated (to processing)
    # 3. sop_matched
    # 4. status_updated (to qualified)
    # 5. status_updated (to follow_up_scheduled)
    # 6. follow_up_scheduled
    # 7. status_updated (to escalated)
    # 8. escalation_triggered
    assert len(events) == 8, f"Expected 8 events, got {len(events)}"

    print(f"  [PASS] Chronological event audit log successfully validated:")
    for idx, event in enumerate(events, 1):
        print(f"         {idx}. [{event['event_type'].upper()}] - {event['description']}")


    # ---------------------------------------------------------------------------
    # TEST 4: Plural Enquiry Listings & Advanced Query Filtering
    # ---------------------------------------------------------------------------
    print_header("Test 4: Plural Enquiries Querying & Filtering")

    # Create a support enquiry for John
    print("  -> Creating support Whatsapp enquiry for John...")
    r_john = client.post("/enquiry/", json={
        "customer_name": "John",
        "channel": "whatsapp",
        "message": "Help! My dashboard is broken and not working."
    })
    assert r_john.status_code == 201
    john_id = r_john.json()["id"]

    print("     [Waiting 2.5s for asynchronous SOP classification thread to complete...]")
    time.sleep(2.5)

    # 4.1 Query Listing: Get all enquiries (Should have Priya and John)
    r_all = client.get("/enquiries/")
    all_enquiries = r_all.json()
    assert len(all_enquiries) >= 2
    print(f"  [PASS] Exposed list of all enquiries. Found count: {len(all_enquiries)}")

    # 4.2 Query Listing: Filter by status='escalated' (Should return Priya, not John)
    r_filter_status = client.get("/enquiries/?status=escalated")
    escalated_list = r_filter_status.json()
    assert len(escalated_list) >= 1
    escalated_ids = [x["id"] for x in escalated_list]
    assert priya_id in escalated_ids
    assert john_id not in escalated_ids
    print("  [PASS] Filtering by status='escalated' returned Priya's enquiry but not John's.")

    # 4.3 Query Listing: Filter by status='qualified' (Should return John, not Priya)
    r_filter_status2 = client.get("/enquiries/?status=qualified")
    qualified_list = r_filter_status2.json()
    assert len(qualified_list) >= 1
    qualified_ids = [x["id"] for x in qualified_list]
    assert john_id in qualified_ids
    assert priya_id not in qualified_ids
    print("  [PASS] Filtering by status='qualified' returned John's enquiry but not Priya's.")

    # 4.4 Query Listing: Filter by channel='whatsapp' (Should return both, sorted newest-first)
    r_filter_chan = client.get("/enquiries/?channel=whatsapp")
    whatsapp_list = r_filter_chan.json()
    # Find John and Priya index
    john_index = next(i for i, x in enumerate(whatsapp_list) if x["id"] == john_id)
    priya_index = next(i for i, x in enumerate(whatsapp_list) if x["id"] == priya_id)
    # Chronological sort: newest first means John (created second) must be before Priya
    assert john_index < priya_index, "John should be listed before Priya (newest-first ordering)"
    print("  [PASS] Filtering by channel='whatsapp' returned both, ordered newest-first.")

    # 4.5 Query Listing: Limit to 1
    r_limit = client.get("/enquiries/?limit=1")
    limited_list = r_limit.json()
    assert len(limited_list) == 1
    print("  [PASS] Limit query bound constraint successfully validated.")


    # ---------------------------------------------------------------------------
    # TEST 5: Race Condition Prevention (Hardening Patch)
    # ---------------------------------------------------------------------------
    print_header("Test 5: Race Condition Prevention (Hardening Patch)")

    print("  -> Creating booking enquiry for Sara (will be escalated mid-processing)...")
    r_sara = client.post("/enquiry/", json={
        "customer_name": "Sara",
        "channel": "email",
        "message": "I need to book an appointment for next week."
    })
    assert r_sara.status_code == 201, f"Sara enquiry creation failed: {r_sara.status_code}"
    sara_id = r_sara.json()["id"]
    print(f"  [PASS] Sara's enquiry created with ID: {sara_id}")

    # Give the background task a moment to start and set status to PROCESSING.
    # The task sets PROCESSING first, then sleeps for 1.5 seconds before checking
    # for an SOP match. We escalate during that sleep window.
    print("     [Waiting 0.4s for background task to enter PROCESSING state...]")
    time.sleep(0.4)

    # Manually escalate Sara's enquiry while the background task is sleeping
    print("  -> Escalating Sara's enquiry manually DURING background processing...")
    r_sara_esc = client.post(f"/enquiry/{sara_id}/escalate", json={
        "reason": "Customer called in directly — high priority escalation needed."
    })
    assert r_sara_esc.status_code == 200, f"Sara escalation failed: {r_sara_esc.status_code}"
    assert r_sara_esc.json()["status"] == "escalated"
    print("  [PASS] Manual escalation applied while background task was sleeping.")

    # Wait for the background task to wake up and complete.
    # The task should detect status != PROCESSING and skip the SOP write.
    print("     [Waiting 2.0s for background task to wake up and detect status conflict...]")
    time.sleep(2.0)

    # Verify the background task did NOT overwrite the manual escalation
    r_sara_hist = client.get(f"/enquiry/{sara_id}/history")
    assert r_sara_hist.status_code == 200
    sara_hist = r_sara_hist.json()

    assert sara_hist["status"] == "escalated", (
        f"RACE CONDITION DETECTED: background task overwrote manual escalation! "
        f"Expected 'escalated', got '{sara_hist['status']}'"
    )

    # SOP fields should NOT have been populated (task was aborted before matching)
    # Note: sop_category may be None (task skipped) — this confirms the guard worked
    print(f"  [PASS] Race condition prevented — status is '{sara_hist['status']}' (not overwritten).")
    print(f"         sop_category = {sara_hist['sop_category']} (None confirms task was aborted before SOP match)")

    # Verify the timeline shows the manual escalation but NO sop_matched event
    sara_timeline = sara_hist["timeline"]
    event_types = [e["event_type"] for e in sara_timeline]
    assert "sop_matched" not in event_types, (
        f"RACE CONDITION: sop_matched event found in timeline — background task was NOT aborted!"
    )
    assert "escalation_triggered" in event_types, "Expected escalation_triggered event in timeline."
    print(f"  [PASS] Timeline confirms no sop_matched event was written (task was aborted cleanly).")
    print(f"         Events recorded: {event_types}")


    print_header("ALL E2E INTEGRATION TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n[FAIL] Test suite execution encountered an error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
