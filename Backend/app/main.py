"""
Closira — FastAPI Application Entry Point

This is the main module that creates and configures the FastAPI application.

Responsibilities:
- Initialize the FastAPI app with metadata (shown in Swagger docs)
- Register routers (singular/plural enquiry, health)
- Implement global middleware for request correlation, endpoint tracing, and timing
- Centralize exception handlers to ensure consistent API JSON error schemas
- Expose the GET / root endpoint with service metadata
"""

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import Base, engine
from app.logging.config import get_logger, request_correlation_id
from app.routers import health, enquiry
from app.utils.exceptions import EnquiryNotFoundError
import app.models  # noqa: F401

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — Startup & Shutdown Logic (with Premium Banner)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # === STARTUP ===
    banner = """
   _____ _                 _             
  / ____| |               (_)            
 | |    | | ___  ___ _ __ _  __ _       
 | |    | |/ _ \\/ __| '__| |/ _` |      
 | |____| | (_) \\__ \\ |  | | (_| |      
  \\_____|_|\\___/|___/_|  |_|\\__,_|      
                                         
AI-Powered Customer Communication Platform
===========================================
Version: 1.0.0
Environment: Development / Debug
Docs: http://127.0.0.1:8000/docs
===========================================
"""
    print(banner)

    logger.info(
        f"Starting {settings.APP_NAME}",
        extra={"extra_data": {"debug": settings.DEBUG, "app_version": "1.0.0"}},
    )

    # Create SQLite database tables automatically
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables successfully created/validated.")

    yield  # Application runs here

    # === SHUTDOWN ===
    logger.info(f"Shutting down {settings.APP_NAME}")


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-powered customer communication platform backend for SMBs. "
        "Intelligently routes WhatsApp messages, Emails, and Calls using "
        "predefined SOP rules, automates responses, schedules follow-ups, and triggers manual escalations."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Global Request-scoped Middleware (Correlation & Processing Time)
# ---------------------------------------------------------------------------
@app.middleware("http")
async def request_observability_middleware(request: Request, call_next):
    """
    Middleware that captures correlation context and maps request latency.

    - Generates/Extracts correlation ID (via X-Correlation-ID header or uuid).
    - Logs incoming endpoints.
    - Appends correlation_id context to all logging records triggered during the request.
    - Calculates and logs duration of endpoint execution in milliseconds.
    """
    start_time = time.time()

    # Generation/extraction of correlation ID
    corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    token = request_correlation_id.set(corr_id)

    path = request.url.path
    method = request.method

    logger.info(
        f"Incoming request: {method} {path}",
        extra={"extra_data": {"method": method, "path": path}},
    )

    response = None
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(
            f"Request execution failed: {method} {path} - {str(e)}",
            extra={"extra_data": {"method": method, "path": path, "error": str(e)}},
        )
        raise e
    finally:
        # Calculate processing duration
        duration_ms = (time.time() - start_time) * 1000
        status_code = response.status_code if response else 500

        logger.info(
            f"Completed request: {method} {path} - {status_code} in {duration_ms:.2f}ms",
            extra={"extra_data": {
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2)
            }}
        )

        # Clear active correlation context
        request_correlation_id.reset(token)


# ---------------------------------------------------------------------------
# Centralized Exception Handling (Standardized Error Payloads)
# ---------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles schema validation errors, standardizing to unified JSON format."""
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg")
        errors.append(f"{loc}: {msg}")

    error_msg = "Validation failed: " + "; ".join(errors)

    logger.warning(
        "Request validation failed",
        extra={"extra_data": {"validation_details": exc.errors(), "body_received": str(exc.body)}},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "type": "validation_error",
                "message": error_msg,
            }
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles standard HTTP exceptions, standardizing error output."""
    logger.warning(
        f"HTTP error occurred: status={exc.status_code}, detail={exc.detail}",
        extra={"extra_data": {"status_code": exc.status_code, "detail": exc.detail}},
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": "http_error",
                "message": exc.detail,
            }
        }
    )


@app.exception_handler(EnquiryNotFoundError)
async def enquiry_not_found_handler(request: Request, exc: EnquiryNotFoundError):
    """
    Maps the EnquiryNotFoundError domain exception to HTTP 404.

    WHY THIS EXISTS:
    Services previously raised HTTPException(status_code=404) directly, which
    coupled business logic to the HTTP transport layer. Now services raise the
    lightweight EnquiryNotFoundError domain exception instead, and this handler
    centralizes the HTTP translation. The service layer stays transport-agnostic.
    """
    logger.warning(
        f"Enquiry not found: {exc.enquiry_id}",
        extra={"extra_data": {"enquiry_id": exc.enquiry_id}},
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": {
                "type": "not_found",
                "message": "Enquiry not found",
            }
        }
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception):
    """Catch-all for internal unexpected server errors to prevent leaking stack traces."""
    logger.exception(
        f"Unexpected exception occurred: {str(exc)}",
        extra={"extra_data": {"error_details": str(exc)}},
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "type": "internal_server_error",
                "message": "An unexpected error occurred. Please contact system support.",
            }
        }
    )


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.get(
    "/",
    summary="Root API Metadata",
    description="Returns baseline metadata, version, and endpoints locations for Closira.",
    response_description="JSON dictionary with service status and metadata.",
)
def read_root():
    return {
        "service": "Closira API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


# Register health and enquiry routers
app.include_router(health.router)
app.include_router(enquiry.router)
app.include_router(enquiry.router_plural)
