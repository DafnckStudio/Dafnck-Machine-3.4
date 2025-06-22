#!/usr/bin/env python3
"""
Generate Python enum file for all agents in cursor_agent/yaml-tools directory.
This tool scans all agent folders and creates a comprehensive enum that can be used
throughout the project for role management and validation.

Features:
- Scans all agent directories in yaml-lib
- Extracts agent names and slugs from job_desc.yaml files
- Generates Python enum with proper naming conventions
- Creates both slug-based and name-based enums
- Includes comprehensive documentation and metadata
- Validates agent directory structure

Usage:
    python generate_enum_agents.py                    # Generate enum file
    python generate_enum_agents.py --output custom.py # Specify output file
    python generate_enum_agents.py --validate         # Validate only, no generation
    python generate_enum_agents.py --verbose          # Detailed output
"""

import os
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re


class AgentInfo:
    """Container for agent information"""
    def __init__(self, folder_name: str, name: str, slug: str, role_definition: str, when_to_use: str, groups: List[str]):
        self.folder_name = folder_name
        self.name = name
        self.slug = slug
        self.role_definition = role_definition
        self.when_to_use = when_to_use
        self.groups = groups
        self.enum_name = self._generate_enum_name()
        self.enum_value = self._generate_enum_value()
    
    def _generate_enum_name(self) -> str:
        """Generate a valid Python enum name from folder name"""
        # Remove _agent suffix if present
        name = self.folder_name
        if name.endswith('_agent'):
            name = name[:-6]
        
        # Convert to uppercase with underscores
        enum_name = name.upper()
        
        # Ensure it starts with a letter
        if not enum_name[0].isalpha():
            enum_name = 'AGENT_' + enum_name
        
        return enum_name
    
    def _generate_enum_value(self) -> str:
        """Generate enum value (using slug, but with underscores)"""
        return self.slug.replace('-', '_')


class AgentEnumGenerator:
    """Generator for Python enum file containing all agents"""
    
    def __init__(self, yaml_lib_path: str = "cursor_agent/yaml-lib"):
        self.yaml_lib_path = Path(yaml_lib_path)
        self.agents: List[AgentInfo] = []
        self.validation_errors: List[str] = []
    
    def scan_agents(self) -> bool:
        """Scan all agent directories and extract information"""
        if not self.yaml_lib_path.exists():
            self.validation_errors.append(f"YAML lib directory not found: {self.yaml_lib_path}")
            return False
        
        agent_dirs = [d for d in self.yaml_lib_path.iterdir() 
                     if d.is_dir() and d.name.endswith('_agent')]
        
        if not agent_dirs:
            self.validation_errors.append("No agent directories found")
            return False
        
        print(f"Found {len(agent_dirs)} agent directories")
        
        for agent_dir in sorted(agent_dirs):
            self._process_agent_directory(agent_dir)
        
        return len(self.agents) > 0
    
    def _process_agent_directory(self, agent_dir: Path) -> None:
        """Process a single agent directory"""
        job_desc_file = agent_dir / "job_desc.yaml"
        
        if not job_desc_file.exists():
            self.validation_errors.append(f"Missing job_desc.yaml in {agent_dir.name}")
            return
        
        try:
            with open(job_desc_file, 'r', encoding='utf-8') as f:
                job_desc = yaml.safe_load(f)
            
            # Extract required fields
            name = job_desc.get('name', '')
            slug = job_desc.get('slug', '')
            role_definition = job_desc.get('role_definition', '')
            when_to_use = job_desc.get('when_to_use', '')
            groups = job_desc.get('groups', [])
            
            # Validate required fields
            if not name or not slug:
                self.validation_errors.append(f"Missing name or slug in {agent_dir.name}")
                return
            
            agent_info = AgentInfo(
                folder_name=agent_dir.name,
                name=name,
                slug=slug,
                role_definition=role_definition,
                when_to_use=when_to_use,
                groups=groups
            )
            
            self.agents.append(agent_info)
            
        except Exception as e:
            self.validation_errors.append(f"Error processing {agent_dir.name}: {e}")
    
    def generate_enum_file(self, output_path: str = "cursor_agent/src/task_mcp/domain/enums/agent_roles.py") -> bool:
        """Generate the Python enum file"""
        if not self.agents:
            print("No agents found to generate enum")
            return False
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        enum_content = self._generate_enum_content()
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(enum_content)
            
            print(f"✅ Generated enum file: {output_file}")
            print(f"📊 Total agents: {len(self.agents)}")
            return True
            
        except Exception as e:
            print(f"❌ Error writing enum file: {e}")
            return False
    
    def _generate_enum_content(self) -> str:
        """Generate the complete enum file content"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f'''"""
Auto-generated Agent Roles Enum
Generated on: {timestamp}
Total agents: {len(self.agents)}

