"""
Closira — Health Check Router

Provides a /health endpoint that reports:
- API status: confirms the FastAPI server is running
- Database status: confirms SQLite is reachable via a simple query

Why a health endpoint?
- Industry best practice for any backend service
- Verifies both the API layer and database layer are functional
- Useful for monitoring, load balancers, and CI/CD pipelines
- Demonstrates operational awareness

Why test the database connection in the health check?
- A running API with a broken database is still broken
- Early detection of database issues saves debugging time
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging.config import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["System"])


@router.get(
    "/health",
    summary="Health Check",
    description="Returns the health status of the API and database connectivity.",
    response_description="Health status with API and database check results.",
    responses={
        200: {
            "description": "System is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "database": "connected",
                    }
                }
            },
        },
        503: {
            "description": "System is unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "database": "disconnected",
                        "detail": "Database connection failed",
                    }
                }
            },
        },
    },
)
def health_check(db: Session = Depends(get_db)):
    """
    Perform a health check on the API and database.

    - Executes a simple `SELECT 1` query to verify database connectivity.
    - Returns 200 if everything is healthy.
    - Returns 503 if the database is unreachable.
    """
    try:
        # Execute a lightweight query to verify the database is reachable
        db.execute(text("SELECT 1"))
        logger.info("Health check passed")

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as e:
        logger.error(
            "Health check failed — database unreachable",
            extra={"extra_data": {"error": str(e)}},
        )

        # Return 503 Service Unavailable when the database is down
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "detail": "Database connection failed",
            },
        )
