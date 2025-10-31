// Step 1: Identify duplicate employees with the same fullName
MATCH (e:Employee)
WHERE e.fullName IS NOT NULL
WITH e.fullName AS name, collect(e) AS employees
WHERE size(employees) > 1
RETURN name, [emp IN employees | emp.email] AS emails, size(employees) AS count
ORDER BY count DESC;

// Step 2: Find which James Anderson is the manager (has outgoing MANAGES relationships)
MATCH (ja:Employee {fullName: "James Anderson"})-[r:MANAGES]->()
RETURN ja.email, count(r) AS outgoing_relationships;

// Step 3: Fix the relationships by identifying the correct manager
// First, find the James Anderson who is actually a manager (has reports)
MATCH (managerJames:Employee {fullName: "James Anderson"})-[:MANAGES]->()
WITH managerJames
// Find employees who report to any James Anderson
MATCH (anyJames:Employee {fullName: "James Anderson"})<-[r:MANAGES]-(report)
WHERE anyJames <> managerJames
// Remove incorrect relationships
MATCH (anyJames)<-[r:MANAGES]-(report)
DELETE r
// Create correct relationships to the manager James
MERGE (managerJames)<-[:MANAGES]-(report)
RETURN "Fixed relationships for James Anderson" AS result;

// Step 4: Verify the fix
MATCH (e:Employee {fullName: "James Anderson"})
OPTIONAL MATCH (e)-[out:MANAGES]->()
OPTIONAL MATCH (e)<-[in:MANAGES]-()
RETURN e.email, 
       size(collect(out)) AS outgoing_reports, 
       size(collect(in)) AS incoming_reports;

// Step 5: General approach to fix all relationships (more comprehensive)
// Add manager_email property to all employees who have an email
MATCH (e:Employee)
WHERE e.email IS NOT NULL
SET e.manager_email = e.email
RETURN count(e) AS employees_updated;

// Step 6: For future imports, use manager_email to create relationships
// This is handled in the updated Python code