import json
import boto3
import io
import csv
import os
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, status, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from neo4j import GraphDatabase
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
import sys

# Configure logging
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
logger.add("app.log", rotation="500 MB", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up")
    neo4j_conn.connect()  # Verify connection at startup
    yield
    # Shutdown
    logger.info("Application shutting down")
    neo4j_conn.close()

app = FastAPI(
    title="OrgChart API",
    description="API for managing organizational chart data using Neo4j",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "health", "description": "Health check endpoints"},
        {"name": "employees", "description": "Employee data management endpoints"},
    ],
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str = Field(..., description="Current health status of the API", json_schema_extra={"example": "healthy"})
    database: dict = Field(..., description="Neo4j database connection details", json_schema_extra={"example": {
        "connected": True,
        "name": "neo4j",
        "version": "5.7.0",
        "edition": "aura"
    }})

class UploadResponse(BaseModel):
    status: str = Field(..., description="Upload operation status", json_schema_extra={"example": "ok"})
    imported: int = Field(..., description="Number of employees imported", json_schema_extra={"example": 5})

class Node(BaseModel):
    id: int = Field(..., description="Neo4j node ID", json_schema_extra={"example": 1234})
    fullName: str = Field(..., description="Employee's full name", json_schema_extra={"example": "John Doe"})
    firstName: Optional[str] = Field(None, description="Employee's first name", json_schema_extra={"example": "John"})
    lastName: Optional[str] = Field(None, description="Employee's last name", json_schema_extra={"example": "Doe"})
    email: Optional[str] = Field(None, description="Employee's email", json_schema_extra={"example": "john.doe@example.com"})
    phone: Optional[str] = Field(None, description="Employee's phone number", json_schema_extra={"example": "+1-555-123-4567"})
    address: Optional[str] = Field(None, description="Employee's address", json_schema_extra={"example": "123 Main St"})

class Link(BaseModel):
    from_id: int = Field(..., description="Source node ID", json_schema_extra={"example": 1234})
    to_id: int = Field(..., description="Target node ID", json_schema_extra={"example": 5678})
    type: str = Field(..., description="Relationship type", json_schema_extra={"example": "MANAGES"})

class EmployeeResponse(BaseModel):
    nodes: List[Node] = Field(..., description="List of employee nodes")
    links: List[Link] = Field(..., description="List of relationships between employees")

