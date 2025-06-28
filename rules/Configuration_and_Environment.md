# Configuration and Environment

## 1. Overview
Describe configuration files, environment variables, and deployment settings for DafnckMachine v3.1.

**Example:**
- "All secrets are stored in .env files and injected at runtime."

## 2. Configuration Files
- List and describe key configuration files (e.g., .env, config.json).

| File         | Purpose                  |
|--------------|--------------------------|
| .env         | Environment variables    |
| config.json  | App configuration        |

## 3. Environment Variables
- List required and optional environment variables.

| Variable            | Example Value      | Description                |
|---------------------|-------------------|----------------------------|
| NODE_ENV            | production        | Environment mode           |
| DATABASE_URL        | postgres://...    | DB connection string       |
| JWT_SECRET          | ...               | JWT signing key            |

## 4. Deployment Settings
- Describe deployment environments (dev, staging, prod) and settings.

## 5. Success Criteria
- All config files and env vars are documented
- Deployment settings are clear

## 6. Validation Checklist
- [ ] Config files are listed
- [ ] Env variables are documented
- [ ] Deployment settings are described
- [ ] Success criteria are specified

---
*This document follows the DafnckMachine v3.1 PRD template. Update as configuration evolves.* 