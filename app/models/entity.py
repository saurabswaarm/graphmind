from typing import Dict, Any, List

from sqlalchemy import String, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .relationship import Relationship


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
    extradata: Mapped[Dict[str, Any]] = mapped_column(
        "entity_extradata", JSONB, default={}, server_default=text("'{}'::jsonb")
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
        # GIN index for JSONB extradata
        Index("ix_entities_extradata_gin", extradata, postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Entity(id='{self.id}', type='{self.type}', name='{self.name}')>"
