from datetime import datetime
from typing import Generic, List, TypeVar, Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

# Generic type for pagination
T = TypeVar('T')


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for models with created_at and updated_at fields."""
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseSchema):
    """Query parameters for pagination."""
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of items to return")
    offset: int = Field(0, ge=0, description="Number of items to skip")


class PaginationResponse(BaseSchema, Generic[T]):
    """Generic response for paginated results."""
    items: List[T]
    total: int
    limit: int
    offset: int


class ErrorResponse(BaseSchema):
    """Standard error response."""
    detail: str | List[Dict[str, Any]] = Field(..., description="Error details")
    code: Optional[str] = Field(None, description="Error code")
