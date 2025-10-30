import pytest
from fastapi import status
from neo4j import Record, Node as Neo4jNode, Relationship
import io

def create_mock_neo4j_node(node_id, **properties):
    node = Neo4jNode("Employee", node_id, **properties)
    return node

def test_get_employee_success(test_client, mock_neo4j_credentials, mock_neo4j_driver):
    mock_driver, mock_session = mock_neo4j_driver
    
    # Create mock nodes and relationships
    manager = create_mock_neo4j_node(1, fullName="John Doe", email="john@example.com")
    employee = create_mock_neo4j_node(2, fullName="Jane Smith", email="jane@example.com")
    rel = Relationship(manager, "MANAGES", employee)
    
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
        files={"file": ("test.csv", file, "text/csv")}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["imported"] == 2

def test_upload_invalid_file(test_client, mock_neo4j_credentials, mock_neo4j_driver):
    file = io.BytesIO(b"not a csv")
    file.name = "test.txt"
    
    response = test_client.post(
        "/upload",
        files={"file": ("test.txt", file, "text/plain")}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "CSV file required" in response.json()["detail"]
