# orgchart_neo4j

Demo project: upload organization CSV data and display an org chart using Neo4j as a graph DB, a React frontend, and a Python FastAPI backend.

This repository contains:
- `frontend/` — React (Vite) single-page app for upload and query UI.
- `backend/` — FastAPI app to parse CSV, write to Neo4j, and expose query endpoints.
- `docker-compose.yml` — to run Neo4j, backend and frontend locally or on an EC2 host.
- `terraform/` — Terraform template to provision a single EC2 instance and run the docker-compose stack (demo/test use).

Quick local run (requires Docker & docker-compose):

1. Copy example env: `cp backend/.env.example backend/.env`
2. Start services: `docker compose up --build`
3. Frontend: http://localhost:3000
4. Backend API: http://localhost:8000
5. Neo4j Browser: http://localhost:7474 (username/password from env)

Architecture
- Admin uploads CSV via frontend -> frontend POSTs to backend `/upload` -> backend parses CSV and MERGE nodes/relationships in Neo4j.
- Normal user searches employee by name -> frontend fetches `/employee?name=` -> backend queries Neo4j and returns nodes/edges for rendering an org chart.

Terraform
- `terraform/` contains a simple example that creates an EC2 instance, sets up security group rules, and runs a user-data script which clones this repo and runs `docker compose up -d` on the instance.

Notes
- This repository provides a minimal, demo-friendly skeleton. For production deployments consider using ECS/Fargate, managed databases, and secure secret management.

Next steps I can do for you:
- Expand the frontend UI with a nicer org-chart library.
- Add GitHub Actions to build and test the backend and frontend.
- Harden Terraform to use proper state backends and modular design.

---

Created by automation — adjust and extend as needed.