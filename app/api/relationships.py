from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db.session import get_db
from ..models.entity import Entity
from ..models.relationship import Relationship
from ..schemas.base import PaginationResponse
from ..schemas.relationship import (
    RelationshipCreate,
    RelationshipRead,
    RelationshipUpdate,
)

router = APIRouter(prefix="/relationships")


@router.post("", response_model=RelationshipRead, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    relationship: RelationshipCreate,
    upsert: bool = Query(
        False,
        description="If true, update the relationship instead of failing on conflict",
    ),
    db: AsyncSession = Depends(get_db),
) -> Relationship:
    """
    Create a new relationship.

    If the relationship already exists (same source, target, and type),
    will return 409 Conflict unless upsert=true.
    """
    # Check if source entity exists
    source_entity = await db.get(Entity, relationship.source_entity_id)
    if not source_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source entity with ID {relationship.source_entity_id} not found",
        )

    # Check if target entity exists
    target_entity = await db.get(Entity, relationship.target_entity_id)
    if not target_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target entity with ID {relationship.target_entity_id} not found",
        )

    # Check for self-relationships if not allowed
    if not settings.ALLOW_SELF_RELATIONSHIPS:
        if relationship.source_entity_id == relationship.target_entity_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Self-relationships are not allowed by configuration",
            )

    # Check if relationship already exists
    existing_query = select(Relationship).where(
        Relationship.source_entity_id == relationship.source_entity_id,
        Relationship.target_entity_id == relationship.target_entity_id,
        Relationship.type == relationship.type,
    )
    result = await db.execute(existing_query)
    existing_relationship = result.scalar_one_or_none()

    if existing_relationship:
        if upsert:
            # Update the existing relationship
            if relationship.metadata:
                existing_relationship.metadata = relationship.metadata
            await db.commit()
            await db.refresh(existing_relationship)
            return existing_relationship
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Relationship with the same source, target, and type already exists",
            )

    # Create new relationship
    db_relationship = Relationship(
        source_entity_id=relationship.source_entity_id,
        target_entity_id=relationship.target_entity_id,
        type=relationship.type,
        metadata=relationship.metadata,
    )

    try:
        db.add(db_relationship)
        await db.commit()
        await db.refresh(db_relationship)
        return db_relationship
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid relationship data or constraints violated",
        )


@router.get("/{relationship_id}", response_model=RelationshipRead)
async def read_relationship(
    relationship_id: UUID = Path(..., description="The ID of the relationship to get"),
    db: AsyncSession = Depends(get_db),
) -> Relationship:
    """
    Get a specific relationship by ID.
    """
    relationship = await db.get(Relationship, relationship_id)

    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship with ID {relationship_id} not found",
        )

    return relationship


