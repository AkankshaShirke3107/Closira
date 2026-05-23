"""
Closira — Enquiry Service

Contains all business logic for enquiry operations.

Design decisions:
- All database operations happen here, NOT in routers
- Routers call service functions and return results
- This makes the business logic testable without HTTP
- Each function does one thing and logs its actions

HARDENING CHANGES (Engineering Audit Patch):
- Domain exceptions: HTTPException replaced with EnquiryNotFoundError.
  Services are now transport-agnostic; the HTTP layer maps domain exceptions
  to status codes in main.py's centralized exception handlers.
- Explicit rollbacks: every mutation path wraps in try/except with db.rollback()
  to prevent partially-open transactions from corrupting session state.
- Race condition guard in process_enquiry_background: re-fetches the enquiry
  after the simulated delay and verifies status is still PROCESSING before
  writing the SOP result. If a concurrent manual escalation or follow-up
  modified the status in the meantime, the background task logs a warning
  and exits without overwriting the newer operational state.
- asyncio.sleep NOTE: BackgroundTasks runs sync functions in Starlette's
  threadpool executor. Using asyncio.sleep() inside a sync thread would block
  the event loop — the opposite of what we want. time.sleep() is correct here.
  It is placed BEFORE any DB writes to minimize lock contention window.
"""

import time
from typing import Optional
from sqlalchemy.orm import Session

from app.models.enquiry import Enquiry, EnquiryStatus, ChannelType
from app.models.event import Event, EventType
from app.models.message import Message, MessageSender
from app.schemas.enquiry import EnquiryCreate
from app.logging.config import get_logger
from app.utils.exceptions import EnquiryNotFoundError

logger = get_logger(__name__)


def create_enquiry(db: Session, enquiry_data: EnquiryCreate) -> Enquiry:
    """
    Create a new enquiry in the database.

    Steps:
    1. Create the Enquiry record with status "new"
    2. Commit to generate the UUID
    3. Create the initial "enquiry_created" event
    4. Commit the event
    5. Refresh to load relationships
    """
    try:
        enquiry = Enquiry(
            customer_name=enquiry_data.customer_name,
            channel=enquiry_data.channel,
            message=enquiry_data.message,
            status=EnquiryStatus.NEW,
        )

        db.add(enquiry)
        db.commit()
        db.refresh(enquiry)

        logger.info(
            f"Enquiry created: {enquiry.id}",
            extra={"extra_data": {
                "enquiry_id": enquiry.id,
                "channel": enquiry.channel.value,
                "customer_name": enquiry.customer_name,
            }},
        )

        # Create the initial timeline event
        create_event(
            db=db,
            enquiry_id=enquiry.id,
            event_type=EventType.ENQUIRY_CREATED,
            description=(
                f"New enquiry received via {enquiry.channel.value} "
                f"from {enquiry.customer_name}."
            ),
        )

        # Create the initial customer message
        create_message(
            db=db,
            enquiry_id=enquiry.id,
            sender=MessageSender.CUSTOMER,
            text=enquiry_data.message,
        )

        # Generate AI insights (sentiment, risk, priority)
        from app.services.ai_insights_service import generate_insights
        insight = generate_insights(enquiry)
        db.add(insight)
        db.commit()
        db.refresh(enquiry)

        return enquiry

    except Exception as e:
        db.rollback()
        logger.error(
            f"Failed to create enquiry: {str(e)}",
            extra={"extra_data": {"error": str(e)}},
            exc_info=True,
        )
        raise


