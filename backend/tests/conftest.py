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
    
    def get_parameter_side_effect(Name, WithDecryption=True):
        if Name == 'neo4j_connection_json_string':
            return {'Parameter': {'Value': json.dumps(credentials)}}
        if Name == 'orgchart_admin_api_key':
            return {'Parameter': {'Value': 'test-admin-key'}}
        raise Exception('Parameter not found')

    with patch('boto3.client') as mock_boto3:
        mock_ssm = MagicMock()
        mock_boto3.return_value = mock_ssm
        mock_ssm.get_parameter.side_effect = get_parameter_side_effect
        yield credentials

@pytest.fixture
def mock_neo4j_driver():
    with patch('neo4j.GraphDatabase.driver') as mock_driver:
        mock_session = MagicMock()
        # Ensure session().__enter__ returns a session-like object
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_session
        mock_driver.return_value.session.return_value = mock_ctx
        yield mock_driver, mock_session
