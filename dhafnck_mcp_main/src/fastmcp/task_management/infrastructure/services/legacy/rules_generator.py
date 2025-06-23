"""
Rules generation functionality for the Cursor Agent system.
Handles generating and formatting .cursor/rules files based on task context.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import re
import yaml
import glob

from .models import TaskContext, AgentRole


class TemplateEngine:
    """Template engine for dynamic content generation"""
    
    def __init__(self, lib_dir: Path):
        self.lib_dir = lib_dir
        self.template_cache = {}
        self.variable_pattern = re.compile(r'\{\{(\w+)\}\}')
        self._agent_cache = {}
    
    def render_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """Render template with variable substitution"""
        def replace_var(match):
            var_name = match.group(1)
            return str(variables.get(var_name, f'{{{{{var_name}}}}}'))
        
        return self.variable_pattern.sub(replace_var, template_content)
    
    def _discover_agent_directories(self) -> List[str]:
        """Dynamically discover all agent directories in yaml-lib"""
        if not self.lib_dir.exists():
            return []
        
        agent_dirs = []
        for item in self.lib_dir.iterdir():
            if item.is_dir() and item.name.endswith('_agent'):
                agent_dirs.append(item.name)
        
        return sorted(agent_dirs)
    
    def _normalize_role_name_to_directory(self, role_name: str) -> str:
        """Convert role name to expected directory name"""
        # Handle various role name formats and convert to directory format
        
        # Common mappings for legacy role names
        legacy_mappings = {
            'Senior Full-Stack Developer': 'coding_agent',
            'senior_developer': 'coding_agent',
            'Senior Task Planning Architect': 'task_planning_agent', 
            'Senior QA Engineer & Test Specialist': 'functional_tester_agent',
            'Senior Code Reviewer & Quality Assurance Specialist': 'code_reviewer_agent',
            'Task Planning Agent': 'task_planning_agent',
            'Coding Agent': 'coding_agent',
            'QA Engineer': 'functional_tester_agent',
            'Code Reviewer': 'code_reviewer_agent',
            'Documentation Agent': 'documentation_agent',
            'DevOps Agent': 'devops_agent',
            'Security Engineer': 'security_auditor_agent',
            'System Architect': 'system_architect_agent'
        }
        
        # Check legacy mappings first
        if role_name in legacy_mappings:
            return legacy_mappings[role_name]
        
        # Try to find by partial name match
        role_lower = role_name.lower()
        agent_dirs = self._discover_agent_directories()
        
        for agent_dir in agent_dirs:
            agent_name = agent_dir.replace('_agent', '').replace('_', ' ')
            if agent_name.lower() in role_lower or role_lower in agent_name.lower():
                return agent_dir
        
        # Fallback: convert role name to directory format
        normalized = role_name.lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove special chars
        normalized = re.sub(r'\s+', '_', normalized)     # Replace spaces with underscores
        
        # Add _agent suffix if not present
        if not normalized.endswith('_agent'):
            normalized += '_agent'
        
        return normalized
    
    def load_role_template(self, role_name: str) -> Optional[str]:
        """Load template for a specific role"""
        role_dir_name = self._normalize_role_name_to_directory(role_name)
        template_file = self.lib_dir / role_dir_name / "template.md"
        
        if template_file.exists():
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass
        
        return None
    
    def load_agent_data(self, role_name: str) -> Dict[str, Any]:
        """Load comprehensive agent data from YAML files"""
        role_dir_name = self._normalize_role_name_to_directory(role_name)
        
        # Use cache if available
        if role_dir_name in self._agent_cache:
            return self._agent_cache[role_dir_name]
        
        agent_dir = self.lib_dir / role_dir_name
        agent_data = {
            'name': role_name,
            'directory': role_dir_name,
            'exists': False,
            'job_desc': {},
            'contexts': {},
            'rules': {},
            'tools': {},
            'output_format': {}
        }
        
        if not agent_dir.exists():
            self._agent_cache[role_dir_name] = agent_data
            return agent_data
        
        agent_data['exists'] = True
        
        # Load job description
        job_desc_file = agent_dir / "job_desc.yaml"
        if job_desc_file.exists():
            try:
                with open(job_desc_file, 'r', encoding='utf-8') as f:
                    agent_data['job_desc'] = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Error loading job_desc.yaml for {role_dir_name}: {e}")
        
        # Load contexts
        contexts_dir = agent_dir / "contexts"
        if contexts_dir.exists():
            for context_file in contexts_dir.glob("*.yaml"):
                try:
                    with open(context_file, 'r', encoding='utf-8') as f:
                        context_data = yaml.safe_load(f) or {}
                        agent_data['contexts'][context_file.stem] = context_data
                except Exception as e:
                    print(f"Error loading context file {context_file}: {e}")
        
        # Load rules
        rules_dir = agent_dir / "rules"
        if rules_dir.exists():
            for rule_file in rules_dir.glob("*.yaml"):
                try:
                    with open(rule_file, 'r', encoding='utf-8') as f:
                        rule_data = yaml.safe_load(f) or {}
                        agent_data['rules'][rule_file.stem] = rule_data
                except Exception as e:
                    print(f"Error loading rule file {rule_file}: {e}")
        
        # Load tools
        tools_dir = agent_dir / "tools"
        if tools_dir.exists():
            for tool_file in tools_dir.glob("*.yaml"):
                try:
                    with open(tool_file, 'r', encoding='utf-8') as f:
                        tool_data = yaml.safe_load(f) or {}
                        agent_data['tools'][tool_file.stem] = tool_data
                except Exception as e:
                    print(f"Error loading tool file {tool_file}: {e}")
        
        # Load output format
        output_dir = agent_dir / "output_format"
        if output_dir.exists():
            for output_file in output_dir.glob("*.yaml"):
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        output_data = yaml.safe_load(f) or {}
                        agent_data['output_format'][output_file.stem] = output_data
                except Exception as e:
                    print(f"Error loading output format file {output_file}: {e}")
        
        # Cache the result
        self._agent_cache[role_dir_name] = agent_data
        return agent_data
    
    def get_default_template(self) -> str:
        """Get the default template structure"""
        return """---
description: {{description}}
globs: {{globs}}
alwaysApply: true
---

# {{role_name}} - {{phase_title}} Phase

## Current Task Context
**Task:** {{task_title}}
**Description:** {{task_description}}
**Phase:** {{phase_upper}}
**Task ID:** {{task_id}}

## Requirements
{{requirements}}

## Active Roles for This Task
**Primary Role (Current Phase):** {{role_name}}
**All Active Roles:** {{assigned_roles}}

{{all_roles_info}}
{{context_link_section}}

