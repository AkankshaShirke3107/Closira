"""
Closira — Enquiry SQLAlchemy Model

Represents a customer enquiry received from WhatsApp, Email, or Phone Call.

Design decisions:
- UUID primary key: prevents enumeration, production-ready pattern
- Enum columns for status and channel: type-safe, clean Swagger docs
- Nullable sop_category and suggested_response: populated later by background task
- updated_at with onupdate: automatically tracks when the record was last modified
- Relationship to Event: one enquiry has many timeline events
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Enquiry Statuses
# ---------------------------------------------------------------------------
# Defined here (not in a separate file) because they are tightly coupled
# to the Enquiry model. If you need them elsewhere, import from here.
#
# Lifecycle:
#   new → processing → qualified → follow_up_scheduled → resolved
#                    ↘ escalated
# ---------------------------------------------------------------------------
import enum


class EnquiryStatus(str, enum.Enum):
    """
    Possible states of an enquiry throughout its lifecycle.

    Inherits from str so that SQLAlchemy stores the string value,
    and Pydantic serializes it cleanly in API responses.
    """
    NEW = "new"
    PROCESSING = "processing"
    QUALIFIED = "qualified"
    ESCALATED = "escalated"
    FOLLOW_UP_SCHEDULED = "follow_up_scheduled"
    RESOLVED = "resolved"


class ChannelType(str, enum.Enum):
    """
    Communication channels through which enquiries arrive.

    Inherits from str for clean serialization in both database and API.
    """
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    CALL = "call"


# ---------------------------------------------------------------------------
# Enquiry Model
# ---------------------------------------------------------------------------
class Enquiry(Base):
    """
    SQLAlchemy model for the enquiries table.

    Stores the main enquiry information including customer details,
    the incoming message, current processing status, and any SOP
    classification results.
    """
    __tablename__ = "enquiries"

    # Primary key: UUID string for security (no sequential enumeration)
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )

    # Customer information
    customer_name = Column(String(255), nullable=False)
    channel = Column(
        SAEnum(ChannelType),
        nullable=False,
        index=True,  # Indexed: GET /enquiries?channel=... triggers a filter query
    )
    message = Column(Text, nullable=False)

    # Processing state
    # Starts as "new", transitions through the lifecycle
    status = Column(
        SAEnum(EnquiryStatus),
        nullable=False,
        default=EnquiryStatus.NEW,
        index=True,  # Indexed: GET /enquiries?status=... is the most common filter
    )

    # SOP classification results (populated by background task)
    # Nullable because they don't exist at creation time
    sop_category = Column(String(255), nullable=True)
    suggested_response = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    # One enquiry has many events (timeline entries).
    # back_populates creates a bidirectional relationship:
    #   enquiry.events → list of events
    #   event.enquiry  → parent enquiry
    #
    # order_by ensures events come back in chronological order by default.
    # cascade="all, delete-orphan" means deleting an enquiry also deletes its events.
    # ---------------------------------------------------------------------------
    events = relationship(
        "Event",
        back_populates="enquiry",
        cascade="all, delete-orphan",
        order_by="Event.created_at",
    )

    messages = relationship(
        "Message",
        back_populates="enquiry",
        cascade="all, delete-orphan",
        order_by="Message.timestamp",
    )

    ai_insights = relationship(
        "EnquiryInsight",
        back_populates="enquiry",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Enquiry(id={self.id}, status={self.status}, channel={self.channel})>"
