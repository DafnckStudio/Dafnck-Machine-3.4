# Development Standards and Conventions (Backend)

## 1. Overview
Define coding standards, naming conventions, and best practices for backend development in DafnckMachine v3.1.

**Example:**
- "All service classes use PascalCase, and files are named after the service."

## 2. Coding Standards
- Use modern JavaScript/TypeScript (ES6+)
- Enforce code style with ESLint and Prettier
- Write modular, testable code

**Example Table:**
| Standard         | Rule/Tool         | Example                        |
|-----------------|-------------------|--------------------------------|
| Service Naming  | PascalCase        | UserService.ts                 |
| File Naming     | kebab-case        | user-service.ts                |
| Linting         | ESLint, Prettier  | Consistent formatting          |

## 3. Naming Conventions
- Classes/Services: PascalCase (e.g., AuthService)
- Variables: camelCase (e.g., userId)
- Constants: UPPER_SNAKE_CASE (e.g., JWT_SECRET)

## 4. Best Practices
- Keep functions small and focused
- Use dependency injection where appropriate
- Document APIs and services with JSDoc or similar
- Avoid hardcoding configuration; use environment variables

## 5. Code Review Process
- All code changes require peer review
- Use pull requests with clear descriptions
- Address all review comments before merging

## 6. Success Criteria
- Codebase is consistent, readable, and maintainable
- All team members follow the same standards

## 7. Validation Checklist
- [ ] Coding standards are defined
- [ ] Naming conventions are specified
- [ ] Best practices are documented
- [ ] Code review process is described

---
*This document follows the DafnckMachine v3.1 PRD template. Update as backend development standards or conventions evolve.* 