"""
Closira — EnquiryInsight SQLAlchemy Model

Stores AI-generated intelligence metadata for each enquiry.

Design decisions:
- 1-to-1 relationship with Enquiry (sidecar pattern): keeps the core
  Enquiry table clean and avoids complex SQLite ALTER TABLE migrations.
- Deterministic fields: all values are computed by a lightweight rules
  engine (no external LLM dependency), making them fast and reproducible.
- Stored at creation time: insights are generated synchronously during
  enquiry creation so the frontend can display risk/priority immediately.
"""

import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Float, Integer, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class SentimentLabel(str, enum.Enum):
    """Sentiment classification labels."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class PriorityLevel(str, enum.Enum):
    """
    Priority levels derived from the escalation risk score.

    P0 = Critical (risk > 80)
    P1 = High     (risk 50–80)
    P2 = Normal   (risk < 50)
    """
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class EnquiryInsight(Base):
    """
    SQLAlchemy model for the enquiry_insights table.

    Stores the AI-computed sentiment, risk, and priority metadata
    for a single enquiry. One enquiry has exactly one insight record.
    """
    __tablename__ = "enquiry_insights"

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
        unique=True,
        index=True,
    )

    # Sentiment analysis results
    sentiment_score = Column(
        Float,
        nullable=False,
        doc="Sentiment polarity score from -1.0 (negative) to +1.0 (positive).",
    )
    sentiment_label = Column(
        SAEnum(SentimentLabel),
        nullable=False,
        doc="Human-readable sentiment classification.",
    )

    # Escalation risk assessment
    escalation_risk_score = Column(
        Integer,
        nullable=False,
        doc="Computed risk score from 0 (safe) to 100 (critical).",
    )

    # Priority classification
    priority_level = Column(
        SAEnum(PriorityLevel),
        nullable=False,
        doc="Auto-computed priority tier based on risk score.",
    )

    # Explanation
    reason = Column(
        Text,
        nullable=False,
        doc="Human-readable explanation of the risk/priority classification.",
    )

    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Bidirectional relationship
    enquiry = relationship("Enquiry", back_populates="ai_insights")

    def __repr__(self):
        return (
            f"<EnquiryInsight(enquiry_id={self.enquiry_id}, "
            f"sentiment={self.sentiment_label}, risk={self.escalation_risk_score}, "
            f"priority={self.priority_level})>"
        )
