# Closira — Mock SOP Matching Package
#
# This package contains the SOP classification logic:
# - rules.py:     keyword-to-category mappings (data)
# - templates.py: response templates per category (data)
# - matcher.py:   matching engine (logic)
#
# Usage:
#   from app.mock_sops.matcher import match_sop
#   result = match_sop("I want to know the pricing")
#   if result:
#       print(result.category)            # "Pricing enquiry"
#       print(result.suggested_response)  # "Thank you for reaching out..."

from app.mock_sops.matcher import match_sop, SOPMatchResult  # noqa: F401
