# Integration Testing Guidelines

## 1. Overview
Describe the approaches, tools, and best practices for integration testing in DafnckMachine v3.1.

**Example:**
- "Integration tests verify interactions between modules and with the database using Supertest."

## 2. Tools and Frameworks
- List recommended tools (e.g., Supertest, Postman, Testcontainers).

| Tool        | Purpose                |
|-------------|------------------------|
| Supertest   | API integration tests  |
| Testcontainers | DB/service mocking  |

## 3. Test Scenarios and Conventions
- Test API endpoints, DB interactions, and service integrations
- Use realistic data and environment

**Example Scenario:**
- "POST /api/v1/users creates a new user and returns 201."

## 4. Data Management
- Use test databases or containers
- Clean up data after tests

## 5. Success Criteria
- All critical integrations are tested
- Tests are reliable and reproducible

## 6. Validation Checklist
- [ ] Tools and frameworks are listed
- [ ] Test scenarios and conventions are described
- [ ] Example scenario is included
- [ ] Data management practices are specified
- [ ] Success criteria are documented

---
*This document follows the DafnckMachine v3.1 PRD template. Update as integration testing practices evolve.* 