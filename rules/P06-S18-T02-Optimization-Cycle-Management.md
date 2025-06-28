---
Previous Task: P06-S18-T01-Feedback-Collection-Analysis-System.md
Current Task: P06-S18-T02-Optimization-Cycle-Management.md
Next Task: P06-S18-T03-Feature-Evolution-Enhancement-Planning.md
---
## Output Artifacts Checklist
- [ ] 01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Optimization_Cycle_Management.md — Optimization_Cycle_Management.md: Systematic improvement workflows and optimization processes (missing)
- [ ] 01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Feature_Evolution_Planning.md — Feature_Evolution_Planning.md: Enhancement prioritization and planning (missing)

# Workflow Metadata
- **Workflow-Step**: Continuous Improvement
- **TaskID**: P05-T02
- **Step ID**: 18
- **Version**: 3.1.0
- **LastUpdate**: 2025-01-27
- **Previous Task**: P06-S18-T01-Feedback-Collection-Analysis-System.md
- **Current Task**: P06-S18-T02-Optimization-Cycle-Management.md
- **Next Task**: P06-S18-T03-Feature-Evolution-Enhancement-Planning.md

# Mission Statement
Design and implement systematic improvement workflows and enhancement prioritization for DafnckMachine v3.1.

# Description
Establish optimization cycle management, including improvement workflow design and enhancement prioritization systems. Enable systematic, data-driven improvement cycles and resource allocation for sustainable product evolution.

# Super-Prompt
You are @knowledge-evolution-agent. Your mission is to design and implement optimization cycles and prioritization systems, ensuring continuous, data-driven improvement and enhancement management for DafnckMachine v3.1.

# MCP Tools Required
- edit_file
- file_search
- list_dir
- run_terminal_cmd
- mcp_taskmaster-ai_get_task
- mcp_taskmaster-ai_set_task_status

# Result We Want
- Systematic optimization cycle management with improvement workflows and enhancement processes

# Add to Brain
- **Optimization Cycles**: Systematic improvement workflows with performance enhancement and efficiency optimization

# Documentation & Templates
- [Optimization_Cycle_Management.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Optimization_Cycle_Management.md): Systematic improvement workflows and optimization processes
- [Feature_Evolution_Planning.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Feature_Evolution_Planning.md): Enhancement prioritization and planning

# Primary Responsible Agent
@knowledge-evolution-agent

# Supporting Agents
- @analytics-setup-agent
- @performance-optimizer-agent
- @development-orchestrator-agent

# Agent Selection Criteria
The Knowledge Evolution Agent is chosen for its expertise in improvement workflow design and optimization cycle management.

# Tasks (Summary)
- Design improvement workflows
- Implement enhancement prioritization system

# Subtasks (Detailed)
## Subtask-01: Improvement Workflow Design
- **ID**: P05-T02-S01
- **Description**: Design workflows for optimization cycles, improvement planning, and iteration management.
- **Agent**: @knowledge-evolution-agent
- **Documentation**: [Optimization_Cycle_Management.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Optimization_Cycle_Management.md)
- **Steps**:
    1. Design improvement workflows: optimization cycles, improvement planning, enhancement processes, iteration management (Tool: edit_file)
        - Success: `config/improvement_workflow.json` exists and contains `"cycleManagementActive": true`
    2. Setup improvement process (Tool: run_terminal_cmd)
        - Success: `improvement_workflow_engine` running, output contains "Improvement workflow engine initialized."
- **Final Subtask Success Criteria**: Systematic improvement workflows are designed, configured, and active.
- **Integration Points**: Enables systematic optimization and continuous enhancement across the product lifecycle.
- **Next Subtask**: P05-T02-S02

## Subtask-02: Enhancement Prioritization System
- **ID**: P05-T02-S02
- **Description**: Implement a data-driven system for prioritizing enhancements based on impact, effort, and ROI.
- **Agent**: @analytics-setup-agent
- **Documentation**: [Feature_Evolution_Planning.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Feature_Evolution_Planning.md)
- **Steps**:
    1. Implement enhancement prioritization: impact analysis, effort estimation, ROI calculation, priority scoring (Tool: edit_file)
        - Success: `config/enhancement_prioritization_config.json` exists and contains `"impactWeight": 0.4`
- **Final Subtask Success Criteria**: Enhancement prioritization system is configured and operational, providing data-driven recommendations.
- **Integration Points**: Guides improvement focus and resource allocation for subsequent development cycles (P06-S18-T03-Feature-Evolution-Enhancement-Planning.md).
- **Next Subtask**: None

# Rollback Procedures
- Revert problematic workflow or prioritization configurations
- Restore previous improvement process state if errors occur

# Integration Points
- Enables systematic optimization and prioritization for all subsequent improvement activities

# Quality Gates
- Process Efficiency: Efficient improvement workflows with optimized resource utilization
- Data Quality: Accurate prioritization and workflow configuration

# Success Criteria
- [ ] Improvement workflow is active and configured
- [ ] Enhancement prioritization system is operational

# Risk Mitigation
- Notify and continue on workflow errors
- Escalate to human on repeated prioritization failures

# Output Artifacts
- [Optimization_Cycle_Management.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Optimization_Cycle_Management.md)
- [Feature_Evolution_Planning.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Feature_Evolution_Planning.md)

# Next Action
Design improvement workflows and implement prioritization system with @knowledge-evolution-agent and @analytics-setup-agent

# Post-Completion Action
Update @Step.json and @DNA.json to reflect SUCCEEDED status for this task and all completed subtasks. 