def create_event(
    db: Session,
    enquiry_id: str,
    event_type: EventType,
    description: str,
) -> Event:
    """
    Create a new event (timeline entry) for an enquiry.

    Events are append-only — they are never updated or deleted.
    This creates a clean audit trail of everything that happened.
    """
    try:
        event = Event(
            enquiry_id=enquiry_id,
            event_type=event_type,
            description=description,
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        logger.info(
            f"Event logged: {event_type.value}",
            extra={"extra_data": {
                "event_id": event.id,
                "enquiry_id": enquiry_id,
                "event_type": event_type.value,
            }},
        )

        return event

    except Exception as e:
        db.rollback()
        logger.error(
            f"Failed to create event for enquiry {enquiry_id}: {str(e)}",
            extra={"extra_data": {"enquiry_id": enquiry_id, "error": str(e)}},
            exc_info=True,
        )
        raise


def create_message(
    db: Session,
    enquiry_id: str,
    sender: MessageSender,
    text: str,
) -> Message:
    """
    Create a new message in the conversation thread.
    """
    try:
        message = Message(
            enquiry_id=enquiry_id,
            sender=sender,
            text=text,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        logger.info(
            f"Message logged: sender={sender.value}",
            extra={"extra_data": {
                "message_id": message.id,
                "enquiry_id": enquiry_id,
                "sender": sender.value,
            }},
        )

        return message

    except Exception as e:
        db.rollback()
        logger.error(
            f"Failed to create message for enquiry {enquiry_id}: {str(e)}",
            extra={"extra_data": {"enquiry_id": enquiry_id, "error": str(e)}},
            exc_info=True,
        )
        raise


def process_enquiry_background(enquiry_id: str) -> None:
    """
    Background task that processes an enquiry asynchronously.

    This runs AFTER the API response has been returned to the client.
    The client gets their enquiry ID immediately without waiting.

    RACE CONDITION GUARD:
    A timing window exists between when this task is scheduled and when it
    actually runs. During that window (and during the simulated processing
    delay), an operator may manually escalate or schedule a follow-up for
    this enquiry, changing its status away from PROCESSING.

    To prevent this task from blindly overwriting a newer operational state:
    1. We re-fetch the enquiry from the database AFTER the processing delay.
    2. We verify that the status is still PROCESSING.
    3. If the status changed, we log a warning and exit without writing.

    NOTE ON asyncio.sleep vs time.sleep:
    Starlette runs sync background task functions in a ThreadPoolExecutor.
    Using asyncio.sleep() inside a synchronous thread would block the entire
    event loop — the opposite of what we want. time.sleep() is the correct
    choice for sync threads. It is placed BEFORE any DB writes to reduce the
    time the database lock is held.
    """
    from app.database import SessionLocal
    from app.mock_sops.matcher import match_sop

    logger.info(
        f"Background processing started for enquiry: {enquiry_id}",
        extra={"extra_data": {"enquiry_id": enquiry_id}},
    )

    db = SessionLocal()

    try:
        # Initial fetch: mark as PROCESSING and log the status change event
        enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()

        if not enquiry:
            logger.error(
                f"Enquiry not found for background processing: {enquiry_id}",
                extra={"extra_data": {"enquiry_id": enquiry_id}},
            )
            return

        enquiry.status = EnquiryStatus.PROCESSING
        db.commit()

        create_event(
            db=db,
            enquiry_id=enquiry_id,
            event_type=EventType.STATUS_UPDATED,
            description="Enquiry status changed to processing.",
        )

        # Simulate processing delay. time.sleep() is correct for a sync thread
        # running in Starlette's ThreadPoolExecutor — see module docstring above.
        time.sleep(1.5)

        # -----------------------------------------------------------------------
        # RACE CONDITION GUARD: Re-fetch from DB after the delay.
        #
        # Another request may have changed the status (e.g. manual escalation)
        # while this task was sleeping. We must NOT overwrite a newer state.
        # -----------------------------------------------------------------------
        db.refresh(enquiry)

        if enquiry.status != EnquiryStatus.PROCESSING:
            logger.warning(
                f"Background task aborted — enquiry status changed externally during processing.",
                extra={"extra_data": {
                    "enquiry_id": enquiry_id,
                    "detected_status": enquiry.status.value,
                    "expected_status": EnquiryStatus.PROCESSING.value,
                    "action": "skipped_stale_update",
                }},
            )
            return  # Exit cleanly without overwriting the newer state

        # Status is still PROCESSING — safe to proceed with SOP matching
        match_result = match_sop(enquiry.message)

        if match_result:
            enquiry.sop_category = match_result.category
            enquiry.suggested_response = match_result.suggested_response
            enquiry.status = EnquiryStatus.QUALIFIED
            db.commit()

            # Log the SOP match event
            create_event(
                db=db,
                enquiry_id=enquiry_id,
                event_type=EventType.SOP_MATCHED,
                description=(
                    f"Matched SOP category: {match_result.category}. "
                    f"Keyword: '{match_result.matched_keyword}'. "
                    f"Suggested response generated."
                ),
            )

            # Insert AI suggested response into the conversation thread
            create_message(
                db=db,
                enquiry_id=enquiry_id,
                sender=MessageSender.AI,
                text=match_result.suggested_response,
            )

            # Log the status change event
            create_event(
                db=db,
                enquiry_id=enquiry_id,
                event_type=EventType.STATUS_UPDATED,
                description="Enquiry status changed to qualified.",
            )

            logger.info(
                f"Enquiry qualified: {enquiry_id}",
                extra={"extra_data": {
                    "enquiry_id": enquiry_id,
                    "sop_category": match_result.category,
                    "matched_keyword": match_result.matched_keyword,
                }},
            )

        else:
            enquiry.status = EnquiryStatus.ESCALATED
            db.commit()

            # Log the escalation event
            create_event(
                db=db,
                enquiry_id=enquiry_id,
                event_type=EventType.ESCALATION_TRIGGERED,
                description=(
                    "No SOP category matched. "
                    "Enquiry automatically escalated for manual review."
                ),
            )

            logger.info(
                f"Enquiry escalated (no SOP match): {enquiry_id}",
                extra={"extra_data": {"enquiry_id": enquiry_id}},
            )

        logger.info(
            f"Background processing completed for enquiry: {enquiry_id}",
            extra={"extra_data": {
                "enquiry_id": enquiry_id,
                "final_status": enquiry.status.value,
            }},
        )

    except Exception as e:
        db.rollback()
        logger.error(
            f"Background processing failed for enquiry: {enquiry_id}",
            extra={"extra_data": {
                "enquiry_id": enquiry_id,
                "error": str(e),
            }},
            exc_info=True,
        )
    finally:
        db.close()


def schedule_follow_up(
    db: Session,
    enquiry_id: str,
    delay_minutes: int,
    message_template: Optional[str] = None,
) -> Enquiry:
    """
    Schedule a follow-up action for a qualified customer enquiry.

    Transitions status: qualified -> follow_up_scheduled.
    Appends events to the timeline for auditable history.

    Raises:
        EnquiryNotFoundError: if no enquiry exists with the given ID.
            This domain exception is transport-agnostic — the HTTP layer
            maps it to a 404 response via main.py's exception handler.
    """
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enquiry:
        raise EnquiryNotFoundError(enquiry_id)

    try:
        old_status = enquiry.status
        enquiry.status = EnquiryStatus.FOLLOW_UP_SCHEDULED
        db.commit()

        # Log status update timeline event
        create_event(
            db=db,
            enquiry_id=enquiry_id,
            event_type=EventType.STATUS_UPDATED,
            description=f"Enquiry status changed from {old_status.value} to {enquiry.status.value}.",
        )

        # Log specific follow-up trigger timeline event
        template_desc = f" Message Template: '{message_template}'" if message_template else ""
        create_event(
            db=db,
            enquiry_id=enquiry_id,
            event_type=EventType.FOLLOW_UP_SCHEDULED,
            description=f"Follow-up scheduled to trigger in {delay_minutes} minutes.{template_desc}",
        )

        logger.info(
            f"Follow-up scheduled for enquiry: {enquiry_id}",
            extra={"extra_data": {
                "enquiry_id": enquiry_id,
                "delay_minutes": delay_minutes,
                "status_transition": f"{old_status.value} -> {enquiry.status.value}"
            }}
        )

        return enquiry

    except EnquiryNotFoundError:
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"Failed to schedule follow-up for enquiry {enquiry_id}: {str(e)}",
            extra={"extra_data": {"enquiry_id": enquiry_id, "error": str(e)}},
            exc_info=True,
        )
        raise


def escalate_enquiry_manual(
    db: Session,
    enquiry_id: str,
    reason: str,
) -> Enquiry:
    """
    Manually escalate a customer enquiry (bypassing automated paths).

    Transitions status: * -> escalated.
    Appends audit events to the timeline tracking manual inputs.

    Raises:
        EnquiryNotFoundError: if no enquiry exists with the given ID.
            This domain exception is transport-agnostic — the HTTP layer
            maps it to a 404 response via main.py's exception handler.
    """
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enquiry:
        raise EnquiryNotFoundError(enquiry_id)

    try:
        old_status = enquiry.status
        enquiry.status = EnquiryStatus.ESCALATED
        db.commit()

        # Log status update timeline event
        create_event(
            db=db,
            enquiry_id=enquiry_id,
            event_type=EventType.STATUS_UPDATED,
            description=f"Enquiry status changed from {old_status.value} to {enquiry.status.value}.",
        )

        # Log manual escalation event detailing the reason
        create_event(
            db=db,
            enquiry_id=enquiry_id,
            event_type=EventType.ESCALATION_TRIGGERED,
            description=f"Enquiry manually escalated. Reason: {reason}",
        )

        logger.info(
            f"Enquiry manually escalated: {enquiry_id}",
            extra={"extra_data": {
                "enquiry_id": enquiry_id,
                "reason": reason,
                "status_transition": f"{old_status.value} -> {enquiry.status.value}"
            }}
        )

        return enquiry

    except EnquiryNotFoundError:
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"Failed to escalate enquiry {enquiry_id}: {str(e)}",
            extra={"extra_data": {"enquiry_id": enquiry_id, "error": str(e)}},
            exc_info=True,
        )
        raise


