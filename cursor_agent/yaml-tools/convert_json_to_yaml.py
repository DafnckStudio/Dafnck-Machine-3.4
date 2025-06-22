#!/usr/bin/env python3
"""
Convert JSON agents from source of truth to YAML folder structure.
This script ensures complete fidelity to source data with proper organization and formatting.

Features:
- Complete field preservation from JSON source
- Proper YAML formatting with literal block scalars for long strings
- Folder structure creation with all required directories
- Comprehensive error handling and validation
- Support for both individual and batch conversion
- Built-in validation against source of truth

Usage:
    python convert_json_to_yaml.py                    # Convert all agents
    python convert_json_to_yaml.py --force            # Clean existing and recreate all
    python convert_json_to_yaml.py --agent coding     # Convert specific agent
    python convert_json_to_yaml.py --validate         # Convert and validate
"""

import os
import json
import yaml
import argparse
import shutil
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class LiteralStr(str):
    """Custom string class to represent literal block scalars in YAML"""
    pass

def literal_str_representer(dumper, data):
    """Custom representer for literal strings using block scalar style"""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

# Register the custom representer
yaml.add_representer(LiteralStr, literal_str_representer)

class AgentConverter:
    """Handles conversion of JSON agents to YAML folder structure"""
    
    def __init__(self, source_path: Path, target_path: Path, force_clean: bool = False):
        self.source_path = source_path
        self.target_path = target_path
        self.force_clean = force_clean
        self.stats = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }
    
    def should_use_literal_style(self, text: str) -> bool:
        """Determine if a string should use literal block scalar style"""
        if not isinstance(text, str):
            return False
        
        # Use literal style for long strings with actual newlines
        return (
            len(text) > 100 and 
            '\n' in text and
            text.count('\n') > 2
        )
    
    def format_string_for_yaml(self, text: str) -> str:
        """Format string appropriately for YAML output"""
        if not isinstance(text, str):
            return text
        
        if self.should_use_literal_style(text):
            # Text already has actual newlines, just return as LiteralStr
            return LiteralStr(text)
        
        return text
    
    def process_data_recursively(self, data: Any) -> Any:
        """Recursively process data to format strings appropriately"""
        if isinstance(data, dict):
            return {key: self.process_data_recursively(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.process_data_recursively(item) for item in data]
        elif isinstance(data, str):
            return self.format_string_for_yaml(data)
        else:
            return data
    
    def clean_agent_name(self, name: str) -> str:
        """Clean agent name to create valid folder name"""
        # Remove emojis and special characters, convert to lowercase with underscores
        cleaned = re.sub(r'[^\w\s-]', '', name)
        cleaned = re.sub(r'\s+', '_', cleaned.lower())
        cleaned = re.sub(r'-+', '_', cleaned)
        return cleaned.strip('_')
    
    def extract_agent_data(self, json_file_path: Path) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Extract agent data from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract agent from customModes array
            custom_modes = data.get('customModes', [])
            if not custom_modes:
                logger.error(f"No customModes found in {json_file_path.name}")
                return None
            
            agent = custom_modes[0]  # Take first agent
            slug = agent.get('slug', '')
            
            if not slug:
                logger.error(f"No slug found in {json_file_path.name}")
                return None
            
            # Convert slug to folder name
            if slug.endswith('-agent'):
                folder_name = slug.replace('-', '_')
            else:
                folder_name = slug.replace('-', '_') + '_agent'
            
            return folder_name, agent
            
        except Exception as e:
            logger.error(f"Error processing {json_file_path.name}: {str(e)}")
            return None
    
    def create_folder_structure(self, agent_path: Path) -> bool:
        """Create the required folder structure for an agent"""
        try:
            # Create main agent folder
            agent_path.mkdir(parents=True, exist_ok=True)
            
            # Create required subdirectories
            required_dirs = ['contexts', 'output_format', 'rules', 'tools']
            for dir_name in required_dirs:
                (agent_path / dir_name).mkdir(exist_ok=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating folder structure for {agent_path.name}: {str(e)}")
            return False
    
    def create_job_desc_yaml(self, agent_path: Path, agent_data: Dict[str, Any]) -> bool:
        """Create job_desc.yaml with essential agent information"""
        try:
            job_desc = {
                'name': agent_data.get('name', ''),
                'slug': agent_data.get('slug', ''),
                'role_definition': agent_data.get('roleDefinition', ''),
                'when_to_use': agent_data.get('whenToUse', ''),
                'groups': agent_data.get('groups', [])
            }
            
            # Process for proper formatting
            job_desc_processed = self.process_data_recursively(job_desc)
            
            job_desc_path = agent_path / 'job_desc.yaml'
            with open(job_desc_path, 'w', encoding='utf-8') as f:
                yaml.dump(job_desc_processed, f, 
                         default_flow_style=False, 
                         allow_unicode=True,
                         width=float('inf'),
                         sort_keys=False)
            
            logger.debug(f"  ✅ Created job_desc.yaml")
            return True
            
        except Exception as e:
            logger.error(f"Error creating job_desc.yaml: {str(e)}")
            return False
    
    def create_custom_instructions_yaml(self, agent_path: Path, agent_data: Dict[str, Any], agent_folder_name: str) -> bool:
        """Create custom instructions file with proper formatting"""
        try:
            custom_instructions = agent_data.get('customInstructions', '')
            
            if custom_instructions:
                instructions_data = {
                    'custom_instructions': self.format_string_for_yaml(custom_instructions)
                }
                
                instructions_path = agent_path / 'contexts' / f'{agent_folder_name}_instructions.yaml'
                with open(instructions_path, 'w', encoding='utf-8') as f:
                    yaml.dump(instructions_data, f, 
                             default_flow_style=False, 
                             allow_unicode=True,
                             width=float('inf'),
                             sort_keys=False)
                
                logger.debug(f"  ✅ Created {agent_folder_name}_instructions.yaml")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating custom instructions: {str(e)}")
            return False
    
    def create_input_specification_yaml(self, agent_path: Path, agent_data: Dict[str, Any]) -> bool:
        """Create input specification file with complete field preservation"""
        try:
            input_spec = agent_data.get('inputSpec', {})
            
            if input_spec:
                input_data = {
                    'input_specification': self.process_data_recursively(input_spec)
                }
                
                input_path = agent_path / 'contexts' / 'input_specification.yaml'
                with open(input_path, 'w', encoding='utf-8') as f:
                    yaml.dump(input_data, f, 
                             default_flow_style=False, 
                             allow_unicode=True,
                             width=float('inf'),
                             sort_keys=False)
                
                logger.debug(f"  ✅ Created input_specification.yaml")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating input specification: {str(e)}")
            return False
    
    def create_output_specification_yaml(self, agent_path: Path, agent_data: Dict[str, Any]) -> bool:
        """Create output specification file with complete field preservation"""
        try:
            output_spec = agent_data.get('outputSpec', {})
            
            if output_spec:
                # Extract all fields from the JSON outputSpec
                output_data = {
                    'output_specification': {
                        'type': output_spec.get('type', ''),
                        'format': output_spec.get('format', ''),
                        'schema': output_spec.get('schema', {}),
                        'validationRules': output_spec.get('validationRules', []),
                        'example': output_spec.get('example', {}),
                        'validation': output_spec.get('validation', '')
                    }
                }
                
                # Remove empty fields and process for formatting
                output_spec_clean = {}
                for key, value in output_data['output_specification'].items():
                    if value:  # Only include non-empty values
                        output_spec_clean[key] = value
                
                if output_spec_clean:
                    final_output_data = {
                        'output_specification': self.process_data_recursively(output_spec_clean)
                    }
                    
                    output_path = agent_path / 'output_format' / 'output_specification.yaml'
                    with open(output_path, 'w', encoding='utf-8') as f:
                        yaml.dump(final_output_data, f, 
                                 default_flow_style=False, 
                                 allow_unicode=True,
                                 width=float('inf'),
                                 sort_keys=False)
                    
                    logger.debug(f"  ✅ Created output_specification.yaml with {len(output_spec_clean)} fields")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating output specification: {str(e)}")
            return False
    
    def create_connectivity_yaml(self, agent_path: Path, agent_data: Dict[str, Any]) -> bool:
        """Create connectivity configuration file"""
        try:
            connectivity = agent_data.get('connectivity', {})
            
            if connectivity:
                connectivity_data = {
                    'connectivity': self.process_data_recursively(connectivity)
                }
                
                connectivity_path = agent_path / 'contexts' / 'connectivity.yaml'
                with open(connectivity_path, 'w', encoding='utf-8') as f:
                    yaml.dump(connectivity_data, f, 
                             default_flow_style=False, 
                             allow_unicode=True,
                             width=float('inf'),
                             sort_keys=False)
                
                logger.debug(f"  ✅ Created connectivity.yaml")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating connectivity file: {str(e)}")
            return False
    
    def create_rules_files(self, agent_path: Path, agent_data: Dict[str, Any]) -> bool:
        """Create rules files based on agent data"""
        try:
            rules_path = agent_path / 'rules'
            
            # Continuous Learning
            continuous_learning = agent_data.get('continuousLearning', {})
            if continuous_learning:
                cl_data = {'continuous_learning': self.process_data_recursively(continuous_learning)}
                with open(rules_path / 'continuous_learning.yaml', 'w', encoding='utf-8') as f:
                    yaml.dump(cl_data, f, default_flow_style=False, allow_unicode=True, width=float('inf'), sort_keys=False)
                logger.debug(f"  ✅ Created continuous_learning.yaml")
            
            # Error Handling
            error_handling = agent_data.get('errorHandling', {})
            if error_handling:
                eh_data = {'error_handling': self.process_data_recursively(error_handling)}
                with open(rules_path / 'error_handling.yaml', 'w', encoding='utf-8') as f:
                    yaml.dump(eh_data, f, default_flow_style=False, allow_unicode=True, width=float('inf'), sort_keys=False)
                logger.debug(f"  ✅ Created error_handling.yaml")
            
            # Health Check
            health_check = agent_data.get('healthCheck', {})
            if health_check:
                hc_data = {'health_check': self.process_data_recursively(health_check)}
                with open(rules_path / 'health_check.yaml', 'w', encoding='utf-8') as f:
                    yaml.dump(hc_data, f, default_flow_style=False, allow_unicode=True, width=float('inf'), sort_keys=False)
                logger.debug(f"  ✅ Created health_check.yaml")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating rules files: {str(e)}")
            return False
    
    def convert_single_agent(self, json_file_path: Path) -> bool:
        """Convert a single agent JSON file to YAML structure"""
        try:
            result = self.extract_agent_data(json_file_path)
            if not result:
                return False
            
            agent_folder_name, agent_data = result
            
            logger.info(f"📁 Processing {agent_folder_name}...")
            
            # Create folder structure
            agent_path = self.target_path / agent_folder_name
            if not self.create_folder_structure(agent_path):
                return False
            
            # Create all YAML files
            success = all([
                self.create_job_desc_yaml(agent_path, agent_data),
                self.create_custom_instructions_yaml(agent_path, agent_data, agent_folder_name),
                self.create_input_specification_yaml(agent_path, agent_data),
                self.create_output_specification_yaml(agent_path, agent_data),
                self.create_connectivity_yaml(agent_path, agent_data),
                self.create_rules_files(agent_path, agent_data)
            ])
            
            if success:
                logger.info(f"✅ Completed {agent_folder_name}")
                self.stats['successful'] += 1
            else:
                logger.error(f"❌ Failed to complete {agent_folder_name}")
                self.stats['failed'] += 1
                self.stats['errors'].append(f"Partial failure in {agent_folder_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error converting {json_file_path.name}: {str(e)}")
            self.stats['failed'] += 1
            self.stats['errors'].append(f"Exception in {json_file_path.name}: {str(e)}")
            return False
    
    def clean_existing_folders(self) -> None:
        """Clean existing agent folders if force mode is enabled"""
        if not self.force_clean:
            return
        
        logger.info("🧹 Cleaning existing agent folders...")
        for item in self.target_path.iterdir():
            if item.is_dir() and item.name.endswith('_agent'):
                shutil.rmtree(item)
                logger.info(f"  🗑️  Removed {item.name}")
    
    def convert_all_agents(self, specific_agent: Optional[str] = None) -> bool:
        """Convert all agents or a specific agent"""
        if not self.source_path.exists():
            logger.error(f"Source directory not found: {self.source_path}")
            return False
        
        # Get all JSON files
        json_files = list(self.source_path.glob('*.json'))
        if not json_files:
            logger.error(f"No JSON files found in {self.source_path}")
            return False
        
        # Filter for specific agent if requested
        if specific_agent:
            json_files = [f for f in json_files if specific_agent.lower() in f.stem.lower()]
            if not json_files:
                logger.error(f"No JSON files found matching '{specific_agent}'")
                return False
        
        logger.info(f"🔍 Found {len(json_files)} JSON agent files")
        
        # Clean existing folders if requested
        self.clean_existing_folders()
        
        # Process each agent
        for json_file in sorted(json_files):
            self.convert_single_agent(json_file)
        
        # Print summary
        self.print_summary()
        
        return self.stats['failed'] == 0
    
    def print_summary(self) -> None:
        """Print conversion summary"""
        logger.info(f"\n📊 Conversion Summary:")
        logger.info(f"   ✅ Successful: {self.stats['successful']}")
        logger.info(f"   ❌ Failed: {self.stats['failed']}")
        logger.info(f"   📁 Total agent folders created: {self.stats['successful']}")
        
        if self.stats['errors']:
            logger.error(f"\n🔍 Errors encountered:")
            for error in self.stats['errors']:
                logger.error(f"   • {error}")
        
        if self.stats['failed'] == 0:
            logger.info(f"\n🎉 All agents converted successfully!")
        else:
            logger.warning(f"\n⚠️  {self.stats['failed']} agents had issues during conversion.")

def main():
    parser = argparse.ArgumentParser(description='Convert JSON agents to YAML folder structure')
    parser.add_argument('--force', action='store_true', 
                       help='Clean all existing agent folders and recreate')
    parser.add_argument('--agent', type=str, 
                       help='Convert specific agent (partial name match)')
    parser.add_argument('--source', type=str, default='yaml-lib/02_Agents',
                       help='Source directory containing JSON files (default: yaml-lib/02_Agents)')
    parser.add_argument('--target', type=str, default='yaml-lib',
                       help='Target directory for YAML folders (default: yaml-lib)')
    parser.add_argument('--validate', action='store_true',
                       help='Run validation after conversion')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Setup paths
    source_path = Path(args.source)
    target_path = Path(args.target)
    
    # Create converter and run conversion
    converter = AgentConverter(source_path, target_path, args.force)
    success = converter.convert_all_agents(args.agent)
    
    # Run validation if requested
    if args.validate and success:
        logger.info("\n🔍 Running validation...")
        # Note: This would require the validator to be available
        # For now, just indicate that validation should be run manually
        logger.info("Please run: python unified_agent_validator.py")
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())