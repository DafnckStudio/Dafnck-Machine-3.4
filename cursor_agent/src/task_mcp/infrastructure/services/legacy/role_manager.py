"""
Role management functionality for the Cursor Agent system.
Handles loading, analyzing, and managing agent roles.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ....domain.enums import AgentRole as AgentRoleEnum
from .models import AgentRole


class RoleManager:
    """Manages agent roles and role-related operations"""

    def __init__(self, lib_dir: Path):
        self.lib_dir = lib_dir
        self.roles = {}

        # Use the new AgentRole enum for role mappings
        self.assignee_to_role_mapping = self._build_assignee_mapping()

    def _build_assignee_mapping(self) -> Dict[str, str]:
        """Build assignee to role mapping using AgentRole enum"""
        mapping = {}

        # Common role mappings
        role_mappings = {
            AgentRoleEnum.CODING: [
                "Lead Developer",
                "Backend Developer",
                "Frontend Developer",
                "AI Systems Developer",
                "Integration Developer",
                "Security Developer",
                "Platform Engineer",
                "Senior Developer",
                "DevOps Engineer",
            ],
            AgentRoleEnum.TASK_PLANNING: [
                "Systems Analyst",
                "Technical Writer",
                "Task Planner",
            ],
            AgentRoleEnum.FUNCTIONAL_TESTER: [
                "QA Engineer",
                "QA Lead",
                "Performance Engineer",
            ],
            AgentRoleEnum.CODE_REVIEWER: ["Code Reviewer"],
        }

        # Build the mapping
        for role_enum, assignees in role_mappings.items():
            role_value = role_enum.value
            for assignee in assignees:
                mapping[assignee] = role_value
                mapping[assignee.lower()] = role_value  # Add lowercase mapping

            # Add the role value itself
            mapping[role_value] = role_value

        return mapping

    def get_available_roles(self) -> List[str]:
        """Get list of all available role names - scans directory or returns fallback"""
        if not self.lib_dir.exists():
            # Return fallback roles for test environments
            return ["senior_developer", "task_planner", "qa_engineer", "code_reviewer"]

        # Return all supported legacy role names
        # These map to actual directories, but we want to expose all legacy names
        supported_legacy_roles = [
            "cache_engineer",  # maps to efficiency_optimization_agent
            "cli_engineer",  # maps to coding_agent
            "code_reviewer",  # maps to code_reviewer_agent
            "context_engineer",  # maps to core_concept_agent
            "devops_engineer",  # maps to devops_agent
            "metrics_engineer",  # maps to analytics_setup_agent
            "platform_engineer",  # maps to devops_agent (same as devops_engineer)
            "qa_engineer",  # maps to functional_tester_agent
            "security_engineer",  # maps to security_auditor_agent
            "senior_developer",  # maps to coding_agent
            "task_planner",  # maps to task_planning_agent
            "technical_writer",  # maps to documentation_agent
        ]

        # Filter to only include roles where the underlying directory exists
        available_roles = []
        legacy_to_directory_mapping = {
            "qa_engineer": "functional_tester_agent",
            "senior_developer": "coding_agent",
            "task_planner": "task_planning_agent",
            "code_reviewer": "code_reviewer_agent",
            "cache_engineer": "efficiency_optimization_agent",
            "context_engineer": "core_concept_agent",
            "devops_engineer": "devops_agent",
            "security_engineer": "security_auditor_agent",
            "technical_writer": "documentation_agent",
            "platform_engineer": "devops_agent",
            "metrics_engineer": "analytics_setup_agent",
            "cli_engineer": "coding_agent",
        }

        for legacy_role in supported_legacy_roles:
            directory_name = legacy_to_directory_mapping.get(legacy_role, legacy_role)
            role_dir = self.lib_dir / directory_name

            # Check if mapped directory exists OR if legacy name directory exists (for tests)
            legacy_dir = self.lib_dir / legacy_role
            if (role_dir.exists() and (role_dir / "job_desc.yaml").exists()) or (
                legacy_dir.exists() and (legacy_dir / "job_desc.yaml").exists()
            ):
                available_roles.append(legacy_role)

        return sorted(available_roles)

    def load_specific_roles(self, role_names: List[str]) -> Dict[str, AgentRole]:
        """Load only the specified roles from library"""
        loaded_roles = {}

        if not self.lib_dir.exists():
            print("⚠️  Library directory not found")
            # Fallback for test environments - create mock roles
            for role_name in role_names:
                if role_name in [
                    "senior_developer",
                    "task_planner",
                    "qa_engineer",
                    "code_reviewer",
                ]:
                    mock_role = self._create_mock_role(role_name)
                    loaded_roles[role_name] = mock_role
                    print(f"✅ Created mock role: {mock_role.name}")
            self.roles = loaded_roles
            return loaded_roles

        for role_name in role_names:
            # Clean up role name
            role_name = role_name.lstrip("@")

            # Map legacy role names to actual directory names
            legacy_to_directory_mapping = {
                "qa_engineer": "functional_tester_agent",
                "senior_developer": "coding_agent",
                "task_planner": "task_planning_agent",
                "code_reviewer": "code_reviewer_agent",
                "cache_engineer": "efficiency_optimization_agent",
                "context_engineer": "core_concept_agent",
                "devops_engineer": "devops_agent",
                "security_engineer": "security_auditor_agent",
                "technical_writer": "documentation_agent",
                "platform_engineer": "devops_agent",
                "metrics_engineer": "analytics_setup_agent",
                "cli_engineer": "coding_agent",
            }

            # Try both the mapped directory name and the original role name
            directory_name = legacy_to_directory_mapping.get(role_name, role_name)
            role_dir = self.lib_dir / directory_name

            # If mapped directory doesn't exist, try the legacy name directly (for tests)
            if not role_dir.exists():
                role_dir = self.lib_dir / role_name

            actual_role_name = role_name  # Keep the legacy name as the key

            if role_dir.exists():
                try:
                    role = self._load_role_from_directory(role_dir)
                    if role:
                        loaded_roles[actual_role_name] = role
                        print(f"✅ Loaded role: {role.name}")
                    else:
                        print(f"⚠️  Failed to load role: {role_name}")
                except Exception as e:
                    print(f"⚠️  Error loading role {role_name}: {e}")
            else:
                print(f"⚠️  Role directory not found: {role_name} (tried {role_dir})")

        # Update the instance roles
        self.roles = loaded_roles
        return loaded_roles

    def analyze_task_requirements(
        self, title: str, description: str, requirements: List[str]
    ) -> List[str]:
        """Analyze task to determine which roles are needed"""
        required_roles = []

        # Convert to lowercase for analysis
        text_to_analyze = f"{title} {description} {' '.join(requirements)}".lower()

        # Always include task_planner for complex tasks
        complexity_indicators = [
            "complex",
            "multiple",
            "system",
            "architecture",
            "integration",
            "full",
            "complete",
            "comprehensive",
            "large",
            "enterprise",
        ]

        simple_indicators = ["fix", "bug", "small", "quick", "simple", "minor", "patch"]

        # Determine if this is a complex task
        is_complex = any(
            indicator in text_to_analyze for indicator in complexity_indicators
        )
        is_simple = any(indicator in text_to_analyze for indicator in simple_indicators)

        # Planning indicators
        planning_indicators = [
            "plan",
            "design",
            "architecture",
            "strategy",
            "roadmap",
            "breakdown",
            "analyze",
            "requirements",
        ]

        # Coding indicators
        coding_indicators = [
            "implement",
            "code",
            "develop",
            "build",
            "create",
            "function",
            "class",
            "module",
            "api",
            "feature",
        ]

        # Testing indicators
        testing_indicators = [
            "test",
            "testing",
            "validation",
            "verify",
            "quality",
            "qa",
        ]

        # Review indicators
        review_indicators = [
            "review",
            "audit",
            "optimize",
            "refactor",
            "improve",
            "security",
        ]

        # Determine required roles based on content analysis
        needs_planning = any(
            indicator in text_to_analyze for indicator in planning_indicators
        )
        needs_coding = any(
            indicator in text_to_analyze for indicator in coding_indicators
        )
        needs_testing = any(
            indicator in text_to_analyze for indicator in testing_indicators
        )
        needs_review = any(
            indicator in text_to_analyze for indicator in review_indicators
        )

        # Role assignment logic
        if is_simple and needs_coding and not (needs_planning or needs_testing):
            # Simple coding task - just developer
            required_roles = ["senior_developer"]
        elif needs_planning and not (needs_coding or needs_testing):
            # Planning only task
            required_roles = ["task_planner"]
        elif needs_testing and not needs_coding:
            # Testing only task
            required_roles = ["qa_engineer"]
        elif needs_review and not needs_coding:
            # Review only task
            required_roles = ["code_reviewer"]
        elif is_complex or (needs_planning and needs_coding and needs_testing):
            # Complex task - full workflow
            required_roles = ["task_planner", "senior_developer", "qa_engineer"]
        elif needs_planning and needs_coding:
            # Planning + coding
            required_roles = ["task_planner", "senior_developer"]
        elif needs_coding and needs_testing:
            # Coding + testing
            required_roles = ["senior_developer", "qa_engineer"]
        elif needs_coding and needs_review:
            # Coding + review
            required_roles = ["senior_developer", "code_reviewer"]
        else:
            # Default: assume it's a development task
            required_roles = ["senior_developer"]

        print("🤖 Task analysis complete:")
        print(f"   Complex: {is_complex}, Simple: {is_simple}")
        print(
            f"   Needs: Planning={needs_planning}, Coding={needs_coding}, Testing={needs_testing}, Review={needs_review}"
        )
        print(f"   Required roles: {required_roles}")

        return required_roles

    def get_role_from_assignee(self, assignee: str) -> Optional[str]:
        """Get role directory name from assignee - returns legacy names for backward compatibility"""
        # Legacy role mapping - return legacy names directly when requested
        legacy_roles = {
            "qa_engineer": "qa_engineer",
            "senior_developer": "senior_developer",
            "task_planner": "task_planner",
            "code_reviewer": "code_reviewer",
            "cache_engineer": "cache_engineer",
            "context_engineer": "context_engineer",
            "devops_engineer": "devops_engineer",
            "security_engineer": "security_engineer",
            "technical_writer": "technical_writer",
            "platform_engineer": "platform_engineer",
            "metrics_engineer": "metrics_engineer",
            "cli_engineer": "cli_engineer",
        }

        # Return legacy role if it exists
        if assignee in legacy_roles:
            return legacy_roles[assignee]

        # Handle display names to legacy mapping
        display_name_mapping = {
            "QA Engineer": "qa_engineer",
            "Senior Developer": "senior_developer",
            "Lead Developer": "senior_developer",
            "Task Planner": "task_planner",
            "Code Reviewer": "code_reviewer",
        }

        if assignee in display_name_mapping:
            return display_name_mapping[assignee]

        # First try direct mapping from the assignee mapping
        role = self.assignee_to_role_mapping.get(assignee)
        if role:
            # Convert back to legacy name if it's a new enum value
            reverse_legacy_mapping = {
                "functional-tester-agent": "qa_engineer",
                "coding-agent": "senior_developer",
                "task-planning-agent": "task_planner",
                "code-reviewer-agent": "code_reviewer",
                "efficiency-optimization-agent": "cache_engineer",
                "core-concept-agent": "context_engineer",
                "devops-agent": "devops_engineer",
                "security-auditor-agent": "security_engineer",
                "documentation-agent": "technical_writer",
                "analytics-setup-agent": "metrics_engineer",
            }
            return reverse_legacy_mapping.get(role, role)

        # Try to find a close match using AgentRole enum
        if AgentRoleEnum.is_valid_role(assignee):
            return assignee

        return None

    def load_role_for_assignee(self, assignee: str) -> bool:
        """Load the appropriate role for an assignee"""
        role_name = self.get_role_from_assignee(assignee)
        if not role_name:
            print(f"⚠️  No role mapping found for assignee: {assignee}")
            return False

        try:
            self.load_specific_roles([role_name])
            return True
        except Exception as e:
            print(f"⚠️  Failed to load role {role_name} for assignee {assignee}: {e}")
            return False

    def _create_mock_role(self, role_name: str) -> AgentRole:
        """Create a mock role for testing environments"""
        role_configs = {
            "senior_developer": {
                "name": "Senior Developer",
                "persona": "Expert Senior Developer focused on clean, maintainable, and efficient code",
                "primary_focus": "Implementation of features, code quality, and technical excellence",
                "rules": [
                    "Write clean, readable, and well-documented code",
                    "Follow established coding standards and conventions",
                    "Use meaningful variable and function names",
                    "Implement proper error handling and input validation",
                    "Consider edge cases and error scenarios",
                ],
            },
            "task_planner": {
                "name": "Task Planner",
                "persona": "Strategic Task Planner focused on project organization and planning",
                "primary_focus": "Task breakdown, planning, and project organization",
                "rules": [
                    "Break down complex tasks into manageable subtasks",
                    "Create clear and actionable task descriptions",
                    "Prioritize tasks based on dependencies and importance",
                    "Ensure all requirements are captured and understood",
                    "Plan for testing and validation at each step",
                ],
            },
            "qa_engineer": {
                "name": "QA Engineer",
                "persona": "Quality Assurance Engineer focused on testing and validation",
                "primary_focus": "Testing, quality assurance, and validation",
                "rules": [
                    "Create comprehensive test cases for all functionality",
                    "Validate both positive and negative test scenarios",
                    "Ensure edge cases are properly tested",
                    "Document test results and findings clearly",
                    "Focus on user experience and usability",
                ],
            },
            "code_reviewer": {
                "name": "Code Reviewer",
                "persona": "Code Reviewer focused on code quality and best practices",
                "primary_focus": "Code review, quality assurance, and best practices",
                "rules": [
                    "Review code for adherence to coding standards",
                    "Check for potential security vulnerabilities",
                    "Ensure proper error handling and edge cases",
                    "Validate code documentation and comments",
                    "Suggest improvements for maintainability",
                ],
            },
        }

        config = role_configs.get(role_name, role_configs["senior_developer"])
        return AgentRole(
            name=config["name"],
            persona=config["persona"],
            primary_focus=config["primary_focus"],
            rules=config["rules"],
            context_instructions=[],
            tools_guidance=[],
            output_format="Complete code files with documentation and usage examples",
        )

    def _load_role_from_directory(self, role_dir: Path) -> Optional[AgentRole]:
        """Load a single role from its directory structure"""
        job_desc_file = role_dir / "job_desc.yaml"

        if not job_desc_file.exists():
            return None

        # Load job description and metadata
        job_desc_data = self._read_yaml_file(job_desc_file)
        if not job_desc_data:
            return None

        # Extract role information
        role_name = job_desc_data.get("name", role_dir.name.replace("_", " ").title())
        persona = job_desc_data.get("persona", f"Expert {role_name}")
        primary_focus = job_desc_data.get(
            "primary_focus",
            job_desc_data.get(
                "description",
                job_desc_data.get("role_definition", f"{role_name} specialist"),
            ),
        )

        # Load rules from rules directory
        rules = self._load_rules_from_yaml_directory(role_dir / "rules")

        # Load context instructions from contexts directory
        context_instructions = self._load_context_instructions_from_yaml_directory(
            role_dir / "contexts"
        )

        # Load tools guidance from tools directory
        tools_guidance = self._load_tools_guidance_from_yaml_directory(
            role_dir / "tools"
        )

        # Load output format from output_format directory
        output_format = self._load_output_format_from_yaml_directory(
            role_dir / "output_format"
        )

        return AgentRole(
            name=role_name,
            persona=persona,
            primary_focus=primary_focus,
            rules=rules,
            context_instructions=context_instructions,
            tools_guidance=tools_guidance,
            output_format=output_format,
        )

    def _read_yaml_file(self, file_path: Path) -> Dict:
        """Read and parse YAML file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️  Failed to read YAML file {file_path}: {e}")
            return {}

    def _load_rules_from_yaml_directory(self, rules_dir: Path) -> List[str]:
        """Load rules from YAML files in rules directory - Enhanced with recursive loading"""
        rules = []
        if not rules_dir.exists():
            return rules

        # Enhanced: Recursively find all YAML files in subdirectories
        rule_files = sorted(rules_dir.rglob("*.yaml"))

        for rule_file in rule_files:
            rule_data = self._read_yaml_file(rule_file)

            # Handle different YAML structures
            if "rules" in rule_data:
                # If rules are in a 'rules' key
                if isinstance(rule_data["rules"], list):
                    rules.extend(rule_data["rules"])
                elif isinstance(rule_data["rules"], str):
                    rules.append(rule_data["rules"])
            elif "items" in rule_data:
                # If rules are in an 'items' key
                if isinstance(rule_data["items"], list):
                    rules.extend(rule_data["items"])
            else:
                # If the file contains a direct list or single rule
                if isinstance(rule_data, list):
                    rules.extend(rule_data)
                elif isinstance(rule_data, str):
                    rules.append(rule_data)
                elif isinstance(rule_data, dict):
                    # Enhanced: Use complex YAML extraction for structured files
                    extracted_rules = self._extract_guidance_from_complex_yaml(
                        rule_data, rule_file.name
                    )
                    if extracted_rules:
                        rules.extend(extracted_rules)
                    else:
                        # Fallback to original logic
                        for key, value in rule_data.items():
                            if isinstance(value, list):
                                rules.extend(value)
                            elif isinstance(value, str) and key not in [
                                "name",
                                "description",
                                "category",
                            ]:
                                rules.append(value)

        return rules

    def _load_context_instructions_from_yaml_directory(
        self, contexts_dir: Path
    ) -> List[str]:
        """Load context instructions from YAML files in contexts directory - Enhanced with recursive loading"""
        instructions = []
        if not contexts_dir.exists():
            return instructions

        # Enhanced: Recursively find all YAML files in subdirectories
        context_files = sorted(contexts_dir.rglob("*.yaml"))

        for context_file in context_files:
            context_data = self._read_yaml_file(context_file)

            # Handle different YAML structures
            if "instructions" in context_data:
                if isinstance(context_data["instructions"], list):
                    instructions.extend(context_data["instructions"])
                elif isinstance(context_data["instructions"], str):
                    instructions.append(context_data["instructions"])
            elif "items" in context_data:
                if isinstance(context_data["items"], list):
                    instructions.extend(context_data["items"])
            else:
                # Handle direct list or single instruction
                if isinstance(context_data, list):
                    instructions.extend(context_data)
                elif isinstance(context_data, str):
                    instructions.append(context_data)
                elif isinstance(context_data, dict):
                    # Enhanced: Use complex YAML extraction for structured files
                    extracted_instructions = self._extract_guidance_from_complex_yaml(
                        context_data, context_file.name
                    )
                    if extracted_instructions:
                        instructions.extend(extracted_instructions)
                    else:
                        # Fallback to original logic
                        for key, value in context_data.items():
                            if isinstance(value, list):
                                instructions.extend(value)
                            elif isinstance(value, str) and key not in [
                                "name",
                                "description",
                                "category",
                            ]:
                                instructions.append(value)

        return instructions

    def _load_tools_guidance_from_yaml_directory(self, tools_dir) -> List[str]:
        """Load tools guidance from YAML files in tools directory - Enhanced with structured extraction"""
        from pathlib import Path

        # Convert string to Path if needed
        if isinstance(tools_dir, str):
            tools_dir = Path(tools_dir)

        guidance = []
        if not tools_dir.exists():
            return guidance

        tool_files = sorted(
            [f for f in tools_dir.iterdir() if f.is_file() and f.suffix == ".yaml"]
        )

        for tool_file in tool_files:
            tool_data = self._read_yaml_file(tool_file)

            # First try to extract individual guidance items from complex YAML
            extracted_items = self._extract_guidance_from_complex_yaml(
                tool_data, tool_file.name
            )

            if extracted_items:
                # Add extracted items with file prefix for context
                for item in extracted_items:
                    guidance.append(f"📌 {tool_file.name}|{item}")
            else:
                # Fallback to traditional extraction methods
                if "guidance" in tool_data:
                    if isinstance(tool_data["guidance"], list):
                        for item in tool_data["guidance"]:
                            guidance.append(f"📌 {tool_file.name}|{item}")
                    elif isinstance(tool_data["guidance"], str):
                        guidance.append(f"📌 {tool_file.name}|{tool_data['guidance']}")
                elif "tools" in tool_data:
                    if isinstance(tool_data["tools"], list):
                        for item in tool_data["tools"]:
                            guidance.append(f"📌 {tool_file.name}|{item}")
                elif "items" in tool_data:
                    if isinstance(tool_data["items"], list):
                        for item in tool_data["items"]:
                            guidance.append(f"📌 {tool_file.name}|{item}")
                else:
                    # Use enhanced formatting as final fallback
                    formatted_content = self._format_yaml_content_enhanced(
                        tool_data, tool_file.name
                    )
                    guidance.append(f"📌 {tool_file.name}|{formatted_content}")

        return guidance

    def _format_yaml_content_enhanced(
        self, yaml_data: Dict[str, Any], filename: str
    ) -> str:
        """Enhanced formatting for YAML content with proper structure and readability"""
        if not yaml_data:
            return ""

        # Detect content type and apply appropriate formatting
        if self._is_checklist_yaml(yaml_data, filename):
            return self._format_checklist_yaml_enhanced(yaml_data)
        elif self._is_workflow_yaml(yaml_data, filename):
            return self._format_workflow_yaml_enhanced(yaml_data)
        else:
            return self._format_generic_yaml_enhanced(yaml_data)

    def _is_checklist_yaml(self, data: Dict[str, Any], filename: str) -> bool:
        """Check if YAML is a checklist type"""
        return (
            "checklist" in filename
            or "assessment" in data
            or "complexity_classification" in str(data)
            or "resource_planning" in data
        )

    def _is_workflow_yaml(self, data: Dict[str, Any], filename: str) -> bool:
        """Check if YAML is a workflow type"""
        return (
            "workflow" in filename
            or "phases" in data
            or "feature_types" in data
            or "lite_workflow" in filename
        )

    def _format_checklist_yaml_enhanced(self, data: Dict[str, Any]) -> str:
        """Format checklist YAML with structured decision guide"""
        content = []

        # Task Assessment Section
        content.append("## 📋 Task Assessment & Planning Guide")
        content.append("")

        # Complexity Classification
        if "assessment" in data and "initial" in data["assessment"]:
            initial = data["assessment"]["initial"]
            if "complexity_classification" in initial:
                content.append("### 🎯 Step 1: Classify Task Complexity")
                content.append("")
                content.append("| Complexity | Duration | Criteria |")
                content.append("|------------|----------|----------|")

                complexity = initial["complexity_classification"]
                complexity_order = ["micro", "standard", "complex", "very_complex"]
                for level in complexity_order:
                    if level in complexity:
                        item = complexity[level]
                        duration = item.get("duration", "N/A")
                        criteria = ", ".join(item.get("criteria", []))
                        content.append(
                            f"| **{level.title()}** | {duration} | {criteria} |"
                        )

                content.append("")

            # Urgency Assessment
            if "urgency_levels" in initial:
                content.append("### ⚡ Step 2: Assess Urgency")
                content.append("")
                for level, level_data in initial["urgency_levels"].items():
                    desc = level_data.get("description", "")
                    shortcuts = (
                        "✅" if level_data.get("shortcuts_available", False) else "❌"
                    )
                    content.append(
                        f"- **{level.title()}**: {desc} (Shortcuts: {shortcuts})"
                    )
                content.append("")

        # Resource Planning
        if "resource_planning" in data:
            content.append("### 👥 Step 3: Plan Required Roles")
            content.append("")

            rp = data["resource_planning"]

            # Always required roles
            if (
                "role_requirements" in rp
                and "always_required" in rp["role_requirements"]
            ):
                always_req = rp["role_requirements"]["always_required"]
                content.append(f"**Always Required:** {', '.join(always_req)}")
                content.append("")

            # Conditional roles table
            if (
                "role_requirements" in rp
                and "conditional_roles" in rp["role_requirements"]
            ):
                content.append("**Conditional Roles:**")
                content.append("")
                content.append("| Role | Required For | Skip Conditions |")
                content.append("|------|--------------|-----------------|")

                conditional = rp["role_requirements"]["conditional_roles"]
                for role, role_data in conditional.items():
                    required_for = ", ".join(role_data.get("required_for", []))
                    skip_conditions = "; ".join(
                        role_data.get("skip_conditions", role_data.get("skip_for", []))
                    )
                    content.append(
                        f"| {role.replace('_', ' ').title()} | {required_for} | {skip_conditions} |"
                    )

                content.append("")

        # Phase Selection Logic
        if "phase_selection" in data:
            content.append("### 🔄 Step 4: Select Workflow Phases")
            content.append("")

            ps = data["phase_selection"]
            complexity_order = ["micro", "standard", "complex", "very_complex"]
            for feature_type in complexity_order:
                type_key = f"{feature_type}_feature"
                if type_key in ps:
                    feature_data = ps[type_key]
                    included = feature_data.get("included_phases", [])
                    skipped = feature_data.get("skipped_phases", [])

                    content.append(f"#### {feature_type.title()} Feature")
                    content.append(f"- **Phases:** {included}")
                    if skipped:
                        content.append(f"- **Skip:** {skipped}")

                    # Additional requirements
                    if "additional_requirements" in feature_data:
                        reqs = feature_data["additional_requirements"]
                        content.append(f"- **Extra Requirements:** {'; '.join(reqs)}")

                    content.append("")

        # Timeline Estimation
        if "timeline_estimation" in data:
            content.append("### ⏱️ Step 5: Estimate Timeline")
            content.append("")

            te = data["timeline_estimation"]

            # Base estimates
            if "base_estimates" in te:
                content.append("**Base Estimates:**")
                for complexity, duration in te["base_estimates"].items():
                    content.append(f"- {complexity.title()}: {duration}")
                content.append("")

            # Adjustment factors
            if "factors" in te:
                content.append("**Adjustment Factors:**")
                factors = te["factors"]
                for factor_type, values in factors.items():
                    content.append(f"- **{factor_type.replace('_', ' ').title()}:**")
                    for level, multiplier in values.items():
                        content.append(f"  - {level.title()}: {multiplier}x")
                content.append("")

        return "\n".join(content)

    def _format_workflow_yaml_enhanced(self, data: Dict[str, Any]) -> str:
        """Format workflow YAML with execution guide"""
        content = []

        content.append("## 🔄 Workflow Execution Guide")
        content.append("")

        # Feature Types Overview
        if "feature_types" in data:
            content.append("### 📊 Feature Types Overview")
            content.append("")
            content.append("| Type | Duration | Description | Phases |")
            content.append("|------|----------|-------------|--------|")

            for type_name, type_data in data["feature_types"].items():
                duration = type_data.get("duration", "N/A")
                description = type_data.get("description", "")
                phases = str(type_data.get("phases", "See docs"))
                content.append(
                    f"| **{type_name.title()}** | {duration} | {description} | {phases} |"
                )

            content.append("")

        # Phase Details (show first 5 phases to avoid overwhelming output)
        if "phases" in data:
            content.append("### 🎯 Phase Execution Details")
            content.append("")

            phases = data["phases"]
            phase_keys = sorted(
                phases.keys(), key=lambda x: int(x) if str(x).isdigit() else 999
            )

            for phase_num in phase_keys[:5]:  # Limit to first 5 phases
                phase_data = phases[phase_num]

                name = phase_data.get("name", f"Phase {phase_num}")
                role = phase_data.get("role", "N/A")
                duration = phase_data.get("duration", "N/A")
                icon = phase_data.get("icon", "📌")

                content.append(f"#### {icon} Phase {phase_num}: {name}")
                content.append(f"**Role:** {role} | **Duration:** {duration}")
                content.append("")

                # Deliverables (limit to first 3)
                if "deliverables" in phase_data:
                    content.append("**Key Deliverables:**")
                    for deliverable in phase_data["deliverables"][:3]:
                        content.append(f"- {deliverable}")
                    if len(phase_data["deliverables"]) > 3:
                        content.append(
                            f"- ... and {len(phase_data['deliverables']) - 3} more"
                        )
                    content.append("")

                # Exit Criteria (limit to first 3)
                if "exit_criteria" in phase_data:
                    content.append("**Exit Criteria:**")
                    for criteria in phase_data["exit_criteria"][:3]:
                        content.append(f"- ✅ {criteria}")
                    if len(phase_data["exit_criteria"]) > 3:
                        content.append(
                            f"- ... and {len(phase_data['exit_criteria']) - 3} more"
                        )
                    content.append("")

                content.append("---")
                content.append("")

            if len(phase_keys) > 5:
                content.append(f"*... and {len(phase_keys) - 5} more phases defined*")
                content.append("")

        return "\n".join(content)

    def _format_generic_yaml_enhanced(self, data: Dict[str, Any]) -> str:
        """Format generic YAML with improved structure"""
        content = []

        content.append("## 🛠️ Tools & Guidance")
        content.append("")

        # Extract guidance from various structures
        if "guidance" in data:
            guidance = data["guidance"]
            if isinstance(guidance, list):
                content.append("### 📋 Key Guidelines")
                for item in guidance:
                    content.append(f"- {item}")
                content.append("")
            elif isinstance(guidance, dict):
                for category, items in guidance.items():
                    content.append(f"### {category.replace('_', ' ').title()}")
                    if isinstance(items, list):
                        for item in items:
                            content.append(f"- {item}")
                    content.append("")

        # Tools section
        if "tools" in data:
            content.append("### 🔧 Available Tools")
            tools = data["tools"]
            if isinstance(tools, list):
                for tool in tools:
                    content.append(f"- {tool}")
            elif isinstance(tools, dict):
                for tool_name, tool_desc in tools.items():
                    content.append(f"- **{tool_name}**: {tool_desc}")
            content.append("")

        return "\n".join(content)

    def _load_output_format_from_yaml_directory(self, output_dir: Path) -> str:
        """Load output format from YAML files in output_format directory - Enhanced with recursive loading"""
        if not output_dir.exists():
            return "Structured output with clear documentation"

        # Enhanced: Recursively find all YAML files in subdirectories
        format_files = sorted(output_dir.rglob("*.yaml"))

        if format_files:
            format_data = self._read_yaml_file(format_files[0])  # Use first file

            # Handle different YAML structures
            if "format" in format_data:
                return str(format_data["format"])
            elif "description" in format_data:
                return str(format_data["description"])
            elif "output_format" in format_data:
                return str(format_data["output_format"])
            elif isinstance(format_data, str):
                return format_data
            elif isinstance(format_data, dict):
                # Try to build a format description from the structure
                if "structure" in format_data:
                    structure = format_data["structure"]
                    if isinstance(structure, list):
                        return (
                            f"{format_data.get('title', 'Output Format')}\n\nStructure:\n"
                            + "\n".join(
                                [f"{i+1}. {item}" for i, item in enumerate(structure)]
                            )
                        )
                    elif isinstance(structure, dict):
                        return (
                            f"{format_data.get('title', 'Output Format')}\n\nStructure:\n"
                            + "\n".join(
                                [
                                    f"- {key}: {value}"
                                    for key, value in structure.items()
                                ]
                            )
                        )

                # Fallback to first string value found
                for key, value in format_data.items():
                    if isinstance(value, str) and key not in ["name", "category"]:
                        return value

        return "Structured output with clear documentation"

    def _extract_guidance_from_complex_yaml(
        self, data: Dict[str, Any], filename: str
    ) -> List[str]:
        """Extract meaningful guidance from complex YAML structures"""
        guidance = []

        # Handle task_planner specific files
        if filename == "002_checklist.yaml":
            guidance.extend(self._extract_checklist_guidance(data))
        elif filename == "003_lite_workflow_config.yaml":
            guidance.extend(self._extract_workflow_guidance(data))
        else:
            # Generic extraction for other complex files
            guidance.extend(self._extract_generic_guidance(data))

        return guidance

    def _extract_checklist_guidance(self, data: Dict[str, Any]) -> List[str]:
        """Extract guidance from checklist YAML structure"""
        guidance = []

        # Extract checklist overview
        if "checklist" in data:
            checklist = data["checklist"]
            name = checklist.get("name", "Task Planning Checklist")
            description = checklist.get("description", "")
            guidance.append(f"📋 **{name}**: {description}")

        # Extract assessment criteria
        if "assessment" in data and "initial" in data["assessment"]:
            initial = data["assessment"]["initial"]
            if "complexity_classification" in initial:
                guidance.append("🎯 **Complexity Classification Guidelines:**")
                for complexity, details in initial["complexity_classification"].items():
                    criteria = details.get("criteria", [])
                    duration = details.get("duration", "Unknown")
                    guidance.append(
                        f"• **{complexity.title()}** ({duration}): {', '.join(criteria)}"
                    )

        # Extract resource planning
        if "resource_planning" in data:
            planning = data["resource_planning"]
            if "role_requirements" in planning:
                roles = planning["role_requirements"]
                if "always_required" in roles:
                    guidance.append(
                        f"👥 **Always Required Roles**: {', '.join(roles['always_required'])}"
                    )
                if "conditional_roles" in roles:
                    guidance.append(
                        "🔄 **Conditional Roles**: Based on complexity and requirements"
                    )

        # Extract phase selection logic
        if "phase_selection" in data:
            phases = data["phase_selection"]
            guidance.append("📊 **Phase Selection Guidelines:**")
            for feature_type, config in phases.items():
                if isinstance(config, dict):
                    included = config.get("included_phases", [])
                    skipped = config.get("skipped_phases", [])
                    guidance.append(
                        f"• **{feature_type.replace('_', ' ').title()}**: Include phases {included}, skip {skipped}"
                    )

        # Extract timeline estimation
        if "timeline_estimation" in data:
            timeline = data["timeline_estimation"]
            if "base_estimates" in timeline:
                guidance.append("⏱️ **Base Time Estimates:**")
                for complexity, estimate in timeline["base_estimates"].items():
                    guidance.append(f"• {complexity.title()}: {estimate}")

        return guidance

    def _extract_workflow_guidance(self, data: Dict[str, Any]) -> List[str]:
        """Extract guidance from workflow config YAML structure"""
        guidance = []

        # Extract workflow overview
        if "workflow" in data:
            workflow = data["workflow"]
            name = workflow.get("name", "Feature Generation Workflow")
            description = workflow.get("description", "")
            guidance.append(f"🔄 **{name}**: {description}")

        # Add specific Workflow Guidelines section
        guidance.append("🎯 **Workflow Guidelines**")

        # Extract feature types with workflow guidelines context
        if "feature_types" in data:
            guidance.append("🎯 **Feature Type Definitions:**")
            for feature_type, config in data["feature_types"].items():
                name = config.get("name", feature_type.title())
                duration = config.get("duration", "Unknown")
                description = config.get("description", "")
                phases = config.get("phases", [])
                guidance.append(f"• **{name}** ({duration}): {description}")
                if phases:
                    guidance.append(f"  Phases: {phases}")

        # Extract key phases information
        if "phases" in data:
            phases = data["phases"]
            guidance.append(f"📋 **Workflow Phases** ({len(phases)} phases defined):")

            # Show first few phases as examples
            for phase_id in sorted(list(phases.keys())[:5]):
                phase = phases[phase_id]
                name = phase.get("name", f"Phase {phase_id}")
                role = phase.get("role", "Unknown")
                duration = phase.get("duration", "Unknown")
                guidance.append(f"• **Phase {phase_id}: {name}** ({role}, {duration})")

        # Extract role information
        if "roles" in data:
            roles = data["roles"]
            guidance.append(f"👥 **Role Definitions** ({len(roles)} roles):")
            for role_name, role_config in list(roles.items())[:3]:  # Show first 3
                name = role_config.get("name", role_name)
                focus = role_config.get("primary_focus", "Unknown")
                guidance.append(f"• **{name}**: {focus}")

        return guidance

    def _extract_generic_guidance(self, data: Dict[str, Any]) -> List[str]:
        """Generic extraction for other complex YAML files"""
        guidance = []

        # Look for common patterns
        for key, value in data.items():
            if isinstance(value, list):
                guidance.extend(value)
            elif isinstance(value, str) and key not in [
                "name",
                "description",
                "category",
            ]:
                guidance.append(value)
            elif isinstance(value, dict):
                # Look for nested guidance
                if "guidance" in value:
                    if isinstance(value["guidance"], list):
                        guidance.extend(value["guidance"])
                    elif isinstance(value["guidance"], str):
                        guidance.append(value["guidance"])
                elif "description" in value:
                    guidance.append(f"{key.title()}: {value['description']}")
                else:
                    # Handle nested rule structures like health_check.selfTest, error_handling.strategy
                    for nested_key, nested_value in value.items():
                        if isinstance(nested_value, str):
                            # Format as "Category - Subcategory: Rule content"
                            guidance.append(
                                f"{key.replace('_', ' ').title()} - {nested_key.replace('_', ' ').title()}: {nested_value}"
                            )
                        elif isinstance(nested_value, list):
                            guidance.extend(nested_value)
                        elif isinstance(nested_value, dict):
                            # Handle deeper nesting if needed
                            for deep_key, deep_value in nested_value.items():
                                if isinstance(deep_value, str):
                                    guidance.append(
                                        f"{key.replace('_', ' ').title()} - {nested_key.replace('_', ' ').title()} - {deep_key.replace('_', ' ').title()}: {deep_value}"
                                    )

        return guidance

    def _categorize_tools_guidance(
        self, guidance_items: List[str]
    ) -> Dict[str, List[str]]:
        """
        Categorize guidance items by file ID prefix and content structure.
        Files with same ID prefix (001_a, 001_b) are grouped together.
        Each file's content is parsed to preserve structure (paragraphs, tables, lists).
        """
        categories = {}

        # Group by file ID prefix (001_, 002_, etc.)
        file_groups = {}
        for item in guidance_items:
            if "|" in item:
                file_path, content = item.split("|", 1)
                file_name = file_path.split("/")[-1]

                # Extract ID prefix (001_, 002_, etc.)
                id_prefix = self._extract_id_prefix(file_name)

                if id_prefix not in file_groups:
                    file_groups[id_prefix] = []
                file_groups[id_prefix].append((file_path, content))

        # Process each file group
        for id_prefix, files in file_groups.items():
            category_content = []

            for file_path, content in files:
                parsed_content = self._parse_file_content_structure(file_path, content)
                category_content.extend(parsed_content)

            if category_content:
                categories[id_prefix] = category_content

        return categories

    def _extract_id_prefix(self, file_name: str) -> str:
        """Extract ID prefix from filename (001_, 002_, etc.)"""
        import re

        match = re.match(r"^(\d{3}_)", file_name)
        if match:
            return match.group(1)
        return "misc_"

    def _parse_file_content_structure(self, file_path: str, content: str) -> List[str]:
        """
        Parse file content while preserving structure (paragraphs, tables, lists).
        Extracts name, category, description and formats nested content properly.
        """
        try:
            import yaml

            data = yaml.safe_load(content)

            if not isinstance(data, dict):
                return [f"**File**: {file_path}\n**Content**: {content}"]

            parsed_items = []
            file_name = file_path.split("/")[-1]

            # Extract main properties
            main_props = self._extract_main_properties(data, file_name)
            if main_props:
                parsed_items.append(main_props)

            # Parse nested content structure
            nested_content = self._parse_nested_content(data, file_name)
            parsed_items.extend(nested_content)

            return parsed_items

        except Exception as e:
            return [
                f"**File**: {file_path}\n**Error parsing**: {str(e)}\n**Raw content**: {content[:200]}..."
            ]

    def _extract_main_properties(self, data: dict, file_name: str) -> str:
        """Extract main properties: name, category, description"""
        props = []
        props.append(f"**📄 File**: `{file_name}`")

        if "name" in data:
            props.append(f"**📋 Name**: {data['name']}")

        if "category" in data:
            props.append(f"**🏷️ Category**: {data['category']}")

        if "description" in data:
            props.append(f"**📝 Description**: {data['description']}")
        elif (
            "workflow" in data
            and isinstance(data["workflow"], dict)
            and "description" in data["workflow"]
        ):
            props.append(f"**📝 Description**: {data['workflow']['description']}")
        elif (
            "checklist" in data
            and isinstance(data["checklist"], dict)
            and "description" in data["checklist"]
        ):
            props.append(f"**📝 Description**: {data['checklist']['description']}")

        return "\n".join(props) if props else ""

    def _parse_nested_content(self, data: dict, file_name: str) -> List[str]:
        """Parse nested content structure based on file type"""
        content_items = []

        # Handle different content types
        if "checklist" in data:
            content_items.extend(self._parse_checklist_content(data["checklist"]))

        if "workflow" in data:
            content_items.extend(self._parse_workflow_content(data["workflow"]))

        if "feature_types" in data:
            content_items.extend(
                self._parse_feature_types_content(data["feature_types"])
            )

        if "phases" in data:
            content_items.extend(self._parse_phases_content(data["phases"]))

        if "assessment" in data:
            content_items.extend(self._parse_assessment_content(data["assessment"]))

        if "resource_planning" in data:
            content_items.extend(
                self._parse_resource_planning_content(data["resource_planning"])
            )

        if "guidance" in data and isinstance(data["guidance"], list):
            content_items.extend(self._parse_guidance_list(data["guidance"]))

        # Handle any other top-level sections
        for key, value in data.items():
            if key not in [
                "name",
                "category",
                "description",
                "checklist",
                "workflow",
                "feature_types",
                "phases",
                "assessment",
                "resource_planning",
                "guidance",
            ]:
                content_items.append(self._parse_generic_section(key, value))

        return content_items

    def _parse_checklist_content(self, checklist_data: dict) -> List[str]:
        """Parse checklist structure into formatted content"""
        items = []
        items.append("## 📋 Checklist Configuration")

        if "version" in checklist_data:
            items.append(f"**Version**: {checklist_data['version']}")

        return items

    def _parse_workflow_content(self, workflow_data: dict) -> List[str]:
        """Parse workflow structure into formatted content"""
        items = []
        items.append("## 🔄 Workflow Configuration")

        if "version" in workflow_data:
            items.append(f"**Version**: {workflow_data['version']}")

        return items

    def _parse_feature_types_content(self, feature_types: dict) -> List[str]:
        """Parse feature types into formatted table"""
        items = []
        items.append("## 🎯 Feature Type Definitions")

        # Create table header
        items.append("| Feature Type | Description |")
        items.append("|-----|----|")

        for feature_type, details in feature_types.items():
            name = details.get("name", feature_type.title())
            description = details.get("description", "No description")
            duration = details.get("duration", "Unknown")
            items.append(f"| {name} ({duration}) | {description} |")

        return items

    def _parse_phases_content(self, phases: dict) -> List[str]:
        """Parse phases into formatted content"""
        items = []
        items.append("## ⏱️ Workflow Phases")

        for phase_num, phase_data in phases.items():
            if isinstance(phase_data, dict):
                name = phase_data.get("name", f"Phase {phase_num}")
                role = phase_data.get("role", "Unknown")
                duration = phase_data.get("duration", "Unknown")
                items.append(f"**Phase {phase_num}: {name}** ({role}, {duration})")

                if "deliverables" in phase_data and isinstance(
                    phase_data["deliverables"], list
                ):
                    items.append("  - Deliverables:")
                    for deliverable in phase_data["deliverables"]:
                        items.append(f"    - {deliverable}")

        return items

    def _parse_assessment_content(self, assessment: dict) -> List[str]:
        """Parse assessment structure into formatted content"""
        items = []
        items.append("## 🔍 Assessment Guidelines")

        if (
            "initial" in assessment
            and "complexity_classification" in assessment["initial"]
        ):
            items.append("### Complexity Classification")
            complexity = assessment["initial"]["complexity_classification"]

            for level, details in complexity.items():
                duration = details.get("duration", "Unknown")
                items.append(f"**{level.title()}** ({duration})")
                if "criteria" in details:
                    for criterion in details["criteria"]:
                        items.append(f"  - {criterion}")

        return items

    def _parse_resource_planning_content(self, resource_planning: dict) -> List[str]:
        """Parse resource planning into formatted content"""
        items = []
        items.append("## 👥 Resource Planning")

        if "role_requirements" in resource_planning:
            roles = resource_planning["role_requirements"]

            if "always_required" in roles:
                items.append("### Always Required Roles")
                for role in roles["always_required"]:
                    items.append(f"  - {role}")

            if "conditional_roles" in roles:
                items.append("### Conditional Roles")
                for role, conditions in roles["conditional_roles"].items():
                    required_for = conditions.get("required_for", [])
                    items.append(f"**{role}**: Required for {', '.join(required_for)}")

        return items

    def _parse_guidance_list(self, guidance: list) -> List[str]:
        """Parse simple guidance list"""
        items = []
        items.append("## 📚 Guidance")

        for item in guidance:
            items.append(f"- {item}")

        return items

    def _parse_generic_section(self, key: str, value) -> str:
        """Parse any other section generically"""
        if isinstance(value, dict):
            return f"**{key.title()}**: {len(value)} items configured"
        elif isinstance(value, list):
            return f"**{key.title()}**: {len(value)} items listed"
        else:
            return f"**{key.title()}**: {str(value)[:100]}..."
