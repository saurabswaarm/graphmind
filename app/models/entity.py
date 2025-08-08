import uuid
from typing import Dict, Any, List, Optional, Type

from sqlalchemy import String, Index, text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy.engine import Dialect

from .base import Base


class JSONType(TypeDecorator):
    """Platform-independent JSON type.
    
    Uses PostgreSQL's JSONB type when available, otherwise uses JSON or TEXT type.
    """
    impl = JSON
    cache_ok = True
    
    def load_dialect_impl(self, dialect: Dialect) -> Type:
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


class Entity(Base):
    """
    Entity model representing nodes in the graph.
    
    Attributes:
        id: UUID primary key
        type: Type of entity (e.g., "person", "company", "asset")
        name: Human-friendly label for the entity
        entity_metadata: JSON metadata for flexible attributes
        created_at: Timestamp when entity was created
        updated_at: Timestamp when entity was last updated
    """
    __tablename__ = "entities"
    
    # Fields
    type: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    entity_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONType, default={}, server_default=text("'{}'::jsonb")
    )
    
    # Relationships
    outgoing_relationships: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="[Relationship.source_entity_id]",
        back_populates="source_entity",
        cascade="all, delete-orphan",
    )
    
    incoming_relationships: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="[Relationship.target_entity_id]",
        back_populates="target_entity",
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        # GIN index for JSONB metadata
        Index("ix_entities_metadata_gin", entity_metadata, postgresql_using="gin"),
    )
    
    def __repr__(self) -> str:
        return f"<Entity(id='{self.id}', type='{self.type}', name='{self.name}')>"
