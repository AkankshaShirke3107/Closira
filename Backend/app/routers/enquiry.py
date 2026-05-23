"""
Closira — Enquiry Router

Handles HTTP routing for enquiry-related endpoints.

Design decisions:
- Thin router: only handles HTTP concerns (request parsing, response formatting)
- All business logic is delegated to services/enquiry_service.py
- Uses FastAPI's BackgroundTasks to trigger async processing
- Exposes clean RESTful patterns with correct status codes (201 for POST creation, 200 for updates/queries)
"""

from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks, status, Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enquiry import ChannelType, EnquiryStatus
from app.schemas.enquiry import (
    EnquiryCreate,
    EnquiryResponse,
    EnquiryFollowUpRequest,
    EnquiryEscalateRequest,
    EnquiryHistoryResponse,
    EnquiryWithMessagesResponse,
    DashboardStatsResponse,
)
from app.services.enquiry_service import (
    create_enquiry,
    process_enquiry_background,
    schedule_follow_up,
    escalate_enquiry_manual,
    get_enquiry_history,
    list_enquiries,
    get_enquiry_with_messages,
    get_dashboard_stats,
)
from app.logging.config import get_logger

logger = get_logger(__name__)

# Singular router prefix (handles resource creation and specific UUID instances)
router = APIRouter(
    prefix="/enquiry",
    tags=["Enquiry"],
)

# Plural router prefix (handles query listings and bulk operations)
router_plural = APIRouter(
    prefix="/enquiries",
    tags=["Enquiries"],
)


# ===========================================================================
# Singular Enquiry Endpoints
# ===========================================================================

@router.post(
    "/",
    response_model=EnquiryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer enquiry",
    description=(
        "Receives a customer enquiry and creates a record in the database. "
        "A background task is immediately scheduled to process the enquiry asynchronously "
        "(SOP matching, classification, template response selection). "
        "The API immediately returns the initial enquiry metadata without blocking."
    ),
    response_description="The created enquiry object with 'new' status and initial timestamps.",
)
def create_new_enquiry(
    enquiry_data: EnquiryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    enquiry = create_enquiry(db=db, enquiry_data=enquiry_data)
    background_tasks.add_task(process_enquiry_background, enquiry.id)

    logger.info(
        f"Enquiry accepted, background task scheduled: {enquiry.id}",
        extra={"extra_data": {"enquiry_id": enquiry.id}},
    )
    return enquiry


@router.get(
    "/{id}",
    response_model=EnquiryWithMessagesResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve an enquiry with its full message thread",
    description=(
        "Fetches the details of a customer enquiry along with the complete chronological "
        "conversation thread (including both customer messages and AI/System responses)."
    ),
)
def get_enquiry(
    id: str = Path(..., description="Unique enquiry identifier (UUID)"),
    db: Session = Depends(get_db),
):
    return get_enquiry_with_messages(db=db, enquiry_id=id)


@router.post(
    "/{id}/follow-up",
    response_model=EnquiryResponse,
    status_code=status.HTTP_200_OK,
    summary="Schedule a follow-up action",
    description=(
        "Schedules an operational follow-up window for an enquiry that has been qualified. "
        "Transitions the status from 'qualified' to 'follow_up_scheduled' and logs detailed parameters in the timeline."
    ),
)
def post_enquiry_follow_up(
    payload: EnquiryFollowUpRequest,
    id: str = Path(..., description="Unique enquiry identifier (UUID)"),
    db: Session = Depends(get_db),
):
    return schedule_follow_up(
        db=db,
        enquiry_id=id,
        delay_minutes=payload.delay_minutes,
        message_template=payload.message_template,
    )


@router.post(
    "/{id}/escalate",
    response_model=EnquiryResponse,
    status_code=status.HTTP_200_OK,
    summary="Manually escalate an enquiry",
    description=(
        "Triggers a manual escalation bypass for an enquiry due to customer frustration or complex custom requirements. "
        "Transitions status from any state to 'escalated' and logs the manual review comment/reason in the timeline."
    ),
)
def post_enquiry_escalate(
    payload: EnquiryEscalateRequest,
    id: str = Path(..., description="Unique enquiry identifier (UUID)"),
    db: Session = Depends(get_db),
):
    return escalate_enquiry_manual(
        db=db,
        enquiry_id=id,
        reason=payload.reason,
    )


@router.get(
    "/{id}/history",
    response_model=EnquiryHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve enquiry timeline history",
    description=(
        "Fetches the complete details of a customer enquiry, including its chronologically sorted timeline audit history. "
        "Useful for tracing automated classifications, agent notes, status updates, and escalations."
    ),
)
def get_enquiry_timeline(
    id: str = Path(..., description="Unique enquiry identifier (UUID)"),
    db: Session = Depends(get_db),
):
    return get_enquiry_history(db=db, enquiry_id=id)


# ===========================================================================
# Plural Enquiries Endpoints
# ===========================================================================

@router_plural.get(
    "/stats",
    response_model=DashboardStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve dashboard statistics",
    description=(
        "Returns aggregated metrics for the dashboard frontend. "
        "Computes counts using optimized database aggregation queries rather than fetching the whole dataset."
    ),
)
def get_stats(db: Session = Depends(get_db)):
    return get_dashboard_stats(db=db)

@router_plural.get(
    "/",
    response_model=list[EnquiryResponse],
    status_code=status.HTTP_200_OK,
    summary="List and filter enquiries",
    description=(
        "Returns a list of customer enquiries sorted with the newest records first. "
        "Supports optional query parameter filters for 'status' and 'channel' and custom 'limit' bounds."
    ),
)
def get_all_enquiries(
    status: Optional[EnquiryStatus] = None,
    channel: Optional[ChannelType] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return list_enquiries(db=db, status=status, channel=channel, limit=limit)
