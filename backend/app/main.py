import os
import csv
import io
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from neo4j import GraphDatabase

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'letmein')

app = FastAPI(title="OrgChart API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

class NodeOut(BaseModel):
    id: int
    fullName: str
    firstName: str | None = None
    lastName: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None

class LinkOut(BaseModel):
    from_id: int
    to_id: int

@app.on_event("shutdown")
def shutdown():
    driver.close()

@app.post('/upload')
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail='CSV file required')
    content = await file.read()
    text = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))
    created = 0
    with driver.session() as session:
        for row in reader:
            first = row.get('First Name') or row.get('first_name') or ''
            last = row.get('Last Name') or row.get('last_name') or ''
            full = (first + ' ' + last).strip() or row.get('Full Name') or ''
            email = row.get('Email') or row.get('email') or ''
            phone = row.get('Phone') or row.get('phone') or ''
            address = row.get('Address') or row.get('address') or ''
            manager = row.get('Manager Name') or row.get('Manager') or ''
            # Merge employee
            session.run(
                "MERGE (e:Employee {email: $email}) "
                "SET e.firstName = $first, e.lastName = $last, e.fullName = $full, e.phone = $phone, e.address = $address",
                first=first, last=last, full=full, email=email if email else full, phone=phone, address=address
            )
            # Create manager node and relationship
            if manager:
                session.run(
                    "MERGE (m:Employee {fullName: $managerFull}) "
                    "MERGE (e2:Employee {email: $email2}) "
                    "MERGE (m)-[:MANAGES]->(e2)",
                    managerFull=manager, email2=email if email else full
                )
            created += 1
    return {"status": "ok", "imported": created}

@app.get('/employee')
def get_employee(name: str = Query(..., description='Full name of employee to search')):
    # Return nodes and links for the sub-tree under the employee
    query = (
        "MATCH p=(e:Employee {fullName: $name})-[:MANAGES*0..]->(sub) "
        "WITH COLLECT(nodes(p)) AS paths_nodes, COLLECT(relationships(p)) AS paths_rels "
        "UNWIND paths_nodes AS nds UNWIND nds AS n WITH COLLECT(DISTINCT n) AS nodes, paths_rels "
        "UNWIND paths_rels AS rls UNWIND rls AS r WITH nodes, COLLECT(DISTINCT r) AS rels "
        "RETURN nodes, rels LIMIT 1"
    )
    with driver.session() as session:
        result = session.run(query, name=name)
        record = result.single()
        if not record:
            return {"nodes": [], "links": []}
        nodes_raw = record['nodes'] or []
        rels_raw = record['rels'] or []
        nodes = []
        id_map = {}
        for n in nodes_raw:
            nid = n.id
            id_map[nid] = len(nodes)
            nodes.append({
                'id': nid,
                'fullName': n.get('fullName'),
                'firstName': n.get('firstName'),
                'lastName': n.get('lastName'),
                'email': n.get('email'),
                'phone': n.get('phone'),
                'address': n.get('address')
            })
        links = []
        for r in rels_raw:
            start = r.start_node.id
            end = r.end_node.id
            links.append({'from': start, 'to': end, 'type': r.type})
        return {'nodes': nodes, 'links': links}

@app.get('/')
def index():
    return {'status': 'ok'}
