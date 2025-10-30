# orgchart_neo4j

Demo project: upload organization CSV data and display an org chart using Neo4j AuraDB, a React frontend, and a Python FastAPI backend.

This repository contains:
- `frontend/` — React (Vite) single-page app for upload and query UI.
- `backend/` — FastAPI app to parse CSV, write to Neo4j, and expose query endpoints.
- `docker-compose.yml` — to run backend and frontend locally.
- `terraform/` — Terraform template to provision a t2.micro EC2 instance running the frontend and backend containers.

## Prerequisites

### Neo4j AuraDB Setup
1. Create a free Neo4j AuraDB instance
2. Note the connection details (URI, username, password)
3. Create an AWS Systems Manager Parameter Store parameter named `neo4j_connection_json_string` with the following JSON structure:
```json
{
    "NEO4J_URI": "neo4j+s://your-instance.databases.neo4j.io:7687",
    "NEO4J_USER": "neo4j",
    "NEO4J_PASSWORD": "your-password"
}
```

### Local Development
1. Create the SSM parameter as described above
2. Start services: `docker compose up --build`
3. Frontend: http://localhost:3000
4. Backend API: http://localhost:8000

### API Endpoints

#### Health Check
- GET `/health`
- Returns database connection status and version information
- Use this to verify Neo4j connectivity

#### Upload Organization Data
- POST `/upload`
- Accepts CSV file with columns:
  - First Name
  - Last Name
  - Email
  - Phone
  - Address
  - Manager Name

#### Query Employee
- GET `/employee?name=<full name>`
- Returns employee and their reporting structure

### AWS Deployment
1. Create the SSM parameter as described above
2. Configure AWS credentials
3. In `terraform/`:
   ```bash
   terraform init
   terraform apply -var="key_name=your-key-pair-name"
   ```
4. The EC2 instance will automatically:
   - Clone this repository
   - Start the frontend and backend containers
   - Backend will read Neo4j credentials from SSM parameter

## Architecture
- Admin uploads CSV via frontend -> frontend POSTs to backend `/upload` -> backend parses CSV and MERGE nodes/relationships in Neo4j AuraDB.
- Normal user searches employee by name -> frontend fetches `/employee?name=` -> backend queries Neo4j and returns nodes/edges for rendering an org chart.

## Features

### Backend Improvements
1. **Retry Logic**
   - Automatic retries for SSM parameter retrieval
   - Exponential backoff between attempts
   - Maximum of 3 retry attempts

2. **Health Monitoring**
   - `/health` endpoint for monitoring
   - Checks Neo4j connection
   - Returns database version and status

3. **Logging**
   - Structured logging with timestamps
   - Log rotation (500 MB files)
   - Console and file output
   - Error tracking for all operations

Notes
- The EC2 instance is t2.micro as requested. This is sufficient for the frontend and backend containers.
- Neo4j runs as a managed service in AuraDB.
- The backend reads Neo4j credentials from AWS Systems Manager Parameter Store.
- The parameter `neo4j_connection_json_string` must be created manually before deployment.
