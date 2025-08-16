from typing import Any, Dict, List

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..schemas.base import ErrorResponse


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handler for request validation errors.
    Formats error details in a consistent way.
    """
    # Convert ErrorDetails to Dict[str, Any] for compatibility
    errors: List[Dict[str, Any]] = [dict(error) for error in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(detail=errors, code="validation_error").model_dump(),
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """
    Handler for SQLAlchemy IntegrityError exceptions.
    Converts database constraint errors into user-friendly messages.
    """
    error_message = str(exc)
    error_code = "integrity_error"
    status_code = status.HTTP_400_BAD_REQUEST

    # Handle specific integrity errors with better messages
    if (
        "unique constraint" in error_message.lower()
        or "duplicate key" in error_message.lower()
    ):
        if (
            "relationships_source_target_type_key" in error_message
            or "uq_relationships_source_target_type" in error_message
        ):
            error_message = (
                "A relationship with the same source, target, and type already exists."
            )
            error_code = "duplicate_relationship"
            status_code = status.HTTP_409_CONFLICT
        else:
            error_message = "A resource with the same unique fields already exists."
            error_code = "duplicate_resource"
            status_code = status.HTTP_409_CONFLICT

    # Foreign key constraint violations
    elif "foreign key constraint" in error_message.lower():
        if "fk_relationships_source_entity_id_entities" in error_message:
            error_message = "The source entity does not exist."
            error_code = "entity_not_found"
            status_code = status.HTTP_404_NOT_FOUND
        elif "fk_relationships_target_entity_id_entities" in error_message:
            error_message = "The target entity does not exist."
            error_code = "entity_not_found"
            status_code = status.HTTP_404_NOT_FOUND
        else:
            error_message = "Referenced resource does not exist."
            error_code = "reference_error"

    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(detail=error_message, code=error_code).model_dump(),
    )


async def sqlalchemy_error_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handler for general SQLAlchemy errors.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="Database error occurred.", code="database_error"
        ).model_dump(),
    )


async def validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """
    Handler for Pydantic validation errors.
    """
    # Convert ErrorDetails to Dict[str, Any] for compatibility
    errors: List[Dict[str, Any]] = [dict(error) for error in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(detail=errors, code="validation_error").model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unhandled exceptions.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="An unexpected error occurred.", code="internal_error"
        ).model_dump(),
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI application.
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
