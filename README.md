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

Create admin API key parameter in SSM (SecureString):
```powershell
aws ssm put-parameter --name "orgchart_admin_api_key" --value "<strong-random-key>" --type "SecureString" --region eu-central-1
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
- POST `/upload` — requires admin API key in header `X-API-Key`
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

### CI
A GitHub Actions workflow is included at `.github/workflows/ci.yml`. It runs backend tests and builds the frontend on every push to `main` and on pull requests.

### Key rotation
Two helper scripts are provided in `scripts/`:
- `create_admin_api_key.py` — generate a new admin key and optionally store in SSM
- `rotate_admin_api_key.py` — rotate the key (overwrite existing SSM parameter)

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

4. **Admin API key protection**
   - Upload endpoint requires header `X-API-Key` matching the SSM SecureString `orgchart_admin_api_key`.

Notes
- The EC2 instance is t2.micro as requested. This is sufficient for the frontend and backend containers.
- Neo4j runs as a managed service in AuraDB.
- The backend reads Neo4j credentials and admin API key from AWS Systems Manager Parameter Store.
- The parameters must be created manually before deployment.
