---
phase: P03
step: S10
task: T07
task_id: P03-S10-T07
title: Performance and Monitoring Framework Selection
<<<<<<< HEAD
agent: ["@performance-optimization-agent", "@system-architect-agent", "@development-orchestrator-agent", "@technology-advisor-agent", "@security-auditor-agent"]
=======
>>>>>>> 8f6410b869c68e2dec6a6798282a4437e78b5f85
previous_task: P03-S10-T06
next_task: P03-S10-T08
version: 3.1.0
source: Step.json
<<<<<<< HEAD
orchestrator: "@uber-orchestrator-agent"
---

# Super Prompt
@performance-optimization-agent (lead), with support from @system-architect-agent, @development-orchestrator-agent, @technology-advisor-agent, and @security-auditor-agent: Select and document performance monitoring, optimization, and caching frameworks for DafnckMachine v3.1. Document all findings, configurations, and selection decisions with clear rationale and evidence. Output all specifications, configuration guides, and analysis to the required files. Communicate blockers or gaps in requirements immediately.

1. **Documentation Reference**
   - Documentation in  `01_Machine/04_Documentation/Doc/Phase_3/10_Detailed_Framework_Selection/`

2. **Collect Data/Input**
   - Gather system health, performance, and scalability requirements from previous steps and team input.
   - Collect preferences and constraints regarding monitoring, optimization, and caching tools.

3. **Save Output**
   - 01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Performance_Monitoring_Tools.md (Markdown)
   - 01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Monitoring_Framework_Specs.json (JSON, schema: {"tools": [string], "metrics": [string], "config": object, "alerting": [string]})
   - 01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Optimization_Framework_Selection.md (Markdown)
   - 01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Caching_Solutions_Analysis.json (JSON, schema: {"solution": string, "strategy": string, "config": object})

4. **Update Progress**
   - Mark this task as done in Step.json and DNA.json when all outputs are complete and reviewed.

5. **Self-Check**
   - [ ] Are all required output files present and complete?
   - [ ] Is the monitoring and optimization rationale clearly documented?
   - [ ] Are configuration guides and analysis justified and reproducible?
   - [ ] Have all blockers and requirements been communicated and addressed? 
=======
agent: "@performance-optimization-agent"
orchestrator: "@uber-orchestrator-agent"
---
## Output Artifacts Checklist
- [ ] 01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Performance_Monitoring_Tools.md — Performance_Monitoring_Tools.md: Performance_Monitoring_Tools.md (missing)
- [ ] 01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Monitoring_Framework_Specs.json — Monitoring_Framework_Specs.json: Monitoring_Framework_Specs.json (missing)
- [ ] 01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Optimization_Framework_Selection.md — Optimization_Framework_Selection.md: Optimization_Framework_Selection.md (missing)
- [ ] 01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Caching_Solutions_Analysis.json — Caching_Solutions_Analysis.json: Caching_Solutions_Analysis.json (missing)

## Mission Statement
Select frameworks and tools for performance monitoring, optimization, and caching for DafnckMachine v3.1, ensuring system health, responsiveness, and resource efficiency.

## Description
This task selects and documents application performance monitoring, logging, metrics, alerting, optimization, and caching frameworks. It ensures the system is observable, performant, and scalable.

## Super-Prompt
You are @performance-optimization-agent. Your mission is to select and document performance monitoring, optimization, and caching frameworks for DafnckMachine v3.1. Document all findings, configurations, and selection decisions with clear rationale and evidence.

## MCP Tools Required
- edit_file

## Result We Want
- Comprehensive monitoring and optimization framework selection
- Documented configuration and recommendations
- Artifacts: Performance_Monitoring_Tools.md, Monitoring_Framework_Specs.json, Optimization_Framework_Selection.md, Caching_Solutions_Analysis.json

## Add to Brain
- Performance and monitoring framework selection rationale

## Documentation & Templates
- [Performance_Monitoring_Tools.md](mdc:01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Performance_Monitoring_Tools.md)
- [Monitoring_Framework_Specs.json](mdc:01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Monitoring_Framework_Specs.json)
- [Optimization_Framework_Selection.md](mdc:01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Optimization_Framework_Selection.md)
- [Caching_Solutions_Analysis.json](mdc:01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Caching_Solutions_Analysis.json)

## Primary Responsible Agent
@performance-optimization-agent

## Supporting Agents
- @system-architect-agent
- @development-orchestrator-agent
- @technology-advisor-agent
- @security-auditor-agent

## Agent Selection Criteria
@performance-optimization-agent is selected for expertise in performance and monitoring frameworks. Supporting agents provide architectural, workflow, technology, and security perspectives.

## Tasks (Summary)
- Select and document performance monitoring tools
- Select and document optimization and caching frameworks
- Document findings and configurations

## Subtasks (Detailed)
### Subtask 1: Performance Monitoring Tools
- **ID**: P03-T07-S01
- **Description**: Select application performance monitoring, logging, metrics, alerting, and dashboard tools.
- **Agent**: @performance-optimization-agent
- **Documentation Links**: Performance_Monitoring_Tools.md, Monitoring_Framework_Specs.json
- **Steps**:
  1. Select and document performance monitoring tools (edit_file)
- **Success Criteria**: Comprehensive monitoring tool selection documented.

### Subtask 2: Optimization & Caching Frameworks
- **ID**: P03-T07-S02
- **Description**: Select optimization frameworks, caching solutions, CDNs, and compression tools.
- **Agent**: @performance-optimization-agent
- **Documentation Links**: Optimization_Framework_Selection.md, Caching_Solutions_Analysis.json
- **Steps**:
  1. Select and document optimization and caching frameworks (edit_file)
- **Success Criteria**: Optimal optimization and caching framework selection documented.

## Rollback Procedures
- If selected frameworks are found unsuitable, re-evaluate and update selection.
- Escalate to @team-lead if repeated failures occur.

## Integration Points
- Performance and monitoring framework selection guide system health and optimization.

## Quality Gates
- Comprehensive comparison and rationale for selections
- System health and scalability considered

## Success Criteria
- [ ] Comprehensive monitoring tool selection documented
- [ ] Optimization and caching framework selection documented
- [ ] Artifacts referenced in all performance-related development tasks

## Risk Mitigation
- Review with supporting agents for completeness
- Update selection as new performance requirements emerge

## Output Artifacts
- [Performance_Monitoring_Tools.md](mdc:01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Performance_Monitoring_Tools.md)
- [Monitoring_Framework_Specs.json](mdc:01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Monitoring_Framework_Specs.json)
- [Optimization_Framework_Selection.md](mdc:01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Optimization_Framework_Selection.md)
- [Caching_Solutions_Analysis.json](mdc:01_Machine/04_Documentation/vision/Phase_3/10_Detailed_Framework_Selection/Caching_Solutions_Analysis.json)

## Next Action
Initiate performance and monitoring framework selection with @performance-optimization-agent.

## Post-Completion Action
Update @Step.json and @DNA.json to reflect task completion and propagate configuration to subsequent tasks. 
>>>>>>> 8f6410b869c68e2dec6a6798282a4437e78b5f85
