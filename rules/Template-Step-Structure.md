# Workflow Step Template

## Workflow Metadata
- **Workflow-Step**: [Step Name]
- **TaskID**: [PREFIX-CATEGORY-###] (e.g., PRJ-INIT-001, USR-BRIEF-002)
- **Step ID**: [##] (Sequential number: 00, 01, 02, etc.)
- **Version**: [X.Y.Z] (Semantic versioning)
- **LastUpdate**: [YYYY-MM-DD]
- **Previous Step**: [Previous step reference or "User initiates interaction (external to workflow)"]
- **Next Step**: [Next step filename.md]

## Mission Statement
[Clear, concise statement of what this step aims to accomplish. Should be 1-2 sentences describing the primary objective.]

## Description
[Detailed explanation of the step's purpose, context, and importance within the overall workflow. Include:
- What the step does
- Why it's necessary
- How it fits into the larger process
- Any special considerations for different project types (new vs existing)
- Expected outcomes and impact on subsequent steps]

## Result We Want
[Specific, measurable outcomes that define success for this step. Be concrete about what should be achieved.]

## Add to Brain
[Information that should be captured and stored in the system's knowledge base:]
- **[Category 1]**: [Description of data type and content]
- **[Category 2]**: [Description of data type and content]
- **[Category 3]**: [Description of data type and content]
- **[Category N]**: [Description of data type and content]

## Documentation & Templates

### Required Documents
[List all documents that must be created or updated during this step:]
1. **[Document_Name.extension]**: [Brief description of purpose and content]
2. **[Document_Name.extension]**: [Brief description of purpose and content]
3. **[Document_Name.extension]**: [Brief description of purpose and content]
N. **[Document_Name.extension]**: [Brief description of purpose and content]

### Optional Documents
[List documents that may be created based on project needs:]
- **[Optional_Document.extension]**: [When and why this might be needed]

## Super-Prompt
"[Detailed prompt for the responsible agent. Should include:
- Role definition
- Specific instructions
- Context requirements
- Expected deliverables
- Quality standards
- Any conditional logic for different scenarios]"

## MCP Tools Required
[List all Model Control Protocol tools needed for this step:]
- **[Tool Category/Name]**: [Specific use case and purpose]
- **[Tool Category/Name]**: [Specific use case and purpose]
- **[Tool Category/Name]**: [Specific use case and purpose]

## Agent Selection & Assignment

### Primary Responsible Agent
**[Agent Slug]** - `[agent-name-from-02_Agents]`
- **Role**: [Brief description of agent's primary responsibility]
- **Capabilities**: [Key capabilities relevant to this step]
- **When to Use**: [Specific conditions that make this agent optimal]

### Agent Selection Criteria
[Explain how this agent was selected from the 67 available agents in `01_Machine/02_Agents/`:]
- **Task Alignment**: [How agent's roleDefinition matches step requirements]
- **Capability Match**: [Specific capabilities needed for this step]
- **Interaction Pattern**: [How agent's interactsWith relationships support this step]
- **Group Permissions**: [Required groups: read, edit, mcp, command]

### Supporting Agents
[List any additional agents that may be called during this step:]
1. **[supporting-agent-slug]**: [When and why this agent is needed]
2. **[supporting-agent-slug]**: [When and why this agent is needed]
3. **[supporting-agent-slug]**: [When and why this agent is needed]

### Agent Discovery Process
To find the right agent for any task:
1. **Review Agent Categories** in `01_Machine/02_Agents/`:
   - Orchestrator agents (uber-orchestrator, development-orchestrator, etc.)
   - System management agents (health-monitor, swarm-scaler, etc.)
   - Specialized domain agents (coding, design, testing, etc.)
2. **Check Agent Capabilities**:
   - Read `roleDefinition` for primary purpose
   - Review `whenToUse` for activation criteria
   - Examine `customInstructions` for detailed capabilities
3. **Validate Agent Interactions**:
   - Check `interactsWith` array for compatible agents
   - Ensure agent has required `groups` permissions
   - Verify agent's `inputSpec` matches step requirements



















### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Quick Agent Reference Guide

**Total Agents Available: 67**

**Orchestration & Management:**
- `@development-orchestrator-agent` - This autonomous agent coordinates and manages comprehensive software development lifecycles, orchestrating teams, processes, and deliverables to ensure efficient, high-quality feature development
- `@marketing-strategy-orchestrator` - This autonomous agent develops and orchestrates comprehensive marketing strategies that drive business growth, brand awareness, and customer acquisition
- `@swarm-scaler-agent` - This autonomous operational agent monitors system workload, complexity metrics, and performance indicators to dynamically scale agent resources
- `@test-orchestrator-agent` - This autonomous agent masterfully orchestrates comprehensive testing strategies and coordinates all testing activities across development lifecycles
- `@uber-orchestrator-agent` - This is the supreme autonomous conductor of complex project lifecycles and multi-agent workflows
- `@workflow-architect-agent` - This autonomous agent designs and architects comprehensive project workflows and operational lifecycles tailored to specific project requirements, compliance needs, and organizational constraints

**Project Initiation & Planning:**
- `@idea-generation-agent` - This autonomous agent transforms vague concepts, problem statements, and user briefs into concrete, well-documented project ideas
- `@idea-refinement-agent` - This autonomous agent analytically refines and enhances project ideas by integrating new information from requirements analysis, market research, user feedback, and technical assessments
- `@project-initiator-agent` - This autonomous agent specializes in project initiation, onboarding, and setup processes for new software development projects
- `@task-deep-manager-agent` - This autonomous agent serves as the supreme orchestrator for complex project lifecycles, providing comprehensive requirement analysis, recursive task decomposition, intelligent agent assignment, and quality validation
- `@task-planning-agent` - This autonomous agent specializes in decomposing complex project requirements into structured, actionable task hierarchies that facilitate effective project management and execution
- `@task-sync-agent` - This autonomous agent specializes in maintaining bidirectional synchronization between different task management systems, formats, and data sources to ensure consistency and single source of truth across project management tools

**Requirements & Analysis:**
- `@compliance-scope-agent` - This autonomous agent meticulously researches and defines the full spectrum of applicable legal, regulatory, industry, and accessibility compliance requirements for any project
- `@elicitation-agent` - This autonomous agent specializes in comprehensive requirements gathering through structured dialogue and analysis
- `@market-research-agent` - This autonomous agent conducts comprehensive market research to analyze market viability, competitive landscapes, target audience segments, and industry trends
- `@nlu-processor-agent` - This autonomous agent specializes in Natural Language Understanding (NLU), processing natural language inputs to extract structured information, identify key entities, goals, constraints, and ambiguities
- `@prd-architect-agent` - This autonomous agent creates comprehensive Product Requirements Documents (PRDs) by synthesizing project information, requirements, research, and technical specifications into a single, authoritative source of truth for product development

**Development & Technical:**
- `@algorithmic-problem-solver-agent` - This autonomous agent specializes in analyzing complex computational problems, designing optimal algorithmic solutions, and creating comprehensive technical specifications
- `@code-reviewer-agent` - Reviews code for quality, correctness, and adherence to standards
- `@coding-agent` - This autonomous agent transforms detailed specifications and algorithmic designs into high-quality, production-ready code
- `@devops-agent` - This autonomous agent designs, implements, and manages comprehensive DevOps lifecycles including CI/CD pipelines, infrastructure as code, deployment strategies, monitoring, and operational excellence
- `@mcp-configuration-agent` - This autonomous agent manages the complete lifecycle of Model Context Protocol (MCP) server integration including installation (with mcp tool : mcp-installer), configuration, credential management, connectivity testing, monitoring, troubleshooting, and documentation
- `@mcp-researcher-agent` - This autonomous agent investigates, evaluates, and recommends suitable Model Context Protocol (MCP) servers, technology platforms, and integration solutions
- `@system-architect-agent` - This autonomous agent designs comprehensive system architectures that translate business requirements into scalable, maintainable, and robust technical solutions
- `@tech-spec-agent` - This autonomous agent translates high-level product requirements and system architecture into comprehensive, detailed technical specifications that serve as definitive blueprints for development teams

**Testing & Quality:**
- `@compliance-testing-agent` - This autonomous agent conducts comprehensive compliance verification across legal, regulatory, industry, and accessibility standards
- `@exploratory-tester-agent` - This autonomous agent excels at unscripted, exploratory testing, leveraging deep understanding of applications, user personas, and common failure patterns to uncover defects and usability issues that formal test cases might miss
- `@functional-tester-agent` - Executes functional tests on software features and user flows
- `@lead-testing-agent` - This autonomous agent serves as the comprehensive testing coordinator and quality assurance leader, orchestrating all testing activities across the software development lifecycle
- `@performance-load-tester-agent` - This autonomous agent designs, executes, and analyzes comprehensive performance tests—including load, stress, soak, spike, and volume testing—to evaluate system responsiveness, stability, and scalability
- `@security-penetration-tester-agent` - Performs security and penetration testing on applications and infrastructure
- `@test-case-generator-agent` - This autonomous agent specializes in generating comprehensive, detailed test cases for all types of software testing including functional, integration, system, and acceptance testing
- `@uat-coordinator-agent` - This autonomous agent expertly plans, coordinates, and manages comprehensive User Acceptance Testing (UAT) programs to ensure software solutions meet end-user requirements and business expectations
- `@usability-heuristic-agent` - This autonomous agent conducts comprehensive usability evaluations and heuristic assessments of user interfaces, prototypes, and digital products
- `@visual-regression-testing-agent` - This autonomous agent performs comprehensive visual regression testing by capturing, comparing, and analyzing UI screenshots to detect unintended visual changes across development iterations

**Design & User Experience:**
- `@branding-agent` - This autonomous agent creates, maintains, and evolves comprehensive brand identities that resonate with target audiences and drive business success
- `@design-qa-analyst` - This autonomous agent conducts comprehensive quality assurance reviews of design artifacts, ensuring adherence to design systems, brand guidelines, usability principles, and accessibility standards
- `@design-system-agent` - This autonomous agent creates, maintains, and evolves comprehensive design systems that ensure consistent, accessible, and scalable user interfaces
- `@graphic-design-agent` - This autonomous agent creates compelling visual assets and graphic designs that enhance brand identity, support marketing campaigns, and communicate messages effectively
- `@prototyping-agent` - This autonomous agent transforms static designs, mockups, and wireframes into interactive, functional prototypes
- `@ui-designer-agent` - This autonomous agent creates visually stunning, user-centric, and brand-consistent user interface designs
- `@ux-researcher-agent` - This autonomous agent conducts comprehensive User Experience (UX) research to understand user needs, behaviors, motivations, and pain points

**Content & Communication:**
- `@content-strategy-agent` - This autonomous agent develops comprehensive content strategies that align with business objectives, audience needs, and brand guidelines
- `@documentation-agent` - This autonomous agent creates, maintains, and optimizes comprehensive documentation across all project levels, from technical specifications to user guides
- `@scribe-agent` - This autonomous agent specializes in comprehensive documentation management, knowledge capture, and information organization across all project phases and activities
- `@user-feedback-collector-agent` - This autonomous agent specializes in comprehensive user feedback collection, analysis, and actionable insights generation
- `@video-production-agent` - This autonomous agent specializes in comprehensive video production, from concept development through final delivery

**Data & Analytics:**
- `@analytics-setup-agent` - This autonomous agent designs and implements comprehensive analytics tracking systems that enable data-driven decision making across all business functions
- `@brainjs-ml-agent` - This autonomous agent specializes in machine learning implementation using Brain
- `@deep-research-agent` - This autonomous agent conducts comprehensive research across multiple domains, utilizing advanced search capabilities, data analysis, and synthesis techniques to provide deep insights and actionable intelligence
- `@knowledge-evolution-agent` - This autonomous meta-agent drives continuous learning and evolution of the entire agentic system

**Business & Strategy:**
- `@campaign-manager-agent` - This autonomous agent orchestrates comprehensive marketing campaigns across multiple channels, ensuring coordinated execution, performance tracking, and optimization
- `@community-strategy-agent` - This autonomous agent develops, executes, and iteratively improves comprehensive community building strategies that foster engagement, growth, and advocacy
- `@growth-hacking-idea-agent` - Generates, evaluates, and documents creative growth hacking ideas for product and marketing
- `@seo-sem-agent` - This autonomous agent optimizes search engine visibility and drives targeted traffic through comprehensive SEO and SEM strategies
- `@social-media-setup-agent` - This autonomous agent establishes and optimizes comprehensive social media presence across all relevant platforms, creating optimized profiles, content strategies, and engagement frameworks that align with brand objectives and target audience preferences
- `@technology-advisor-agent` - This autonomous agent analyzes project requirements, technical constraints, and business objectives to recommend optimal technology stacks and architectural solutions

**Security & Compliance:**
- `@ethical-review-agent` - This autonomous agent conducts comprehensive ethical reviews of projects, products, and systems to identify potential ethical risks, bias, privacy concerns, and societal impacts
- `@security-auditor-agent` - This autonomous agent conducts comprehensive security audits of codebases, dependencies, configurations, and infrastructure to identify vulnerabilities, misconfigurations, and security risks

**Operations & Monitoring:**
- `@adaptive-deployment-strategist-agent` - This autonomous agent analyzes project context and designs optimal deployment strategies to ensure safe, efficient, and reliable software delivery
- `@efficiency-optimization-agent` - This autonomous agent continuously monitors, analyzes, and optimizes system performance, resource utilization, and operational efficiency
- `@health-monitor-agent` - This autonomous monitoring agent continuously observes system health metrics, detects anomalies, and provides proactive health management
- `@incident-learning-agent` - This autonomous learning agent captures, analyzes, and synthesizes knowledge from incidents and operational experiences
- `@remediation-agent` - This autonomous operational agent executes automated remediation actions, implements recovery procedures, and manages incident response workflows
- `@root-cause-analysis-agent` - This autonomous investigative agent conducts comprehensive root cause analysis of incidents, system failures, and performance issues

**Specialized Tools:**
- `@core-concept-agent` - This autonomous agent synthesizes insights from ideation, market research, and competitive analysis to define and articulate compelling core concepts for products and services
- `@debugger-agent` - This autonomous agent is an expert in software defect diagnosis and remediation across all programming languages and platforms

### Agent Selection Decision Tree
```
1. Is this a coordination/orchestration task?
   → Use orchestrator agents (uber-orchestrator, development-orchestrator, etc.)

2. Is this project initiation or planning?
   → Use project-initiator, task-planning, or idea-generation agents

3. Is this requirements gathering or analysis?
   → Use elicitation, nlu-processor, or market-research agents

4. Is this development or technical implementation?
   → Use coding, system-architect, or devops agents

5. Is this testing or quality assurance?
   → Use test-orchestrator, functional-tester, or compliance-testing agents

6. Is this design or user experience?
   → Use ux-designer, ui-designer, or accessibility agents

7. Is this content creation or documentation?
   → Use content-creator, technical-writer, or scribe agents

8. Is this data analysis or business intelligence?
   → Use analytics-setup or data-analyst agents

9. Is this business strategy or growth?
   → Use growth-hacking-idea or campaign-manager agents
```

## Agent Validation Checklist
Before finalizing agent selection, verify:
- [ ] Agent's `roleDefinition` aligns with step objectives
- [ ] Agent's `whenToUse` criteria match current context
- [ ] Agent has required `groups` permissions for this step
- [ ] Agent's `inputSpec` matches available inputs
- [ ] Agent's `outputSpec` produces required deliverables
- [ ] Agent's `interactsWith` includes necessary supporting agents
- [ ] Agent's `customInstructions` cover step-specific requirements

## Task Breakdown

### Phase Structure (Synchronized with DNA.json, Step.json, workflow_state.json)

```
[] Phase-[##] ([Phase Name] - Strategic Level)
├── [] Task-01 ([Primary Task Name] - Tactical Level)
│   ├── [] Subtask-01 ([Subtask Description] - Operational Level)
│   │   ├── [] 01 Agent Assignment: `[primary-agent-slug]` - [Agent capability]
│   │   ├── [] 02 Agent Prompt: "[Detailed prompt for the agent including role, context, and deliverables]"
│   │   ├── [] 03 Documentation Links: [Document references and templates]
│   │   ├── [] 04 Success Criteria: [Specific measurable outcomes]
│   │   └── [] 05 Integration Points: [System/process connections]
│   ├── [] Subtask-02 ([Subtask Description] - Operational Level)
│   │   ├── [] 01 Agent Assignment: `[supporting-agent-slug]` - [Agent capability]
│   │   ├── [] 02 Agent Prompt: "[Detailed prompt for the agent including role, context, and deliverables]"
│   │   ├── [] 03 Documentation Links: [Document references and templates]
│   │   ├── [] 04 Success Criteria: [Specific measurable outcomes]
│   │   └── [] 05 Integration Points: [System/process connections]
├── [] Task-02 ([Secondary Task Name] - Tactical Level)
│   ├── [] Subtask-01 ([Subtask Description] - Operational Level)
│   │   ├── [] 01 Agent Assignment: `[secondary-agent-slug]` - [Agent capability]
│   │   ├── [] 02 Agent Prompt: "[Detailed prompt for the agent including role, context, and deliverables]"
│   │   ├── [] 03 Documentation Links: [Document references and templates]
│   │   ├── [] 04 Success Criteria: [Specific measurable outcomes]
│   │   └── [] 05 Integration Points: [System/process connections]
│   ├── [] Subtask-02 ([Subtask Description] - Operational Level)
│   │   ├── [] 01 Agent Assignment: `[tertiary-agent-slug]` - [Agent capability]
│   │   ├── [] 02 Agent Prompt: "[Detailed prompt for the agent including role, context, and deliverables]"
│   │   ├── [] 03 Documentation Links: [Document references and templates]
│   │   ├── [] 04 Success Criteria: [Specific measurable outcomes]
│   │   └── [] 05 Integration Points: [System/process connections]
├── [] Task-03 ([Tertiary Task Name] - Tactical Level)
│   ├── [] Subtask-01 ([Subtask Description] - Operational Level)
│   │   ├── [] 01 Agent Assignment: `[additional-agent-slug]` - [Agent capability]
│   │   ├── [] 02 Agent Prompt: "[Detailed prompt for the agent including role, context, and deliverables]"
│   │   ├── [] 03 Documentation Links: [Document references and templates]
│   │   ├── [] 04 Success Criteria: [Specific measurable outcomes]
│   │   └── [] 05 Integration Points: [System/process connections]
│   ├── [] Subtask-02 ([Subtask Description] - Operational Level)
│   │   ├── [] 01 Agent Assignment: `[supporting-agent-slug]` - [Agent capability]
│   │   ├── [] 02 Agent Prompt: "[Detailed prompt for the agent including role, context, and deliverables]"
│   │   ├── [] 03 Documentation Links: [Document references and templates]
│   │   ├── [] 04 Success Criteria: [Specific measurable outcomes]
│   │   └── [] 05 Integration Points: [System/process connections]
```

### Synchronization Guidelines

**Phase Level (Strategic)**
- Maps to `DNA.json` → `step_definitions.[step_name].phase`
- Maps to `workflow_state.json` → `current_position.phase`
- Format: `phase_[0-6]` (e.g., `phase_0`, `phase_1`, etc.)

**Task Level (Tactical)**
- Maps to `DNA.json` → `step_definitions.[step_name].task_id`
- Maps to `workflow_state.json` → `current_position.task`
- Format: `[PREFIX-CATEGORY-###]` (e.g., `PRJ-INIT-001`, `USR-BRIEF-002`)

**Subtask Level (Operational)**
- Maps to `workflow_state.json` → `current_position.subtask`
- Maps to `Step.json` → tracking and validation
- Format: Sequential numbering within task scope

**Agent Assignment Synchronization**
- Maps to `DNA.json` → `agentRegistry[].agentName`
- Maps to `DNA.json` → `step_definitions.[step_name].agent`
- Maps to `workflow_state.json` → `current_position.agent`
- Format: `@[agent-name-from-02_Agents]`

**Agent Prompt Integration**
- Maps to agent's `customInstructions` in `01_Machine/02_Agents/[agent-name].json`
- Inherits from template's `Super-Prompt` section for context
- Includes specific task context, deliverables, and quality standards
- Format: Detailed instruction string with role definition and expected outputs

### Tracking Integration Points

**Progress Tracking**
- Each checkbox `[]` represents a trackable unit in `workflow_state.json`
- Completion status syncs with `progress.completed_steps`
- Current position tracked in `current_position` object

**Agent Coordination**
- Agent assignments must exist in `DNA.json` → `agentRegistry`
- Agent capabilities validated against `01_Machine/02_Agents/` directory
- Inter-agent communication tracked through `interactsWith` relationships

**Documentation Synchronization**
- Document links reference files created during step execution
- Template references align with `Required Documents` section
- Version control integrated with step completion tracking

## Success Criteria
[Checklist format for validation:]
- [ ] [Specific measurable outcome 1]
- [ ] [Specific measurable outcome 2]
- [ ] [Specific measurable outcome 3]
- [ ] [Specific measurable outcome N]
- [ ] [System readiness for next step]

## Quality Gates
[Validation checkpoints that must pass before proceeding:]
1. **[Gate Name]**: [Description of validation criteria and acceptance standards]
2. **[Gate Name]**: [Description of validation criteria and acceptance standards]
3. **[Gate Name]**: [Description of validation criteria and acceptance standards]

## Risk Mitigation
[Potential issues and their solutions:]
- **[Risk Category]**: [Description of risk and mitigation strategy]
- **[Risk Category]**: [Description of risk and mitigation strategy]
- **[Risk Category]**: [Description of risk and mitigation strategy]

## Dependencies
[Prerequisites and constraints:]
### Input Dependencies
- [What must be completed before this step can begin]
- [Required resources or information]

### Output Dependencies
- [What other steps depend on this step's completion]
- [Critical deliverables for downstream processes]

## Performance Metrics
[How to measure step effectiveness:]
- **Duration**: [Expected time range]
- **Quality Score**: [How quality is measured]
- **Completeness**: [Percentage of objectives achieved]
- **[Custom Metric]**: [Step-specific measurement]

## Output Artifacts
[Numbered list of all deliverables:]
1. [Primary deliverable]
2. [Secondary deliverable]
3. [Documentation artifact]
4. [Configuration artifact]
5. [Report or analysis]
N. [Additional artifacts]

## Rollback Procedures
[Steps to undo this phase if needed:]
1. [Rollback step 1]
2. [Rollback step 2]
3. [Rollback step N]

## Integration Points
[How this step connects with other systems/processes:]
- **[System/Process Name]**: [Integration description]
- **[System/Process Name]**: [Integration description]

---

## Template Usage Guidelines

### Filling Out This Template
1. **Replace all bracketed placeholders** with actual content
2. **Select appropriate agents** using the Agent Selection Decision Tree
3. **Validate agent capabilities** against step requirements using the checklist
4. **Map tasks to agent capabilities** in the Task Breakdown section
5. **Remove unused sections** if not applicable to your step
6. **Add custom sections** as needed for specific requirements
7. **Maintain consistent formatting** across all workflow steps
8. **Use clear, actionable language** throughout

### Agent Selection Best Practices
1. **Start with the Decision Tree**: Use the provided decision tree to narrow down agent categories
2. **Review Agent Files**: Read the actual agent JSON files in `01_Machine/02_Agents/` for detailed capabilities
3. **Check Interactions**: Ensure selected agents can work together (check `interactsWith` arrays)
4. **Validate Permissions**: Confirm agents have required `groups` permissions for the step
5. **Consider Workflow**: Think about the sequence of agent interactions within the step
6. **Document Rationale**: Explain why specific agents were chosen for each task

### Naming Conventions
- **TaskID Format**: [PREFIX-CATEGORY-###]
  - PREFIX: Project area (PRJ, USR, DEV, etc.)
  - CATEGORY: Step category (INIT, BRIEF, DESIGN, etc.)
  - ###: Sequential number (001, 002, 003, etc.)
- **Step ID**: Two-digit sequential (00, 01, 02, etc.)
- **File Names**: ##_Step_Name.md (e.g., 00_Project_Initialization.md)

### Quality Standards
- Each section must be complete and actionable
- Tasks must be specific and measurable
- Success criteria must be verifiable
- Documentation must be comprehensive
- Integration points must be clearly defined

---

**Template Version**: 1.0.0  
**Last Updated**: 2025-05-26  
**Status**: Ready for Use
