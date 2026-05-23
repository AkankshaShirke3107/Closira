"""
Closira — AI Insights Service

A lightweight, deterministic rules engine that computes sentiment,
escalation risk, and priority for each customer enquiry.

Design decisions:
- No external API calls or LLM dependencies: all classification is
  keyword-based and reproducible, making it fast and testable.
- Channel weighting: phone calls inherently carry higher urgency than
  text-based channels, reflected in the risk score.
- Composable pipeline: analyze_sentiment → calculate_risk → generate_priority
  can be extended independently without touching each other.

IMPORTANT: This service is stateless and side-effect-free.
It computes values but does NOT write to the database. The caller
(enquiry_service.create_enquiry) handles persistence.
"""

from app.models.enquiry import ChannelType
from app.models.insight import EnquiryInsight, SentimentLabel, PriorityLevel
from app.logging.config import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Keyword Dictionaries
# ---------------------------------------------------------------------------
# Curated word lists for sentiment classification. Each word is assigned
# a weight reflecting its intensity. These lists are intentionally small
# and deterministic — in production, they would be replaced with an NLP
# model or external API call.
# ---------------------------------------------------------------------------

NEGATIVE_KEYWORDS = {
    "angry": -0.8,
    "furious": -0.9,
    "terrible": -0.8,
    "horrible": -0.8,
    "worst": -0.9,
    "refund": -0.6,
    "bad": -0.5,
    "issue": -0.4,
    "problem": -0.4,
    "complaint": -0.7,
    "broken": -0.6,
    "frustrated": -0.7,
    "disappointed": -0.6,
    "unacceptable": -0.8,
    "delay": -0.3,
    "slow": -0.3,
    "error": -0.4,
    "wrong": -0.4,
    "fail": -0.5,
    "failed": -0.5,
    "scam": -0.9,
    "useless": -0.7,
    "poor": -0.5,
    "never": -0.3,
    "hate": -0.8,
    "cancel": -0.5,
    "unhappy": -0.6,
}

POSITIVE_KEYWORDS = {
    "good": 0.4,
    "great": 0.6,
    "excellent": 0.8,
    "amazing": 0.8,
    "thanks": 0.3,
    "thank": 0.3,
    "satisfied": 0.6,
    "happy": 0.6,
    "love": 0.7,
    "wonderful": 0.7,
    "perfect": 0.8,
    "best": 0.6,
    "helpful": 0.5,
    "appreciate": 0.5,
    "recommended": 0.4,
    "pleased": 0.5,
    "fantastic": 0.7,
    "awesome": 0.7,
}

# High-risk keywords that directly inflate the escalation score
HIGH_RISK_KEYWORDS = {
    "refund", "complaint", "broken", "cancel", "scam",
    "lawyer", "legal", "court", "sue", "fraud",
    "manager", "supervisor", "escalate",
}

# Channel urgency weights (higher = more urgent)
CHANNEL_WEIGHTS = {
    ChannelType.CALL: 15,
    ChannelType.WHATSAPP: 8,
    ChannelType.EMAIL: 3,
}


# ---------------------------------------------------------------------------
# Core Analysis Functions
# ---------------------------------------------------------------------------

def analyze_sentiment(text: str) -> tuple[float, SentimentLabel]:
    """
    Compute sentiment score and label from message text.

    Algorithm:
    1. Tokenize the message into lowercase words.
    2. Sum up keyword weights from positive and negative dictionaries.
    3. Normalize the score to the [-1.0, +1.0] range.
    4. Classify based on thresholds: < -0.1 negative, > 0.1 positive.

    Returns:
        (score, label) tuple
    """
    words = text.lower().split()
    score = 0.0
    matches = 0

    for word in words:
        # Strip common punctuation from word edges
        cleaned = word.strip(".,!?;:'\"()[]{}#@")
        if cleaned in NEGATIVE_KEYWORDS:
            score += NEGATIVE_KEYWORDS[cleaned]
            matches += 1
        elif cleaned in POSITIVE_KEYWORDS:
            score += POSITIVE_KEYWORDS[cleaned]
            matches += 1

    # Normalize: clamp to [-1, 1]
    if matches > 0:
        score = max(-1.0, min(1.0, score / max(matches, 1)))

    # Classify
    if score < -0.1:
        label = SentimentLabel.NEGATIVE
    elif score > 0.1:
        label = SentimentLabel.POSITIVE
    else:
        label = SentimentLabel.NEUTRAL

    return round(score, 2), label


