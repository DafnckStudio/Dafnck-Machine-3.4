# Template Usage Guide - DafnckMachine v3.1

## Quick Start: Creating a Workflow Step

### Step 1: Copy the Template
```bash
cp "01_Machine/04_Documentation/01_System/Template-Step-Structure.md" \
   "01_Machine/04_Documentation/Doc/[##_Step_Name].md"
```

### Step 2: Fill in Metadata
Replace these placeholders in the template:

```markdown
## Workflow Metadata
- **Workflow-Step**: [Your Step Name]
- **TaskID**: [PREFIX-CATEGORY-###] (from DNA.json)
- **Step ID**: [##] (Sequential: 00, 01, 02...)
- **Version**: [X.Y.Z]
- **LastUpdate**: [YYYY-MM-DD]
- **Previous Step**: [Previous step or "User initiates"]
- **Next Step**: [Next step filename.md]
```

### Step 3: Define Mission & Description
- **Mission Statement**: 1-2 sentences describing the primary objective
- **Description**: Detailed explanation of purpose, context, and importance
- **Result We Want**: Specific, measurable outcomes

### Step 4: Select Agents
Use the Agent Selection Decision Tree from the template:

1. **Coordination/orchestration?** → Use orchestrator agents
2. **Project initiation/planning?** → Use project-initiator, task-planning agents
3. **Requirements/analysis?** → Use elicitation, nlu-processor agents
4. **Development/technical?** → Use coding, system-architect agents
5. **Testing/QA?** → Use test-orchestrator, functional-tester agents
6. **Design/UX?** → Use ux-designer, ui-designer agents
7. **Content/documentation?** → Use content-creator, technical-writer agents
8. **Data/analytics?** → Use analytics-setup, data-analyst agents
9. **Business/growth?** → Use growth-hacking-idea, campaign-manager agents

### Step 5: Create Task Breakdown
Use the new hierarchical format:

```markdown
[] Phase-[##] ([Phase Name] - Strategic Level)
├── [] Task-01 ([Primary Task Name] - Tactical Level)
│   ├── [] Subtask-01 ([Subtask Description] - Operational Level)
│   │   ├── [] 01 Agent Assignment: `@agent-name` - [capability]
│   │   ├── [] 02 Agent Prompt: "[Detailed instructions]"
│   │   ├── [] 03 Documentation Links: [References]
│   │   ├── [] 04 Success Criteria: [Measurable outcomes]
│   │   └── [] 05 Integration Points: [Connections]
```

### Step 6: Validate JSON Synchronization

**Check DNA.json alignment:**
- Agent exists in `agentRegistry[]`
- Step defined in `step_definitions`
- Phase mapping correct

**Check workflow_state.json mapping:**
- Current position tracking
- Progress calculation
- Agent assignment

**Check Step.json integration:**
- Validation tracking
- System health monitoring

## Template Sections Checklist

### Required Sections
- [ ] Workflow Metadata
- [ ] Mission Statement  
- [ ] Description
- [ ] Result We Want
- [ ] Add to Brain
- [ ] Documentation & Templates
- [ ] Super-Prompt
- [ ] MCP Tools Required
- [ ] Agent Selection & Assignment
- [ ] Task Breakdown (new hierarchical format)
- [ ] Success Criteria
- [ ] Quality Gates
- [ ] Output Artifacts

### Optional Sections (add as needed)
- [ ] Risk Mitigation
- [ ] Dependencies
- [ ] Performance Metrics
- [ ] Rollback Procedures
- [ ] Integration Points

## Agent Assignment Best Practices

### 1. Primary Agent Selection
- Review agent's `roleDefinition` in JSON file
- Check `whenToUse` criteria match your step
- Validate required `groups` permissions
- Ensure `inputSpec` matches available inputs

### 2. Supporting Agents
- Check `interactsWith` arrays for compatibility
- Plan agent interaction sequence
- Define handoff points between agents

### 3. Agent Prompts
- Include role definition
- Provide specific context
- Define expected deliverables
- Set quality standards
- Add conditional logic for different scenarios

## Common Patterns

### Orchestration Steps
- Primary: `@uber-orchestrator-agent` or `@development-orchestrator-agent`
- Supporting: Domain-specific agents
- Focus: Coordination and delegation

### Technical Implementation Steps  
- Primary: `@coding-agent` or `@system-architect-agent`
- Supporting: `@code-reviewer-agent`, `@security-auditor-agent`
- Focus: Implementation and quality

### Research/Analysis Steps
- Primary: `@market-research-agent` or `@deep-research-agent`
- Supporting: `@analytics-setup-agent`, `@data-analyst-agent`
- Focus: Information gathering and insights

### Design Steps
- Primary: `@ui-designer-agent` or `@ux-researcher-agent`
- Supporting: `@design-system-agent`, `@design-qa-analyst`
- Focus: User experience and visual design

## Validation Checklist

Before finalizing your step documentation:

- [ ] All placeholders replaced with actual content
- [ ] Agent assignments validated against agent registry
- [ ] Task breakdown follows new hierarchical format
- [ ] JSON synchronization mappings correct
- [ ] Success criteria are measurable
- [ ] Integration points clearly defined
- [ ] Agent prompts are specific and actionable
- [ ] Documentation links reference actual files
- [ ] Quality gates have clear acceptance criteria

## Example: Quick Step Creation

```markdown
## Workflow Metadata
- **Workflow-Step**: Problem Validation
- **TaskID**: MKT-DISC-003
- **Step ID**: 02
- **Version**: 1.0.0
- **LastUpdate**: 2025-01-27
- **Previous Step**: 01_User_Briefing.md
- **Next Step**: 03_Market_Research.md

## Mission Statement
Validate the identified problem through research and stakeholder feedback to ensure we're solving a real, significant issue.

## Primary Responsible Agent
**@market-research-agent** - Conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends.
```

---
**Template Version**: 1.0.0  
**Last Updated**: 2025-01-27  
**Status**: Ready for use 