"""
Closira — SOP Response Templates

Defines suggested response templates for each SOP category.

When an enquiry is matched to an SOP category, the corresponding template
is used as the suggested response. These templates are what a human agent
would review and potentially send to the customer.

Design decisions:
- Dict[str, str] structure: category name → response template
- Templates are professional and polite
- Templates include placeholders for personalization (future enhancement)
- Separate from rules.py: you can change responses without touching keywords

Future evolution:
- Templates could use Jinja2 for dynamic personalization
- Templates could be stored in a database for admin editing
- AI/LLM could generate custom responses instead of using templates
"""

# ---------------------------------------------------------------------------
# Response Templates by SOP Category
# ---------------------------------------------------------------------------
# Key   = SOP category name (must match keys in rules.py)
# Value = suggested response text for the agent to review
# ---------------------------------------------------------------------------

SOP_TEMPLATES: dict[str, str] = {
    "Booking enquiry": (
        "Thank you for your interest in booking with us! "
        "We'd be happy to help you schedule an appointment. "
        "Could you please share your preferred date and time? "
        "Our available slots are Monday to Friday, 9 AM to 6 PM."
    ),

    "Pricing enquiry": (
        "Thank you for reaching out about our pricing! "
        "We offer flexible plans tailored to your needs. "
        "Our team will share a detailed pricing breakdown with you shortly. "
        "In the meantime, feel free to let us know your specific requirements."
    ),

    "Complaint": (
        "We sincerely apologize for the inconvenience you've experienced. "
        "Your feedback is very important to us and we take it seriously. "
        "A senior team member will review your concern and get back to you "
        "within 24 hours. Thank you for your patience."
    ),

    "Support request": (
        "Thank you for contacting our support team! "
        "We understand you're facing an issue and we're here to help. "
        "A support specialist will review your request and respond "
        "with a solution as soon as possible."
    ),

    "After-hours message": (
        "Thank you for reaching out! Our office is currently closed. "
        "Our business hours are Monday to Friday, 9 AM to 6 PM. "
        "We've logged your enquiry and our team will respond "
        "first thing on the next business day."
    ),
}
