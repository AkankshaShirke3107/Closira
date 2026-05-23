"""
Closira — Message SQLAlchemy Model

Stores the conversation thread for a given enquiry.
"""

import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class MessageSender(str, enum.Enum):
    """
    Indicates who sent the message.
    """
    CUSTOMER = "customer"
    AI = "ai"
    SYSTEM = "system"


class Message(Base):
    """
    SQLAlchemy model for the messages table.
    Represents a single message in an enquiry's conversation thread.
    """
    __tablename__ = "messages"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )

    enquiry_id = Column(
        String(36),
        ForeignKey("enquiries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sender = Column(SAEnum(MessageSender), nullable=False)
    text = Column(Text, nullable=False)

    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Bidirectional relationship
    enquiry = relationship("Enquiry", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, enquiry_id={self.enquiry_id}, sender={self.sender})>"
