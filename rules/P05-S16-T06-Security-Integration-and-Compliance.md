---
phase: P05
step: S16
task: T06
task_id: P05-S16-T06
title: Security Integration and Compliance
agent:
  - "@security-auditor-agent"
  - "@compliance-scope-agent"
  - "@devops-agent"
previous_task: P05-S16-T05
next_task: P05-S16-T07
version: 3.1.0
source: Step.json
---

# Super Prompt
You are @security-auditor-agent, collaborating with @compliance-scope-agent and @devops-agent. Your mission is to integrate automated security scanning and compliance automation into the deployment pipelines for DafnckMachine v3.1, ensuring vulnerability detection, code analysis, policy enforcement, and audit logging. Document all procedures and best practices. Save all outputs to the specified documentation directory and update workflow progress upon completion.

1. **Documentation Reference**
   - Documentation in  `01_Machine/04_Documentation/Doc/Phase_5/16_Deployment_Automation/`

2. **Collect Data/Input**
   - Reference security and compliance requirements and best practices
   - Review previous security, compliance, and audit documentation if available
   - Gather standards for vulnerability scanning, policy enforcement, and audit logging

3. **Save Output**
   - Save security integration framework: `Security_Integration_Framework.md`
   - Save vulnerability scan configuration: `Vulnerability_Scan_Configuration.json`
   - Save compliance automation framework: `Compliance_Automation_Framework.md`
   - Save policy enforcement configuration: `Policy_Enforcement_Configuration.json`
   - Minimal JSON schema example for vulnerability scan configuration:
     ```json
     {
       "tool": "Trivy",
       "scanStages": ["build", "deploy"],
       "report": true,
       "policyEnforcement": true
     }
     ```

4. **Update Progress**
   - Upon completion, update `Step.json` and `DNA.json` to mark this task as SUCCEEDED
   - Proceed to the next task: P05-S16-T07

5. **Self-Check**
   - [ ] All required files are present in the documentation directory
   - [ ] Security and compliance integrations are automated and validated
   - [ ] Documentation and configs are clear and complete
   - [ ] Task status updated in workflow tracking files 