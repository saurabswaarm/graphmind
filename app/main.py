from fastapi import FastAPI, APIRouter, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .logging import setup_logging
from .api.errors import register_exception_handlers

# Import API routers
from .api import entities, relationships, graph, health


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    # Setup logging
    setup_logging(settings.LOG_LEVEL)

    # Create FastAPI app
    app = FastAPI(
        title="Graph API",
        description="Backend service for managing entities, relationships, and graph data.",
        version="0.1.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register global exception handlers
    register_exception_handlers(app)

    # Global exception handler for UUID parsing
    @app.exception_handler(ValueError)
    async def uuid_exception_handler(request: Request, exc: ValueError):
        if "invalid UUID" in str(exc):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid UUID format", "code": "invalid_uuid"},
            )
        raise exc  # Re-raise the exception if it's not a UUID parsing error

    # Create API router and include all routers
    api_router = APIRouter()
    api_router.include_router(health.router, tags=["health"])
    api_router.include_router(entities.router, tags=["entities"])
    api_router.include_router(relationships.router, tags=["relationships"])
    api_router.include_router(graph.router, tags=["graph"])

    # Include the API router in the main app
    app.include_router(api_router)

    return app


# Create the FastAPI app instance
app = create_app()
