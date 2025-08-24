from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..models.entity import Entity
from ..models.relationship import Relationship
from ..schemas.base import PaginationResponse
from ..schemas.entity import EntityCreate, EntityRead, EntityUpdate

router = APIRouter(prefix="/entities")


@router.post("", response_model=EntityRead, status_code=status.HTTP_201_CREATED)
async def create_entity(entity: EntityCreate, db: AsyncSession = Depends(get_db)) -> EntityRead:

    existingEntitties = await db.execute(select(Entity).where(Entity.name == entity.name)) 

    if len(existingEntitties.scalars().all()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Entity with the name {entity.name} already exists"
        )
    
    """
    Create a new entity.
    """
    try:
        db_entity = Entity(type=entity.type, name=entity.name, extradata=entity.extradata)

        db.add(db_entity)
        await db.commit()
        await db.refresh(db_entity)

        # Return EntityRead schema instead of Entity model
        return EntityRead(
            id=db_entity.id,
            type=db_entity.type,
            name=db_entity.name,
            extradata=db_entity.extradata,
            created_at=db_entity.created_at,
            updated_at=db_entity.updated_at,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create entity: {str(e)}"
        )


@router.get("/{entity_id}", response_model=EntityRead)
async def read_entity(
    entity_id: UUID = Path(..., description="The ID of the entity to get"),
    db: AsyncSession = Depends(get_db),
) -> EntityRead:
    """
    Get a specific entity by ID.
    """
    entity = await db.get(Entity, entity_id)

    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found",
        )

    # Return EntityRead schema instead of Entity model
    return EntityRead(
        id=entity.id,
        type=entity.type,
        name=entity.name,
        extradata=entity.extradata,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


@router.get("", response_model=PaginationResponse[EntityRead])
async def list_entities(
    type: Optional[str] = Query(None, description="Filter by entity type"),
    name: Optional[str] = Query(None, description="Filter by exact entity name"),
    name_contains: Optional[str] = Query(
        None, description="Filter by name containing string (case-insensitive)"
    ),
    extradata_contains: Optional[str] = Query(
        None, description="Filter by extradata containing JSON (as string)"
    ),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    sort: str = Query("created_at:desc", description="Sort field and direction (field:asc|desc)"),
    db: AsyncSession = Depends(get_db),
) -> PaginationResponse[EntityRead]:
    """
    List entities with optional filtering, sorting, and pagination.
    """
    # Parse sort parameter
    sort_field, sort_direction = sort.split(":", 1) if ":" in sort else (sort, "desc")

    # Build query
    query = select(Entity)
    count_query = select(func.count()).select_from(Entity)

    # Apply filters
    if type:
        query = query.where(Entity.type == type)
        count_query = count_query.where(Entity.type == type)

    if name:
        query = query.where(Entity.name == name)
        count_query = count_query.where(Entity.name == name)

    if name_contains:
        query = query.where(Entity.name.ilike(f"%{name_contains}%"))
        count_query = count_query.where(Entity.name.ilike(f"%{name_contains}%"))

    if extradata_contains:
        # Parse extradata_contains as JSON
        import json

        try:
            extradata_dict = json.loads(extradata_contains)
            query = query.where(
                text("entity_extradata @> :extradata").bindparams(extradata=json.dumps(extradata_dict))
            )
            count_query = count_query.where(
                text("entity_extradata @> :extradata").bindparams(extradata=json.dumps(extradata_dict))
            )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON in extradata_contains parameter",
            )

    # Apply sorting
    if sort_field == "created_at" and sort_direction == "desc":
        query = query.order_by(Entity.created_at.desc())
    elif sort_field == "created_at" and sort_direction == "asc":
        query = query.order_by(Entity.created_at.asc())
    elif sort_field == "updated_at" and sort_direction == "desc":
        query = query.order_by(Entity.updated_at.desc())
    elif sort_field == "updated_at" and sort_direction == "asc":
        query = query.order_by(Entity.updated_at.asc())
    elif sort_field == "name" and sort_direction == "desc":
        query = query.order_by(Entity.name.desc())
    elif sort_field == "name" and sort_direction == "asc":
        query = query.order_by(Entity.name.asc())
    elif sort_field == "type" and sort_direction == "desc":
        query = query.order_by(Entity.type.desc())
    elif sort_field == "type" and sort_direction == "asc":
        query = query.order_by(Entity.type.asc())
    else:
        query = query.order_by(Entity.created_at.desc())

    # Apply pagination
    query = query.offset(offset).limit(limit)

    # Execute queries
    result = await db.execute(query)
    entities = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Handle case where total is None (e.g., when no entities exist)
    total = total if total is not None else 0

    # Convert Entity models to EntityRead schemas
    entity_reads = [
        EntityRead(
            id=entity.id,
            type=entity.type,
            name=entity.name,
            extradata=entity.extradata,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        for entity in entities
    ]

    return PaginationResponse(items=entity_reads, total=total, limit=limit, offset=offset)


@router.patch("/{entity_id}", response_model=EntityRead)
async def update_entity(
    entity_update: EntityUpdate,
    entity_id: UUID = Path(..., description="The ID of the entity to update"),
    extradata_mode: str = Query(
        "replace", description="How to handle extradata updates: 'merge' or 'replace'"
    ),
    db: AsyncSession = Depends(get_db),
) -> EntityRead:
    """
    Update an entity by ID.
    """
    entity = await db.get(Entity, entity_id)

    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found",
        )

    # Update fields if provided in request
    if entity_update.type is not None:
        entity.type = entity_update.type

    if entity_update.name is not None:
        entity.name = entity_update.name

    if entity_update.extradata is not None:
        if extradata_mode == "merge":
            # Merge existing extradata with new extradata
            entity.extradata = {**entity.extradata, **entity_update.extradata}
        else:
            # Replace extradata completely
            entity.extradata = entity_update.extradata

    await db.commit()
    await db.refresh(entity)

    # Return EntityRead schema instead of Entity model
    return EntityRead(
        id=entity.id,
        type=entity.type,
        name=entity.name,
        extradata=entity.extradata,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


@router.delete("/{entity_id}", status_code=status.HTTP_200_OK)
async def delete_entity(
    entity_id: UUID = Path(..., description="The ID of the entity to delete"),
    force: bool = Query(False, description="Force delete even if relationships exist"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, bool]:
    """
    Delete an entity by ID.

    By default, will reject deletion if relationships exist for this entity.
    Use force=true to cascade delete relationships.
    """
    entity = await db.get(Entity, entity_id)

    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found",
        )

    if not force:
        # Check if entity has any relationships
        relationship_query = (
            select(func.count())
            .select_from(Relationship)
            .where(
                or_(
                    Relationship.source_entity_id == entity_id,
                    Relationship.target_entity_id == entity_id,
                )
            )
        )
        result = await db.execute(relationship_query)
        relationship_count = result.scalar()

        relationship_count = relationship_count if relationship_count is not None else 0

        if relationship_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete entity with ID {entity_id} because it has {relationship_count} relationships. Use force=true to delete anyway.",
            )

    await db.delete(entity)
    await db.commit()

    return {"deleted": True}
