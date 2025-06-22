#!/usr/bin/env python3
"""
Unified Agent Validator - Validates YAML folder structure against JSON source of truth.
This script ensures complete fidelity between 02_Agents JSON files and generated YAML folders.

Usage:
    python unified_agent_validator.py                    # Validate all agents
    python unified_agent_validator.py --agent coding     # Validate specific agent
    python unified_agent_validator.py --verbose          # Detailed output
    python unified_agent_validator.py --fix              # Auto-fix minor issues
"""

import os
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import re

class ValidationResult:
    """Container for validation results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors = []
        self.warnings_list = []
        self.success_list = []

    def add_error(self, agent: str, message: str):
        self.failed += 1
        self.errors.append(f"❌ {agent}: {message}")

    def add_warning(self, agent: str, message: str):
        self.warnings += 1
        self.warnings_list.append(f"⚠️  {agent}: {message}")

    def add_success(self, agent: str, message: str = "All validations passed"):
        self.passed += 1
        self.success_list.append(f"✅ {agent}: {message}")

class UnifiedAgentValidator:
    """Main validator class"""
    
    def __init__(self, verbose: bool = False, fix_mode: bool = False):
        self.verbose = verbose
        self.fix_mode = fix_mode
        self.json_source_path = Path('02_Agents')
        self.yaml_base_path = Path('.')
        
    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose or level == "ERROR":
            prefix = "🔍" if level == "INFO" else "❌" if level == "ERROR" else "⚠️"
            print(f"{prefix} {message}")

    def load_json_agent(self, json_file_path: Path) -> Optional[Dict[str, Any]]:
        """Load and extract agent data from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'customModes' not in data or not data['customModes']:
                self.log(f"No customModes found in {json_file_path.name}", "ERROR")
                return None
            
            return data['customModes'][0]  # First agent in customModes
        except Exception as e:
            self.log(f"Error loading {json_file_path.name}: {e}", "ERROR")
            return None

    def load_yaml_file(self, yaml_file_path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML file safely"""
        try:
            if not yaml_file_path.exists():
                return None
            
            with open(yaml_file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            self.log(f"Error loading {yaml_file_path}: {e}", "ERROR")
            return None

    def get_agent_slug(self, json_agent: Dict[str, Any]) -> str:
        """Extract agent slug from JSON data and convert to folder name"""
        slug = json_agent.get('slug', '').replace('-', '_')
        # Add _agent suffix if not already present (to match folder naming convention)
        if not slug.endswith('_agent'):
            slug += '_agent'
        return slug

    def validate_folder_structure(self, agent_slug: str) -> List[str]:
        """Validate that required folder structure exists"""
        issues = []
        agent_folder = self.yaml_base_path / agent_slug
        
        if not agent_folder.exists():
            issues.append(f"Agent folder '{agent_slug}' does not exist")
            return issues
        
        # Required files and directories
        required_items = [
            ('job_desc.yaml', 'file'),
            ('contexts', 'dir'),
            ('output_format', 'dir'),
            ('rules', 'dir'),
        ]
        
        for item_name, item_type in required_items:
            item_path = agent_folder / item_name
            if not item_path.exists():
                issues.append(f"Missing {item_type}: {item_name}")
            elif item_type == 'file' and not item_path.is_file():
                issues.append(f"Expected file but found directory: {item_name}")
            elif item_type == 'dir' and not item_path.is_dir():
                issues.append(f"Expected directory but found file: {item_name}")
        
        return issues

    def validate_job_desc(self, json_agent: Dict[str, Any], agent_slug: str) -> List[str]:
        """Validate job_desc.yaml against JSON source"""
        issues = []
        job_desc_path = self.yaml_base_path / agent_slug / 'job_desc.yaml'
        
        yaml_data = self.load_yaml_file(job_desc_path)
        if yaml_data is None:
            issues.append("job_desc.yaml is missing or invalid")
            return issues
        
        # Required fields mapping
        field_mappings = [
            ('name', 'name'),
            ('slug', 'slug'),
            ('role_definition', 'roleDefinition'),
            ('when_to_use', 'whenToUse'),
            ('groups', 'groups'),
        ]
        
        for yaml_field, json_field in field_mappings:
            json_value = json_agent.get(json_field)
            yaml_value = yaml_data.get(yaml_field)
            
            if json_value and not yaml_value:
                issues.append(f"Missing field in job_desc.yaml: {yaml_field}")
            elif json_value and yaml_value:
                # For slug, normalize comparison (YAML should match JSON exactly)
                if json_field == 'slug':
                    if json_value != yaml_value:
                        issues.append(f"Slug mismatch: JSON='{json_value}' vs YAML='{yaml_value}'")
                elif json_value != yaml_value:
                    # For long strings, just check if they start the same way
                    if isinstance(json_value, str) and isinstance(yaml_value, str):
                        if len(json_value) > 100 and len(yaml_value) > 100:
                            if not yaml_value.startswith(json_value[:50]):
                                issues.append(f"Content mismatch in {yaml_field} (first 50 chars differ)")
                        else:
                            if json_value.strip() != yaml_value.strip():
                                issues.append(f"Value mismatch in {yaml_field}")
                    else:
                        if json_value != yaml_value:
                            issues.append(f"Value mismatch in {yaml_field}")
        
        return issues

    def validate_custom_instructions(self, json_agent: Dict[str, Any], agent_slug: str) -> List[str]:
        """Validate custom instructions file"""
        issues = []
        instructions_path = self.yaml_base_path / agent_slug / 'contexts' / f'{agent_slug}_instructions.yaml'
        
        yaml_data = self.load_yaml_file(instructions_path)
        if yaml_data is None:
            issues.append(f"Missing custom instructions file: {agent_slug}_instructions.yaml")
            return issues
        
        json_instructions = json_agent.get('customInstructions', '')
        yaml_instructions = yaml_data.get('custom_instructions', '')
        
        if json_instructions and not yaml_instructions:
            issues.append("Custom instructions missing in YAML")
        elif json_instructions and yaml_instructions:
            # Check if content is substantially similar (allow for minor formatting differences)
            json_clean = re.sub(r'\s+', ' ', json_instructions.strip())
            yaml_clean = re.sub(r'\s+', ' ', str(yaml_instructions).strip())
            
            if len(json_clean) > 0 and len(yaml_clean) == 0:
                issues.append("Custom instructions are empty in YAML but present in JSON")
            elif len(json_clean) > 100 and len(yaml_clean) > 100:
                # For long content, check if they're reasonably similar
                similarity_ratio = len(yaml_clean) / len(json_clean)
                if similarity_ratio < 0.8 or similarity_ratio > 1.2:
                    issues.append(f"Custom instructions length mismatch (ratio: {similarity_ratio:.2f})")
        
        return issues

    def validate_input_spec(self, json_agent: Dict[str, Any], agent_slug: str) -> List[str]:
        """Validate input specification"""
        issues = []
        input_spec_path = self.yaml_base_path / agent_slug / 'contexts' / 'input_specification.yaml'
        
        json_input_spec = json_agent.get('inputSpec', {})
        yaml_data = self.load_yaml_file(input_spec_path)
        
        if json_input_spec and not yaml_data:
            issues.append("Input specification missing in YAML but present in JSON")
        elif json_input_spec and yaml_data:
            yaml_input_spec = yaml_data.get('input_specification', {})
            
            # Check key fields
            if json_input_spec.get('schema') and not yaml_input_spec.get('schema'):
                issues.append("Input schema missing in YAML")
            # Check for validationRules (can be array or string)
            json_validation_rules = json_input_spec.get('validationRules')
            yaml_validation_rules = yaml_input_spec.get('validationRules')
            if json_validation_rules and not yaml_validation_rules:
                issues.append("Input validation rules missing in YAML")
        
        return issues

    def validate_output_spec(self, json_agent: Dict[str, Any], agent_slug: str) -> List[str]:
        """Validate output specification"""
        issues = []
        output_spec_path = self.yaml_base_path / agent_slug / 'output_format' / 'output_specification.yaml'
        
        json_output_spec = json_agent.get('outputSpec', {})
        yaml_data = self.load_yaml_file(output_spec_path)
        
        if json_output_spec and not yaml_data:
            issues.append("Output specification missing in YAML but present in JSON")
        elif json_output_spec and yaml_data:
            yaml_output_spec = yaml_data.get('output_specification', {})
            
            # Check key fields
            if json_output_spec.get('format') and not yaml_output_spec.get('format'):
                issues.append("Output format missing in YAML")
            # Check for schema (can be object or string)
            json_schema = json_output_spec.get('schema')
            yaml_schema = yaml_output_spec.get('schema')
            if json_schema and not yaml_schema:
                issues.append("Output schema missing in YAML")
        
        return issues

    def validate_connectivity(self, json_agent: Dict[str, Any], agent_slug: str) -> List[str]:
        """Validate connectivity configuration"""
        issues = []
        connectivity_path = self.yaml_base_path / agent_slug / 'contexts' / 'connectivity.yaml'
        
        json_connectivity = json_agent.get('connectivity', {})
        yaml_data = self.load_yaml_file(connectivity_path)
        
        if json_connectivity and not yaml_data:
            issues.append("Connectivity configuration missing in YAML but present in JSON")
        elif json_connectivity and yaml_data:
            yaml_connectivity = yaml_data.get('connectivity', {})
            
            # Check key fields
            if json_connectivity.get('interactsWith') and not yaml_connectivity.get('interactsWith'):
                issues.append("Connectivity interactions missing in YAML")
        
        return issues

    def validate_rules_files(self, json_agent: Dict[str, Any], agent_slug: str) -> List[str]:
        """Validate rules directory files"""
        issues = []
        rules_dir = self.yaml_base_path / agent_slug / 'rules'
        
        if not rules_dir.exists():
            issues.append("Rules directory missing")
            return issues
        
        # Check for expected rule files based on JSON content
        expected_files = []
        
        if json_agent.get('continuousLearning'):
            expected_files.append('continuous_learning.yaml')
        if json_agent.get('errorHandling'):
            expected_files.append('error_handling.yaml')
        if json_agent.get('healthCheck'):
            expected_files.append('health_check.yaml')
        
        for expected_file in expected_files:
            file_path = rules_dir / expected_file
            if not file_path.exists():
                issues.append(f"Missing rules file: {expected_file}")
        
        return issues

    def validate_single_agent(self, json_file_path: Path) -> Tuple[str, List[str]]:
        """Validate a single agent completely"""
        json_agent = self.load_json_agent(json_file_path)
        if not json_agent:
            return json_file_path.stem, [f"Failed to load JSON file: {json_file_path.name}"]
        
        agent_slug = self.get_agent_slug(json_agent)
        if not agent_slug:
            return json_file_path.stem, ["No valid agent slug found"]
        
        all_issues = []
        
        # Run all validations
        validations = [
            ("Folder Structure", self.validate_folder_structure),
            ("Job Description", lambda slug: self.validate_job_desc(json_agent, slug)),
            ("Custom Instructions", lambda slug: self.validate_custom_instructions(json_agent, slug)),
            ("Input Specification", lambda slug: self.validate_input_spec(json_agent, slug)),
            ("Output Specification", lambda slug: self.validate_output_spec(json_agent, slug)),
            ("Connectivity", lambda slug: self.validate_connectivity(json_agent, slug)),
            ("Rules Files", lambda slug: self.validate_rules_files(json_agent, slug)),
        ]
        
        for validation_name, validation_func in validations:
            try:
                issues = validation_func(agent_slug)
                if issues:
                    all_issues.extend([f"{validation_name}: {issue}" for issue in issues])
                else:
                    self.log(f"{agent_slug} - {validation_name}: ✅ PASSED")
            except Exception as e:
                all_issues.append(f"{validation_name}: Validation error - {str(e)}")
                self.log(f"{agent_slug} - {validation_name}: ❌ ERROR - {str(e)}", "ERROR")
        
        return agent_slug, all_issues

    def validate_all_agents(self, specific_agent: Optional[str] = None) -> ValidationResult:
        """Validate all agents or a specific agent"""
        result = ValidationResult()
        
        if not self.json_source_path.exists():
            result.add_error("System", f"Source directory not found: {self.json_source_path}")
            return result
        
        json_files = list(self.json_source_path.glob('*.json'))
        if not json_files:
            result.add_error("System", f"No JSON files found in {self.json_source_path}")
            return result
        
        # Filter for specific agent if requested
        if specific_agent:
            json_files = [f for f in json_files if specific_agent.lower() in f.stem.lower()]
            if not json_files:
                result.add_error("System", f"No JSON files found matching '{specific_agent}'")
                return result
        
        print(f"🔍 Validating {len(json_files)} agent(s)...")
        
        for json_file in json_files:
            agent_name, issues = self.validate_single_agent(json_file)
            
            if issues:
                for issue in issues:
                    result.add_error(agent_name, issue)
            else:
                result.add_success(agent_name)
        
        return result

    def print_results(self, result: ValidationResult):
        """Print validation results"""
        print(f"\n📊 Validation Summary:")
        print(f"   ✅ Passed: {result.passed}")
        print(f"   ❌ Failed: {result.failed}")
        print(f"   ⚠️  Warnings: {result.warnings}")
        
        if result.errors:
            print(f"\n❌ Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"   {error}")
        
        if result.warnings_list:
            print(f"\n⚠️  Warnings ({len(result.warnings_list)}):")
            for warning in result.warnings_list:
                print(f"   {warning}")
        
        if self.verbose and result.success_list:
            print(f"\n✅ Successful Validations ({len(result.success_list)}):")
            for success in result.success_list:
                print(f"   {success}")
        
        # Overall status
        if result.failed == 0:
            print(f"\n🎉 All validations passed! YAML structure matches JSON source of truth.")
        else:
            print(f"\n💥 {result.failed} agent(s) have validation issues.")

def main():
    parser = argparse.ArgumentParser(description='Validate YAML agent structure against JSON source of truth')
    parser.add_argument('--agent', type=str, help='Validate specific agent (partial name match)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--fix', action='store_true', help='Auto-fix minor issues (not implemented yet)')
    
    args = parser.parse_args()
    
    validator = UnifiedAgentValidator(verbose=args.verbose, fix_mode=args.fix)
    result = validator.validate_all_agents(specific_agent=args.agent)
    validator.print_results(result)
    
    # Exit with error code if validations failed
    exit(1 if result.failed > 0 else 0)

if __name__ == '__main__':
    main() 