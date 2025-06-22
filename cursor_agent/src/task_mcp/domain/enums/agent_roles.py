"""
Auto-generated Agent Roles Enum
Generated on: 2025-06-19 13:25:05
Total agents: 68

This file contains all available agent roles from the YAML library.
Do not edit manually - regenerate using tools/generate_enum_agents.py
"""

import os
from enum import Enum
from typing import Dict, List, Optional

import yaml


class AgentRole(Enum):
    """Enumeration of all available agent roles"""

    ADAPTIVE_DEPLOYMENT_STRATEGIST = "adaptive_deployment_strategist_agent"
    ALGORITHMIC_PROBLEM_SOLVER = "algorithmic_problem_solver_agent"
    ANALYTICS_SETUP = "analytics_setup_agent"
    BRAINJS_ML = "brainjs_ml_agent"
    BRANDING = "branding_agent"
    CAMPAIGN_MANAGER = "campaign_manager_agent"
    CODE_REVIEWER = "code_reviewer_agent"
    CODING = "coding_agent"
    COMMUNITY_STRATEGY = "community_strategy_agent"
    COMPLIANCE_SCOPE = "compliance_scope_agent"
    COMPLIANCE_TESTING = "compliance_testing_agent"
    CONTENT_STRATEGY = "content_strategy_agent"
    CORE_CONCEPT = "core_concept_agent"
    DEBUGGER = "debugger_agent"
    DEEP_RESEARCH = "deep_research_agent"
    DESIGN_QA_ANALYST = "design_qa_analyst"
    DESIGN_SYSTEM = "design_system_agent"
    DEVELOPMENT_ORCHESTRATOR = "development_orchestrator_agent"
    DEVOPS = "devops_agent"
    DOCUMENTATION = "documentation_agent"
    EFFICIENCY_OPTIMIZATION = "efficiency_optimization_agent"
    ELICITATION = "elicitation_agent"
    ETHICAL_REVIEW = "ethical_review_agent"
    EXPLORATORY_TESTER = "exploratory_tester_agent"
    FUNCTIONAL_TESTER = "functional_tester_agent"
    GENERIC_PURPOSE = "generic_purpose_agent"
    GRAPHIC_DESIGN = "graphic_design_agent"
    GROWTH_HACKING_IDEA = "growth_hacking_idea_agent"
    HEALTH_MONITOR = "health_monitor_agent"
    IDEA_GENERATION = "idea_generation_agent"
    IDEA_REFINEMENT = "idea_refinement_agent"
    INCIDENT_LEARNING = "incident_learning_agent"
    KNOWLEDGE_EVOLUTION = "knowledge_evolution_agent"
    LEAD_TESTING = "lead_testing_agent"
    MARKETING_STRATEGY_ORCHESTRATOR = "marketing_strategy_orchestrator"
    MARKET_RESEARCH = "market_research_agent"
    MCP_CONFIGURATION = "mcp_configuration_agent"
    MCP_RESEARCHER = "mcp_researcher_agent"
    NLU_PROCESSOR = "nlu_processor_agent"
    PERFORMANCE_LOAD_TESTER = "performance_load_tester_agent"
    PRD_ARCHITECT = "prd_architect_agent"
    PROJECT_INITIATOR = "project_initiator_agent"
    PROTOTYPING = "prototyping_agent"
    REMEDIATION = "remediation_agent"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis_agent"
    SCRIBE = "scribe_agent"
    SECURITY_AUDITOR = "security_auditor_agent"
    SECURITY_PENETRATION_TESTER = "security_penetration_tester_agent"
    SEO_SEM = "seo_sem_agent"
    SOCIAL_MEDIA_SETUP = "social_media_setup_agent"
    SWARM_SCALER = "swarm_scaler_agent"
    SYSTEM_ARCHITECT = "system_architect_agent"
    TASK_DEEP_MANAGER = "task_deep_manager_agent"
    TASK_PLANNING = "task_planning_agent"
    TASK_SYNC = "task_sync_agent"
    TECHNOLOGY_ADVISOR = "technology_advisor_agent"
    TECH_SPEC = "tech_spec_agent"
    TEST_CASE_GENERATOR = "test_case_generator_agent"
    TEST_ORCHESTRATOR = "test_orchestrator_agent"
    UAT_COORDINATOR = "uat_coordinator_agent"
    UBER_ORCHESTRATOR = "uber_orchestrator_agent"
    UI_DESIGNER = "ui_designer_agent"
    USABILITY_HEURISTIC = "usability_heuristic_agent"
    USER_FEEDBACK_COLLECTOR = "user_feedback_collector_agent"
    UX_RESEARCHER = "ux_researcher_agent"
    VIDEO_PRODUCTION = "video_production_agent"
    VISUAL_REGRESSION_TESTING = "visual_regression_testing_agent"
    WORKFLOW_ARCHITECT = "workflow_architect_agent"

    @classmethod
    def get_all_roles(cls) -> List[str]:
        """Get list of all available role slugs"""
        return [role.value for role in cls]

    @classmethod
    def get_role_by_slug(cls, slug: str) -> Optional["AgentRole"]:
        """Get role enum by slug"""
        for role in cls:
            if role.value == slug:
                return role
        return None

    @classmethod
    def is_valid_role(cls, slug: str) -> bool:
        """Check if a slug is a valid role"""
        return slug in cls.get_all_roles()

    @property
    def folder_name(self) -> str:
        """Get the folder name for this role"""
        return self.value.replace("-", "_")

    @property
    def display_name(self) -> str:
        """Get the display name for this role"""
        metadata = get_role_metadata_from_yaml(self)
        return metadata.get("name", "") if metadata else ""

    @property
    def description(self) -> str:
        """Get the role definition"""
        metadata = get_role_metadata_from_yaml(self)
        return metadata.get("role_definition", "") if metadata else ""

    @property
    def when_to_use(self) -> str:
        """Get usage guidelines"""
        metadata = get_role_metadata_from_yaml(self)
        return metadata.get("when_to_use", "") if metadata else ""

    @property
    def groups(self) -> List[str]:
        """Get role groups"""
        metadata = get_role_metadata_from_yaml(self)
        return metadata.get("groups", []) if metadata else []


