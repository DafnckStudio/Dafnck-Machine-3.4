import sys
import yaml
from pathlib import Path

def yaml_to_markdown_section(yaml_data, indent=0):
    md_lines = []
    prefix = '    ' * indent + '- '
    sub_prefix = '    ' * (indent + 1) + '- '
    if isinstance(yaml_data, dict):
        for key, value in yaml_data.items():
            if isinstance(value, dict):
                md_lines.append(f"{prefix}{key}:")
                md_lines.extend(yaml_to_markdown_section(value, indent + 1))
            elif isinstance(value, list):
                md_lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, (dict, list)):
                        md_lines.extend(yaml_to_markdown_section(item, indent + 1))
                    else:
                        md_lines.append(f"{sub_prefix}{item}")
            else:
                md_lines.append(f"{prefix}{key}: {value}")
    elif isinstance(yaml_data, list):
        for item in yaml_data:
            if isinstance(item, (dict, list)):
                md_lines.extend(yaml_to_markdown_section(item, indent))
            else:
                md_lines.append(f"{prefix}{item}")
    else:
        md_lines.append(f"{prefix}{yaml_data}")
    return md_lines

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_yaml_to_mdc_format.py <yaml_file>")
        sys.exit(1)
    yaml_path = Path(sys.argv[1])
    if not yaml_path.exists():
        print(f"File not found: {yaml_path}")
        sys.exit(1)
    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
    title = yaml_path.stem.replace('_', ' ').title()
    print(f"### {title}")
    md_section = yaml_to_markdown_section(yaml_data)
    print('\n'.join(md_section))

if __name__ == "__main__":
    main() 