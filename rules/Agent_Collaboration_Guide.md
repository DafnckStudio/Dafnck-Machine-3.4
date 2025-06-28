---
title: Agent Collaboration Guide for P01-S01-T02 (Project Vision Elicitation)
version: 1.0
status: new
---

# Agent Collaboration Guide for P01-S01-T02: Project Vision Elicitation

## 1. Purpose of This Guide
This document outlines the roles, responsibilities, and collaboration flow of the AI agents involved in **Task P01-S01-T02: Project Vision Elicitation**. The goal of this task is to elicit the core project concept and define measurable success criteria, including main objectives, target audience, key features, and unique value proposition, documenting this in `Project_Vision_Statement.md`.

## 2. Primary Responsible Agent: @elicitation-agent

*   **Role**: The `@elicitation-agent` is the lead agent for this task.
*   **Primary Responsibilities**:
    *   **Direct User Collaboration**: Actively engage with the user (e.g., through structured questions, prompts, and discussions) to discover and articulate all components of the project vision.
    *   **Information Synthesis**: Gather all inputs and synthesize them into a coherent project vision.
    *   **Documentation**: Populate and refine the `Project_Vision_Statement.md` file with the elicited information, ensuring clarity, completeness, and adherence to defined structures.
    *   **Clarification and Iteration**: Seek clarifications from the user on ambiguous points and iterate on the vision statement based on feedback.
*   **Key Interactions**: The `@elicitation-agent` will be the primary interface with the user for discovering the vision. It will use the information provided in the "Super-Prompt" of the task file as a starting point.

## 3. Supporting Agents and Their Roles

### @nlu-processor-agent
*   **Role**: Supports the `@elicitation-agent` by processing and understanding user inputs.
*   **Contribution**: Helps in interpreting natural language responses from the user, identifying key entities, intents, and sentiments. This allows the `@elicitation-agent` to ask more targeted follow-up questions and to more accurately capture the user's meaning in the vision statement.
*   **Collaboration**: Works in the background, providing processed information to the `@elicitation-agent`.

### @project-initiator-agent
*   **Role**: Provides context and support for framing the overall project.
*   **Contribution**: Helps ensure that the elicited vision aligns with the general principles of project initiation. May provide high-level structuring advice or ensure that the scope of the vision is appropriate for an initial definition.
*   **Collaboration**: May be consulted by the `@elicitation-agent` if the vision seems too broad, too narrow, or lacks foundational project elements.

### @market-research-agent
*   **Role**: Provides external context, particularly for defining the Unique Value Proposition (UVP) and competitive advantages.
*   **Contribution**: If the user struggles to articulate the UVP or competitive landscape, the `@elicitation-agent` can leverage insights (potentially pre-existing or fetched by `@market-research-agent` in a broader context) to ask guiding questions. For this specific task, direct market research might not be performed, but the agent's knowledge base is relevant.
*   **Collaboration**: The `@elicitation-agent` can frame questions informed by typical market research considerations (e.g., "How does this compare to existing solutions you know?").

### @tech-spec-agent
*   **Role**: Provides a high-level technical perspective to ensure feasibility considerations for mentioned features.
*   **Contribution**: As key features are discussed, the `@tech-spec-agent` (or its knowledge) can help the `@elicitation-agent` prompt the user to consider if the features are technically plausible at a high level. This is not a deep technical dive but a sanity check.
*   **Collaboration**: If the user proposes highly complex or novel technical features as core to the vision, the `@elicitation-agent` might use this perspective to ask clarifying questions about constraints or dependencies.

## 4. Expected Collaboration Workflow

1.  **Initiation**: The `@uber-orchestrator-agent` assigns P01-S01-T02 to the `@elicitation-agent`.
2.  **User Interaction**: The `@elicitation-agent`, supported by the `@nlu-processor-agent`, interacts with the user to gather information about the project vision (objectives, audience, features, UVP, competitive advantages).
3.  **Contextual Input (as needed)**: The `@elicitation-agent` may internally leverage knowledge or guidance aligned with the perspectives of `@project-initiator-agent`, `@market-research-agent`, and `@tech-spec-agent` to refine its questioning and analysis of user input.
4.  **Documentation**: The `@elicitation-agent` uses the `edit_file` tool to create and update `Project_Vision_Statement.md`.
5.  **Verification**: The `@elicitation-agent` may use `file_search` to ensure no conflicting vision documents exist or `list_dir` to confirm proper file placement.
6.  **Iteration**: The `@elicitation-agent` presents the documented vision (or parts of it) to the user for feedback and iterates until the vision is clearly articulated and agreed upon, meeting the success criteria of the task.
7.  **Completion**: Once the vision is documented and meets quality gates, the task is marked complete.

This collaborative approach ensures that the project vision is not only captured from the user but also implicitly considers broader project initiation, market, and technical contexts at a high level. 