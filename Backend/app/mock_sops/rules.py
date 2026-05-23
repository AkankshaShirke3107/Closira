"""
Closira — SOP Matching Rules

Defines the keyword-to-category mappings for SOP classification.

Each SOP category has a list of keywords. If any keyword appears in the
customer's message (case-insensitive), the message is classified under
that category.

Design decisions:
- Dict[str, list[str]] structure: simple, readable, easy to extend
- Keywords are lowercase: matching is always case-insensitive
- Order matters: first matching category wins (predictable behavior)
- Adding a new SOP category = adding one dict entry (no code changes)

Future evolution:
- These hardcoded rules can later be replaced with AI/LLM classification
- The matcher.py interface stays the same — only the implementation changes
"""

# ---------------------------------------------------------------------------
# SOP Categories and Their Keywords
# ---------------------------------------------------------------------------
# Key   = SOP category name (human-readable)
# Value = list of keywords that trigger this category
#
# The matcher checks if ANY keyword appears in the customer's message.
# Matching is case-insensitive and uses substring matching.
# ---------------------------------------------------------------------------

SOP_RULES: dict[str, list[str]] = {
    "Booking enquiry": [
        "book",
        "booking",
        "reserve",
        "reservation",
        "schedule",
        "appointment",
        "slot",
    ],

    "Pricing enquiry": [
        "price",
        "pricing",
        "cost",
        "quote",
        "rate",
        "charge",
        "fee",
        "how much",
        "estimate",
    ],

    "Complaint": [
        "complaint",
        "complain",
        "unhappy",
        "dissatisfied",
        "terrible",
        "worst",
        "bad experience",
        "poor service",
        "not satisfied",
        "frustrated",
    ],

    "Support request": [
        "help",
        "support",
        "issue",
        "problem",
        "not working",
        "broken",
        "error",
        "fix",
        "trouble",
        "assist",
    ],

    "After-hours message": [
        "after hours",
        "closed",
        "opening hours",
        "business hours",
        "working hours",
        "when do you open",
        "are you open",
        "weekend",
        "holiday",
    ],
}