def calculate_risk(
    text: str,
    sentiment_label: SentimentLabel,
    channel: ChannelType,
) -> tuple[int, list[str]]:
    """
    Compute escalation risk score (0–100) based on multiple signals.

    Scoring breakdown:
    - Negative sentiment:     +40 points
    - Neutral sentiment:      +10 points
    - Each high-risk keyword: +10 points (capped contribution at +30)
    - Channel weight:         +3 to +15 points depending on channel

    Returns:
        (risk_score, triggered_reasons) tuple
    """
    risk = 0
    reasons = []

    # 1. Sentiment contribution
    if sentiment_label == SentimentLabel.NEGATIVE:
        risk += 40
        reasons.append("Negative sentiment detected")
    elif sentiment_label == SentimentLabel.NEUTRAL:
        risk += 10
        reasons.append("Neutral sentiment — no strong positive signals")

    # 2. High-risk keyword scanning
    words = set(word.strip(".,!?;:'\"()[]{}#@").lower() for word in text.split())
    matched_risk_keywords = words.intersection(HIGH_RISK_KEYWORDS)

    if matched_risk_keywords:
        keyword_score = min(len(matched_risk_keywords) * 10, 30)  # Cap at 30
        risk += keyword_score
        reasons.append(f"High-risk keywords: {', '.join(sorted(matched_risk_keywords))}")

    # 3. Channel urgency
    channel_weight = CHANNEL_WEIGHTS.get(channel, 5)
    risk += channel_weight
    reasons.append(f"Channel weight ({channel.value}): +{channel_weight}")

    # Clamp final score
    risk = min(risk, 100)

    return risk, reasons


def generate_priority(risk_score: int) -> PriorityLevel:
    """
    Map risk score to priority level.

    P0 (Critical): risk > 80
    P1 (High):     50 ≤ risk ≤ 80
    P2 (Normal):   risk < 50
    """
    if risk_score > 80:
        return PriorityLevel.P0
    elif risk_score >= 50:
        return PriorityLevel.P1
    else:
        return PriorityLevel.P2


def generate_insights(enquiry) -> EnquiryInsight:
    """
    Full AI analysis pipeline for a single enquiry.

    Orchestrates: sentiment → risk → priority → explanation.
    Returns a hydrated EnquiryInsight object ready for DB persistence.

    This function is intentionally side-effect-free — it does not
    touch the database. The caller is responsible for adding the
    returned object to the session and committing.
    """
    text = enquiry.message
    channel = enquiry.channel

    # Step 1: Sentiment
    sentiment_score, sentiment_label = analyze_sentiment(text)

    # Step 2: Risk
    risk_score, risk_reasons = calculate_risk(text, sentiment_label, channel)

    # Step 3: Priority
    priority = generate_priority(risk_score)

    # Step 4: Build explanation
    reason = f"Priority {priority.value} (risk score: {risk_score}/100). " + "; ".join(risk_reasons) + "."

    logger.info(
        f"AI insights generated for enquiry {enquiry.id}",
        extra={"extra_data": {
            "enquiry_id": enquiry.id,
            "sentiment": sentiment_label.value,
            "sentiment_score": sentiment_score,
            "risk_score": risk_score,
            "priority": priority.value,
        }},
    )

    return EnquiryInsight(
        enquiry_id=enquiry.id,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        escalation_risk_score=risk_score,
        priority_level=priority,
        reason=reason,
    )
