# Unit Testing Guidelines

## 1. Overview
Describe the standards, tools, and best practices for unit testing in DafnckMachine v3.1.

**Example:**
- "All core functions and modules are covered by Jest unit tests."

## 2. Tools and Frameworks
- List recommended tools (e.g., Jest, Mocha, Vitest).

| Tool   | Purpose         |
|--------|----------------|
| Jest   | Unit testing   |
| ts-mock| Mocking        |

## 3. Test Structure and Conventions
- Use descriptive test names
- Arrange-Act-Assert pattern
- Isolate units (no external dependencies)

**Example Test Case:**
```js
test('adds two numbers', () => {
  expect(add(2, 3)).toBe(5);
});
```

## 4. Coverage and Quality
- Aim for 80%+ coverage of core logic
- Review tests in code review

## 5. Success Criteria
- All core logic is covered by unit tests
- Tests are reliable and easy to maintain

## 6. Validation Checklist
- [ ] Tools and frameworks are listed
- [ ] Test structure and conventions are described
- [ ] Example test case is included
- [ ] Coverage and quality goals are specified
- [ ] Success criteria are documented

---
*This document follows the DafnckMachine v3.1 PRD template. Update as unit testing practices evolve.* 