@retry(
    stop=stop_after_attempt(1),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def get_neo4j_credentials():
    # Check if we're running locally or in AWS
    env = os.getenv("ENVIRONMENT", "aws")  # Default to AWS if not specified
    
    if env == "local":
        # Use local environment variables
        logger.info("Using local environment configuration")
        return (
            os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            os.getenv('NEO4J_USER', 'neo4j'),
            os.getenv('NEO4J_PASSWORD', 'password')           
        )
    else:
        # Original AWS SSM implementation
        aws_region = os.getenv('AWS_REGION', 'eu-central-1')
        ssm = boto3.client('ssm', region_name=aws_region)
        try:
            logger.info("Attempting to retrieve Neo4j credentials from SSM")
            parameter = ssm.get_parameter(
                Name='neo4j_connection_string',
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

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True
)
def get_admin_api_key():
    # Check if we're running locally or in AWS
    env = os.getenv("ENVIRONMENT", "aws")  # Default to AWS if not specified
    
    if env == "local":
        # Use local environment variable
        logger.info("Using local API key configuration")
        return os.getenv('ADMIN_API_KEY', 'local-api-key')
    else:
        # Original AWS SSM implementation
        ssm = boto3.client('ssm')
        try:
            logger.info("Retrieving admin API key from SSM")
            parameter = ssm.get_parameter(
                Name='orgchart_admin_api_key',
                WithDecryption=True
            )
            api_key = parameter['Parameter']['Value']
            logger.info("Successfully retrieved admin API key")
            return api_key
        except Exception as e:
            logger.error(f"Error reading admin API key from SSM: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Could not retrieve admin API key"
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

async def require_admin(x_api_key: Optional[str] = Header(None, alias='X-API-Key')):
    if not x_api_key:
        logger.warning("Missing X-API-Key header for admin operation")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")
    expected = get_admin_api_key()
    if x_api_key != expected:
        logger.warning("Invalid admin API key provided")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
    return True

@app.get('/health', response_model=HealthResponse, tags=["health"],
         summary="Check API and database health",
         description="Returns the health status of the API and Neo4j database connection.")
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
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )

@app.post('/upload', response_model=UploadResponse, tags=["employees"],
          summary="Upload employee data CSV",
          description="Upload a CSV file containing employee information. The file should include columns for First Name, Last Name, Email, Phone, Address, and Manager Name.")
async def upload_csv(file: UploadFile = File(...), authorized: bool = Depends(require_admin)):
    if not file.filename.endswith('.csv'):
        logger.warning(f"Invalid file type attempted: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='CSV file required'
        )
    
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
                manager = row.get('Manager Name') or row.get('Manager') or row.get('manager_name') or ''
                manager_email = row.get('manager_email') or ''
                
                logger.debug(f"Processing employee: {full}")
                
                # Merge employee
                session.run(
                    "MERGE (e:Employee {email: $email}) "
                    "SET e.firstName = $first, e.lastName = $last, e.fullName = $full, e.phone = $phone, e.address = $address",
                    first=first, last=last, full=full, email=email if email else full, phone=phone, address=address
                )
                
                # Create manager node and relationship
                # Use manager_email if available, otherwise fall back to manager name
                if manager_email:
                    session.run(
                        "MERGE (m:Employee {email: $managerEmail}) "
                        "MERGE (e2:Employee {email: $email2}) "
                        "MERGE (m)-[:MANAGES]->(e2)",
                        managerEmail=manager_email, email2=email if email else full
                    )
                elif manager:
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing upload: {str(e)}"
        )

@app.get('/employee', response_model=EmployeeResponse, tags=["employees"],
         summary="Get employee org chart",
         description="Retrieve an employee and their reporting structure by full name.")
def get_employee(name: str = Query(..., description='Full name of employee to search')):
    try:
        logger.info(f"Searching for employee: {name}")
        # Return nodes and links for the sub-tree under the employee
        # Updated query to support any employee, whether they manage others or not
        query = (
            "MATCH (e:Employee {fullName: $name}) "
            "OPTIONAL MATCH p=(e)-[:MANAGES*0..]->(sub) "
            "WITH COLLECT(nodes(p)) AS paths_nodes, COLLECT(relationships(p)) AS paths_rels, e "
            "UNWIND paths_nodes AS nds UNWIND nds AS n WITH COLLECT(DISTINCT n) AS nodes, paths_rels, e "
            "UNWIND paths_rels AS rls UNWIND rls AS r WITH nodes, COLLECT(DISTINCT r) AS rels, e "
            "RETURN "
            "CASE WHEN size(nodes) = 0 THEN [e] ELSE nodes END AS nodes, "
            "rels "
            "LIMIT 1"
        )
        
        driver = neo4j_conn.get_driver()
        with driver.session() as session:
            result = session.run(query, name=name)
            record = result.single()
            
            if not record:
                # Let's also check what employees exist in the database to help with debugging
                logger.warning(f"No employee found with name: {name}")
                all_employees_query = "MATCH (e:Employee) RETURN e.fullName AS fullName LIMIT 10"
                all_employees_result = session.run(all_employees_query)
                employee_names = [record["fullName"] for record in all_employees_result]
                logger.info(f"Available employees: {employee_names}")
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
                links.append({
                    'from_id': start,
                    'to_id': end,
                    'type': r.type
                })
                
            logger.info(f"Found {len(nodes)} nodes and {len(links)} relationships for {name}")
            return {'nodes': nodes, 'links': links}
            
    except Exception as e:
        logger.error(f"Error retrieving employee data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving employee data: {str(e)}"
        )

@app.get('/')
def index():
    return {'status': 'ok'}