This file contains all available agent roles from the YAML library.
Do not edit manually - regenerate using tools/generate_enum_agents.py
"""

from enum import Enum
from typing import List, Dict, Optional
import os
import yaml


class AgentRole(Enum):
    """Enumeration of all available agent roles"""
    
'''
        
        # Add enum values
        for agent in sorted(self.agents, key=lambda x: x.enum_name):
            content += f'    {agent.enum_name} = "{agent.enum_value}"\n'
        
        content += '''

    @classmethod
    def get_all_roles(cls) -> List[str]:
        """Get list of all available role slugs"""
        return [role.value for role in cls]
    
    @classmethod
    def get_role_by_slug(cls, slug: str) -> Optional['AgentRole']:
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
        return self.value.replace('-', '_')
    
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
    folder_name = role.value.replace('-', '_')
    
    # Build path to job_desc.yaml file
    yaml_path = os.path.join("cursor_agent", "yaml-lib", folder_name, "job_desc.yaml")
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            yaml_data = yaml.safe_load(file)
            
        if yaml_data:
            # Add folder_name and slug to the metadata
            yaml_data['folder_name'] = folder_name
            yaml_data['slug'] = role.value
            return yaml_data
            
    except (FileNotFoundError, yaml.YAMLError, IOError):
        # Return None if file doesn't exist or can't be parsed
        pass
    
    return None


# Legacy role mappings for backward compatibility
LEGACY_ROLE_MAPPINGS = {
    "senior_developer": "coding-agent",
    "platform_engineer": "devops-agent", 
    "qa_engineer": "functional-tester-agent",
    "code_reviewer": "code-reviewer-agent",
    "devops_engineer": "devops-agent",
    "security_engineer": "security-auditor-agent",
    "technical_writer": "documentation-agent",
    "task_planner": "task-planning-agent",
    "context_engineer": "core-concept-agent",
    "cache_engineer": "efficiency-optimization-agent",
    "metrics_engineer": "analytics-setup-agent",
    "cli_engineer": "coding-agent"
}


def resolve_legacy_role(legacy_role: str) -> Optional[str]:
    """Resolve legacy role names to current slugs"""
    return LEGACY_ROLE_MAPPINGS.get(legacy_role)


def get_all_role_slugs_with_legacy() -> List[str]:
    """Get all role slugs including legacy mappings"""
    current_roles = AgentRole.get_all_roles()
    legacy_roles = list(LEGACY_ROLE_MAPPINGS.keys())
    return current_roles + legacy_roles


'''
        
        return content
    
    def validate_agents(self) -> bool:
        """Validate all agents and report issues"""
        print(f"🔍 Validating {len(self.agents)} agents...")
        
        # Check for duplicate slugs
        slugs = [agent.slug for agent in self.agents]
        duplicate_slugs = [slug for slug in set(slugs) if slugs.count(slug) > 1]
        
        if duplicate_slugs:
            self.validation_errors.extend([f"Duplicate slug: {slug}" for slug in duplicate_slugs])
        
        # Check for duplicate enum names
        enum_names = [agent.enum_name for agent in self.agents]
        duplicate_enum_names = [name for name in set(enum_names) if enum_names.count(name) > 1]
        
        if duplicate_enum_names:
            self.validation_errors.extend([f"Duplicate enum name: {name}" for name in duplicate_enum_names])
        
        # Report validation results
        if self.validation_errors:
            print(f"❌ Validation failed with {len(self.validation_errors)} errors:")
            for error in self.validation_errors:
                print(f"   • {error}")
            return False
        else:
            print("✅ All agents validated successfully")
            return True
    
    def print_summary(self) -> None:
        """Print summary of discovered agents"""
        if not self.agents:
            print("No agents found")
            return
        
        print(f"\n📊 Agent Summary ({len(self.agents)} total):")
        print("-" * 80)
        
        for agent in sorted(self.agents, key=lambda x: x.name):
            groups_str = ", ".join(agent.groups) if agent.groups else "none"
            print(f"• {agent.name}")
            print(f"  Slug: {agent.slug}")
            print(f"  Enum: {agent.enum_name}")
            print(f"  Folder: {agent.folder_name}")
            print(f"  Groups: {groups_str}")
            print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate Python enum for all agents")
    parser.add_argument('--output', '-o', type=str, 
                       default='cursor_agent/src/task_mcp/domain/enums/agent_roles.py',
                       help='Output file path (default: cursor_agent/src/task_mcp/domain/enums/agent_roles.py)')
    parser.add_argument('--yaml-lib', type=str, default='cursor_agent/yaml-lib',
                       help='Path to yaml-lib directory (default: cursor_agent/yaml-lib)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate only, do not generate file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output with agent summary')
    
    args = parser.parse_args()
    
    print("🚀 Agent Enum Generator")
    print(f"📁 YAML Library: {args.yaml_lib}")
    
    # Create generator
    generator = AgentEnumGenerator(args.yaml_lib)
    
    # Scan agents
    if not generator.scan_agents():
        print("❌ Failed to scan agents")
        return 1
    
    # Validate agents
    if not generator.validate_agents():
        print("❌ Validation failed")
        return 1
    
    # Print summary if verbose
    if args.verbose:
        generator.print_summary()
    
    # Generate enum file (unless validate-only)
    if not args.validate:
        if not generator.generate_enum_file(args.output):
            print("❌ Failed to generate enum file")
            return 1
        
        print(f"✅ Successfully generated enum file: {args.output}")
    else:
        print("✅ Validation complete (no file generated)")
    
    return 0


if __name__ == "__main__":
    exit(main())
