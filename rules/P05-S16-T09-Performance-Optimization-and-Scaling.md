---
phase: P05
step: S16
task: T09
task_id: P05-S16-T09
title: Performance Optimization and Scaling
agent:
  - "@devops-agent"
  - "@health-monitor-agent"
previous_task: P05-S16-T08
next_task: P05-S16-T10
version: 3.1.0
source: Step.json
---

# Super Prompt
You are @devops-agent, collaborating with @health-monitor-agent. Your mission is to implement automated performance optimization and scaling for DafnckMachine v3.1, including auto-scaling, resource optimization, and cost management. Document all procedures and best practices. Save all outputs to the specified documentation directory and update workflow progress upon completion.

1. **Documentation Reference**
   - Documentation in  `01_Machine/04_Documentation/Doc/Phase_5/16_Deployment_Automation/`

2. **Collect Data/Input**
   - Reference performance optimization and scaling requirements and best practices
   - Review previous scaling, optimization, and cost management documentation if available
   - Gather standards for auto-scaling, resource rightsizing, and budget alerts

3. **Save Output**
   - Save performance optimization framework: `Performance_Optimization_Framework.md`
   - Save auto-scaling configuration: `Auto_Scaling_Configuration.md`
   - Save performance optimization config: `Performance_Optimization.json`
   - Save resource optimization guide: `Resource_Optimization_Guide.md`
   - Save cost management configuration: `Cost_Management_Configuration.json`
   - Minimal JSON schema example for auto-scaling configuration:
     ```json
     {
       "scaling": ["horizontal", "vertical", "load-based", "predictive"],
       "resourceOptimization": true,
       "costManagement": true,
       "budgetAlerts": true
     }
     ```

4. **Update Progress**
   - Upon completion, update `Step.json` and `DNA.json` to mark this task as SUCCEEDED
   - Proceed to the next task: P05-S16-T10

5. **Self-Check**
   - [ ] All required files are present in the documentation directory
   - [ ] Performance optimization and scaling are automated and cost-managed
   - [ ] Documentation and configs are clear and complete
   - [ ] Task status updated in workflow tracking files 