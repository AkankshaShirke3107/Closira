"""
Closira — Event SQLAlchemy Model

Represents a single timeline event associated with an enquiry.

Design decisions:
- Append-only pattern: events are never updated or deleted, only created.
  This creates a clean, auditable history of everything that happened to an enquiry.
- event_type as a string (not enum): new event types can be added without
  database migrations. The flexibility outweighs the type-safety tradeoff here.
- Foreign key to enquiries: each event belongs to exactly one enquiry.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base


class EventType(str, enum.Enum):
    """
    Centralized event types for operational timeline logging.
    Enforces type-safety, prevents typos, and guarantees DB validation.
    """
    ENQUIRY_CREATED = "enquiry_created"
    STATUS_UPDATED = "status_updated"
    SOP_MATCHED = "sop_matched"
    ESCALATION_TRIGGERED = "escalation_triggered"
    FOLLOW_UP_SCHEDULED = "follow_up_scheduled"


class Event(Base):
    """
    SQLAlchemy model for the events (history/timeline) table.

    Each event captures a single action or state change related to an enquiry.
    Events form a chronological timeline that makes the system observable.
    """
    __tablename__ = "events"

    # Primary key: UUID string
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )

    # Foreign key: which enquiry does this event belong to?
    enquiry_id = Column(
        String(36),
        ForeignKey("enquiries.id"),
        nullable=False,
        index=True,  # Indexed for fast lookups by enquiry
    )

    # Centralized event type enum (consistency & typo prevention)
    # Indexed: timeline history queries filter by event_type for audit searches
    event_type = Column(SAEnum(EventType), nullable=False, index=True)

    # Human-readable description of what happened
    description = Column(Text, nullable=False)

    # When did it happen?
    # Events are append-only, so we only need created_at (no updated_at).
    # Indexed: chronological ordering (ORDER BY created_at) uses this index.
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    # back_populates creates the reverse side of the Enquiry.events relationship.
    # event.enquiry → the parent Enquiry object
    # ---------------------------------------------------------------------------
    enquiry = relationship("Enquiry", back_populates="events")

    def __repr__(self):
        return f"<Event(id={self.id}, type={self.event_type}, enquiry_id={self.enquiry_id})>"
