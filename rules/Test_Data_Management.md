# Test Data Management

## 1. Overview
Describe strategies for managing test data and environments in DafnckMachine v3.1.

**Example:**
- "Test data is seeded before each test run and cleaned up after."

## 2. Data Generation and Seeding
- Use factories or fixtures to generate test data
- Seed databases with known data for repeatable tests

| Method     | Tool/Library | Example Use           |
|------------|--------------|-----------------------|
| Factory    | factory-girl | Generate user objects |
| Fixture    | YAML/JSON    | Predefined datasets   |

## 3. Data Isolation and Cleanup
- Use separate databases for tests
- Clean up or reset data after each test

## 4. Environment Management
- Use containers or cloud environments for test isolation
- Document environment setup steps

## 5. Success Criteria
- Test data is reliable, isolated, and repeatable
- Environments are easy to set up and reset

## 6. Validation Checklist
- [ ] Data generation and seeding strategies are described
- [ ] Data isolation and cleanup practices are specified
- [ ] Environment management is documented
- [ ] Success criteria are included

---
*This document follows the DafnckMachine v3.1 PRD template. Update as test data management practices evolve.* 