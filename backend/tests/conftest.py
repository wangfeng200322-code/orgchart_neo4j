import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
from unittest.mock import patch, MagicMock

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_neo4j_credentials():
    credentials = {
        "NEO4J_URI": "neo4j+s://test.databases.neo4j.io:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "test-password"
    }
    
    with patch('boto3.client') as mock_boto3:
        mock_ssm = MagicMock()
        mock_boto3.return_value = mock_ssm
        mock_ssm.get_parameter.return_value = {
            'Parameter': {
                'Value': json.dumps(credentials)
            }
        }
        yield credentials

@pytest.fixture
def mock_neo4j_driver():
    with patch('neo4j.GraphDatabase.driver') as mock_driver:
        mock_session = MagicMock()
        mock_driver.return_value.session.return_value = mock_session
        mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
        yield mock_driver, mock_session
