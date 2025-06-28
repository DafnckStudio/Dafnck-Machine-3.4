# DafnckMachine v3.1 - Step Documentation Index

## Overview
This directory contains step-by-step documentation for the DafnckMachine v3.1 workflow, organized sequentially and synchronized with the system's JSON configuration files.

## Documentation Structure

### Phase 0: Project Setup
- **[00_Project_Initialization.md](./00_Project_Initialization.md)** - `PRJ-INIT-001`
  - Agent: `@initialization-agent`
  - Duration: ~30 minutes
  - Status: 📝 *Ready for content*

### Phase 1: Initial User Input & Project Inception  
- **[01_User_Briefing.md](./01_User_Briefing.md)** - `USR-BRIEF-002`
  - Agent: `@elicitation-agent` 
  - Duration: ~45 minutes
  - Status: ✅ *Complete* - Updated with new template structure and JSON synchronization

### Phase 2: Discovery & Strategy
- **[02_Problem_Validation.md](./02_Problem_Validation.md)** - `MKT-DISC-003`
  - Agent: `@discovery-agent`
  - Duration: ~60 minutes  
  - Status: 📝 *Ready for content*

- **[03_Market_Research.md](./03_Market_Research.md)** - `MKT-RES-004`
  - Agent: `@discovery-agent`
  - Duration: ~90 minutes
  - Status: 📝 *Ready for content*

- **[04_Business_Strategy.md](./04_Business_Strategy.md)** - `BIZ-STRAT-005`
  - Agent: `@discovery-agent`
  - Duration: ~75 minutes
  - Status: 📝 *Ready for content*

### Phase 3: Product Definition & Design
- **[05_PRD_Generator.md](./05_PRD_Generator.md)** - `PRD-GEN-006`
  - Agent: `@product-agent`
  - Duration: ~120 minutes
  - Status: 📝 *Ready for content*

- **[06_Feature_Prioritization.md](./06_Feature_Prioritization.md)** - `FEAT-PRIOR-007`
  - Agent: `@product-agent`
  - Duration: ~60 minutes
  - Status: 📝 *Ready for content*

- **[07_User_Experience_Design.md](./07_User_Experience_Design.md)** - `UX-DES-008`
  - Agent: `@product-agent`
  - Duration: ~90 minutes
  - Status: 📝 *Ready for content*

- **[08_User_Interface_Design.md](./08_User_Interface_Design.md)** - `UI-DES-009`
  - Agent: `@technical-agent`
  - Duration: ~120 minutes
  - Status: 📝 *Ready for content*

- **[09_Technical_Architecture.md](./09_Technical_Architecture.md)** - `TECH-ARCH-010`
  - Agent: `@technical-agent`
  - Duration: ~90 minutes
  - Status: 📝 *Ready for content*

- **[10_Framework_Selection.md](./10_Framework_Selection.md)** - `FRAME-SEL-011`
  - Agent: `@technical-agent`
  - Duration: ~60 minutes
  - Status: 📝 *Ready for content*

## How to Use This Documentation

### 1. Template-Based Creation
Each step documentation should be created using the **Template-Step-Structure.md** as the foundation:
```
01_Machine/04_Documentation/01_System/Template-Step-Structure.md
```

### 2. JSON Synchronization
All step documentation must align with:
- **DNA.json** - Agent registry and step definitions
- **Step.json** - System status and validation
- **workflow_state.json** - Current position and progress tracking

### 3. Agent Integration
Each step includes:
- Primary agent assignment from the 67 available agents
- Specific agent prompts and instructions
- Supporting agent coordination
- Agent capability validation

### 4. Documentation Workflow
1. Copy `Template-Step-Structure.md` 
2. Fill in step-specific information
3. Map to JSON configuration files
4. Assign appropriate agents
5. Define task breakdown using the new hierarchical format
6. Create agent prompts and success criteria

## Status Legend
- 📝 *Ready for content* - Template structure ready, awaiting step-specific content
- ✏️ *In progress* - Currently being developed
- ✅ *Complete* - Fully documented and validated
- 🔄 *Under review* - Content complete, pending validation

## Next Steps
1. Select a step to document (recommend starting with 00_Project_Initialization)
2. Use Template-Step-Structure.md as your guide
3. Fill in step-specific content following the new hierarchical task format
4. Validate agent assignments against the agent registry
5. Test integration with JSON configuration files

---
**Last Updated**: 2025-01-27  
**Template Version**: 1.0.0  
**Synchronization Status**: ✅ Aligned with DNA.json, Step.json, workflow_state.json 