## Role & Persona
You are a **{{role_persona}}**.
**Primary Focus:** {{role_primary_focus}}

## Context Summary
{{context_summary}}

## Core Operating Rules
{{core_rules}}

## Context-Specific Instructions
{{context_instructions}}

## Tools & Output Guidance
{{tools_guidance}}

## Expected Output Format
{{output_format}}

## Phase-Specific Context
{{phase_specific_context}}

## Project Context
{{project_context}}

---
*Generated: {{generation_timestamp}}*
*Use 'python cursor_agent_cli.py next' to advance to next phase*
*Use 'python cursor_agent_cli.py roles' to see all available roles*
"""


class RulesTemplateSystem:
    """Advanced template system for rules generation"""
    
    def __init__(self, lib_dir: Path):
        self.lib_dir = lib_dir
        self.template_engine = TemplateEngine(lib_dir)
        self.content_builders = {
            'requirements': self._build_requirements_content,
            'core_rules': self._build_core_rules_content,
            'context_instructions': self._build_context_instructions_content,
            'tools_guidance': self._build_tools_guidance_content,
            'phase_specific_context': self._build_phase_specific_content,
            'project_context': self._build_project_context_content,
            'all_roles_info': self._build_all_roles_info_content,
            'context_link_section': self._build_context_link_content
        }
    
    def generate_rules_content(self, task: TaskContext, role: AgentRole, project_context: Dict) -> str:
        """Generate complete rules content using template system"""
        
        # Try to load role-specific template, fallback to default
        template_content = self.template_engine.load_role_template(role.name)
        if not template_content:
            template_content = self.template_engine.get_default_template()
        
        # Load comprehensive agent data from YAML files
        agent_data = self.template_engine.load_agent_data(role.name)
        
        # Build template variables
        variables = self._build_template_variables(task, role, project_context, agent_data)
        
        # Render template with variables
        return self.template_engine.render_template(template_content, variables)
    
    def _build_template_variables(self, task: TaskContext, role: AgentRole, project_context: Dict, agent_data: Dict) -> Dict[str, Any]:
        """Build all template variables for rendering"""
        project_root = project_context.get("project_root", Path("."))
        
        # Extract information from agent YAML data
        job_desc = agent_data.get('job_desc', {})
        contexts = agent_data.get('contexts', {})
        
        # Get display name from YAML or fallback to role name
        display_name = job_desc.get('name', role.name)
        
        # Get role definition and persona
        role_definition = job_desc.get('role_definition', role.persona)
        when_to_use = job_desc.get('when_to_use', '')
        
        # Extract custom instructions from contexts
        custom_instructions = ""
        for context_name, context_data in contexts.items():
            if 'custom_instructions' in context_data:
                custom_instructions = context_data['custom_instructions']
                break
        
        variables = {
            # Basic task information
            'task_title': task.title,
            'task_description': task.description,
            'task_id': task.id,
            'phase_title': task.current_phase.title(),
            'phase_upper': task.current_phase.upper(),
            'assigned_roles': ', '.join(task.assigned_roles),
            
            # Role information from YAML
            'role_name': display_name,
            'role_persona': role_definition or role.persona,
            'role_primary_focus': when_to_use or role.primary_focus,
            'output_format': role.output_format,
            'persona': role.persona,
            'persona_icon': role.persona_icon or '',
            
            # YAML frontmatter
            'description': f'Dynamic AI Agent Rules for {role.persona_icon or ""} {display_name}'.strip(),
            'globs': job_desc.get('globs', ['**/*']),
            
            # Context summary
            'context_summary': self._generate_context_summary(task),
            
            # Generation timestamp
            'generation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Build complex content sections
        for content_type, builder in self.content_builders.items():
            variables[content_type] = builder(task, role, project_context, project_root, agent_data)
        
        return variables
    
    def _extract_rules_from_agent_data(self, agent_data: Dict) -> List[str]:
        """Extract rules from agent YAML data"""
        rules = []
        
        # Extract from contexts (custom_instructions)
        contexts = agent_data.get('contexts', {})
        for context_name, context_data in contexts.items():
            if 'custom_instructions' in context_data:
                instructions = context_data['custom_instructions']
                # Parse instructions for rule-like content
                if isinstance(instructions, str):
                    # Extract bullet points and numbered lists as rules
                    lines = instructions.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\.', line):
                            rule = line.lstrip('- *0123456789. ')
                            if rule and len(rule) > 10:  # Filter out very short items
                                rules.append(rule)
        
        # Extract from rules files
        rules_data = agent_data.get('rules', {})
        for rule_file, rule_content in rules_data.items():
            if isinstance(rule_content, dict):
                for key, value in rule_content.items():
                    if isinstance(value, dict) and 'mechanism' in value:
                        rules.append(f"{key.replace('_', ' ').title()}: {value['mechanism']}")
                    elif isinstance(value, str) and len(value) > 20:
                        rules.append(f"{key.replace('_', ' ').title()}: {value}")
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and len(item) > 10:
                                rules.append(item)
        
        return rules[:20]  # Limit to top 20 rules for readability
    
    def _extract_tools_guidance_from_agent_data(self, agent_data: Dict) -> List[str]:
        """Extract tools guidance from agent YAML data"""
        guidance = []
        
        # Extract from tools files
        tools_data = agent_data.get('tools', {})
        for tool_file, tool_content in tools_data.items():
            if isinstance(tool_content, dict):
                # Extract tool descriptions and usage
                for key, value in tool_content.items():
                    if isinstance(value, str) and len(value) > 20:
                        guidance.append(f"**{key.replace('_', ' ').title()}**: {value}")
                    elif isinstance(value, dict):
                        if 'description' in value:
                            guidance.append(f"**{key.replace('_', ' ').title()}**: {value['description']}")
                        if 'usage' in value:
                            guidance.append(f"**{key} Usage**: {value['usage']}")
        
        # Extract from contexts (tool-related content)
        contexts = agent_data.get('contexts', {})
        for context_name, context_data in contexts.items():
            if 'custom_instructions' in context_data:
                instructions = context_data['custom_instructions']
                if isinstance(instructions, str):
                    # Look for tool-related sections
                    if 'tools' in instructions.lower() or 'mcp' in instructions.lower():
                        lines = instructions.split('\n')
                        in_tools_section = False
                        for line in lines:
                            if 'tools' in line.lower() or 'mcp' in line.lower():
                                in_tools_section = True
                            elif in_tools_section and line.strip():
                                if line.startswith('  ') or line.startswith('- '):
                                    guidance.append(line.strip().lstrip('- '))
                                elif line.startswith('#'):
                                    in_tools_section = False
        
        return guidance[:15]  # Limit for readability
    
    def _extract_context_instructions_from_agent_data(self, agent_data: Dict) -> List[str]:
        """Extract context instructions from agent YAML data"""
        instructions = []
        
        # Extract from contexts
        contexts = agent_data.get('contexts', {})
        for context_name, context_data in contexts.items():
            if 'custom_instructions' in context_data:
                custom_inst = context_data['custom_instructions']
                if isinstance(custom_inst, str):
                    # Extract key process steps and guidelines
                    lines = custom_inst.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('**') and line.endswith('**:'):
                            # This is a section header, include it
                            instructions.append(line.replace('**', '').replace(':', ''))
                        elif line.startswith('- ') and len(line) > 20:
                            # This is a bullet point with substantial content
                            instructions.append(line[2:])
                        elif re.match(r'^\d+\.', line) and len(line) > 20:
                            # This is a numbered list item
                            instructions.append(line.split('.', 1)[1].strip())
        
        return instructions[:10]  # Limit for readability
    
    def _build_requirements_content(self, task: TaskContext, role: AgentRole, project_context: Dict, project_root: Path, agent_data: Dict = None) -> str:
        """Build requirements section content"""
        if not task.requirements:
            return ""
        return '\n'.join([f"- {req}" for req in task.requirements])
    
    def _build_core_rules_content(self, task: TaskContext, role: AgentRole, project_context: Dict, project_root: Path, agent_data: Dict = None) -> str:
        """Build core rules section content with improved formatting and categorization"""
        # Use agent data if available, otherwise fall back to role rules
        if agent_data:
            rules = self._extract_rules_from_agent_data(agent_data)
        else:
            rules = role.rules if role.rules else []
        
        if not rules:
            return "No specific rules defined for this role."
        
        # Group rules into categories for better readability
        categorized_rules = self._categorize_rules(rules)
        
        if categorized_rules:
            content = []
            for category, category_rules in categorized_rules.items():
                content.append(f"\n### {category}\n")
                for i, rule in enumerate(category_rules, 1):
                    content.append(f"{i}. {rule}")
                content.append("")  # Add spacing between categories
            return '\n'.join(content)
        else:
            # Fallback to numbered list with better spacing
            rules_content = []
            for i, rule in enumerate(rules, 1):
                rules_content.append(f"{i}. {rule}")
                # Add spacing every 5 rules for better readability
                if i % 5 == 0 and i < len(rules):
                    rules_content.append("")
            return '\n'.join(rules_content)
    
    def _categorize_rules(self, rules: List[str]) -> Dict[str, List[str]]:
        """Categorize rules for better organization"""
        categories = {
            "🎯 Core Principles": [],
            "📋 Planning & Analysis": [],
            "💻 Implementation": [],
            "🔍 Quality & Review": [],
            "📚 Documentation": [],
            "🔧 Tools & Process": []
        }
        
        # Keywords for categorization
        planning_keywords = ["plan", "analyze", "requirement", "breakdown", "decompos", "strategy", "roadmap"]
        implementation_keywords = ["implement", "code", "develop", "build", "create", "write", "follow", "use"]
        quality_keywords = ["quality", "test", "review", "validate", "error", "edge", "maintain", "clean", "standard"]
        documentation_keywords = ["document", "comment", "explain", "describe", "record", "track"]
        tools_keywords = ["tool", "framework", "automation", "version", "monitor", "measure"]
        
        for rule in rules:
            rule_lower = rule.lower()
            categorized = False
            
            # Check for planning keywords
            if any(keyword in rule_lower for keyword in planning_keywords):
                categories["📋 Planning & Analysis"].append(rule)
                categorized = True
            # Check for implementation keywords
            elif any(keyword in rule_lower for keyword in implementation_keywords):
                categories["💻 Implementation"].append(rule)
                categorized = True
            # Check for quality keywords
            elif any(keyword in rule_lower for keyword in quality_keywords):
                categories["🔍 Quality & Review"].append(rule)
                categorized = True
            # Check for documentation keywords
            elif any(keyword in rule_lower for keyword in documentation_keywords):
                categories["📚 Documentation"].append(rule)
                categorized = True
            # Check for tools keywords
            elif any(keyword in rule_lower for keyword in tools_keywords):
                categories["🔧 Tools & Process"].append(rule)
                categorized = True
            
            # If not categorized, put in core principles
            if not categorized:
                categories["🎯 Core Principles"].append(rule)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _build_context_instructions_content(self, task: TaskContext, role: AgentRole, project_context: Dict, project_root: Path, agent_data: Dict = None) -> str:
        """Build context-specific instructions content with improved markdown formatting"""
        # Use agent data if available, otherwise fall back to role instructions
        if agent_data:
            instructions = self._extract_context_instructions_from_agent_data(agent_data)
        else:
            instructions = role.context_instructions if role.context_instructions else []
        
        if not instructions:
            return "No specific context instructions defined."
        
        # Format as clean markdown list with proper spacing
        content = []
        for instruction in instructions:
            content.append(f"- {instruction}")
        
        # Add spacing every 5 instructions for better readability
        formatted_content = []
        for i, line in enumerate(content):
            formatted_content.append(line)
            if (i + 1) % 5 == 0 and i < len(content) - 1:
                formatted_content.append("")
        
        return '\n'.join(formatted_content)
    
    def _build_tools_guidance_content(self, task: TaskContext, role: AgentRole, project_context: Dict, project_root: Path, agent_data: Dict = None) -> str:
        """Build tools guidance section content with enhanced markdown formatting"""
        # Use agent data if available, otherwise fall back to role guidance
        if agent_data:
            guidance = self._extract_tools_guidance_from_agent_data(agent_data)
        else:
            guidance = role.tools_guidance if role.tools_guidance else []
        
        if not guidance:
            return "No specific tools guidance defined."
        
        # Categorize tools guidance for better organization
        categorized_guidance = self._categorize_tools_guidance(guidance)
        
        if categorized_guidance:
            content = []
            for category, items in categorized_guidance.items():
                content.append(f"\n### {category}\n")
                
                # Enhanced formatting for different content types
                formatted_content = self._format_category_content(category, items)
                content.append(formatted_content)
                content.append("")  # Add spacing between categories
            
            return '\n'.join(content)
        else:
            # Fallback formatting with proper markdown lists
            content = []
            for item in guidance:
                formatted_item = self._format_guidance_item(item)
                content.append(formatted_item)
            
            return '\n'.join(content)
    
    def _format_category_content(self, category: str, items: List[str]) -> str:
        """Enhanced formatting for different category types"""
        formatted_items = []
        
        for item in items:
            # Check if this is already pre-formatted content from role_manager
            if self._is_pre_formatted_content(item):
                formatted_item = self._extract_pre_formatted_content(item)
            # Check if this is a complex YAML structure
            elif self._is_complex_yaml_structure(item):
                formatted_item = self._format_complex_yaml_item(item)
            else:
                formatted_item = self._format_guidance_item(item)
            formatted_items.append(formatted_item)
        
        return '\n'.join(formatted_items)
    
    def _is_pre_formatted_content(self, item: str) -> bool:
        """Check if content is already pre-formatted from role_manager"""
        # Pre-formatted content contains markdown headers and structured sections
        pre_format_indicators = [
            '## 📋 Task Assessment', '## 🔄 Workflow Execution', '## 🛠️ Tools & Guidance',
            '### 🎯 Step', '### 📊 Feature Types', '### 👥 Step', '### ⚡ Step',
            '| Complexity |', '| Type |', '| Role |'
        ]
        return any(indicator in item for indicator in pre_format_indicators)
    
    def _extract_pre_formatted_content(self, item: str) -> str:
        """Extract the pre-formatted content, removing file path prefix"""
        # Content format is "filepath|formatted_content"
        if '|' in item:
            parts = item.split('|', 1)
            if len(parts) == 2:
                return parts[1]  # Return the formatted content part
        return item
    
    def _is_complex_yaml_structure(self, item: str) -> bool:
        """Check if an item contains complex YAML structure"""
        yaml_indicators = [
            'category:', 'checklist:', 'workflow:', 'phases:', 'assessment:', 
            'feature_types:', 'roles:', 'buffers:', 'emergency_options:',
            'complexity_classification:', 'phase_selection:', 'resource_planning:'
        ]
        return any(indicator in item for indicator in yaml_indicators)
    
    def _format_complex_yaml_item(self, item: str) -> str:
        """Format complex YAML structures into beautiful markdown with enhanced nested support"""
        try:
            # Try to parse as YAML first
            if self._looks_like_yaml(item):
                return self._format_yaml_structure(item)
            else:
                # Parse the YAML-like content line by line
                return self._format_yaml_content_lines(item)
            
        except Exception as e:
            # Fallback to simple formatting if parsing fails
            return self._format_guidance_item(item)
    
    def _looks_like_yaml(self, content: str) -> bool:
        """Check if content looks like structured YAML"""
        yaml_indicators = [
            'assessment:', 'checklist:', 'workflow:', 'phases:', 'feature_types:',
            'resource_planning:', 'timeline_estimation:', 'risk_assessment:',
            'phase_selection:', 'emergency_options:', 'communication_setup:'
        ]
        return any(indicator in content for indicator in yaml_indicators)
    
    def _format_yaml_structure(self, content: str) -> str:
        """Format structured YAML content with proper hierarchy"""
        try:
            # Parse YAML content
            yaml_data = yaml.safe_load(content)
            if not yaml_data:
                return self._format_yaml_content_lines(content)
            
            return self._format_yaml_data_structure(yaml_data)
            
        except Exception:
            return self._format_yaml_content_lines(content)
    
    def _format_yaml_data_structure(self, data: Dict[str, Any], level: int = 0) -> str:
        """Recursively format YAML data structure"""
        formatted_content = []
        
        for key, value in data.items():
            if key in ['name', 'category', 'version']:
                continue  # Skip metadata
            
            # Format section header
            section_title = self._format_section_title(key, level)
            formatted_content.append(section_title)
            
            # Format section content
            if isinstance(value, dict):
                if self._is_special_section(key):
                    formatted_section = self._format_special_section(key, value)
                else:
                    formatted_section = self._format_yaml_data_structure(value, level + 1)
                formatted_content.append(formatted_section)
            elif isinstance(value, list):
                formatted_list = self._format_yaml_list(value, level + 1)
                formatted_content.append(formatted_list)
            else:
                formatted_content.append(f"- {value}")
            
            formatted_content.append("")  # Add spacing
        
        return '\n'.join(formatted_content)
    
    def _format_section_title(self, key: str, level: int) -> str:
        """Format section title with appropriate header level and emoji"""
        emoji_map = {
            'assessment': '📊', 'checklist': '📋', 'workflow': '🔄', 'phases': '⚡',
            'feature_types': '🎯', 'resource_planning': '👥', 'timeline_estimation': '⏰',
            'risk_assessment': '⚠️', 'phase_selection': '🎛️', 'emergency_options': '🚨',
            'communication_setup': '💬', 'monitoring_setup': '📊', 'roles': '👥',
            'complexity_classification': '📈', 'urgency_levels': '⚡',
            'role_requirements': '👥', 'base_estimates': '⏱️', 'factors': '📊'
        }
        
        emoji = emoji_map.get(key, '📌')
        title = key.replace('_', ' ').title()
        header_level = "####" if level == 0 else "#####"
        
        return f"{header_level} {emoji} {title}"
    
    def _is_special_section(self, key: str) -> bool:
        """Check if section needs special formatting"""
        special_sections = [
            'complexity_classification', 'feature_types', 'phases', 'roles',
            'urgency_levels', 'role_requirements', 'phase_selection'
        ]
        return key in special_sections
    
    def _format_special_section(self, section_key: str, data: Dict[str, Any]) -> str:
        """Format special sections with custom layouts"""
        if section_key == 'complexity_classification':
            return self._format_complexity_table(data)
        elif section_key == 'feature_types':
            return self._format_feature_types_table(data)
        elif section_key == 'phases':
            return self._format_phases_details(data)
        elif section_key == 'roles':
            return self._format_roles_table(data)
        elif section_key == 'role_requirements':
            return self._format_role_requirements(data)
        elif section_key == 'phase_selection':
            return self._format_phase_selection(data)
        else:
            return self._format_yaml_data_structure(data, 1)
    
    def _format_complexity_table(self, data: Dict[str, Any]) -> str:
        """Format complexity classification as a table"""
        content = ["| Complexity | Duration | Criteria |"]
        content.append("|------------|----------|----------|")
        
        complexity_order = ['micro', 'standard', 'complex', 'very_complex']
        for complexity in complexity_order:
            if complexity in data:
                item = data[complexity]
                duration = item.get('duration', 'N/A')
                criteria = ', '.join(item.get('criteria', []))
                content.append(f"| **{complexity.title()}** | {duration} | {criteria} |")
        
        return '\n'.join(content)
    
    def _format_feature_types_table(self, data: Dict[str, Any]) -> str:
        """Format feature types as a table"""
        content = ["| Type | Duration | Description | Phases |"]
        content.append("|------|----------|-------------|--------|")
        
        for type_name, type_data in data.items():
            duration = type_data.get('duration', 'N/A')
            description = type_data.get('description', '')
            phases = str(type_data.get('phases', 'See docs'))
            content.append(f"| **{type_name.title()}** | {duration} | {description} | {phases} |")
        
        return '\n'.join(content)
    
    def _format_phases_details(self, data: Dict[str, Any]) -> str:
        """Format phases with detailed information"""
        content = []
        
        for phase_num in sorted(data.keys(), key=lambda x: int(x) if x.isdigit() else 999):
            phase_data = data[phase_num]
            
            name = phase_data.get('name', f'Phase {phase_num}')
            role = phase_data.get('role', 'N/A')
            duration = phase_data.get('duration', 'N/A')
            icon = phase_data.get('icon', '📌')
            
            content.append(f"##### {icon} Phase {phase_num}: {name}")
            content.append(f"**Role:** {role} | **Duration:** {duration}")
            content.append("")
            
            # Deliverables
            if 'deliverables' in phase_data:
                content.append("**Deliverables:**")
                for deliverable in phase_data['deliverables']:
                    content.append(f"- {deliverable}")
                content.append("")
            
            # Exit Criteria
            if 'exit_criteria' in phase_data:
                content.append("**Exit Criteria:**")
                for criteria in phase_data['exit_criteria']:
                    content.append(f"- ✅ {criteria}")
                content.append("")
            
            # Dependencies
            if 'dependencies' in phase_data:
                deps = phase_data['dependencies']
                content.append(f"**Dependencies:** Phases {deps}")
                content.append("")
            
            content.append("---")
            content.append("")
        
        return '\n'.join(content)
    
    def _format_roles_table(self, data: Dict[str, Any]) -> str:
        """Format roles with responsibilities"""
        content = []
        
        for role_name, role_data in data.items():
            icon = role_data.get('icon', '👤')
            responsibilities = role_data.get('responsibilities', [])
            
            content.append(f"##### {icon} {role_name.replace('_', ' ').title()}")
            for resp in responsibilities:
                content.append(f"- {resp}")
            content.append("")
        
        return '\n'.join(content)
    
    def _format_role_requirements(self, data: Dict[str, Any]) -> str:
        """Format role requirements with conditions"""
        content = []
        
        # Always required roles
        if 'always_required' in data:
            always_req = data['always_required']
            content.append(f"**Always Required:** {', '.join(always_req)}")
            content.append("")
        
        # Conditional roles
        if 'conditional_roles' in data:
            content.append("**Conditional Roles:**")
            content.append("")
            content.append("| Role | Required For | Skip Conditions |")
            content.append("|------|--------------|-----------------|")
            
            conditional = data['conditional_roles']
            for role, role_data in conditional.items():
                required_for = ", ".join(role_data.get('required_for', []))
                skip_conditions = "; ".join(role_data.get('skip_conditions', role_data.get('skip_for', [])))
                content.append(f"| {role.replace('_', ' ').title()} | {required_for} | {skip_conditions} |")
        
        return '\n'.join(content)
    
    def _format_phase_selection(self, data: Dict[str, Any]) -> str:
        """Format phase selection logic"""
        content = []
        
        complexity_order = ['micro_feature', 'standard_feature', 'complex_feature', 'very_complex_feature']
        for feature_type in complexity_order:
            if feature_type in data:
                feature_data = data[feature_type]
                display_name = feature_type.replace('_feature', '').title()
                
                content.append(f"##### {display_name} Feature")
                
                included = feature_data.get('included_phases', [])
                skipped = feature_data.get('skipped_phases', [])
                
                content.append(f"- **Phases:** {included}")
                if skipped:
                    content.append(f"- **Skip:** {skipped}")
                
                # Additional requirements
                if 'additional_requirements' in feature_data:
                    reqs = feature_data['additional_requirements']
                    content.append(f"- **Extra Requirements:** {'; '.join(reqs)}")
                
                content.append("")
        
        return '\n'.join(content)
    
    def _format_yaml_list(self, items: List[Any], level: int) -> str:
        """Format YAML list items"""
        content = []
        for item in items:
            if isinstance(item, dict):
                # Handle nested dictionaries in lists
                for key, value in item.items():
                    content.append(f"- **{key}**: {value}")
            else:
                content.append(f"- {item}")
        return '\n'.join(content)
    
    def _format_yaml_content_lines(self, content: str) -> str:
        """Format YAML content line by line (fallback method)"""
        lines = content.split('\n')
        formatted_content = []
        current_section = None
        
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            
            # Detect section headers
            if self._is_section_header(stripped_line):
                section_name = self._extract_section_name(stripped_line)
                formatted_content.append(f"\n#### {section_name}")
                current_section = section_name.lower()
                continue
            
            # Format based on content type
            if current_section:
                formatted_line = self._format_yaml_line(stripped_line, current_section)
                if formatted_line:
                    formatted_content.append(formatted_line)
            else:
                # General formatting
                formatted_line = self._format_yaml_line(stripped_line, "general")
                if formatted_line:
                    formatted_content.append(formatted_line)
        
        return '\n'.join(formatted_content)
    
    def _is_section_header(self, line: str) -> bool:
        """Check if a line is a section header"""
        section_patterns = [
            'category:', 'checklist:', 'workflow:', 'phases:', 'assessment:',
            'feature_types:', 'roles:', 'emergency_options:', 'phase_selection:',
            'complexity_classification:', 'resource_planning:', 'timeline_estimation:',
            'communication_setup:', 'monitoring_setup:', 'quick_reference:'
        ]
        return any(pattern in line.lower() for pattern in section_patterns)
    
    def _extract_section_name(self, line: str) -> str:
        """Extract and format section name"""
        # Remove YAML syntax and format as title
        name = line.replace(':', '').strip()
        # Convert snake_case to Title Case
        name = name.replace('_', ' ').title()
        # Add appropriate emoji
        emoji_map = {
            'Checklist': '📋',
            'Workflow': '🔄',
            'Phases': '⚡',
            'Assessment': '📊',
            'Feature Types': '🎯',
            'Roles': '👥',
            'Emergency Options': '🚨',
            'Phase Selection': '🎛️',
            'Complexity Classification': '📈',
            'Resource Planning': '📋',
            'Timeline Estimation': '⏰',
            'Communication Setup': '💬',
            'Monitoring Setup': '📊',
            'Quick Reference': '⚡'
        }
        emoji = emoji_map.get(name, '📌')
        return f"{emoji} {name}"
    
    def _format_yaml_line(self, line: str, section: str) -> str:
        """Format individual YAML lines based on section context"""
        # Skip file paths and metadata
        if line.startswith('/') or line.startswith('name:') or line.startswith('category:'):
            return None
        
        # Handle different line types
        if ':' in line and not line.startswith('-'):
            # Key-value pairs
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Format based on content
            if section in ['complexity classification', 'feature types']:
                return self._format_complexity_item(key, value)
            elif section in ['phases', 'workflow']:
                return self._format_phase_item(key, value)
            elif section in ['roles']:
                return self._format_role_item(key, value)
            else:
                return f"- **{key.replace('_', ' ').title()}:** {value}"
        
        elif line.startswith('-'):
            # List items
            item = line[1:].strip()
            return f"  - {item}"
        
        else:
            # Regular content
            return f"- {line}"
    
    def _format_complexity_item(self, key: str, value: str) -> str:
        """Format complexity classification items"""
        complexity_map = {
            'micro': '🟢 Micro',
            'standard': '🟡 Standard', 
            'complex': '🟠 Complex',
            'very_complex': '🔴 Very Complex'
        }
        display_name = complexity_map.get(key, key.replace('_', ' ').title())
        return f"- **{display_name}:** {value}"
    
    def _format_phase_item(self, key: str, value: str) -> str:
        """Format workflow phase items"""
        if key.isdigit():
            return f"- **Phase {key}:** {value}"
        else:
            return f"- **{key.replace('_', ' ').title()}:** {value}"
    
    def _format_role_item(self, key: str, value: str) -> str:
        """Format role definition items"""
        role_emojis = {
            'task_planner': '📋',
            'senior_developer': '💻',
            'qa_engineer': '🧪',
            'devops_engineer': '⚙️',
            'security_engineer': '🔒',
            'code_reviewer': '👁️',
            'cache_engineer': '⚡',
            'context_engineer': '🔍',
            'metrics_engineer': '📊',
            'technical_writer': '📝'
        }
        emoji = role_emojis.get(key, '👤')
        role_name = key.replace('_', ' ').title()
        return f"- **{emoji} {role_name}:** {value}"
     
    def _format_guidance_item(self, item: str) -> str:
        """Format a single guidance item with proper markdown"""
        # Clean up the item
        cleaned_item = item.strip()
        
        # Remove existing bullet points
        if cleaned_item.startswith("• •"):
            cleaned_item = cleaned_item[4:].strip()
            return f"  - {cleaned_item}"
        elif cleaned_item.startswith("•"):
            cleaned_item = cleaned_item[2:].strip()
        
        # Handle special formatting
        if "**" in cleaned_item and ":" in cleaned_item:
            # This looks like a definition or important item
            return f"- **{cleaned_item}**"
        elif cleaned_item.startswith("Phase") and ":" in cleaned_item:
            # Phase information
            return f"- {cleaned_item}"
        elif "(" in cleaned_item and ")" in cleaned_item and any(word in cleaned_item.lower() for word in ["hour", "day", "week"]):
            # Time estimate
            return f"- {cleaned_item}"
        else:
            # Regular item
            return f"- {cleaned_item}"
     
    def _categorize_tools_guidance(self, guidance: List[str]) -> Dict[str, List[str]]:
        """Categorize tools guidance for better organization"""
        categories = {
            "🛠️ Development Tools": [],
            "📊 Planning & Analysis": [],
            "🎯 Workflow Guidelines": [],
            "📋 Checklists & Standards": [],
            "⏱️ Time & Effort Estimation": [],
            "🔄 Process & Methodology": []
        }
        
        # Keywords for categorization
        dev_tools_keywords = ["markdown", "flowchart", "diagram", "tool", "framework", "automation", "version"]
        planning_keywords = ["complexity", "classification", "estimate", "planning", "breakdown", "analysis"]
        workflow_keywords = ["workflow", "phase", "feature", "generation", "lite", "streamlined"]
        checklist_keywords = ["checklist", "guideline", "standard", "required", "role", "definition"]
        time_keywords = ["time", "estimate", "effort", "hour", "day", "week", "micro", "standard", "complex"]
        process_keywords = ["process", "methodology", "approach", "practice", "pattern", "convention"]
        
        for item in guidance:
            item_lower = item.lower()
            categorized = False
            
            # Check for development tools keywords
            if any(keyword in item_lower for keyword in dev_tools_keywords):
                categories["🛠️ Development Tools"].append(item)
                categorized = True
            # Check for planning keywords
            elif any(keyword in item_lower for keyword in planning_keywords):
                categories["📊 Planning & Analysis"].append(item)
                categorized = True
            # Check for workflow keywords
            elif any(keyword in item_lower for keyword in workflow_keywords):
                categories["🎯 Workflow Guidelines"].append(item)
                categorized = True
            # Check for checklist keywords
            elif any(keyword in item_lower for keyword in checklist_keywords):
                categories["📋 Checklists & Standards"].append(item)
                categorized = True
            # Check for time keywords
            elif any(keyword in item_lower for keyword in time_keywords):
                categories["⏱️ Time & Effort Estimation"].append(item)
                categorized = True
            # Check for process keywords
            elif any(keyword in item_lower for keyword in process_keywords):
                categories["🔄 Process & Methodology"].append(item)
                categorized = True
            
            # If not categorized, put in development tools as default
            if not categorized:
                categories["🛠️ Development Tools"].append(item)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _build_phase_specific_content(self, task: TaskContext, role: AgentRole, project_context: Dict, project_root: Path, agent_data: Dict = None) -> str:
        """Build dynamic phase-specific context content from role YAML data"""
        phase_content = []
        
        # Extract phase-specific guidance from role's tools_guidance and rules
        phase_specific_items = []
        
        # Look for phase-specific content in tools_guidance
        if agent_data and agent_data.get('tools', {}):
            for item in agent_data['tools'].values():
                item_lower = item.lower()
                if (task.current_phase.lower() in item_lower or 
                    self._is_phase_relevant_content(item, task.current_phase)):
                    phase_specific_items.append(item)
        
        # Look for phase-specific content in rules
        if agent_data and agent_data.get('rules', {}):
            for rule in agent_data['rules'].values():
                if isinstance(rule, str):
                    rule_lower = rule.lower()
                    if (task.current_phase.lower() in rule_lower or 
                        self._is_phase_relevant_content(rule, task.current_phase)):
                        phase_specific_items.append(rule)
        
        # Look for phase-specific content in context_instructions
        if agent_data and agent_data.get('contexts', {}):
            for context_name, context_data in agent_data['contexts'].items():
                if 'custom_instructions' in context_data:
                    custom_inst = context_data['custom_instructions']
                    if isinstance(custom_inst, str):
                        # Extract key process steps and guidelines
                        lines = custom_inst.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line.startswith('**') and line.endswith('**:'):
                                # This is a section header, include it
                                phase_specific_items.append(line.replace('**', '').replace(':', ''))
                            elif line.startswith('- ') and len(line) > 20:
                                # This is a bullet point with substantial content
                                phase_specific_items.append(line[2:])
                            elif re.match(r'^\d+\.', line) and len(line) > 20:
                                # This is a numbered list item
                                phase_specific_items.append(line.split('.', 1)[1].strip())
        
        # Build the phase-specific content
        if phase_specific_items:
            phase_content.append(f"### {task.current_phase.title()} Phase Focus")
            
            # Categorize and format the phase-specific items
            categorized_items = self._categorize_phase_content(phase_specific_items, task.current_phase)
            
            for category, items in categorized_items.items():
                if items:
                    phase_content.append(f"\n#### {category}")
                    for item in items:
                        # Format the item properly
                        formatted_item = self._format_phase_guidance_item(item)
                        phase_content.append(f"- {formatted_item}")
        else:
            # Fallback to generic phase guidance if no specific content found
            phase_content.append(f"### {task.current_phase.title()} Phase Focus")
            generic_guidance = self._get_generic_phase_guidance(task.current_phase, role)
            phase_content.extend(generic_guidance)
        
        return '\n'.join(phase_content)
    
    def _is_phase_relevant_content(self, content: str, phase: str) -> bool:
        """Check if content is relevant to the current phase"""
        phase_keywords = {
            "planning": ["plan", "analyze", "requirement", "breakdown", "decompos", "strategy", "roadmap", "design", "architecture"],
            "coding": ["implement", "code", "develop", "build", "create", "write", "function", "class", "module", "api"],
            "testing": ["test", "testing", "validation", "verify", "quality", "qa", "coverage", "scenario", "edge case"],
            "review": ["review", "audit", "optimize", "refactor", "improve", "security", "quality", "standard", "best practice"]
        }
        
        content_lower = content.lower()
        keywords = phase_keywords.get(phase.lower(), [])
        
        return any(keyword in content_lower for keyword in keywords)
    
    def _categorize_phase_content(self, items: List[str], phase: str) -> Dict[str, List[str]]:
        """Categorize phase-specific content items"""
        categories = {
            "Key Activities": [],
            "Tools & Techniques": [],
            "Quality Standards": [],
            "Deliverables": []
        }
        
        for item in items:
            item_lower = item.lower()
            
            # Check for tools and techniques
            if any(keyword in item_lower for keyword in ["tool", "framework", "automation", "use", "implement"]):
                categories["Tools & Techniques"].append(item)
            # Check for quality standards
            elif any(keyword in item_lower for keyword in ["quality", "standard", "best practice", "validate", "ensure"]):
                categories["Quality Standards"].append(item)
            # Check for deliverables
            elif any(keyword in item_lower for keyword in ["create", "generate", "produce", "deliver", "output"]):
                categories["Deliverables"].append(item)
            else:
                # Default to key activities
                categories["Key Activities"].append(item)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _format_phase_guidance_item(self, item: str) -> str:
        """Format a phase guidance item for display"""
        # Remove file path prefix if present
        if '|' in item and item.startswith('📌'):
            parts = item.split('|', 1)
            if len(parts) == 2:
                item = parts[1].strip()
        
        # Clean up the item
        item = item.strip()
        
        # Remove leading bullet points or numbers
        item = item.lstrip('•-*123456789. ')
        
        return item
    
    def _get_generic_phase_guidance(self, phase: str, role: AgentRole) -> List[str]:
        """Get generic phase guidance when no specific content is found"""
        generic_guidance = {
            "planning": [
                "- Analyze requirements thoroughly based on role expertise",
                "- Break down complex tasks into manageable components",
                "- Identify dependencies and potential risks",
                "- Create realistic timeline estimates",
                "- Define clear acceptance criteria"
            ],
            "coding": [
                "- Implement according to established plans and requirements",
                "- Follow coding standards and best practices",
                "- Include proper error handling and validation",
                "- Write clean, maintainable, and well-documented code",
                "- Consider performance, security, and scalability"
            ],
            "testing": [
                "- Create comprehensive test coverage",
                "- Test both positive and negative scenarios",
                "- Include edge cases and error conditions",
                "- Validate against defined acceptance criteria",
                "- Ensure tests are maintainable and reliable"
            ],
            "review": [
                "- Review all deliverables for quality and completeness",
                "- Check adherence to standards and best practices",
                "- Identify potential improvements or optimizations",
                "- Validate completeness against requirements",
                "- Provide actionable feedback and recommendations"
            ]
        }
        
        return generic_guidance.get(phase.lower(), [f"- Focus on {phase} activities according to role responsibilities"])
    
    def _build_project_context_content(self, task: TaskContext, role: AgentRole, project_context: Dict, project_root: Path, agent_data: Dict = None) -> str:
        """Build project context section content with improved formatting and truncation"""
        structure = project_context.get("project_structure", {})
        patterns = project_context.get("existing_patterns", [])
        deps = project_context.get("dependencies", [])
        tree_formatter = project_context.get("tree_formatter")
        
        # Format the tree structure with truncation for readability
        if tree_formatter and structure:
            tree_display = tree_formatter(structure)
            # Truncate very long project structures
            tree_lines = tree_display.split('\n')
            if len(tree_lines) > 50:
                # Keep first 30 lines and last 10 lines with a truncation indicator
                truncated_tree = '\n'.join(tree_lines[:30])
                truncated_tree += '\n... (truncated for readability) ...\n'
                truncated_tree += '\n'.join(tree_lines[-10:])
                tree_display = truncated_tree
        else:
            tree_display = "No project structure analyzed"
        
        # Format patterns with better organization
        patterns_content = ""
        if patterns:
            if len(patterns) > 8:
                # Show first 8 patterns and indicate there are more
                patterns_content = '\n'.join([f"- {pattern}" for pattern in patterns[:8]])
                patterns_content += f"\n- ... and {len(patterns) - 8} more patterns"
            else:
                patterns_content = '\n'.join([f"- {pattern}" for pattern in patterns])
        else:
            patterns_content = "- No specific patterns detected"
        
        # Format dependencies with better organization
        deps_content = ""
        if deps:
            if len(deps) > 10:
                # Show first 10 dependencies and indicate there are more
                deps_content = '\n'.join([f"- {dep}" for dep in deps[:10]])
                deps_content += f"\n- ... and {len(deps) - 10} more dependencies"
            else:
                deps_content = '\n'.join([f"- {dep}" for dep in deps])
        else:
            deps_content = "- No major dependencies detected"

        return f"""
