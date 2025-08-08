import uuid
import pytest
from httpx import AsyncClient
from fastapi import status

# Test data
TEST_ENTITY = {
    "type": "person",
    "name": "John Doe",
    "metadata": {"age": 30, "location": "New York"}
}

TEST_ENTITY_UPDATE = {
    "name": "Jane Doe",
    "metadata": {"age": 31, "location": "Boston"}
}


@pytest.mark.asyncio
async def test_create_entity(test_client: AsyncClient):
    """Test creating a new entity."""
    response = await test_client.post("/entities", json=TEST_ENTITY)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["type"] == TEST_ENTITY["type"]
    assert data["name"] == TEST_ENTITY["name"]
    assert data["metadata"] == TEST_ENTITY["metadata"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    
    # Store entity ID for other tests
    return data["id"]


@pytest.mark.asyncio
async def test_get_entity(test_client: AsyncClient):
    """Test retrieving an entity by ID."""
    # First create an entity
    create_response = await test_client.post("/entities", json=TEST_ENTITY)
    entity_id = create_response.json()["id"]
    
    # Then retrieve it
    response = await test_client.get(f"/entities/{entity_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == entity_id
    assert data["type"] == TEST_ENTITY["type"]
    assert data["name"] == TEST_ENTITY["name"]
    assert data["metadata"] == TEST_ENTITY["metadata"]


@pytest.mark.asyncio
async def test_update_entity(test_client: AsyncClient):
    """Test updating an entity."""
    # First create an entity
    create_response = await test_client.post("/entities", json=TEST_ENTITY)
    entity_id = create_response.json()["id"]
    
    # Then update it
    response = await test_client.patch(
        f"/entities/{entity_id}", 
        json=TEST_ENTITY_UPDATE
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == entity_id
    assert data["type"] == TEST_ENTITY["type"]  # Type should not change
    assert data["name"] == TEST_ENTITY_UPDATE["name"]
    assert data["metadata"]["age"] == TEST_ENTITY_UPDATE["metadata"]["age"]
    assert data["metadata"]["location"] == TEST_ENTITY_UPDATE["metadata"]["location"]


@pytest.mark.asyncio
async def test_delete_entity(test_client: AsyncClient):
    """Test deleting an entity."""
    # First create an entity
    create_response = await test_client.post("/entities", json=TEST_ENTITY)
    entity_id = create_response.json()["id"]
    
    # Then delete it
    delete_response = await test_client.delete(f"/entities/{entity_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's gone
    get_response = await test_client.get(f"/entities/{entity_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_list_entities(test_client: AsyncClient):
    """Test listing entities with pagination and filters."""
    # Create multiple entities
    entity_types = ["person", "organization", "person"]
    entity_names = ["Alice", "Acme Inc", "Bob"]
    
    for i in range(3):
        await test_client.post("/entities", json={
            "type": entity_types[i],
            "name": entity_names[i],
            "metadata": {"index": i}
        })
    
    # Test basic listing
    response = await test_client.get("/entities")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 3  # There might be other entities from other tests
    assert data["total"] >= 3
    assert data["page"] == 1
    assert data["size"] == 50  # Default page size
    
    # Test filtering by type
    response = await test_client.get("/entities?type=person")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) >= 2
    for item in data["items"]:
        assert item["type"] == "person"
    
    # Test pagination
    response = await test_client.get("/entities?page=1&size=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["size"] == 2


@pytest.mark.asyncio
async def test_entity_not_found(test_client: AsyncClient):
    """Test entity not found error case."""
    random_id = str(uuid.uuid4())
    response = await test_client.get(f"/entities/{random_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
