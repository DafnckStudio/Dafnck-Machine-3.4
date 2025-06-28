---
phase: P05
step: S16
task: T07
task_id: P05-S16-T07
title: Monitoring System Setup
agent:
  - "@health-monitor-agent"
  - "@devops-agent"
previous_task: P05-S16-T06
next_task: P05-S16-T08
version: 3.1.0
source: Step.json
---

# Super Prompt
You are @health-monitor-agent, collaborating with @devops-agent. Your mission is to setup comprehensive production monitoring for DafnckMachine v3.1, including metrics collection, performance monitoring, health checks, dashboards, alerting, and notification channels. Document all procedures and best practices. Save all outputs to the specified documentation directory and update workflow progress upon completion.

1. **Documentation Reference**
   - Documentation in  `01_Machine/04_Documentation/Doc/Phase_5/16_Deployment_Automation/`

2. **Collect Data/Input**
   - Reference monitoring and alerting requirements and best practices
   - Review previous monitoring, alerting, and dashboard documentation if available
   - Gather standards for metrics, health checks, and notification channels

3. **Save Output**
   - Save monitoring and alerting setup: `Monitoring_Alerting_Setup.md`
   - Save metrics dashboard configuration: `Metrics_Dashboard_Configuration.json`
   - Save alerting system implementation: `Alerting_System_Implementation.md`
   - Save notification channels configuration: `Notification_Channels_Configuration.json`
   - Minimal JSON schema example for metrics dashboard configuration:
     ```json
     {
       "dashboard": "production",
       "metrics": ["cpu", "memory", "latency"],
       "alerts": true,
       "notificationChannels": ["email", "slack"]
     }
     ```

4. **Update Progress**
   - Upon completion, update `Step.json` and `DNA.json` to mark this task as SUCCEEDED
   - Proceed to the next task: P05-S16-T08

5. **Self-Check**
   - [ ] All required files are present in the documentation directory
   - [ ] Monitoring and alerting systems are automated and reliable
   - [ ] Documentation and configs are clear and complete
   - [ ] Task status updated in workflow tracking files 