### Project Structure
```
{tree_display}
```

### Existing Patterns Detected
{patterns_content}

### Key Dependencies
{deps_content}
"""
    
    def _build_all_roles_info_content(self, task: TaskContext, role: AgentRole, project_context: Dict, project_root: Path, agent_data: Dict = None) -> str:
        """Build all roles information content"""
        if len(task.assigned_roles) <= 1:
            return ""
        
        # This would need access to all role objects, for now return placeholder
        info_lines = ["### All Active Roles Information"]
        for role_name in task.assigned_roles:
            info_lines.append(f"**{role_name}:** Active role in this task")
        
        return "\n".join(info_lines)
    
    def _build_context_link_content(self, task: TaskContext, role: AgentRole, project_context: Dict, project_root: Path, agent_data: Dict = None) -> str:
        """Build context file link section content"""
        context_dir = project_root / ".cursor" / "rules" / "contexts"
        context_file = context_dir / f"context_{task.id}.txt"
        
        if context_file.exists():
            return f"""
## 📋 Task Context File
**Context File:** [`contexts/context_{task.id}.txt`](.cursor/rules/contexts/context_{task.id}.txt)
**Status:** ✅ Context file exists - Contains detailed progress, decisions, and notes for this task
**Usage:** Review the context file for complete task history and continuation notes
"""
        else:
            return f"""
