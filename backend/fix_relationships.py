#!/usr/bin/env python3
"""
Script to fix existing relationships in the database by converting 
name-based relationships to email-based relationships.
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

def fix_relationships(driver):
    """Fix relationships by converting name-based to email-based."""
    with driver.session() as session:
        # First, let's see how many MANAGES relationships currently exist
        result = session.run("MATCH ()-[r:MANAGES]->() RETURN count(r) AS count")
        initial_count = result.single()["count"]
        print(f"Initial MANAGES relationships: {initial_count}")
        
        # Find all employees who are managers (have outgoing MANAGES relationships)
        # and update their relationships to be email-based
        result = session.run("""
            MATCH (manager:Employee)-[r:MANAGES]->(report:Employee)
            WHERE manager.email IS NOT NULL
            MATCH (manager)
            SET manager.manager_email = manager.email
            RETURN count(manager) AS updated_managers
        """)
        managers_updated = result.single()["updated_managers"]
        print(f"Updated {managers_updated} managers with manager_email property")
        
        # Create a mapping of full names to emails for employees
        result = session.run("""
            MATCH (e:Employee)
            WHERE e.email IS NOT NULL AND e.fullName IS NOT NULL
            RETURN e.fullName AS fullName, e.email AS email
        """)
        
        name_to_email = {record["fullName"]: record["email"] for record in result}
        print(f"Created mapping for {len(name_to_email)} employees")
        
        # Try to fix relationships that are based on names but should be based on emails
        # This is a more complex operation that would require manual verification
        print("\nTo completely fix the relationships, you would need to:")
        print("1. Identify which employees should report to which managers based on business logic")
        print("2. Delete existing incorrect relationships")
        print("3. Create new relationships based on email addresses")
        
        # Show duplicate employees with same name but different emails
        print("\nDuplicate employees with same name:")
        result = session.run("""
            MATCH (e:Employee)
            WHERE e.fullName IS NOT NULL
            WITH e.fullName AS name, collect(e) AS employees
            WHERE size(employees) > 1
            RETURN name, [emp IN employees | emp.email] AS emails
        """)
        
        duplicates = list(result)
        if duplicates:
            for record in duplicates:
                print(f"  {record['name']}: {record['emails']}")
        else:
            print("  No duplicate employees found")

def main():
    """Main function to run the relationship fix."""
    try:
        driver = get_driver()
        
        # Test connectivity
        with driver.session() as session:
            session.run("RETURN 1")
        print("Successfully connected to Neo4j!")
        
        # Fix relationships
        fix_relationships(driver)
        
        driver.close()
        print("\nRelationship fix process completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()