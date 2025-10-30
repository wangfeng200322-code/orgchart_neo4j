# Backend Tests

This directory contains integration tests for the backend API. Tests use pytest and cover the main functionality including health checks and employee data management.

## Running Tests

From the backend directory:
```bash
pytest -v tests/
```

## Test Coverage

1. Health Check (`test_health.py`)
   - Successful health check
   - Database connection failure

2. Employee Management (`test_employees.py`)
   - Get employee org chart
   - Employee not found
   - CSV upload success
   - Invalid file upload

## Mocking

Tests use pytest fixtures to mock:
- AWS SSM Parameter Store
- Neo4j driver and session
- Database queries and responses
