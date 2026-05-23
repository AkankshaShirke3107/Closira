"""
Closira — SOP Matcher

The matching engine that classifies customer messages against SOP rules.

Takes a customer message, checks it against keyword rules, and returns
a match result with the category and suggested response.

Design decisions:
- Returns a dataclass (SOPMatchResult) instead of a tuple:
  self-documenting, named fields, easy to extend
- Returns None if no match: clean, explicit, easy to check
- Case-insensitive: converts message to lowercase before matching
- Substring matching: "price" matches "pricing" and "what's the price?"
- First-match-wins: predictable, debuggable, easy to explain
- Pure function: no side effects, no database access, fully testable

Future evolution:
- Replace keyword matching with AI/LLM classification
- The interface (match_sop function signature) stays the same
- Only the internal implementation changes
"""

from dataclasses import dataclass
from typing import Optional

from app.mock_sops.rules import SOP_RULES
from app.mock_sops.templates import SOP_TEMPLATES
from app.logging.config import get_logger

logger = get_logger(__name__)


@dataclass
class SOPMatchResult:
    """
    Result of an SOP matching attempt.

    Attributes:
        category: The matched SOP category name (e.g., "Pricing enquiry")
        suggested_response: The template response for this category
        matched_keyword: The specific keyword that triggered the match
    """
    category: str
    suggested_response: str
    matched_keyword: str


def match_sop(message: str) -> Optional[SOPMatchResult]:
    """
    Attempt to match a customer message against SOP rules.

    How it works:
    1. Convert the message to lowercase (case-insensitive matching)
    2. Iterate through SOP categories in order
    3. For each category, check if any keyword appears in the message
    4. If a keyword matches, return the result with category + template
    5. If no keywords match any category, return None

    Args:
        message: The customer's enquiry message (raw text)

    Returns:
        SOPMatchResult if a match is found, None otherwise

    Examples:
        >>> match_sop("What is the price of your service?")
        SOPMatchResult(category="Pricing enquiry", ...)

        >>> match_sop("asdfghjkl random text")
        None
    """
    message_lower = message.lower()

    for category, keywords in SOP_RULES.items():
        for keyword in keywords:
            if keyword in message_lower:
                # Match found — get the response template
                suggested_response = SOP_TEMPLATES.get(
                    category,
                    "Thank you for your enquiry. Our team will get back to you shortly.",
                )

                result = SOPMatchResult(
                    category=category,
                    suggested_response=suggested_response,
                    matched_keyword=keyword,
                )

                logger.info(
                    f"SOP matched: {category}",
                    extra={"extra_data": {
                        "category": category,
                        "matched_keyword": keyword,
                        "message_preview": message[:80],
                    }},
                )

                return result

    # No match found
    logger.info(
        "No SOP match found",
        extra={"extra_data": {
            "message_preview": message[:80],
        }},
    )

    return None
