Backend (FastAPI)

Endpoints:
- POST /upload  — multipart/form-data, file field `file` (CSV). Parses CSV and creates/updates Employee nodes and MANAGES relationships.
- GET /employee?name= — returns nodes and links for org chart starting at the named employee.

Run locally (recommended inside docker-compose):
- `docker compose up --build backend`

Environment
- NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

