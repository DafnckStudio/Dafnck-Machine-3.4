# User Profile Documentation (User_Profile.json)

**Associated Task:** [P01-S01-T01-User-Profile-Development.md](mdc:01_Machine/01_Workflow/Phase%201%3A%20Initial%20User%20Input%20%26%20Project%20Inception/01_User_Briefing/P01-S01-T01-User-Profile-Development.md)

## 1. Introduction

*   **Purpose:** Explains that `User_Profile.json` stores comprehensive information about the user interacting with DafnckMachine v3.1. This profile is crucial for tailoring agent interactions, selecting appropriate supporting agents, and aligning the project approach with the user's background, expertise, and preferences.
*   **Location of Template:** `01_Machine/04_Documentation/Doc/Phase_1/01_User_Briefing/User_Profile.json`
*   **Location of Filled Profile (Output):** `01_Machine/04_Documentation/vision/Phase_1/01_User_Briefing/User_Profile.json`
*   **Key Benefits:**
    *   Personalized agent communication.
    *   Efficient agent delegation based on user's strengths and weaknesses.
    *   Reduced misunderstandings and aligned expectations.
    *   More effective project execution.

## 2. File Structure and Schema Overview

Briefly describe the main sections of the JSON file.

```json
{
  "profile_schema_version": "string (e.g., 1.0.0)",
  "last_updated": "ISO 8601 datetime string (YYYY-MM-DDTHH:MM:SSZ)",
  "user_identifier": "string",
  "general_info": { /* ... */ },
  "background": { /* ... */ },
  "technical_expertise": { /* ... */ },
  "industry_experience": [ /* ... */ ],
  "previous_project_involvement": [ /* ... */ ],
  "working_styles_and_preferences": { /* ... */ },
  "goals_and_expectations_for_dafnckmachine": { /* ... */ },
  "additional_notes": "string"
}
```

## 3. Detailed Field Descriptions

For each main section and its sub-fields:
*   Provide a clear description of the field.
*   Specify the data type (e.g., string, number, array of objects, object).
*   Indicate if the field is mandatory or optional.
*   Give clear examples.

### 3.1. `profile_schema_version` (string, mandatory)
*   **Description:** Version of the user profile schema. Helps in managing changes to the profile structure over time.
*   **Example:** `"1.0.0"`

### 3.2. `last_updated` (string, mandatory)
*   **Description:** ISO 8601 timestamp indicating when the profile was last updated.
*   **Example:** `"2024-07-27T10:30:00Z"`

### 3.3. `user_identifier` (string, mandatory)
*   **Description:** A unique identifier for the user (e.g., username, email, or a generated ID).
*   **Example:** `"user_alpha_001"`

### 3.4. `general_info` (object, mandatory)
    *   `full_name` (string, optional): User's full name. Example: `"Dr. Evelyn Reed"`
    *   `contact_email` (string, optional): User's primary contact email. Example: `"e.reed@example.com"`
    *   `role_in_project` (string, optional): User's designated role for this project. Example: `"Project Lead"`

### 3.5. `background` (object, mandatory)
    *   `summary` (string, optional): Brief narrative overview of the user's professional background.
    *   `years_of_experience` (number, optional): Total years of professional experience. Example: `15`
    *   `primary_industry` (string, optional): The main industry the user has experience in. Example: `"Biotechnology"`
    *   `secondary_industries` (array of strings, optional): Other industries the user has experience in. Example: `["Pharmaceuticals", "Healthcare IT"]`

### 3.6. `technical_expertise` (object, mandatory)
    *   `programming_languages` (array of objects, optional):
        *   `language` (string): e.g., `"Python"`
        *   `proficiency` (string - e.g., "Beginner", "Intermediate", "Advanced", "Expert"): e.g., `"Advanced"`
        *   `years_experience` (number): e.g., `10`
    *   `frameworks_libraries` (array of objects, optional): (Similar structure: `name`, `proficiency`, `years_experience`)
    *   `tools_platforms` (array of objects, optional): (Similar structure: `name`, `proficiency`, `years_experience`) e.g., Platforms like Docker, Kubernetes, Jira.
    *   `database_systems` (array of objects, optional): (Similar structure: `name`, `proficiency`, `years_experience`)
    *   `cloud_platforms` (array of objects, optional):
        *   `name` (string): e.g., `"AWS"`
        *   `proficiency` (string): e.g., `"Intermediate"`
        *   `services` (array of strings): Key services familiar with. e.g., `["EC2", "S3", "RDS", "Lambda"]`
    *   `ai_ml_expertise` (object, optional):
        *   `areas` (array of strings): e.g., `["Natural Language Processing", "Machine Learning Operations (MLOps)"]`
        *   `tools` (array of strings): e.g., `["Scikit-learn", "TensorFlow", "Kubeflow"]`
        *   `project_experience_summary` (string): Brief summary of AI/ML project experience.
    *   `other_technical_skills` (array of strings, optional): Any other relevant technical skills. Example: `["Data Visualization", "Agile Methodologies"]`

