Backend (FastAPI)

Endpoints:
- POST /upload  — multipart/form-data, file field `file` (CSV). Parses CSV and creates/updates Employee nodes and MANAGES relationships.
- GET /employee?name= — returns nodes and links for org chart starting at the named employee.

Run locally (recommended inside docker-compose):
- `docker compose up --build backend`

Environment
- NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

CSV Format:
The CSV file should contain the following columns:
- first_name: Employee's first name
- last_name: Employee's last name
- email: Employee's email address (used as unique identifier)
- phone: Employee's phone number
- address: Employee's address
- manager_name: Manager's full name (optional, for backward compatibility)
- manager_email: Manager's email address (preferred, for creating relationships)

Notes:
- The `email` field is used as the unique identifier for employees
- Relationships are created using the `manager_email` field when available
- If `manager_email` is not provided, the system will fall back to using `manager_name`
- The `manager_name` column is kept for backward compatibility but is less reliable due to potential name duplicates