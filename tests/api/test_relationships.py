import uuid
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
class TestRelationships:
    """Test suite for relationship API endpoints."""
    
    @pytest.fixture(autouse=True)
    async def setup(self, test_client: AsyncClient):
        """Set up test entities for relationship tests."""
        # Create source and target entities
        source_entity = {
            "type": "person",
            "name": "Source Person",
            "metadata": {"role": "source"}
        }
        target_entity = {
            "type": "organization",
            "name": "Target Organization",
            "metadata": {"role": "target"}
        }
        
        source_resp = await test_client.post("/entities", json=source_entity)
        target_resp = await test_client.post("/entities", json=target_entity)
        
        self.source_id = source_resp.json()["id"]
        self.target_id = target_resp.json()["id"]
        
        # Basic relationship for tests
        self.test_relationship = {
            "source_entity_id": self.source_id,
            "target_entity_id": self.target_id,
            "type": "works_for",
            "metadata": {"start_date": "2023-01-01", "department": "Engineering"}
        }
    
    async def test_create_relationship(self, test_client: AsyncClient):
        """Test creating a new relationship between entities."""
        response = await test_client.post("/relationships", json=self.test_relationship)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["source_entity_id"] == self.source_id
        assert data["target_entity_id"] == self.target_id
        assert data["type"] == self.test_relationship["type"]
        assert data["metadata"] == self.test_relationship["metadata"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        return data["id"]
    
    async def test_get_relationship(self, test_client: AsyncClient):
        """Test retrieving a relationship by ID."""
        # First create a relationship
        create_response = await test_client.post("/relationships", json=self.test_relationship)
        relationship_id = create_response.json()["id"]
        
        # Then retrieve it
        response = await test_client.get(f"/relationships/{relationship_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == relationship_id
        assert data["source_entity_id"] == self.source_id
        assert data["target_entity_id"] == self.target_id
        assert data["type"] == self.test_relationship["type"]
        assert data["metadata"] == self.test_relationship["metadata"]
    
    async def test_update_relationship(self, test_client: AsyncClient):
        """Test updating a relationship."""
        # First create a relationship
        create_response = await test_client.post("/relationships", json=self.test_relationship)
        relationship_id = create_response.json()["id"]
        
        # Define update payload
        update_data = {
            "metadata": {
                "start_date": "2023-02-01", 
                "department": "Product",
                "is_manager": True
            }
        }
        
        # Then update it
        response = await test_client.patch(
            f"/relationships/{relationship_id}", 
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == relationship_id
        assert data["source_entity_id"] == self.source_id
        assert data["target_entity_id"] == self.target_id
        assert data["type"] == self.test_relationship["type"]  # Type should not change
        assert data["metadata"]["start_date"] == update_data["metadata"]["start_date"]
        assert data["metadata"]["department"] == update_data["metadata"]["department"]
        assert data["metadata"]["is_manager"] == update_data["metadata"]["is_manager"]
    
    async def test_delete_relationship(self, test_client: AsyncClient):
        """Test deleting a relationship."""
        # First create a relationship
        create_response = await test_client.post("/relationships", json=self.test_relationship)
        relationship_id = create_response.json()["id"]
        
        # Then delete it
        delete_response = await test_client.delete(f"/relationships/{relationship_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's gone
        get_response = await test_client.get(f"/relationships/{relationship_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_list_relationships(self, test_client: AsyncClient):
        """Test listing relationships with pagination and filters."""
        # Create additional test entity for multiple relationships
        another_entity = {
            "type": "project",
            "name": "Test Project",
            "metadata": {"role": "project"}
        }
        another_resp = await test_client.post("/entities", json=another_entity)
        another_id = another_resp.json()["id"]
        
        # Create multiple relationships
        rel_types = ["works_for", "manages", "contributes_to"]
        rel_targets = [self.target_id, self.target_id, another_id]
        
        for i in range(3):
            await test_client.post("/relationships", json={
                "source_entity_id": self.source_id,
                "target_entity_id": rel_targets[i],
                "type": rel_types[i],
                "metadata": {"index": i}
            })
        
        # Test basic listing
        response = await test_client.get("/relationships")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 3
        assert data["total"] >= 3
        assert data["page"] == 1
        assert data["size"] == 50  # Default page size
        
        # Test filtering by type
        response = await test_client.get("/relationships?type=works_for")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 1
        for item in data["items"]:
            assert item["type"] == "works_for"
        
        # Test filtering by source
        response = await test_client.get(f"/relationships?source_entity_id={self.source_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 3
        for item in data["items"]:
            assert item["source_entity_id"] == self.source_id
    
    async def test_relationship_not_found(self, test_client: AsyncClient):
        """Test relationship not found error case."""
        random_id = str(uuid.uuid4())
        response = await test_client.get(f"/relationships/{random_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_unique_relationship_constraint(self, test_client: AsyncClient):
        """Test that duplicate relationships are not allowed."""
        # Create a relationship
        await test_client.post("/relationships", json=self.test_relationship)
        
        # Try to create the same relationship again
        response = await test_client.post("/relationships", json=self.test_relationship)
        assert response.status_code == status.HTTP_409_CONFLICT
        
        # Test upsert flag works
        upsert_response = await test_client.post(
            "/relationships?upsert=true", 
            json=self.test_relationship
        )
        assert upsert_response.status_code == status.HTTP_200_OK