@router.get("", response_model=PaginationResponse[RelationshipRead])
async def list_relationships(
    source_id: Optional[UUID] = Query(None, description="Filter by source entity ID"),
    target_id: Optional[UUID] = Query(None, description="Filter by target entity ID"),
    type: Optional[str] = Query(None, description="Filter by relationship type"),
    metadata_contains: Optional[str] = Query(
        None, description="Filter by metadata containing JSON (as string)"
    ),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    sort: str = Query("created_at:desc", description="Sort field and direction (field:asc|desc)"),
    db: AsyncSession = Depends(get_db),
) -> PaginationResponse[RelationshipRead]:
    """
    List relationships with optional filtering, sorting, and pagination.
    """
    # Parse sort parameter
    sort_field, sort_direction = sort.split(":", 1) if ":" in sort else (sort, "desc")

    # Build query
    query = select(Relationship)
    count_query = select(func.count()).select_from(Relationship)

    # Apply filters
    if source_id:
        query = query.where(Relationship.source_entity_id == source_id)
        count_query = count_query.where(Relationship.source_entity_id == source_id)

    if target_id:
        query = query.where(Relationship.target_entity_id == target_id)
        count_query = count_query.where(Relationship.target_entity_id == target_id)

    if type:
        query = query.where(Relationship.type == type)
        count_query = count_query.where(Relationship.type == type)

    if metadata_contains:
        # Parse metadata_contains as JSON
        import json

        try:
            metadata_dict = json.loads(metadata_contains)
            query = query.where(
                text("metadata @> :metadata").bindparams(metadata=json.dumps(metadata_dict))
            )
            count_query = count_query.where(
                text("metadata @> :metadata").bindparams(metadata=json.dumps(metadata_dict))
            )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON in metadata_contains parameter",
            )

    # Apply sorting
    if sort_field == "created_at" and sort_direction == "desc":
        query = query.order_by(Relationship.created_at.desc())
    elif sort_field == "created_at" and sort_direction == "asc":
        query = query.order_by(Relationship.created_at.asc())
    elif sort_field == "updated_at" and sort_direction == "desc":
        query = query.order_by(Relationship.updated_at.desc())
    elif sort_field == "updated_at" and sort_direction == "asc":
        query = query.order_by(Relationship.updated_at.asc())
    elif sort_field == "type" and sort_direction == "desc":
        query = query.order_by(Relationship.type.desc())
    elif sort_field == "type" and sort_direction == "asc":
        query = query.order_by(Relationship.type.asc())
    else:
        query = query.order_by(Relationship.created_at.desc())

    # Apply pagination
    query = query.offset(offset).limit(limit)

    # Execute queries
    result = await db.execute(query)
    relationships = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    if total is None:
        total = 0

    # Convert SQLAlchemy models to Pydantic models
    relationship_reads = [
        RelationshipRead.model_validate(relationship) for relationship in relationships
    ]

    return PaginationResponse(items=relationship_reads, total=total, limit=limit, offset=offset)


@router.patch("/{relationship_id}", response_model=RelationshipRead)
async def update_relationship(
    relationship_update: RelationshipUpdate,
    relationship_id: UUID = Path(..., description="The ID of the relationship to update"),
    metadata_mode: str = Query(
        "replace", description="How to handle metadata updates: 'merge' or 'replace'"
    ),
    db: AsyncSession = Depends(get_db),
) -> Relationship:
    """
    Update a relationship by ID.
    """
    relationship = await db.get(Relationship, relationship_id)

    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship with ID {relationship_id} not found",
        )

    # Check if the update would cause a self-relationship
    new_source_id = relationship_update.source_entity_id or relationship.source_entity_id
    new_target_id = relationship_update.target_entity_id or relationship.target_entity_id

    if new_source_id == new_target_id and not settings.ALLOW_SELF_RELATIONSHIPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Self-relationships are not allowed by configuration",
        )

    # Update fields if provided in request
    if relationship_update.source_entity_id is not None:
        # Check if source entity exists
        source_entity = await db.get(Entity, relationship_update.source_entity_id)
        if not source_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source entity with ID {relationship_update.source_entity_id} not found",
            )
        relationship.source_entity_id = relationship_update.source_entity_id

    if relationship_update.target_entity_id is not None:
        # Check if target entity exists
        target_entity = await db.get(Entity, relationship_update.target_entity_id)
        if not target_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target entity with ID {relationship_update.target_entity_id} not found",
            )
        relationship.target_entity_id = relationship_update.target_entity_id

    if relationship_update.type is not None:
        relationship.type = relationship_update.type

    if relationship_update.metadata is not None:
        if metadata_mode == "merge":
            # Merge existing metadata with new metadata
            relationship.metadata = {
                **relationship.metadata,
                **relationship_update.metadata,
            }
        else:
            # Replace metadata completely
            relationship.metadata = relationship_update.metadata

    try:
        await db.commit()
        await db.refresh(relationship)
        return relationship
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Relationship with the same source, target, and type already exists",
        )


@router.delete("/{relationship_id}", status_code=status.HTTP_200_OK)
async def delete_relationship(
    relationship_id: UUID = Path(..., description="The ID of the relationship to delete"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, bool]:
    """
    Delete a relationship by ID.
    """
    relationship = await db.get(Relationship, relationship_id)

    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship with ID {relationship_id} not found",
        )

    await db.delete(relationship)
    await db.commit()

    return {"deleted": True}