## 📋 Task Context File
**Context File:** `contexts/context_{task.id}.txt` 
**Status:** ❌ Context file not created yet
**Next Action:** AI should create `.cursor/rules/contexts/context_{task.id}.txt` to track progress, decisions, and notes for this task
**Template:** Follow the context file format from existing context files in the contexts directory
"""
    
    def _generate_context_summary(self, task: TaskContext) -> str:
        """Generate a dynamic summary of current context and progress"""
        # Dynamic phase descriptions with emojis
        phase_emojis = {
            "planning": "📋",
            "coding": "💻", 
            "testing": "🧪",
            "review": "🔍",
            "completed": "✅"
        }
        
        emoji = phase_emojis.get(task.current_phase, "🔄")
        phase_title = task.current_phase.title()
        
        # Generate dynamic description based on phase
        if task.current_phase == "planning":
            description = "Focus on requirement analysis and task decomposition"
        elif task.current_phase == "coding":
            description = "Implement the solution according to the plan"
        elif task.current_phase == "testing":
            description = "Create comprehensive tests and validate implementation"
        elif task.current_phase == "review":
            description = "Code review and final optimization"
        elif task.current_phase == "completed":
            description = "Task finished and ready for deployment"
        else:
            description = f"Focus on {task.current_phase} activities"
        
        return f"{emoji} **{phase_title} Phase**: {description}"


class RulesGenerator:
    """Generates .cursor/rules files based on task context and roles"""
    
    def __init__(self, lib_dir: Path):
        self.lib_dir = lib_dir
        self.template_system = RulesTemplateSystem(lib_dir)
    
    def build_rules_content(self, task: TaskContext, role: AgentRole, project_context: Dict) -> str:
        """Build the complete rules file content with proper Cursor rules structure"""
        return self.template_system.generate_rules_content(task, role, project_context)
    
    def get_primary_role_for_phase(self, phase: str, assigned_roles: List[str]) -> str:
        """Get the primary role for the current phase"""
        phase_role_mapping = {
            "planning": "task_planning_agent",
            "coding": "coding_agent",
            "testing": "functional_tester_agent",
            "review": "code_reviewer_agent"
        }
        
        preferred_role = phase_role_mapping.get(phase, "coding_agent")
        
        # Return preferred role if available, otherwise return first available role
        if preferred_role in assigned_roles:
            return preferred_role
        else:
            return assigned_roles[0] if assigned_roles else "coding_agent"
    
    def _build_all_roles_info(self, assigned_roles: List[str], roles: Dict) -> str:
        """Build information section about all active roles"""
        if len(assigned_roles) <= 1:
            return ""
        
        info_lines = ["### All Active Roles Information"]
        
        for role_name in assigned_roles:
            if role_name in roles:
                role = roles[role_name]
                info_lines.append(f"**{role.name}:**")
                info_lines.append(f"- Focus: {role.primary_focus}")
                info_lines.append(f"- Persona: {role.persona}")
                info_lines.append("")
        
        return "\n".join(info_lines)
    
    def _get_phase_specific_context(self, task: TaskContext) -> str:
        """Get context specific to current phase - DEPRECATED: Use _build_phase_specific_content instead"""
        # This method is deprecated in favor of the dynamic _build_phase_specific_content
        # Keeping for backward compatibility but should be replaced
        return f"### {task.current_phase.title()} Phase Focus\n- Focus on {task.current_phase} activities according to role responsibilities"
    
    def _format_project_context(self, context_data: Dict) -> str:
        """Format project context information"""
        structure = context_data.get("project_structure", {})
        patterns = context_data.get("existing_patterns", [])
        deps = context_data.get("dependencies", [])
        tree_formatter = context_data.get("tree_formatter")
        
        # Format the tree structure
        if tree_formatter and structure:
            tree_display = tree_formatter(structure)
        else:
            tree_display = "No project structure analyzed"
        
        return f"""