def get_enquiry_history(db: Session, enquiry_id: str) -> dict:
    """
    Retrieve an enquiry's details along with its chronologically ordered history events.

    Raises:
        EnquiryNotFoundError: if no enquiry exists with the given ID.
    """
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enquiry:
        raise EnquiryNotFoundError(enquiry_id)

    # Chronological ordering is already guaranteed by SQLAlchemy relationship order_by rules
    return {
        "id": enquiry.id,
        "customer_name": enquiry.customer_name,
        "channel": enquiry.channel,
        "message": enquiry.message,
        "status": enquiry.status,
        "sop_category": enquiry.sop_category,
        "suggested_response": enquiry.suggested_response,
        "created_at": enquiry.created_at,
        "updated_at": enquiry.updated_at,
        "timeline": enquiry.events,
    }


def list_enquiries(
    db: Session,
    status: Optional[EnquiryStatus] = None,
    channel: Optional[ChannelType] = None,
    limit: int = 100,
) -> list[Enquiry]:
    """
    Retrieve list of enquiries with newest-first ordering and optional query filters.
    """
    query = db.query(Enquiry)

    if status:
        query = query.filter(Enquiry.status == status)
    if channel:
        query = query.filter(Enquiry.channel == channel)

    return query.order_by(Enquiry.created_at.desc()).limit(limit).all()


