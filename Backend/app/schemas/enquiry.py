"""
Closira — Enquiry Pydantic Schemas

Defines the request/response contracts for the enquiry API.

Design decisions:
- EnquiryCreate: strict input validation (what the client sends)
- EnquiryResponse: controlled output (what the client receives back)
- Separate input and output schemas: never expose internal fields (like raw DB columns)
  to the client. This is a security and maintainability best practice.

Why Pydantic?
- Automatic validation with clear error messages
- Type coercion (e.g., string → enum)
- JSON serialization out of the box
- FastAPI uses Pydantic schemas to generate Swagger docs automatically
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enquiry import ChannelType, EnquiryStatus
from app.models.event import EventType
from app.models.message import MessageSender
from app.models.insight import SentimentLabel, PriorityLevel


# ---------------------------------------------------------------------------
# Request Schemas (what the client sends)
# ---------------------------------------------------------------------------

class EnquiryCreate(BaseModel):
    """
    Schema for creating a new enquiry.

    Validates that:
    - customer_name is provided and between 1-255 characters
    - channel is one of: whatsapp, email, call
    - message is provided and non-empty

    The Field() definitions include examples that appear in Swagger docs,
    making the API documentation self-documenting and testable.
    """
    customer_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the customer making the enquiry.",
        examples=["Akanksha Shirke"],
    )
    channel: ChannelType = Field(
        ...,
        description="Communication channel the enquiry was received from.",
        examples=["whatsapp"],
    )
    message: str = Field(
        ...,
        min_length=1,
        description="The customer's message or enquiry content.",
        examples=["Hi, I want to know the pricing for your services."],
    )


# ---------------------------------------------------------------------------
# Response Schemas (what the client receives)
# ---------------------------------------------------------------------------

class AIInsightsResponse(BaseModel):
    """
    Schema representing the AI-computed intelligence metadata for an enquiry.

    Field aliases bridge the database column names to the clean API field names:
    - sentiment_label (DB) → sentiment (API)
    - escalation_risk_score (DB) → risk_score (API)
    - priority_level (DB) → priority (API)
    """
    sentiment: SentimentLabel = Field(..., alias="sentiment_label", description="Sentiment classification (positive/neutral/negative).")
    sentiment_score: float = Field(..., description="Sentiment polarity score from -1.0 to +1.0.")
    risk_score: int = Field(..., alias="escalation_risk_score", description="Escalation risk score from 0 to 100.")
    priority: PriorityLevel = Field(..., alias="priority_level", description="Auto-computed priority tier (P0/P1/P2).")
    reason: str = Field(..., description="Human-readable explanation of the classification.")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class EnquiryResponse(BaseModel):
    """
    Schema for the enquiry response returned by the API.

    This controls exactly what fields are exposed to the client.
    Internal fields (like raw SQLAlchemy objects) are never leaked.

    model_config with from_attributes=True tells Pydantic to read data
    from SQLAlchemy model attributes (instead of expecting a dict).
    """
    id: str = Field(
        ...,
        description="Unique identifier for the enquiry (UUID).",
    )
    customer_name: str = Field(
        ...,
        description="Name of the customer.",
    )
    channel: ChannelType = Field(
        ...,
        description="Communication channel.",
    )
    message: str = Field(
        ...,
        description="The customer's enquiry message.",
    )
    status: EnquiryStatus = Field(
        ...,
        description="Current processing status of the enquiry.",
    )
    sop_category: Optional[str] = Field(
        None,
        description="Matched SOP category (populated after background processing).",
    )
    suggested_response: Optional[str] = Field(
        None,
        description="Suggested response based on SOP match (populated after background processing).",
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the enquiry was created.",
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the enquiry was last updated.",
    )
    ai_insights: Optional[AIInsightsResponse] = Field(
        None,
        description="AI-computed intelligence metadata (sentiment, risk, priority).",
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "customer_name": "Akanksha Shirke",
                    "channel": "whatsapp",
                    "message": "Hi, I want to know the pricing for your services.",
                    "status": "new",
                    "sop_category": None,
                    "suggested_response": None,
                    "created_at": "2026-05-23T10:30:00Z",
                    "updated_at": "2026-05-23T10:30:00Z",
                }
            ]
        },
    }


# ---------------------------------------------------------------------------
# Operational Workflow Schemas (Step 4 & 5)
# ---------------------------------------------------------------------------

class EnquiryFollowUpRequest(BaseModel):
    """
    Schema for scheduling a follow-up action.
    """
    delay_minutes: int = Field(
        ...,
        gt=0,
        description="Delay in minutes before the follow-up should execute (must be positive).",
        examples=[60],
    )
    message_template: Optional[str] = Field(
        None,
        description="Optional custom message template to be sent to the customer.",
        examples=["Hi Akanksha, following up on your pricing query..."],
    )


class EnquiryEscalateRequest(BaseModel):
    """
    Schema for manual escalation with tracking comments.
    """
    reason: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Detailed reason for escalating the enquiry.",
        examples=["Customer requested manager callback regarding custom integration plan."],
    )


class EventResponse(BaseModel):
    """
    Schema representing a single historical timeline audit event.
    """
    id: str = Field(..., description="Unique event identifier (UUID).")
    event_type: EventType = Field(..., description="The type of event logged.")
    description: str = Field(..., description="Human-readable event summary.")
    created_at: datetime = Field(..., description="Event timestamp.")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "e9f8g7h6-1234-5678-abcd-ef9876543210",
                    "event_type": "sop_matched",
                    "description": "Matched SOP category: Pricing enquiry. Keyword: 'pricing'.",
                    "created_at": "2026-05-23T10:31:30Z",
                }
            ]
        },
    }


class EnquiryHistoryResponse(EnquiryResponse):
    """
    Schema exposing the complete enquiry details and its sorted chronological timeline logs.
    """
    timeline: list[EventResponse] = Field(
        ...,
        description="The chronological sequence of operational lifecycle events.",
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "customer_name": "Akanksha Shirke",
                    "channel": "whatsapp",
                    "message": "Hi, I want to know the pricing for your services.",
                    "status": "follow_up_scheduled",
                    "sop_category": "Pricing enquiry",
                    "suggested_response": "Thank you for reaching out about our pricing...",
                    "created_at": "2026-05-23T10:30:00Z",
                    "updated_at": "2026-05-23T11:30:00Z",
                    "timeline": [
                        {
                            "id": "e1-...",
                            "event_type": "enquiry_created",
                            "description": "New enquiry received via whatsapp from Akanksha Shirke.",
                            "created_at": "2026-05-23T10:30:00Z",
                        },
                        {
                            "id": "e2-...",
                            "event_type": "sop_matched",
                            "description": "Matched SOP category: Pricing enquiry. Keyword: 'pricing'.",
                            "created_at": "2026-05-23T10:31:30Z",
                        }
                    ]
                }
            ]
        },
    }


class MessageResponse(BaseModel):
    """
    Schema representing a single message in a conversation thread.
    """
    id: str = Field(..., description="Unique message identifier (UUID).")
    sender: MessageSender = Field(..., description="Who sent the message (customer, ai, or system).")
    text: str = Field(..., description="The message content.")
    timestamp: datetime = Field(..., description="When the message was sent.")

    model_config = {
        "from_attributes": True,
    }


class EnquiryWithMessagesResponse(EnquiryResponse):
    """
    Schema exposing the enquiry details along with the full message thread.
    """
    messages: list[MessageResponse] = Field(
        ...,
        description="The chronologically ordered conversation thread.",
    )

    model_config = {
        "from_attributes": True,
    }


class DashboardStatsResponse(BaseModel):
    """
    Schema for the high-level metrics needed by the dashboard frontend.
    """
    totalLeadsToday: int = Field(..., description="Count of enquiries currently in 'new' state.")
    missedEnquiries: int = Field(..., description="Count of 'new' enquiries older than 2 hours.")
    openEscalations: int = Field(..., description="Count of enquiries currently in 'escalated' state.")
    followUpsDue: int = Field(..., description="Count of enquiries currently in 'follow_up_scheduled' state.")
