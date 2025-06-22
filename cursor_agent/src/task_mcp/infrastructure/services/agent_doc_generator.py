import argparse
import subprocess
from pathlib import Path

import yaml


def _get_project_root() -> Path:
    """Find the project root directory by locating the 'cursor_agent' directory."""
    current_dir = Path(__file__).resolve()
    while current_dir != current_dir.parent:
        if (current_dir / "cursor_agent").is_dir():
            return current_dir
        current_dir = current_dir.parent

    # Fallback for when script is inside cursor_agent
    current_dir = Path(__file__).resolve()
    if "cursor_agent" in current_dir.parts:
        while current_dir.name != "cursor_agent":
            current_dir = current_dir.parent
        return current_dir.parent

    raise FileNotFoundError(
        "Could not find the project root containing 'cursor_agent' directory."
    )


# Always resolve relative to the project root
PROJECT_ROOT = _get_project_root()
AGENT_YAML_LIB = PROJECT_ROOT / "cursor_agent/yaml-lib"
AGENTS_OUTPUT_DIR = PROJECT_ROOT / ".cursor/rules/agents"
CONVERT_SCRIPT = PROJECT_ROOT / "cursor_agent/yaml-lib/convert_yaml_to_mdc_format.py"


def clear_agents_output_dir():
    if AGENTS_OUTPUT_DIR.exists() and AGENTS_OUTPUT_DIR.is_dir():
        for file in AGENTS_OUTPUT_DIR.iterdir():
            if file.is_file():
                file.unlink()


def convert_yaml_to_mdc(yaml_file: Path) -> str:
    try:
        result = subprocess.run(
            ["python", str(CONVERT_SCRIPT), str(yaml_file)],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"(Error converting {yaml_file.name} to MDC: {e})"


def generate_agent_docs(agent_name=None, clear_all=False):
    AGENTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if clear_all:
        clear_agents_output_dir()
    agent_dirs = []
    if agent_name:
        target_dir = AGENT_YAML_LIB / agent_name
        if target_dir.exists() and target_dir.is_dir():
            agent_dirs = [target_dir]
        else:
            print(f"Agent directory '{agent_name}' not found.")
            return
    else:
        agent_dirs = [
            d
            for d in AGENT_YAML_LIB.iterdir()
            if d.is_dir() and d.name.endswith("_agent")
        ]
    for agent_dir in agent_dirs:
        job_desc_file = agent_dir / "job_desc.yaml"
        if not job_desc_file.exists():
            continue
        try:
            with open(job_desc_file, "r", encoding="utf-8") as f:
                job_desc = yaml.safe_load(f)
        except Exception:
            continue
        # Compose markdown
        md_lines = [f"# {job_desc.get('name', agent_dir.name)}\n"]
        md_lines.append(f"**Slug:** `{job_desc.get('slug', agent_dir.name)}`  ")
        if "role_definition" in job_desc:
            md_lines.append(f"**Role Definition:** {job_desc['role_definition']}  ")
        if "when_to_use" in job_desc:
            md_lines.append(f"**When to Use:** {job_desc['when_to_use']}  ")
        if "groups" in job_desc:
            md_lines.append(f"**Groups:** {', '.join(job_desc['groups'])}  ")
        md_lines.append("\n---\n")
        # Add more details from contexts, rules, tools, output_format if desired
        for subdir in ["contexts", "rules", "tools", "output_format"]:
            subdir_path = agent_dir / subdir
            if subdir_path.exists() and subdir_path.is_dir():
                md_lines.append(f"## {subdir.title()}\n")
                for file in subdir_path.glob("*.yaml"):
                    md_lines.append(f"### {file.stem}\n")
                    md_section = convert_yaml_to_mdc(file)
                    md_lines.append(md_section)
        # Write to .cursor/rules/agents/{agent_name}.mdc
        output_file = AGENTS_OUTPUT_DIR / f"{agent_dir.name}.mdc"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))


def generate_docs_for_assignees(assignees, clear_all=False):
    """Generate agent docs for all unique assignees in the list."""
    seen = set()
    for assignee in assignees or []:
        if assignee.startswith("@"):  # Remove '@' if present
            assignee_name = assignee[1:]
        else:
            assignee_name = assignee
        if not assignee_name.endswith("_agent"):
            agent_name = f"{assignee_name}_agent"
        else:
            agent_name = assignee_name
        if agent_name not in seen:
            generate_agent_docs(agent_name=agent_name, clear_all=clear_all)
            seen.add(agent_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate agent documentation.")
    parser.add_argument(
        "--agent", type=str, help="Name of the agent directory (e.g., coding_agent)"
    )
    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Clear all agent docs before generating",
    )
    args = parser.parse_args()
    generate_agent_docs(agent_name=args.agent, clear_all=args.clear_all)