def get_enquiry_with_messages(db: Session, enquiry_id: str) -> Enquiry:
    """
    Retrieve an enquiry along with its complete message thread.
    """
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()

    if not enquiry:
        logger.warning(f"Enquiry not found for fetching messages: {enquiry_id}")
        raise EnquiryNotFoundError(f"Enquiry with ID {enquiry_id} not found.")

    return enquiry


def get_dashboard_stats(db: Session) -> dict:
    """
    Aggregate database metrics for the frontend dashboard.
    Uses highly optimized SQL COUNT queries rather than fetching the dataset.
    """
    from sqlalchemy import func
    from datetime import datetime, timedelta, timezone

    # 1. Total Leads Today (Enquiries currently in NEW state)
    total_leads = db.query(func.count(Enquiry.id)).filter(Enquiry.status == EnquiryStatus.NEW).scalar() or 0

    # 2. Missed Enquiries (NEW state older than 2 hours)
    two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
    missed_enquiries = db.query(func.count(Enquiry.id)).filter(
        Enquiry.status == EnquiryStatus.NEW,
        Enquiry.created_at < two_hours_ago
    ).scalar() or 0

    # 3. Open Escalations
    open_escalations = db.query(func.count(Enquiry.id)).filter(Enquiry.status == EnquiryStatus.ESCALATED).scalar() or 0

    # 4. Follow-Ups Due
    follow_ups_due = db.query(func.count(Enquiry.id)).filter(Enquiry.status == EnquiryStatus.FOLLOW_UP_SCHEDULED).scalar() or 0

    return {
        "totalLeadsToday": total_leads,
        "missedEnquiries": missed_enquiries,
        "openEscalations": open_escalations,
        "followUpsDue": follow_ups_due
    }
