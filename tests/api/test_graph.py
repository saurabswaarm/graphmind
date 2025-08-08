import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
class TestGraph:
    """Test suite for graph API endpoint."""
    
    @pytest.fixture(autouse=True)
    async def setup_graph(self, test_client: AsyncClient):
        """Set up a small graph for testing."""
        # Create entities
        entities = [
            {"type": "person", "name": "Alice", "metadata": {"role": "developer"}},
            {"type": "person", "name": "Bob", "metadata": {"role": "manager"}},
            {"type": "organization", "name": "TechCorp", "metadata": {"industry": "tech"}},
            {"type": "project", "name": "ProjectX", "metadata": {"status": "active"}},
            {"type": "project", "name": "ProjectY", "metadata": {"status": "planning"}}
        ]
        
        self.entity_ids = []
        for entity in entities:
            response = await test_client.post("/entities", json=entity)
            self.entity_ids.append(response.json()["id"])
        
        # Create relationships
        relationships = [
            {
                "source_entity_id": self.entity_ids[0],  # Alice
                "target_entity_id": self.entity_ids[2],  # TechCorp
                "type": "works_for",
                "metadata": {"start_date": "2022-01-01"}
            },
            {
                "source_entity_id": self.entity_ids[1],  # Bob
                "target_entity_id": self.entity_ids[2],  # TechCorp
                "type": "works_for",
                "metadata": {"start_date": "2021-01-01"}
            },
            {
                "source_entity_id": self.entity_ids[1],  # Bob
                "target_entity_id": self.entity_ids[0],  # Alice
                "type": "manages",
                "metadata": {"start_date": "2022-02-01"}
            },
            {
                "source_entity_id": self.entity_ids[0],  # Alice
                "target_entity_id": self.entity_ids[3],  # ProjectX
                "type": "contributes_to",
                "metadata": {"role": "developer"}
            },
            {
                "source_entity_id": self.entity_ids[1],  # Bob
                "target_entity_id": self.entity_ids[3],  # ProjectX
                "type": "oversees",
                "metadata": {"role": "manager"}
            },
            {
                "source_entity_id": self.entity_ids[0],  # Alice
                "target_entity_id": self.entity_ids[4],  # ProjectY
                "type": "interested_in",
                "metadata": {"status": "future"}
            }
        ]
        
        for rel in relationships:
            await test_client.post("/relationships", json=rel)
    
    async def test_get_full_graph(self, test_client: AsyncClient):
        """Test retrieving the full graph."""
        response = await test_client.get("/graph")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check graph structure
        assert "nodes" in data
        assert "edges" in data
        assert "stats" in data
        
        # Verify nodes count
        assert len(data["nodes"]) == 5
        assert data["stats"]["node_count"] == 5
        
        # Verify edges count
        assert len(data["edges"]) == 6
        assert data["stats"]["edge_count"] == 6
        
        # Verify node structure
        for node in data["nodes"]:
            assert "id" in node
            assert "type" in node
            assert "name" in node
            assert "metadata" in node
        
        # Verify edge structure
        for edge in data["edges"]:
            assert "id" in edge
            assert "source" in edge
            assert "target" in edge
            assert "type" in edge
            assert "metadata" in edge
    
    async def test_filter_graph_by_entity_type(self, test_client: AsyncClient):
        """Test filtering the graph by entity type."""
        response = await test_client.get("/graph?entity_types=person")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should only include person nodes
        assert len(data["nodes"]) == 2
        for node in data["nodes"]:
            assert node["type"] == "person"
    
    async def test_filter_graph_by_relationship_type(self, test_client: AsyncClient):
        """Test filtering the graph by relationship type."""
        response = await test_client.get("/graph?relationship_types=works_for")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should include all nodes but only works_for edges
        assert len(data["nodes"]) > 0
        assert len(data["edges"]) > 0
        
        for edge in data["edges"]:
            assert edge["type"] == "works_for"
    
    async def test_get_neighborhood(self, test_client: AsyncClient):
        """Test retrieving the neighborhood of a node."""
        # Get neighborhood of Alice (entity_ids[0])
        response = await test_client.get(f"/graph/neighborhood/{self.entity_ids[0]}?depth=1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should include Alice and immediate neighbors
        assert len(data["nodes"]) >= 4  # Alice, Bob, TechCorp, ProjectX, ProjectY
        
        # Check if Alice is in the nodes
        alice_found = False
        for node in data["nodes"]:
            if node["id"] == self.entity_ids[0]:
                alice_found = True
                break
        assert alice_found
        
        # All edges should connect to Alice
        for edge in data["edges"]:
            assert edge["source"] == self.entity_ids[0] or edge["target"] == self.entity_ids[0]
    
    async def test_exclude_metadata(self, test_client: AsyncClient):
        """Test excluding metadata from graph response."""
        response = await test_client.get("/graph?include_metadata=false")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Metadata should be excluded
        for node in data["nodes"]:
            assert "metadata" not in node
        
        for edge in data["edges"]:
            assert "metadata" not in edge
    
    async def test_limit_graph_size(self, test_client: AsyncClient):
        """Test limiting the graph size."""
        # Limit to 2 nodes
        response = await test_client.get("/graph?node_limit=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should only include 2 nodes
        assert len(data["nodes"]) == 2
        assert data["stats"]["truncated"] == True
