import pytest
from fastapi import status
import io

def create_mock_neo4j_node(node_id, **properties):
    # Build a lightweight mock object mimicking neo4j Node
    class SimpleNode(dict):
        def __init__(self, id, **props):
            super().__init__(**props)
            self.id = id
        def get(self, k):
            return dict.get(self, k)
    return SimpleNode(node_id, **properties)

def create_mock_relationship(start_node, rel_type, end_node):
    class SimpleRel:
        def __init__(self, start_node, rel_type, end_node):
            self.start_node = start_node
            self.end_node = end_node
            self.type = rel_type
    return SimpleRel(start_node, rel_type, end_node)

def test_get_employee_success(test_client, mock_neo4j_credentials, mock_neo4j_driver):
    mock_driver, mock_session = mock_neo4j_driver
    
    # Create mock nodes and relationships
    manager = create_mock_neo4j_node(1, fullName="John Doe", email="john@example.com")
    employee = create_mock_neo4j_node(2, fullName="Jane Smith", email="jane@example.com")
    rel = create_mock_relationship(manager, "MANAGES", employee)
    
    # Mock Neo4j query result
    mock_session.run.return_value.single.return_value = {
        "nodes": [manager, employee],
        "rels": [rel]
    }
    
    response = test_client.get("/employee?name=John%20Doe")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert len(data["nodes"]) == 2
    assert len(data["links"]) == 1
    assert data["nodes"][0]["fullName"] == "John Doe"
    assert data["nodes"][1]["fullName"] == "Jane Smith"
    assert data["links"][0]["type"] == "MANAGES"

def test_get_employee_not_found(test_client, mock_neo4j_credentials, mock_neo4j_driver):
    mock_driver, mock_session = mock_neo4j_driver
    mock_session.run.return_value.single.return_value = None
    
    response = test_client.get("/employee?name=NonExistent")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nodes"] == []
    assert data["links"] == []

def test_upload_csv_success(test_client, mock_neo4j_credentials, mock_neo4j_driver):
    mock_driver, mock_session = mock_neo4j_driver
    
    # Create test CSV content
    csv_content = """First Name,Last Name,Email,Phone,Address,Manager Name
John,Doe,john@example.com,123-456-7890,123 Main St,Boss Person
Jane,Smith,jane@example.com,098-765-4321,456 Oak St,John Doe"""
    
    # Create file-like object
    file = io.BytesIO(csv_content.encode())
    file.name = "test.csv"
    
    response = test_client.post(
        "/upload",
        files={"file": ("test.csv", file, "text/csv")},
        headers={"X-API-Key": "test-admin-key"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["imported"] == 2

def test_upload_requires_api_key(test_client, mock_neo4j_credentials, mock_neo4j_driver):
    file = io.BytesIO(b"First Name,Last Name\nA,B")
    file.name = "test.csv"
    response = test_client.post(
        "/upload",
        files={"file": ("test.csv", file, "text/csv")}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_upload_invalid_api_key(test_client, mock_neo4j_credentials, mock_neo4j_driver):
    file = io.BytesIO(b"First Name,Last Name\nA,B")
    file.name = "test.csv"
    response = test_client.post(
        "/upload",
        files={"file": ("test.csv", file, "text/csv")},
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_upload_with_valid_api_key(test_client, mock_neo4j_credentials, mock_neo4j_driver):
    file = io.BytesIO(b"First Name,Last Name\nA,B")
    file.name = "test.csv"
    response = test_client.post(
        "/upload",
        files={"file": ("test.csv", file, "text/csv")},
        headers={"X-API-Key": "test-admin-key"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["imported"] == 1
