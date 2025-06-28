---
title: MCP Tool Usage Guide for P01-S01-T02 (Project Vision Elicitation)
version: 1.0
status: new
---

# MCP Tool Usage Guide for P01-S01-T02: Project Vision Elicitation

## 1. Purpose of This Guide
This document provides specific guidance on how the `@elicitation-agent` should utilize the mandated MCP (Machine Control Protocol) tools for **Task P01-S01-T02: Project Vision Elicitation**. Effective tool usage is crucial for creating, managing, and verifying the primary output artifact: `Project_Vision_Statement.md`.

The MCP tools required for this task are:
*   `edit_file`
*   `file_search`
*   `list_dir`

## 2. Using `edit_file`

*   **Purpose**: To create and iteratively update the `Project_Vision_Statement.md` document based on collaboration with the user.
*   **Key Actions**:
    *   **Initial Creation**: If `Project_Vision_Statement.md` does not exist, use `edit_file` to create it in the designated path (`01_Machine/04_Documentation/Doc/Phase_1/01_User_Briefing/Project_Vision_Statement.md` or `01_Machine/04_Documentation/vision/Phase_1/01_User_Briefing/Project_Vision_Statement.md` as per project convention for output artifacts).
        *   *Instruction Example*: "I will create the `Project_Vision_Statement.md` with initial sections for Objectives, Target Audience, Key Features, Unique Value Proposition, and Competitive Advantages."
    *   **Iterative Updates**: As the user provides more information or clarifications, use `edit_file` to add or modify content within the document. This is an ongoing process throughout the elicitation subtask.
        *   *Instruction Example*: "I will update the 'Key Features' section in `Project_Vision_Statement.md` based on our latest discussion."
*   **Best Practices for Content Structure within `Project_Vision_Statement.md`**:
    *   Use clear Markdown headings for each section (e.g., `## Main Objectives`, `## Target Audience`).
    *   Employ bullet points for lists of features, objectives, etc., to enhance readability.
    *   Ensure the language is aligned with the user's phrasing as much as possible, while maintaining clarity and conciseness.
    *   Adhere to any specific formatting guidelines or templates mentioned in the project's documentation standards.

## 3. Using `file_search`

*   **Purpose**: To locate existing vision statements or related documentation before creating a new one, or to find specific information within the project documentation.
*   **Key Actions**:
    *   **Pre-Creation Check**: Before creating `Project_Vision_Statement.md`, use `file_search` to check if a similar document (e.g., with a slightly different name or in a different location) already exists. This helps prevent duplication.
        *   *Query Example*: `query="project vision statement P01"`, `explanation="Searching for any existing project vision documents for Phase 1 to avoid duplication."`
    *   **Finding Related Documents**: If the user mentions related concepts or previous discussions documented elsewhere, `file_search` can help locate these for context.
        *   *Query Example*: `query="user persona research P01"`, `explanation="Searching for user persona documents relevant to the target audience discussion for Phase 1."`
*   **Interpreting Results**: Carefully review search results to determine relevance before acting on them.

## 4. Using `list_dir`

*   **Purpose**: To verify the documentation structure, confirm file placement, and understand the context of surrounding files.
*   **Key Actions**:
    *   **Verify File Location**: After creating or updating `Project_Vision_Statement.md`, use `list_dir` to confirm it has been placed in the correct directory as per project standards (e.g., `01_Machine/04_Documentation/Doc/Phase_1/01_User_Briefing/` or `01_Machine/04_Documentation/vision/Phase_1/01_User_Briefing/`).
        *   *Instruction Example*: `relative_workspace_path="01_Machine/04_Documentation/Doc/Phase_1/01_User_Briefing/"`, `explanation="Verifying the location of Project_Vision_Statement.md."`
    *   **Understand Surrounding Structure**: `list_dir` can help visualize the organization of other documents within the phase and step, ensuring consistency.
*   **Contextual Awareness**: This tool helps maintain an organized documentation repository.

## 5. Integrated Tool Usage Workflow Example (Subtask-01)

1.  **Start**: `@elicitation-agent` begins Subtask-01: Core Concept Discovery.
2.  **Check Existing**: Use `file_search` for `"Project_Vision_Statement.md P01-S01"` to see if a draft exists.
3.  **Verify Location (if found)**: If found, use `list_dir` on its parent directory to confirm it's in the right place.
4.  **Create/Open**: Use `edit_file` to either create a new `Project_Vision_Statement.md` or to add to an existing one.
    *   Populate initial structure (Objectives, Target Audience, Key Features, UVP, Competitive Advantages).
5.  **Elicit & Document**: Engage with the user. As information for each section is gathered:
    *   Use `edit_file` to add the content to the respective section in `Project_Vision_Statement.md`.
6.  **Review & Iterate**: After drafting sections, present to the user. Based on feedback:
    *   Use `edit_file` to make revisions.
7.  **Final Check**: Once all sections are documented and user confirms, use `list_dir` on the target output directory (e.g. `01_Machine/04_Documentation/vision/Phase_1/01_User_Briefing/`) to ensure the final `Project_Vision_Statement.md` is correctly placed as an output artifact.

By following these guidelines, the `@elicitation-agent` can effectively use the MCP tools to fulfill the requirements of Task P01-S01-T02 and produce a comprehensive `Project_Vision_Statement.md`. 