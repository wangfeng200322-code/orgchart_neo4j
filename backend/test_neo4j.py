#!/usr/bin/env python3
"""
Simple Neo4j test script to query employee data directly.
This script helps debug issues with the /employee API endpoint.
"""

import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

def get_driver():
    """Create and return a Neo4j driver instance."""
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'password')
    
    print(f"Connecting to Neo4j at {uri}")
    return GraphDatabase.driver(uri, auth=(user, password))

def test_simple_queries(driver):
    """Run simple queries to check data in the database."""
    with driver.session() as session:
        # Test 1: Count total employees
        print("\n=== Test 1: Counting total employees ===")
        result = session.run("MATCH (e:Employee) RETURN count(e) AS count")
        count = result.single()["count"]
        print(f"Total employees in database: {count}")
        
        # Test 2: List all employees with their names
        print("\n=== Test 2: Listing all employees ===")
        result = session.run("MATCH (e:Employee) RETURN e.fullName AS name LIMIT 10")
        employees = list(result)
        if employees:
            for record in employees:
                print(f"Employee: {record['name']}")
        else:
            print("No employees found!")
            
        # Test 3: Check if a specific employee exists
        print("\n=== Test 3: Checking for specific employee ===")
        employee_name = input("Enter employee name to search for (or press Enter to skip): ").strip()
        if employee_name:
            result = session.run(
                "MATCH (e:Employee {fullName: $name}) RETURN e",
                name=employee_name
            )
            employee = result.single()
            if employee:
                node = employee["e"]
                print(f"Found employee:")
                print(f"  ID: {node.id}")
                print(f"  Full Name: {node.get('fullName')}")
                print(f"  First Name: {node.get('firstName')}")
                print(f"  Last Name: {node.get('lastName')}")
                print(f"  Email: {node.get('email')}")
            else:
                print(f"No employee found with name '{employee_name}'")
                
                # Try a partial match
                result = session.run(
                    "MATCH (e:Employee) WHERE e.fullName CONTAINS $name RETURN e.fullName AS name LIMIT 5",
                    name=employee_name
                )
                matches = list(result)
                if matches:
                    print(f"Did you mean one of these?")
                    for match in matches:
                        print(f"  - {match['name']}")

def main():
    """Main function to run the test."""
    try:
        # Ensure we're in the right directory
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        if os.path.exists(backend_dir):
            os.chdir(backend_dir)
            load_dotenv()
        
        driver = get_driver()
        
        # Test connectivity
        with driver.session() as session:
            session.run("RETURN 1")
        print("Successfully connected to Neo4j!")
        
        # Run tests
        test_simple_queries(driver)
        
        driver.close()
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()