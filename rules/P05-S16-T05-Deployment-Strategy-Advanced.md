---
phase: P05
step: S16
task: T05
task_id: P05-S16-T05
title: Deployment Strategy Advanced
agent:
  - "@devops-agent"
  - "@health-monitor-agent"
previous_task: P05-S16-T04
next_task: P05-S16-T06
version: 3.1.0
source: Step.json
---

# Super Prompt
You are @devops-agent, collaborating with @health-monitor-agent. Your mission is to implement advanced deployment strategies for DafnckMachine v3.1, including blue-green and canary deployments, zero-downtime switching, gradual rollout, A/B testing, automated rollback, and performance monitoring. Document all procedures and best practices. Save all outputs to the specified documentation directory and update workflow progress upon completion.

1. **Documentation Reference**
   - Documentation in  `01_Machine/04_Documentation/Doc/Phase_5/16_Deployment_Automation/`

2. **Collect Data/Input**
   - Reference advanced deployment strategy requirements and best practices
   - Review previous deployment, rollback, and monitoring documentation if available
   - Gather standards for blue-green, canary, A/B testing, and rollback

3. **Save Output**
   - Save blue-green deployment implementation: `Blue_Green_Deployment_Implementation.md`
   - Save rollback configuration: `Rollback_Configuration.json`
   - Save canary release implementation: `Canary_Release_Implementation.md`
   - Save A/B testing configuration: `AB_Testing_Configuration.json`
   - Minimal JSON schema example for rollback configuration:
     ```json
     {
       "strategy": "canary",
       "rollback": "auto",
       "healthMonitoring": true,
       "abTesting": true
     }
     ```

4. **Update Progress**
   - Upon completion, update `Step.json` and `DNA.json` to mark this task as SUCCEEDED
   - Proceed to the next task: P05-S16-T06

5. **Self-Check**
   - [ ] All required files are present in the documentation directory
   - [ ] Deployment strategies are automated, monitored, and support rollback
   - [ ] Documentation and configs are clear and complete
   - [ ] Task status updated in workflow tracking files 