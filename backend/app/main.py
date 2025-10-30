import json
import boto3
import io
import csv
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from neo4j import GraphDatabase
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
import sys

# Configure logging
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
logger.add("app.log", rotation="500 MB", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")

app = FastAPI(title="OrgChart API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def get_neo4j_credentials():
    ssm = boto3.client('ssm')
    try:
        logger.info("Attempting to retrieve Neo4j credentials from SSM")
        parameter = ssm.get_parameter(
            Name='neo4j_connection_json_string',
            WithDecryption=True
        )
        credentials = json.loads(parameter['Parameter']['Value'])
        logger.info("Successfully retrieved Neo4j credentials")
        return (
            credentials.get('NEO4J_URI'),
            credentials.get('NEO4J_USER'),
            credentials.get('NEO4J_PASSWORD')
        )
    except Exception as e:
        logger.error(f"Error reading SSM parameter: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve database credentials"
        )

class Neo4jConnection:
    def __init__(self):
        self.driver = None

    def connect(self):
        if not self.driver:
            try:
                logger.info("Initializing Neo4j connection")
                uri, user, password = get_neo4j_credentials()
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
                logger.info("Successfully connected to Neo4j")
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Database connection failed: {str(e)}"
                )

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("Neo4j connection closed")

    def get_driver(self):
        if not self.driver:
            self.connect()
        return self.driver

neo4j_conn = Neo4jConnection()

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

@app.on_event("startup")
async def startup():
    logger.info("Application starting up")
    neo4j_conn.connect()  # Verify connection at startup

@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shutting down")
    neo4j_conn.close()

@app.get('/health')
async def health_check():
    try:
        # Test database connection
        driver = neo4j_conn.get_driver()
        with driver.session() as session:
            result = session.run("RETURN 1 as n")
            result.single()
        
        # Get database info
        with driver.session() as session:
            result = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition")
            db_info = result.single()
            
        return {
            "status": "healthy",
            "database": {
                "connected": True,
                "name": db_info["name"],
                "version": db_info["versions"][0],
                "edition": db_info["edition"]
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {str(e)}"
        )

@app.post('/upload')
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        logger.warning(f"Invalid file type attempted: {file.filename}")
        raise HTTPException(status_code=400, detail='CSV file required')
    
    try:
        content = await file.read()
        text = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(text))
        created = 0
        
        driver = neo4j_conn.get_driver()
        with driver.session() as session:
            for row in reader:
                first = row.get('First Name') or row.get('first_name') or ''
                last = row.get('Last Name') or row.get('last_name') or ''
                full = (first + ' ' + last).strip() or row.get('Full Name') or ''
                email = row.get('Email') or row.get('email') or ''
                phone = row.get('Phone') or row.get('phone') or ''
                address = row.get('Address') or row.get('address') or ''
                manager = row.get('Manager Name') or row.get('Manager') or ''
                
                logger.debug(f"Processing employee: {full}")
                
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
                
        logger.info(f"Successfully imported {created} employees from CSV")
        return {"status": "ok", "imported": created}
    
    except Exception as e:
        logger.error(f"Error processing CSV upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing upload: {str(e)}"
        )

@app.get('/employee')
def get_employee(name: str = Query(..., description='Full name of employee to search')):
    try:
        logger.info(f"Searching for employee: {name}")
        # Return nodes and links for the sub-tree under the employee
        query = (
            "MATCH p=(e:Employee {fullName: $name})-[:MANAGES*0..]->(sub) "
            "WITH COLLECT(nodes(p)) AS paths_nodes, COLLECT(relationships(p)) AS paths_rels "
            "UNWIND paths_nodes AS nds UNWIND nds AS n WITH COLLECT(DISTINCT n) AS nodes, paths_rels "
            "UNWIND paths_rels AS rls UNWIND rls AS r WITH nodes, COLLECT(DISTINCT r) AS rels "
            "RETURN nodes, rels LIMIT 1"
        )
        
        driver = neo4j_conn.get_driver()
        with driver.session() as session:
            result = session.run(query, name=name)
            record = result.single()
            
            if not record:
                logger.warning(f"No employee found with name: {name}")
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
                
            logger.info(f"Found {len(nodes)} nodes and {len(links)} relationships for {name}")
            return {'nodes': nodes, 'links': links}
            
    except Exception as e:
        logger.error(f"Error retrieving employee data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving employee data: {str(e)}"
        )

@app.get('/')
def index():
    return {'status': 'ok'}
