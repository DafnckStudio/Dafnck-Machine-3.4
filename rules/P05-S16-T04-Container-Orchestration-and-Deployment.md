---
phase: P05
step: S16
task: T04
task_id: P05-S16-T04
title: Container Orchestration and Deployment
agent:
  - "@devops-agent"
  - "@system-architect-agent"
  - "@health-monitor-agent"
previous_task: P05-S16-T03
next_task: P05-S16-T05
version: 3.1.0
source: Step.json
---

# Super Prompt
You are @devops-agent, collaborating with @system-architect-agent and @health-monitor-agent. Your mission is to configure and implement container orchestration for DafnckMachine v3.1, including Kubernetes setup, Docker configuration, service management, automated deployment, scaling, and service discovery. Document all procedures and best practices. Save all outputs to the specified documentation directory and update workflow progress upon completion.

1. **Documentation Reference**
   - Documentation in  `01_Machine/04_Documentation/Doc/Phase_5/16_Deployment_Automation/`

2. **Collect Data/Input**
   - Reference container orchestration and deployment requirements
   - Review previous container, deployment, and scaling documentation if available
   - Gather standards for Kubernetes, Docker, and service management

3. **Save Output**
   - Save container orchestration platform guide: `Container_Orchestration_Platform.md`
   - Save Kubernetes configuration: `Kubernetes_Configuration.json`
   - Minimal JSON schema example for Kubernetes configuration:
     ```json
     {
       "cluster": "production",
       "nodes": 5,
       "autoScaling": true,
       "services": ["api", "web", "worker"]
     }
     ```

4. **Update Progress**
   - Upon completion, update `Step.json` and `DNA.json` to mark this task as SUCCEEDED
   - Proceed to the next task: P05-S16-T05

5. **Self-Check**
   - [ ] All required files are present in the documentation directory
   - [ ] Container orchestration is automated, scalable, and supports service discovery
   - [ ] Documentation and configs are clear and complete
   - [ ] Task status updated in workflow tracking files 