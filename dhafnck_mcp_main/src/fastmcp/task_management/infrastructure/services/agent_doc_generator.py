import os
import yaml
from pathlib import Path
import shutil
import argparse
import subprocess
from typing import Optional, List


class AgentDocGenerator:
    """Agent Documentation Generator for converting YAML agent definitions to MDC format"""
    
    def __init__(self, agent_yaml_lib: Optional[Path] = None, agents_output_dir: Optional[Path] = None):
        self.project_root = self._get_project_root()
        self.agent_yaml_lib = agent_yaml_lib or self.project_root / "yaml-lib"
        self.agents_output_dir = agents_output_dir or self.project_root / ".cursor/rules/agents"
        self.convert_script = self.project_root / "yaml-lib/convert_yaml_to_mdc_format.py"
    
    def _get_project_root(self) -> Path:
        """Find the project root directory by locating common project markers."""
        current_dir = Path(__file__).resolve()
        
        # Look for project markers (CLAUDE.md, .cursor directory, yaml-lib directory)
        while current_dir != current_dir.parent:
            if ((current_dir / "CLAUDE.md").exists() or 
                (current_dir / ".cursor").is_dir() or 
                (current_dir / "yaml-lib").is_dir() or
                (current_dir / "dhafnck_mcp_main").is_dir()):
                return current_dir
            current_dir = current_dir.parent

        # If no project markers found, assume the parent of dhafnck_mcp_main is the project root
        current_dir = Path(__file__).resolve()
        while current_dir != current_dir.parent:
            if current_dir.name == "dhafnck_mcp_main":
                return current_dir.parent
            current_dir = current_dir.parent

        raise FileNotFoundError("Could not find the project root. Expected to find CLAUDE.md, .cursor, yaml-lib, or dhafnck_mcp_main directory.")
    
    def clear_agents_output_dir(self):
        """Clear all files in the agents output directory"""
        if self.agents_output_dir.exists() and self.agents_output_dir.is_dir():
            for file in self.agents_output_dir.iterdir():
                if file.is_file():
                    file.unlink()
    
    def convert_yaml_to_mdc(self, yaml_file: Path) -> str:
        """Convert a YAML file to MDC format by loading and dumping it."""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return yaml.dump(data)
        except Exception as e:
            return f"(Error converting {yaml_file.name} to MDC: {e})"
    
    def generate_agent_docs(self, agent_name: Optional[str] = None, clear_all: bool = False):
        """Generate agent documentation for specified agent or all agents"""
        self.agents_output_dir.mkdir(parents=True, exist_ok=True)
        
        if clear_all:
            self.clear_agents_output_dir()
        
        agent_dirs = []
        if agent_name:
            target_dir = self.agent_yaml_lib / agent_name
            if target_dir.exists() and target_dir.is_dir():
                agent_dirs = [target_dir]
            else:
                print(f"Agent directory '{agent_name}' not found.")
                return
        else:
            agent_dirs = [d for d in self.agent_yaml_lib.iterdir() if d.is_dir() and d.name.endswith('_agent')]
        
        for agent_dir in agent_dirs:
            self._generate_single_agent_doc(agent_dir)
    
    def _generate_single_agent_doc(self, agent_dir: Path):
        """Generate documentation for a single agent"""
        job_desc_file = agent_dir / "job_desc.yaml"
        if not job_desc_file.exists():
            return
        
        try:
            with open(job_desc_file, 'r', encoding='utf-8') as f:
                job_desc = yaml.safe_load(f)
        except Exception as e:
            return
        
        # Compose markdown
        md_lines = [f"# {job_desc.get('name', agent_dir.name)}\n"]
        md_lines.append(f"**Slug:** `{job_desc.get('slug', agent_dir.name)}`  ")
        
        if 'role_definition' in job_desc:
            md_lines.append(f"**Role Definition:** {job_desc['role_definition']}  ")
        
        if 'when_to_use' in job_desc:
            md_lines.append(f"**When to Use:** {job_desc['when_to_use']}  ")
        
        if 'groups' in job_desc:
            md_lines.append(f"**Groups:** {', '.join(job_desc['groups'])}  ")
        
        md_lines.append("\n---\n")
        
        # Add more details from contexts, rules, tools, output_format if desired
        for subdir in ["contexts", "rules", "tools", "output_format"]:
            subdir_path = agent_dir / subdir
            if subdir_path.exists() and subdir_path.is_dir():
                md_lines.append(f"## {subdir.title()}\n")
                for file in subdir_path.glob("*.yaml"):
                    md_lines.append(f"### {file.stem}\n")
                    md_section = self.convert_yaml_to_mdc(file)
                    md_lines.append(md_section)
        
        # Write to .cursor/rules/agents/{agent_name}.mdc
        output_file = self.agents_output_dir / f"{agent_dir.name}.mdc"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
    
    def generate_docs_for_assignees(self, assignees: Optional[List[str]], clear_all: bool = False):
        """Generate agent docs for all unique assignees in the list."""
        if not assignees:
            return
            
        seen = set()
        for assignee in assignees:
            if assignee.startswith("@"):  # Remove '@' if present
                assignee_name = assignee[1:]
            else:
                assignee_name = assignee
            
            if not assignee_name.endswith("_agent"):
                agent_name = f"{assignee_name}_agent"
            else:
                agent_name = assignee_name
            
            if agent_name not in seen:
                self.generate_agent_docs(agent_name=agent_name, clear_all=clear_all)
                seen.add(agent_name)


# Backward compatibility functions (keeping the original function-based API)
def _get_project_root() -> Path:
    """Find the project root directory by locating the 'cursor_agent' directory."""
    generator = AgentDocGenerator()
    return generator.project_root


# Always resolve relative to the project root
PROJECT_ROOT = _get_project_root()
AGENT_YAML_LIB = PROJECT_ROOT / "cursor_agent/yaml-lib"
AGENTS_OUTPUT_DIR = PROJECT_ROOT / ".cursor/rules/agents"
CONVERT_SCRIPT = PROJECT_ROOT / "cursor_agent/yaml-lib/convert_yaml_to_mdc_format.py"


def clear_agents_output_dir():
    generator = AgentDocGenerator(agents_output_dir=AGENTS_OUTPUT_DIR)
    generator.clear_agents_output_dir()


def convert_yaml_to_mdc(yaml_file: Path) -> str:
    generator = AgentDocGenerator()
    return generator.convert_yaml_to_mdc(yaml_file)


def generate_agent_docs(agent_name=None, clear_all=False):
    generator = AgentDocGenerator(
        agent_yaml_lib=AGENT_YAML_LIB, 
        agents_output_dir=AGENTS_OUTPUT_DIR
    )
    generator.generate_agent_docs(agent_name, clear_all)


def generate_docs_for_assignees(assignees, clear_all=False):
    """Generate agent docs for all unique assignees in the list."""
    generator = AgentDocGenerator(
        agent_yaml_lib=AGENT_YAML_LIB,
        agents_output_dir=AGENTS_OUTPUT_DIR
    )
    generator.generate_docs_for_assignees(assignees, clear_all)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate agent documentation.")
    parser.add_argument('--agent', type=str, help='Name of the agent directory (e.g., coding_agent)')
    parser.add_argument('--clear-all', action='store_true', help='Clear all agent docs before generating')
    args = parser.parse_args()
    generate_agent_docs(agent_name=args.agent, clear_all=args.clear_all) 