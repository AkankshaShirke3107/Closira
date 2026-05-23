"""
Closira — Custom Domain Exceptions

WHY THIS EXISTS:
Previously, services raised FastAPI's HTTPException directly, which tightly
coupled business logic to the HTTP transport layer. This violates the principle
that a service should be callable from any context (HTTP, CLI, tests, workers)
without depending on a web framework.

These lightweight domain exceptions solve that:
- Services raise domain exceptions (e.g. EnquiryNotFoundError)
- A centralized exception handler in main.py maps them to HTTP responses
- The service layer stays completely transport-agnostic

HOW TO USE:
  # In a service function:
  raise EnquiryNotFoundError(enquiry_id)

  # In main.py (already registered):
  @app.exception_handler(EnquiryNotFoundError)
  async def ...: return JSONResponse(status_code=404, ...)
"""


class DomainException(Exception):
    """
    Base class for all Closira domain exceptions.

    All custom business-logic exceptions should inherit from this class.
    This makes it easy to catch any domain-level error with a single handler
    if needed, while still allowing specific handlers for each subclass.
    """
    pass


class EnquiryNotFoundError(DomainException):
    """
    Raised when an enquiry lookup returns no result from the database.

    Replaces: raise HTTPException(status_code=404, detail="Enquiry not found")
    Mapped to: HTTP 404 Not Found in main.py's exception handler.
    """

    def __init__(self, enquiry_id: str):
        self.enquiry_id = enquiry_id
        super().__init__(f"Enquiry not found: {enquiry_id}")
