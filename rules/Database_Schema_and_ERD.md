# Database Schema and ERD

## 1. Overview
Describe the database structure, main entities, and relationships for DafnckMachine v3.1.

**Example:**
- "The system uses PostgreSQL with tables for users, tasks, agents, and logs."

## 2. Entity-Relationship Diagram (ERD)
- Include an ERD (as ASCII, UML, or reference to diagram file).

**Example (ASCII):**
```
[User]---<owns>---[Task]
  |                 |
<created_by>     <assigned_to>
  |                 |
[Agent]         [Log]
```

## 3. Table Definitions
- List main tables, columns, and types.

| Table  | Column     | Type      | Description         |
|--------|------------|-----------|---------------------|
| users  | id         | UUID      | Primary key         |
| users  | email      | String    | User email          |
| tasks  | id         | UUID      | Primary key         |
| tasks  | title      | String    | Task title          |

## 4. Migration Strategy
- Describe how schema changes are managed (e.g., migrations, versioning).

## 5. Success Criteria
- ERD and table definitions are clear and up-to-date
- Migration strategy is documented

## 6. Validation Checklist
- [ ] ERD is included
- [ ] Table definitions are present
- [ ] Migration strategy is described
- [ ] Success criteria are specified

---
*This document follows the DafnckMachine v3.1 PRD template. Update as schema evolves.* 