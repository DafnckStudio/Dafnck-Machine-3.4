---
phase: P05
step: S16
task: T08
task_id: P05-S16-T08
title: Rollback and Recovery Automation
agent:
  - "@devops-agent"
  - "@health-monitor-agent"
previous_task: P05-S16-T07
next_task: P05-S16-T09
version: 3.1.0
source: Step.json
---

# Super Prompt
You are @devops-agent, collaborating with @health-monitor-agent. Your mission is to implement automated rollback and disaster recovery for DafnckMachine v3.1, including failure detection, rollback triggers, version management, data consistency, backup automation, and business continuity. Document all procedures and best practices. Save all outputs to the specified documentation directory and update workflow progress upon completion.

1. **Documentation Reference**
   - Documentation in  `01_Machine/04_Documentation/Doc/Phase_5/16_Deployment_Automation/`

2. **Collect Data/Input**
   - Reference rollback and recovery requirements and best practices
   - Review previous rollback, backup, and disaster recovery documentation if available
   - Gather standards for failure detection, backup, and business continuity

3. **Save Output**
   - Save rollback and recovery procedures: `Rollback_Recovery_Procedures.md`
   - Save recovery procedures: `Recovery_Procedures.json`
   - Save disaster recovery implementation: `Disaster_Recovery_Implementation.md`
   - Save backup configuration: `Backup_Configuration.json`
   - Minimal JSON schema example for recovery procedures:
     ```json
     {
       "failureDetection": true,
       "rollback": "auto",
       "backup": "daily",
       "businessContinuity": true
     }
     ```

4. **Update Progress**
   - Upon completion, update `Step.json` and `DNA.json` to mark this task as SUCCEEDED
   - Proceed to the next task: P05-S16-T09

5. **Self-Check**
   - [ ] All required files are present in the documentation directory
   - [ ] Rollback and recovery systems are automated and reliable
   - [ ] Documentation and configs are clear and complete
   - [ ] Task status updated in workflow tracking files 