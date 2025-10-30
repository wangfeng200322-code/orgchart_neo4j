import pytest
from fastapi import status

def test_health_check_success(test_client, mock_neo4j_credentials, mock_neo4j_driver):
    mock_driver, mock_session = mock_neo4j_driver
    
    # Mock Neo4j version query
    mock_session.run.return_value.single.return_value = {
        "name": "neo4j",
        "versions": ["5.7.0"],
        "edition": "aura"
    }
    
    response = test_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"]["connected"] == True
    assert data["database"]["name"] == "neo4j"
    assert data["database"]["version"] == "5.7.0"
    assert data["database"]["edition"] == "aura"

def test_health_check_db_failure(test_client, mock_neo4j_credentials, mock_neo4j_driver):
    mock_driver, mock_session = mock_neo4j_driver
    mock_session.run.side_effect = Exception("Database connection failed")
    
    response = test_client.get("/health")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Database connection failed" in response.json()["detail"]
