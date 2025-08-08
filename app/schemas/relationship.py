from typing import Dict, Any, Optional
from uuid import UUID

from pydantic import Field, field_validator

from .base import BaseSchema, TimestampMixin


class RelationshipBase(BaseSchema):
    """Base schema with common attributes for Relationship models."""
    source_entity_id: UUID = Field(..., description="UUID of source entity")
    target_entity_id: UUID = Field(..., description="UUID of target entity")
    type: str = Field(..., description="Type of relationship (e.g., 'owns', 'works_at', 'connected_to')")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible metadata as JSON")

    @field_validator('type')
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validate that type is not empty."""
        if not v or not v.strip():
            raise ValueError("Relationship type must not be empty")
        return v.strip()


class RelationshipCreate(RelationshipBase):
    """Schema for creating a new relationship."""
    pass


class RelationshipUpdate(BaseSchema):
    """Schema for updating an existing relationship."""
    source_entity_id: Optional[UUID] = Field(None, description="UUID of source entity")
    target_entity_id: Optional[UUID] = Field(None, description="UUID of target entity")
    type: Optional[str] = Field(None, description="Type of relationship")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Flexible metadata as JSON")

    @field_validator('type')
    @classmethod
    def validate_non_empty_if_present(cls, v: Optional[str]) -> Optional[str]:
        """Validate that type is not empty if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Relationship type must not be empty")
            return v.strip()
        return v


class RelationshipRead(RelationshipBase, TimestampMixin):
    """Schema for reading a relationship."""
    id: UUID = Field(..., description="UUID primary key")


class RelationshipFilter(BaseSchema):
    """Schema for relationship filtering parameters."""
    source_entity_id: Optional[UUID] = Field(None, description="Filter by source entity ID")
    target_entity_id: Optional[UUID] = Field(None, description="Filter by target entity ID")
    type: Optional[str] = Field(None, description="Filter by relationship type")
    metadata_contains: Optional[Dict[str, Any]] = Field(None, description="Filter by metadata containing these key-value pairs")