### Project Structure
```
{tree_display}
```

### Existing Patterns Detected
{chr(10).join([f"- {pattern}" for pattern in patterns]) if patterns else "- No specific patterns detected"}

### Key Dependencies
{chr(10).join([f"- {dep}" for dep in deps]) if deps else "- No major dependencies detected"}
"""
    
    def _check_context_file(self, task_id: str, project_root: Path) -> Dict:
        """Check if context file exists for the current task and return link info"""
        context_dir = project_root / ".cursor" / "rules" / "contexts"
        context_file = context_dir / f"context_{task_id}.txt"
        
        if context_file.exists():
            return {
                "exists": True,
                "path": f".cursor/rules/contexts/context_{task_id}.txt",
                "relative_path": f"contexts/context_{task_id}.txt"
            }
        else:
            return {
                "exists": False,
                "path": f".cursor/rules/contexts/context_{task_id}.txt",
                "relative_path": f"contexts/context_{task_id}.txt"
            }
    
    def _generate_context_link_section(self, task_id: str, project_root: Path) -> str:
        """Generate the context file link section"""
        context_info = self._check_context_file(task_id, project_root)
        
        if context_info["exists"]:
            return f"""
## 📋 Task Context File
**Context File:** [`{context_info['relative_path']}`]({context_info['path']})
**Status:** ✅ Context file exists - Contains detailed progress, decisions, and notes for this task
**Usage:** Review the context file for complete task history and continuation notes
"""
        else:
            return f"""
## 📋 Task Context File
**Context File:** `{context_info['relative_path']}` 
**Status:** ❌ Context file not created yet
**Next Action:** AI should create `{context_info['path']}` to track progress, decisions, and notes for this task
**Template:** Follow the context file format from existing context files in the contexts directory
""" 