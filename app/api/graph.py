from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..config import settings
from ..db.session import get_db
from ..models.entity import Entity
from ..models.relationship import Relationship


class GraphScope(str, Enum):
    ALL = "all"
    BY_TYPE = "by_type"
    NEIGHBORHOOD = "neighborhood"


class Node(BaseModel):
    """Node representation for graph visualization."""

    id: UUID
    type: str
    name: str
    metadata: Optional[Dict[str, Any]] = None


class Edge(BaseModel):
    """Edge representation for graph visualization."""

    id: UUID
    source: UUID
    target: UUID
    type: str
    metadata: Optional[Dict[str, Any]] = None


class GraphStats(BaseModel):
    """Statistics about the returned graph."""

    node_count: int
    edge_count: int
    truncated: bool


class GraphResponse(BaseModel):
    """Response model for the graph endpoint."""

    nodes: List[Node]
    edges: List[Edge]
    stats: GraphStats


router = APIRouter(prefix="/graph")


@router.get("", response_model=GraphResponse)
async def get_graph(
    scope: GraphScope = Query(
        GraphScope.ALL, description="Scope of the graph to return"
    ),
    entity_type: Optional[str] = Query(
        None, description="Filter by entity type (when scope=by_type)"
    ),
    relationship_type: Optional[str] = Query(
        None, description="Filter by relationship type"
    ),
    root_id: Optional[UUID] = Query(
        None, description="Root entity ID (when scope=neighborhood)"
    ),
    depth: int = Query(1, ge=1, le=3, description="Depth of neighborhood traversal"),
    include_metadata: bool = Query(
        True, description="Whether to include metadata in the response"
    ),
    limit_nodes: Optional[int] = Query(
        None, description="Maximum number of nodes to return"
    ),
    limit_edges: Optional[int] = Query(
        None, description="Maximum number of edges to return"
    ),
    db: AsyncSession = Depends(get_db),
) -> GraphResponse:
    """
    Return a graph snapshot suitable for visualization.

    The graph can be filtered by scope:
    - all: Return all entities and relationships (potentially limited)
    - by_type: Return entities of a specific type and their relationships
    - neighborhood: Return entities in the neighborhood of a root entity

    Additional filtering and limits can be applied as needed.
    """
    # Set default limits from settings if not provided
    limit_nodes = limit_nodes or settings.GRAPH_DEFAULT_LIMIT_NODES
    limit_edges = limit_edges or settings.GRAPH_DEFAULT_LIMIT_EDGES

    # Check parameters based on scope
    if scope == GraphScope.BY_TYPE and entity_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="entity_type parameter is required when scope is 'by_type'",
        )

    if scope == GraphScope.NEIGHBORHOOD and root_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="root_id parameter is required when scope is 'neighborhood'",
        )

    # Initialize node and edge collections
    nodes = {}  # UUID -> Entity
    edges = {}  # UUID -> Relationship
    truncated = False

    # Fetch graph data based on scope
    if scope == GraphScope.ALL:
        # Fetch all entities, respecting the node limit
        entity_query = select(Entity).limit(limit_nodes + 1)  # +1 to check if truncated
        entity_result = await db.execute(entity_query)
        entities = entity_result.scalars().all()

        # Check if truncated
        if len(entities) > limit_nodes:
            entities = entities[:limit_nodes]
            truncated = True

        # Add entities to nodes dictionary
        for entity in entities:
            nodes[entity.id] = entity

        # Fetch relationships between these entities, respecting edge limit
        if nodes:
            entity_ids = list(nodes.keys())
            relationship_query = select(Relationship).where(
                and_(
                    Relationship.source_entity_id.in_(entity_ids),
                    Relationship.target_entity_id.in_(entity_ids),
                )
            )

            if relationship_type:
                relationship_query = relationship_query.where(
                    Relationship.type == relationship_type
                )

            relationship_query = relationship_query.limit(
                limit_edges + 1
            )  # +1 to check if truncated
            relationship_result = await db.execute(relationship_query)
            relationships = relationship_result.scalars().all()

            # Check if relationships are truncated
            if len(relationships) > limit_edges:
                relationships = relationships[:limit_edges]
                truncated = True

            # Add relationships to edges dictionary
            for rel in relationships:
                edges[rel.id] = rel

    elif scope == GraphScope.BY_TYPE:
        # Fetch entities of the specified type
        entity_query = (
            select(Entity).where(Entity.type == entity_type).limit(limit_nodes + 1)
        )
        entity_result = await db.execute(entity_query)
        entities = entity_result.scalars().all()

        # Check if truncated
        if len(entities) > limit_nodes:
            entities = entities[:limit_nodes]
            truncated = True

        # Add entities to nodes dictionary
        for entity in entities:
            nodes[entity.id] = entity

        # Fetch relationships between these entities
        if nodes:
            entity_ids = list(nodes.keys())
            relationship_query = select(Relationship).where(
                and_(
                    Relationship.source_entity_id.in_(entity_ids),
                    Relationship.target_entity_id.in_(entity_ids),
                )
            )

            if relationship_type:
                relationship_query = relationship_query.where(
                    Relationship.type == relationship_type
                )

            relationship_query = relationship_query.limit(limit_edges + 1)
            relationship_result = await db.execute(relationship_query)
            relationships = relationship_result.scalars().all()

            # Check if relationships are truncated
            if len(relationships) > limit_edges:
                relationships = relationships[:limit_edges]
                truncated = True

            # Add relationships to edges dictionary
            for rel in relationships:
                edges[rel.id] = rel

    elif scope == GraphScope.NEIGHBORHOOD:
        # Check if the root entity exists
        root_entity = await db.get(Entity, root_id)
        if root_entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Root entity with ID {root_id} not found",
            )

        # Add root entity to nodes
        nodes[root_entity.id] = root_entity

        # BFS traversal to find neighborhood
        frontier = [root_entity.id]
        visited = {root_entity.id}

        for current_depth in range(depth):
            next_frontier = []

            # For each entity in the current frontier
            for entity_id in frontier:
                # Find outgoing relationships
                out_rel_query = select(Relationship).where(
                    Relationship.source_entity_id == entity_id
                )
                if relationship_type:
                    out_rel_query = out_rel_query.where(
                        Relationship.type == relationship_type
                    )

                out_rel_result = await db.execute(out_rel_query)
                out_relationships = out_rel_result.scalars().all()

                # Find incoming relationships
                in_rel_query = select(Relationship).where(
                    Relationship.target_entity_id == entity_id
                )
                if relationship_type:
                    in_rel_query = in_rel_query.where(
                        Relationship.type == relationship_type
                    )

                in_rel_result = await db.execute(in_rel_query)
                in_relationships = in_rel_result.scalars().all()

                # Process outgoing relationships
                for rel in out_relationships:
                    if rel.id not in edges and len(edges) < limit_edges:
                        edges[rel.id] = rel

                        # Add target entity to next frontier if not visited
                        if rel.target_entity_id not in visited:
                            visited.add(rel.target_entity_id)

                            # Add target entity to nodes if within limit
                            if len(nodes) < limit_nodes:
                                target_entity = await db.get(
                                    Entity, rel.target_entity_id
                                )
                                if target_entity:
                                    nodes[target_entity.id] = target_entity
                                    next_frontier.append(target_entity.id)
                            else:
                                truncated = True
                    elif rel.id not in edges:
                        truncated = True

                # Process incoming relationships
                for rel in in_relationships:
                    if rel.id not in edges and len(edges) < limit_edges:
                        edges[rel.id] = rel

                        # Add source entity to next frontier if not visited
                        if rel.source_entity_id not in visited:
                            visited.add(rel.source_entity_id)

                            # Add source entity to nodes if within limit
                            if len(nodes) < limit_nodes:
                                source_entity = await db.get(
                                    Entity, rel.source_entity_id
                                )
                                if source_entity:
                                    nodes[source_entity.id] = source_entity
                                    next_frontier.append(source_entity.id)
                            else:
                                truncated = True
                    elif rel.id not in edges:
                        truncated = True

            # Update frontier for next iteration
            frontier = next_frontier

            # Stop if we've reached the limits
            if len(nodes) >= limit_nodes or len(edges) >= limit_edges:
                truncated = True
                break

    # Convert to response format
    node_list = [
        Node(
            id=entity.id,
            type=entity.type,
            name=entity.name,
            metadata=entity.metadata if include_metadata else None,
        )
        for entity in nodes.values()
    ]

    edge_list = [
        Edge(
            id=rel.id,
            source=rel.source_entity_id,
            target=rel.target_entity_id,
            type=rel.type,
            metadata=rel.metadata if include_metadata else None,
        )
        for rel in edges.values()
    ]

    # Create graph statistics
    stats = GraphStats(
        node_count=len(node_list), edge_count=len(edge_list), truncated=truncated
    )

    return GraphResponse(nodes=node_list, edges=edge_list, stats=stats)
