import uuid
from typing import Dict, Any

from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Relationship(Base):
    """
    Relationship model representing edges in the graph.

    Attributes:
        id: UUID primary key
        source_entity_id: UUID foreign key to source entity
        target_entity_id: UUID foreign key to target entity
        type: Type of relationship (e.g., "owns", "works_at", "connected_to")
        relationship_metadata: JSON metadata for flexible attributes
        created_at: Timestamp when relationship was created
        updated_at: Timestamp when relationship was last updated
    """

    __tablename__ = "relationships"

    # Fields
    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"), index=True
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(String, index=True)
    metadata: Mapped[Dict[str, Any]] = mapped_column(
        "relationship_metadata", JSONB, default={}, server_default=text("'{}'::jsonb")
    )

    # Relationships
    source_entity = relationship(
        "Entity",
        foreign_keys=[source_entity_id],
        back_populates="outgoing_relationships",
    )
    target_entity = relationship(
        "Entity",
        foreign_keys=[target_entity_id],
        back_populates="incoming_relationships",
    )

    # Constraints and Indexes
    __table_args__ = (
        # Prevent exact duplicates
        UniqueConstraint(
            "source_entity_id",
            "target_entity_id",
            "type",
            name="uq_relationships_source_target_type",
        ),
        # GIN index for JSONB metadata
        Index("ix_relationships_metadata_gin", metadata, postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Relationship(id='{self.id}', type='{self.type}', source='{self.source_entity_id}', target='{self.target_entity_id}')>"
