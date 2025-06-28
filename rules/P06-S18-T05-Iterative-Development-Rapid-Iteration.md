---
Previous Task: P06-S18-T04-Performance-Enhancement-Optimization.md
Current Task: P06-S18-T05-Iterative-Development-Rapid-Iteration.md
Next Task: P06-S18-T06-Data-Driven-Improvement-Analytics.md
---
## Output Artifacts Checklist
- [ ] 01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Iterative_Development_Framework.md — Iterative_Development_Framework.md: Agile improvement and CI/CD (missing)
- [ ] 01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/CI_CD_Improvement_Optimization.md — CI_CD_Improvement_Optimization.md: CI/CD pipeline optimization (missing)

# Workflow Metadata
- **Workflow-Step**: Continuous Improvement
- **TaskID**: P05-T05
- **Step ID**: 18
- **Version**: 3.1.0
- **LastUpdate**: 2025-01-27
- **Previous Task**: P06-S18-T04-Performance-Enhancement-Optimization.md
- **Current Task**: P06-S18-T05-Iterative-Development-Rapid-Iteration.md
- **Next Task**: P06-S18-T06-Data-Driven-Improvement-Analytics.md

# Mission Statement
Implement agile improvement processes and optimize CI/CD for rapid iteration in DafnckMachine v3.1.

# Description
Establish agile improvement processes, iterative development cycles, and optimize CI/CD pipelines for rapid and reliable deployment of improvements.

# Super-Prompt
You are @development-orchestrator-agent. Your mission is to implement agile improvement processes and optimize CI/CD for rapid iteration and continuous delivery in DafnckMachine v3.1.

# MCP Tools Required
- edit_file
- file_search
- list_dir
- run_terminal_cmd
- mcp_taskmaster-ai_get_task
- mcp_taskmaster-ai_set_task_status

# Result We Want
- Iterative development processes with agile improvement cycles and rapid iteration capabilities

# Add to Brain
- **Iterative Development**: Agile improvement processes with rapid iteration and continuous delivery

# Documentation & Templates
- [Iterative_Development_Framework.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Iterative_Development_Framework.md): Agile improvement and CI/CD
- [CI_CD_Improvement_Optimization.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/CI_CD_Improvement_Optimization.md): CI/CD pipeline optimization

# Primary Responsible Agent
@development-orchestrator-agent

# Supporting Agents
- @development-orchestrator-agent

# Agent Selection Criteria
The Development Orchestrator Agent is chosen for its expertise in agile improvement, iterative development, and CI/CD optimization.

# Tasks (Summary)
- Implement agile improvement processes
- Optimize CI/CD pipelines

# Subtasks (Detailed)
## Subtask-01: Agile Improvement Processes
- **ID**: P05-T05-S01
- **Description**: Implement iterative development cycles, rapid prototyping, and continuous delivery.
- **Agent**: @development-orchestrator-agent
- **Documentation**: [Iterative_Development_Framework.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Iterative_Development_Framework.md)
- **Steps**:
    1. Implement agile improvement: iterative development cycles, rapid prototyping, continuous delivery, feedback integration (Tool: edit_file)
        - Success: `config/agile_process_config.json` exists and contains `"sprintDurationDays": 14`
    2. Initialize agile development environment (Tool: run_terminal_cmd)
        - Success: `agile_board_service` running, output contains "Agile development environment initialized."
- **Final Subtask Success Criteria**: Agile improvement processes are established, enabling iterative development and continuous delivery.
- **Integration Points**: Facilitates rapid improvement and continuous enhancement of the product.
- **Next Subtask**: P05-T05-S02

## Subtask-02: Continuous Integration & Deployment
- **ID**: P05-T05-S02
- **Description**: Optimize CI/CD pipelines for improvement deployment, including automation and testing.
- **Agent**: @development-orchestrator-agent
- **Documentation**: [CI_CD_Improvement_Optimization.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/CI_CD_Improvement_Optimization.md)
- **Steps**:
    1. Optimize CI/CD for improvements: deployment automation, testing integration, release management, rollback procedures (Tool: edit_file)
        - Success: `cicd/pipeline_config_v2.yml` exists and contains `enableAutomatedRollback: true`
    2. Validate CI/CD pipeline (Tool: run_terminal_cmd)
        - Success: All improvement tests pass, output contains "CI/CD pipeline validation successful."
- **Final Subtask Success Criteria**: CI/CD pipeline is optimized for rapid and reliable deployment of improvements.
- **Integration Points**: Enables automated and tested deployment of improvements developed via agile processes.
- **Next Subtask**: None

# Rollback Procedures
- Revert problematic agile or CI/CD configurations
- Restore previous development or deployment state if errors occur

# Integration Points
- Enables rapid improvement and continuous enhancement of the product

# Quality Gates
- Iterative Development: Agile improvement and rapid iteration
- CI/CD Optimization: Reliable and automated deployment

# Success Criteria
- [ ] Agile improvement processes are established
- [ ] CI/CD pipeline is optimized and validated

# Risk Mitigation
- Revert state on repeated agile or CI/CD failures
- Escalate to human on persistent issues

# Output Artifacts
- [Iterative_Development_Framework.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/Iterative_Development_Framework.md)
- [CI_CD_Improvement_Optimization.md](mdc:01_Machine/04_Documentation/vision/Phase_5/18_Continuous_Improvement/CI_CD_Improvement_Optimization.md)

# Next Action
Implement agile improvement processes and optimize CI/CD with @development-orchestrator-agent

# Post-Completion Action
Update @Step.json and @DNA.json to reflect SUCCEEDED status for this task and all completed subtasks. 