### 3.7. `industry_experience` (array of objects, optional)
    *   `industry` (string): e.g., `"Aerospace"`
    *   `roles` (array of strings): Roles held in this industry. e.g., `["Systems Engineer", "R&D Manager"]`
    *   `years_in_industry` (number): e.g., `8`
    *   `project_examples_summary` (string): Brief summary of key projects or experiences in this industry.

### 3.8. `previous_project_involvement` (array of objects, optional)
    *   `project_name_or_type` (string): Name or type of a significant past project. Example: `"Mars Rover Navigation System"`
    *   `role` (string): User's role in that project. Example: `"Lead Software Architect"`
    *   `technologies_used` (array of strings): Key technologies. Example: `["C++", "ROS", "Real-time Linux"]`
    *   `duration_months` (number): Duration of involvement. Example: `36`
    *   `key_responsibilities_achievements` (string): Summary of responsibilities and achievements.

### 3.9. `working_styles_and_preferences` (object, mandatory)
    *   `preferred_communication_channels` (array of strings): e.g., `["Slack", "Email", "Video Calls"]`
    *   `meeting_preferences` (object, optional):
        *   `frequency` (string): e.g., `"Weekly check-ins, ad-hoc for issues"`
        *   `preferred_duration_minutes` (number): e.g., `30`
        *   `style` (string): e.g., `"Agenda-driven, clear action items"`
    *   `feedback_style` (object, optional):
        *   `preferred_to_give` (string): How the user prefers to give feedback.
        *   `preferred_to_receive` (string): How the user prefers to receive feedback.
    *   `project_methodology_preference` (array of strings): e.g., `["Agile (Scrum)", "Waterfall (for specific phases)"]`
    *   `documentation_preference` (string): e.g., `"Concise, with clear diagrams and API specs"`
    *   `working_hours_timezone` (string, optional): e.g., `"08:00-18:00 CET (UTC+1)"`
    *   `collaboration_tools_familiarity` (array of strings, optional): e.g., `["Microsoft Teams", "Asana", "Miro"]`
    *   `learning_preferences` (string, optional): How the user prefers to learn new things.
    *   `decision_making_style` (string, optional): How the user approaches decisions.
    *   `areas_of_interest_for_this_project` (array of strings, optional): Specific aspects of the current project the user is keen on.

### 3.10. `goals_and_expectations_for_dafnckmachine` (object, mandatory)
    *   `primary_objectives` (array of strings): What the user primarily aims to achieve using DafnckMachine.
    *   `key_success_metrics` (array of strings): How the user will measure the success of using DafnckMachine.
    *   `concerns_or_hesitations` (array of strings, optional): Any concerns the user has.
    *   `desired_level_of_automation` (string, optional): e.g., `"High for repetitive tasks, medium for complex decision-making support"`

### 3.11. `additional_notes` (string, optional)
*   **Description:** Any other relevant information not captured elsewhere.

## 4. How This Profile is Used

*   **Agent Selection:** The `@uber-orchestrator-agent` and other orchestrators use this profile to select the most suitable specialist agents for tasks, considering the user's technical depth and industry knowledge.
*   **Communication Strategy:** Agents adapt their language, level of technical detail, and communication frequency based on the user's preferences and expertise.
*   **Task Elicitation & Clarification:** The `@nlu-processor-agent` and `@elicitation-agent` use this to understand the user's context better when gathering requirements.
*   **Expectation Management:** Helps in aligning DafnckMachine's capabilities and outputs with the user's stated goals and success metrics.
*   **Proactive Support:** Can highlight areas where the user might need more guidance or where DafnckMachine can offer specific value.

## 5. Maintaining the Profile

*   **Initial Creation:** Filled out during the P01-S01-T01 task by the `@nlu-processor-agent` through interaction with the user.
*   **Updates:** The profile is a living document. It should be reviewed and updated if:
    *   The user's role or objectives change.
    *   There are significant shifts in the user's technical skills or preferences.
    *   Feedback indicates a mismatch between agent interaction and user expectations.
*   The `last_updated` field must be modified upon each update.

## 6. Example `User_Profile.json`

(Include a snippet or a fully populated example here, derived from the template structure previously defined, but with placeholder or illustrative data.)

```json
{
  "profile_schema_version": "1.0.0",
  "last_updated": "2024-07-27T14:00:00Z",
  "user_identifier": "example_user_01",
  "general_info": {
    "full_name": "Jane Doe",
    "contact_email": "jane.doe@example.com",
    "role_in_project": "Product Owner"
  },
  // ... (other sections filled with example data) ...
  "working_styles_and_preferences": {
    "preferred_communication_channels": ["Slack", "Weekly Sync Calls"],
    "meeting_preferences": {
      "frequency": "Weekly",
      "preferred_duration_minutes": 45,
      "style": "Structured with agenda and action items"
    }
    // ...
  },
  "goals_and_expectations_for_dafnckmachine": {
    "primary_objectives": ["Rapidly prototype new features", "Automate PRD generation"],
    "key_success_metrics": ["Time to MVP reduced by 30%", "PRD accuracy > 90%"]
    // ...
  }
}
```

## 7. Integration with Workflow

*   References how this profile, once created in the `vision` folder, is picked up by subsequent tasks and agents as per the project's `DNA.json` and `Step.json`.
--- 