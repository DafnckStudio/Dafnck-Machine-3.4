---
phase: P05
step: S16
task: T03
task_id: P05-S16-T03
title: Deployment Strategy Implementation
agent:
  - "@devops-agent"
  - "@system-architect-agent"
  - "@health-monitor-agent"
previous_task: P05-S16-T02
next_task: P05-S16-T04
version: 3.1.0
source: Step.json
---

# Super Prompt
You are @devops-agent, collaborating with @system-architect-agent and @health-monitor-agent. Your mission is to design and implement zero-downtime deployment strategies for DafnckMachine v3.1, including blue-green and canary deployments, automated traffic management, health monitoring, and robust rollback procedures. Document all procedures and best practices. Save all outputs to the specified documentation directory and update workflow progress upon completion.

1. **Documentation Reference**
   - Documentation in  `01_Machine/04_Documentation/Doc/Phase_5/16_Deployment_Automation/`

2. **Collect Data/Input**
   - Reference deployment strategy requirements and best practices
   - Review previous deployment, traffic management, and monitoring documentation if available
   - Gather standards for zero-downtime, health checks, and rollback

3. **Save Output**
   - Save deployment strategy configuration: `Deployment_Strategy_Configuration.md`
   - Save traffic management plan: `Traffic_Management_Plan.json`
   - Minimal JSON schema example for traffic management plan:
     ```json
     {
       "strategy": "blue-green",
       "trafficSplit": {"blue": 0.5, "green": 0.5},
       "healthChecks": true,
       "rollback": "auto"
     }
     ```

4. **Update Progress**
   - Upon completion, update `Step.json` and `DNA.json` to mark this task as SUCCEEDED
   - Proceed to the next task: P05-S16-T04

5. **Self-Check**
   - [ ] All required files are present in the documentation directory
   - [ ] Deployment strategy is zero-downtime, automated, and supports rollback
   - [ ] Documentation and configs are clear and complete
   - [ ] Task status updated in workflow tracking files 