# Metadata for each role - now loaded dynamically from YAML files


# Convenience functions for backward compatibility
def get_supported_roles() -> List[str]:
    """Get list of supported roles for rule generation"""
    return AgentRole.get_all_roles()


def get_role_metadata(role_slug: str) -> Optional[Dict[str, any]]:
    """Get metadata for a specific role"""
    return get_role_metadata_from_yaml(role_slug)


def get_role_folder_name(role_slug: str) -> Optional[str]:
    """Get folder name for a role slug"""
    role = AgentRole.get_role_by_slug(role_slug)
    if role:
        return role.folder_name
    return None


def get_yaml_lib_path(role_input) -> Optional[str]:
    """Get relative path to yaml-lib directory for a role

    Args:
        role_input: Either a role slug (string) or AgentRole enum

    Returns:
        Relative path to yaml-lib directory (e.g., "yaml-lib/coding_agent")
        or None if role is invalid
    """
    if isinstance(role_input, str):
        role = AgentRole.get_role_by_slug(role_input)
    elif isinstance(role_input, AgentRole):
        role = role_input
    else:
        return None

    if role:
        return f"cursor_agent/yaml-lib/{role.folder_name}"
    return None


def get_role_metadata_from_yaml(role_input) -> Optional[Dict[str, any]]:
    """Get role metadata by reading from YAML files

    Args:
        role_input: Either a role slug (string) or AgentRole enum

    Returns:
        Dictionary containing role metadata or None if role is invalid or file not found
    """
    if isinstance(role_input, str):
        role = AgentRole.get_role_by_slug(role_input)
    elif isinstance(role_input, AgentRole):
        role = role_input
    else:
        return None

    if not role:
        return None

    # Calculate folder name from role slug
    folder_name = role.value.replace("-", "_")

    # Build path to job_desc.yaml file
    yaml_path = os.path.join("cursor_agent", "yaml-lib", folder_name, "job_desc.yaml")

    try:
        with open(yaml_path, "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)

        if yaml_data:
            # Add folder_name and slug to the metadata
            yaml_data["folder_name"] = folder_name
            yaml_data["slug"] = role.value
            return yaml_data

    except (FileNotFoundError, yaml.YAMLError, IOError):
        # Return None if file doesn't exist or can't be parsed
        pass

    return None


# Legacy role mappings for backward compatibility
LEGACY_ROLE_MAPPINGS = {
    "senior_developer": "coding_agent",
    "platform_engineer": "devops_agent",
    "qa_engineer": "functional_tester_agent",
    "code_reviewer": "code_reviewer_agent",
    "devops_engineer": "devops_agent",
    "security_engineer": "security_auditor_agent",
    "technical_writer": "documentation_agent",
    "task_planner": "task_planning_agent",
    "context_engineer": "core_concept_agent",
    "cache_engineer": "efficiency_optimization_agent",
    "metrics_engineer": "analytics_setup_agent",
    "cli_engineer": "coding_agent",
}


def resolve_legacy_role(legacy_role: str) -> Optional[str]:
    """Resolve legacy role names to current slugs"""
    if not legacy_role:
        return None

    # Clean up the role name (remove @ prefix, strip whitespace)
    clean_role = legacy_role.strip().lstrip("@")

    # First check if it's already a valid role
    if AgentRole.is_valid_role(clean_role):
        return clean_role

    # Check legacy mappings
    resolved = LEGACY_ROLE_MAPPINGS.get(clean_role)
    if resolved:
        # Validate that the resolved role is actually valid
        if AgentRole.is_valid_role(resolved):
            return resolved

    # Try converting hyphens to underscores for common variants
    underscore_variant = clean_role.replace("-", "_")
    if AgentRole.is_valid_role(underscore_variant):
        return underscore_variant

    # Try converting underscores to hyphens (less common but possible)
    hyphen_variant = clean_role.replace("_", "-")
    if AgentRole.is_valid_role(hyphen_variant):
        return hyphen_variant

    # Return None if no valid resolution found
    return None


def get_all_role_slugs_with_legacy() -> List[str]:
    """Get all role slugs including legacy mappings"""
    current_roles = AgentRole.get_all_roles()
    legacy_roles = list(LEGACY_ROLE_MAPPINGS.keys())
    return current_roles + legacy_roles
