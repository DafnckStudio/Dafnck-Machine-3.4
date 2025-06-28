---
phase: P05
step: S16
task: T02
task_id: P05-S16-T02
title: Infrastructure as Code Implementation
agent:
  - "@devops-agent"
  - "@system-architect-agent"
  - "@development-orchestrator-agent"
  - "@health-monitor-agent"
previous_task: P05-S16-T01
next_task: P05-S16-T03
version: 3.1.0
source: Step.json
---

# Super Prompt
You are @devops-agent, collaborating with @system-architect-agent, @development-orchestrator-agent, and @health-monitor-agent. Your mission is to develop and implement comprehensive infrastructure as code (IaC) for DafnckMachine v3.1, ensuring automated provisioning, environment management, resource scaling, and version control. Document all procedures and best practices. Save all outputs to the specified documentation directory and update workflow progress upon completion.

1. **Documentation Reference**
   - Documentation in  `01_Machine/04_Documentation/Doc/Phase_5/16_Deployment_Automation/`

2. **Collect Data/Input**
   - Reference infrastructure as code requirements and best practices
   - Review previous infrastructure, environment, and scaling documentation if available
   - Gather standards for provisioning, isolation, and resource management

3. **Save Output**
   - Save infrastructure as code framework: `Infrastructure_as_Code_Framework.md`
   - Save IaC templates: `IaC_Templates.json`
   - Minimal JSON schema example for IaC templates:
     ```json
     {
       "provider": "aws",
       "resources": ["ec2", "s3", "rds"],
       "environments": ["dev", "staging", "prod"],
       "scaling": true
     }
     ```

4. **Update Progress**
   - Upon completion, update `Step.json` and `DNA.json` to mark this task as SUCCEEDED
   - Proceed to the next task: P05-S16-T03

5. **Self-Check**
   - [ ] All required files are present in the documentation directory
   - [ ] Infrastructure as code is automated, version-controlled, and supports scaling
   - [ ] Documentation and configs are clear and complete
   - [ ] Task status updated in workflow tracking files 