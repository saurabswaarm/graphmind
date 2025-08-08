from typing import Dict, Any, Optional
from uuid import UUID

from pydantic import Field, field_validator

from .base import BaseSchema, TimestampMixin


class EntityBase(BaseSchema):
    """Base schema with common attributes for Entity models."""
    type: str = Field(..., description="Type of entity (e.g., 'person', 'company', 'asset')")
    name: str = Field(..., description="Human-friendly label for the entity")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible metadata as JSON")

    @field_validator('type', 'name')
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validate that type and name are not empty strings."""
        if not v or not v.strip():
            raise ValueError("Must not be empty")
        return v.strip()


class EntityCreate(EntityBase):
    """Schema for creating a new entity."""
    pass


class EntityUpdate(BaseSchema):
    """Schema for updating an existing entity."""
    type: Optional[str] = Field(None, description="Type of entity")
    name: Optional[str] = Field(None, description="Human-friendly label for the entity")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Flexible metadata as JSON")

    @field_validator('type', 'name')
    @classmethod
    def validate_non_empty_if_present(cls, v: Optional[str]) -> Optional[str]:
        """Validate that type and name are not empty if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Must not be empty")
            return v.strip()
        return v


class EntityRead(EntityBase, TimestampMixin):
    """Schema for reading an entity."""
    id: UUID = Field(..., description="UUID primary key")


class EntityFilter(BaseSchema):
    """Schema for entity filtering parameters."""
    type: Optional[str] = Field(None, description="Filter by entity type")
    name: Optional[str] = Field(None, description="Filter by exact entity name")
    name_contains: Optional[str] = Field(None, description="Filter by name containing string (case-insensitive)")
    metadata_contains: Optional[Dict[str, Any]] = Field(None, description="Filter by metadata containing these key-value pairs")
