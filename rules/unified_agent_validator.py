#!/usr/bin/env python3
"""
Unified Agent Validator for DafnckMachine v3.1
Combines agent format validation, loading tests, system initialization, and repair functionality
"""

import os
import json
import re
import sys
import logging
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import glob

# --- Configuration ---
BASE_DIR = Path(__file__).parent.parent.parent.parent
MACHINE_DIR = BASE_DIR / '01_Machine'
AGENTS_DIR = MACHINE_DIR / '02_Agents'
AGENT_RUN_DIR = MACHINE_DIR / '03_Brain' / 'Agents-Check'
BRAIN_DIR = MACHINE_DIR / '03_Brain'
DOCS_DIR = MACHINE_DIR / '04_Documentation'
VISION_DIR = BASE_DIR / '02_Vision'
ROOMODES_FILE = BASE_DIR / '.roomodes'
AGENT_FORMAT_SCHEMA_PATH = AGENT_RUN_DIR / 'Agent-Format.json'
LOG_DIR = AGENT_RUN_DIR / 'Log'
AGENT_HEALTH_REPORT = LOG_DIR / 'unified_validation_report.md'
SYSTEM_INIT_LOG = LOG_DIR / 'unified_system_init.log'
STEP_FILE = BRAIN_DIR / 'Step.json'
BACKUP_DIR = AGENT_RUN_DIR / 'backups'

# Cursor configuration paths
CURSORRULES_FILE = BASE_DIR / '.cursorrules'
CURSOR_DIR = AGENT_RUN_DIR / 'cursor'

# Template update configuration
TEMPLATE_FILE = DOCS_DIR / '01_System' / 'Template-Step-Structure.md'

# Workflow agent order for .roomodes synchronization
WORKFLOW_AGENT_ORDER = [
    "uber-orchestrator-agent", "nlu-processor-agent", "elicitation-agent",
    "compliance-scope-agent", "idea-generation-agent", "idea-refinement-agent",
    "core-concept-agent", "market-research-agent", "mcp-researcher-agent",
    "technology-advisor-agent", "system-architect-agent", "branding-agent",
    "design-system-agent", "ui-designer-agent", "prototyping-agent",
    "design-qa-analyst", "ux-researcher-agent", "tech-spec-agent",
    "task-planning-agent", "prd-architect-agent", "mcp-configuration-agent",
    "algorithmic-problem-solver-agent", "coding-agent", "code-reviewer-agent",
    "documentation-agent", "development-orchestrator-agent", "test-case-generator-agent",
    "test-orchestrator-agent", "functional-tester-agent", "exploratory-tester-agent",
    "performance-load-tester-agent", "visual-regression-testing-agent",
    "uat-coordinator-agent", "lead-testing-agent", "compliance-testing-agent",
    "security-penetration-tester-agent", "usability-heuristic-agent",
    "adaptive-deployment-strategist-agent", "devops-agent",
    "user-feedback-collector-agent", "efficiency-optimization-agent",
    "knowledge-evolution-agent", "security-auditor-agent", "swarm-scaler-agent",
    "root-cause-analysis-agent", "remediation-agent", "health-monitor-agent",
    "incident-learning-agent", "marketing-strategy-orchestrator", "campaign-manager-agent",
    "content-strategy-agent", "graphic-design-agent", "growth-hacking-idea-agent",
    "video-production-agent", "analytics-setup-agent", "seo-sem-agent",
    "social-media-setup-agent", "community-strategy-agent", "project-initiator-agent"
]

# --- Logging Setup ---
AGENT_RUN_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(SYSTEM_INIT_LOG),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Utility Functions ---

def load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    """Loads a JSON file, returning its content or None if an error occurs."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading {path}: {e}")
        return None

def write_json_file(path: Path, data: Dict[str, Any]):
    """Writes data to a JSON file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error writing to {path}: {e}")

def create_backup(file_path: Path) -> Path:
    """Creates a backup of a file before modification."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{file_path.stem}_{timestamp}.json"
    shutil.copy2(file_path, backup_path)
    return backup_path

def list_agent_files() -> List[Path]:
    """Lists all JSON files in the Agents directory."""
    if not AGENTS_DIR.exists():
        logger.warning(f"Agents directory not found: {AGENTS_DIR}")
        return []
    return [f for f in AGENTS_DIR.iterdir() if f.is_file() and f.suffix.lower() == '.json']

# --- Cursor Configuration Functions ---

def convert_agent_to_cursor_instruction(agent_data: Dict[str, Any], agent_name: str) -> str:
    """Converts a single agent to Cursor instruction format."""
    if 'customModes' not in agent_data or not agent_data['customModes']:
        return ""
    
    mode = agent_data['customModes'][0]
    
    # Extract agent information
    name = mode.get('name', agent_name)
    description = mode.get('description', '')
    instructions = mode.get('instructions', '')
    
    # Build cursor instruction
    cursor_instruction = f"## @{agent_name}\n\n"
    cursor_instruction += f"**{name}**\n\n"
    
    if description:
        cursor_instruction += f"{description}\n\n"
    
    if instructions:
        cursor_instruction += f"### Instructions:\n{instructions}\n\n"
    
    # Add connectivity information if available
    connectivity = mode.get('connectivity', {})
    if connectivity.get('interactsWith'):
        cursor_instruction += f"### Collaborates with:\n"
        for agent in connectivity['interactsWith']:
            cursor_instruction += f"- @{agent}\n"
        cursor_instruction += "\n"
    
    cursor_instruction += "---\n\n"
    return cursor_instruction

def generate_cursor_config() -> bool:
    """Generates .cursorrules file from current agent files."""
    try:
        logger.info("🎯 Generating Cursor configuration...")
        
        # Get all agent files
        agent_files = list_agent_files()
        if not agent_files:
            logger.error("No agent files found")
            return False
        
        # Start building the .cursorrules content
        cursor_content = """# DafnckMachine v3.1 - Specialized AI Agents for Cursor

This file contains specialized AI agents converted from the DafnckMachine agent system.
Each agent has specific expertise and can be invoked using @agent-name syntax.

## Usage
- Use @agent-name to invoke a specific agent
- Agents can collaborate with each other as specified in their connectivity
- Each agent has specialized knowledge and capabilities

## Available Agents

"""
        
        # Process agents in workflow order
        processed_agents = set()
        
        # First, process agents in the defined workflow order
        for agent_name in WORKFLOW_AGENT_ORDER:
            agent_file = AGENTS_DIR / f"{agent_name}.json"
            if agent_file.exists():
                agent_data = load_json_file(agent_file)
                if agent_data:
                    cursor_content += convert_agent_to_cursor_instruction(agent_data, agent_name)
                    processed_agents.add(agent_name)
        
        # Then process any remaining agents
        for agent_file in agent_files:
            agent_name = agent_file.stem
            if agent_name not in processed_agents:
                agent_data = load_json_file(agent_file)
                if agent_data:
                    cursor_content += convert_agent_to_cursor_instruction(agent_data, agent_name)
        
        # Write the .cursorrules file
        with open(CURSORRULES_FILE, 'w', encoding='utf-8') as f:
            f.write(cursor_content)
        
        logger.info(f"✅ Generated .cursorrules with {len(agent_files)} agents")
        return True
        
    except Exception as e:
        logger.error(f"Error generating cursor config: {e}")
        return False

def backup_cursor_files() -> bool:
    """Creates backups of existing cursor files."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if CURSORRULES_FILE.exists():
            backup_path = BACKUP_DIR / f"cursorrules_{timestamp}.txt"
            shutil.copy2(CURSORRULES_FILE, backup_path)
            logger.info(f"📋 Backed up .cursorrules to {backup_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error backing up cursor files: {e}")
        return False

def sync_cursor_config(backup: bool = True) -> bool:
    """Synchronizes cursor configuration with current agents."""
    try:
        logger.info("🔄 Synchronizing Cursor configuration...")
        
        if backup:
            backup_cursor_files()
        
        success = generate_cursor_config()
        
        if success:
            logger.info("✅ Cursor configuration synchronized successfully")
        else:
            logger.error("❌ Failed to synchronize cursor configuration")
        
        return success
        
    except Exception as e:
        logger.error(f"Error synchronizing cursor config: {e}")
        return False

# --- Template Update System ---

def get_current_agent_list() -> Dict[str, List[str]]:
    """Gets the current agent list organized by categories."""
    agent_files = list_agent_files()
    
    # Categorize agents based on their names and roles
    categories = {
        "Orchestration & Management": [],
        "Project Initiation & Planning": [],
        "Requirements & Analysis": [],
        "Development & Technical": [],
        "Testing & Quality": [],
        "Design & User Experience": [],
        "Content & Communication": [],
        "Data & Analytics": [],
        "Business & Strategy": [],
        "Security & Compliance": [],
        "Operations & Monitoring": [],
        "Specialized Tools": []
    }
    
    # Define categorization patterns
    orchestration_patterns = ['orchestrator', 'uber-', 'swarm-scaler', 'workflow-architect']
    planning_patterns = ['project-initiator', 'idea-generation', 'idea-refinement', 'task-planning', 'task-deep-manager', 'task-sync']
    requirements_patterns = ['nlu-processor', 'elicitation', 'market-research', 'compliance-scope', 'prd-architect']
    development_patterns = ['coding', 'system-architect', 'devops', 'tech-spec', 'algorithmic-problem-solver', 'code-reviewer', 'mcp-configuration', 'mcp-researcher']
    testing_patterns = ['test-', 'functional-tester', 'exploratory-tester', 'performance-load-tester', 'visual-regression-testing', 'uat-coordinator', 'lead-testing', 'compliance-testing', 'security-penetration-tester', 'usability-heuristic']
    design_patterns = ['ui-designer', 'ux-researcher', 'design-', 'prototyping', 'branding', 'graphic-design']
    content_patterns = ['content-strategy', 'documentation', 'scribe', 'user-feedback-collector', 'video-production']
    data_patterns = ['analytics-setup', 'brainjs-ml', 'knowledge-evolution', 'deep-research']
    business_patterns = ['growth-hacking-idea', 'campaign-manager', 'marketing-strategy', 'seo-sem', 'social-media-setup', 'community-strategy', 'technology-advisor']
    security_patterns = ['security-auditor', 'ethical-review', 'compliance-testing']
    operations_patterns = ['health-monitor', 'remediation', 'root-cause-analysis', 'incident-learning', 'efficiency-optimization', 'adaptive-deployment-strategist']
    specialized_patterns = ['debugger', 'core-concept']
    
    for agent_file in agent_files:
        agent_name = agent_file.stem
        
        # Load agent data to get description
        agent_data = load_json_file(agent_file)
        description = ""
        if agent_data and 'customModes' in agent_data and agent_data['customModes']:
            mode = agent_data['customModes'][0]
            role_def = mode.get('roleDefinition', '')
            description = role_def.split('.')[0] if role_def else mode.get('name', '')
        
        # Categorize based on patterns
        categorized = False
        
        for pattern in orchestration_patterns:
            if pattern in agent_name:
                categories["Orchestration & Management"].append(f"`@{agent_name}` - {description}")
                categorized = True
                break
        
        if not categorized:
            for pattern in planning_patterns:
                if pattern in agent_name:
                    categories["Project Initiation & Planning"].append(f"`@{agent_name}` - {description}")
                    categorized = True
                    break
        
        if not categorized:
            for pattern in requirements_patterns:
                if pattern in agent_name:
                    categories["Requirements & Analysis"].append(f"`@{agent_name}` - {description}")
                    categorized = True
                    break
        
        if not categorized:
            for pattern in development_patterns:
                if pattern in agent_name:
                    categories["Development & Technical"].append(f"`@{agent_name}` - {description}")
                    categorized = True
                    break
        
        if not categorized:
            for pattern in testing_patterns:
                if pattern in agent_name:
                    categories["Testing & Quality"].append(f"`@{agent_name}` - {description}")
                    categorized = True
                    break
        
        if not categorized:
            for pattern in design_patterns:
                if pattern in agent_name:
                    categories["Design & User Experience"].append(f"`@{agent_name}` - {description}")
                    categorized = True
                    break
        
        if not categorized:
            for pattern in content_patterns:
                if pattern in agent_name:
                    categories["Content & Communication"].append(f"`@{agent_name}` - {description}")
                    categorized = True
                    break
        
        if not categorized:
            for pattern in data_patterns:
                if pattern in agent_name:
                    categories["Data & Analytics"].append(f"`@{agent_name}` - {description}")
                    categorized = True
                    break
        
        if not categorized:
            for pattern in business_patterns:
                if pattern in agent_name:
                    categories["Business & Strategy"].append(f"`@{agent_name}` - {description}")
                    categorized = True
                    break
        
        if not categorized:
            for pattern in security_patterns:
                if pattern in agent_name:
                    categories["Security & Compliance"].append(f"`@{agent_name}` - {description}")
                    categorized = True
                    break
        
        if not categorized:
            for pattern in operations_patterns:
                if pattern in agent_name:
                    categories["Operations & Monitoring"].append(f"`@{agent_name}` - {description}")
                    categorized = True
                    break
        
        if not categorized:
            for pattern in specialized_patterns:
                if pattern in agent_name:
                    categories["Specialized Tools"].append(f"`@{agent_name}` - {description}")
                    categorized = True
                    break
        
        # If still not categorized, put in specialized tools
        if not categorized:
            categories["Specialized Tools"].append(f"`@{agent_name}` - {description}")
    
    # Sort each category
    for category in categories:
        categories[category].sort()
    
    return categories

def update_template_agent_list() -> bool:
    """Updates the Template-Step-Structure.md with current agent list."""
    try:
        logger.info("🔄 Updating Template-Step-Structure.md with current agent list...")
        
        if not TEMPLATE_FILE.exists():
            logger.error(f"Template file not found: {TEMPLATE_FILE}")
            return False
        
        # Read current template
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get current agent list
        agent_categories = get_current_agent_list()
        total_agents = sum(len(agents) for agents in agent_categories.values())
        
        # Build new Quick Agent Reference Guide section
        new_guide = "### Quick Agent Reference Guide\n\n"
        new_guide += f"**Total Agents Available: {total_agents}**\n\n"
        
        for category, agents in agent_categories.items():
            if agents:  # Only include categories that have agents
                new_guide += f"**{category}:**\n"
                for agent in agents:
                    new_guide += f"- {agent}\n"
                new_guide += "\n"
        
        # Find and replace the Quick Agent Reference Guide section
        import re
        
        # Pattern to match the entire Quick Agent Reference Guide section
        pattern = r'### Quick Agent Reference Guide\n.*?(?=### [A-Z]|\n## [A-Z])'
        
        # Replace the section
        new_content = re.sub(pattern, new_guide, content, flags=re.DOTALL)
        
        # If no match found, try to insert after "Agent Discovery Process"
        if new_content == content:
            discovery_pattern = r'(### Agent Discovery Process\n.*?)\n(### [A-Z])'
            replacement = r'\1\n\n' + new_guide + r'\2'
            new_content = re.sub(discovery_pattern, replacement, content, flags=re.DOTALL)
        
        # If still no match, append at the end of the file
        if new_content == content:
            new_content = content + "\n\n" + new_guide
        
        # Write updated template
        with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"✅ Updated Template-Step-Structure.md with {total_agents} agents in {len([c for c, a in agent_categories.items() if a])} categories")
        return True
        
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        return False

# --- Agent Repair System ---

class AgentRepairer:
    """Comprehensive agent repair system for fixing common issues."""
    
    def __init__(self):
        self.repairs_made = []
        self.reference_mappings = self._build_reference_mappings()
        self.invalid_references = self._build_invalid_references()
        
    def _build_reference_mappings(self) -> Dict[str, str]:
        """Builds mapping of broken references to valid agent names."""
        return {
            # PascalCase fixes
            "MarketingStrategyOrchestrator": "marketing-strategy-orchestrator",
            "DesignQAAnalyst": "design-qa-analyst",
            
            # Quality Assurance mappings
            "quality-assurance-agent": "test-orchestrator-agent",
            "qa-agent": "test-orchestrator-agent",
            
            # Business and Product Management mappings
            "business-analyst-agent": "market-research-agent",
            "product-manager-agent": "prd-architect-agent",
            "ProductOwner": "prd-architect-agent",
            
            # Technical Leadership mappings
            "technical-lead-agent": "system-architect-agent",
            "TechnicalArchitect": "system-architect-agent",
            "architect-agent": "system-architect-agent",
            
            # Project Management mappings
            "project-manager-agent": "task-planning-agent",
            "ProjectManager": "task-planning-agent",
            "scrum-master-agent": "task-planning-agent",
            
            # Development Team mappings
            "developer-agent": "coding-agent",
            "DevelopmentTeam": "development-orchestrator-agent",
            "frontend-developer-agent": "ui-designer-agent",
            "web-developer-agent": "ui-designer-agent",
            
            # Design mappings
            "design-agent": "ui-designer-agent",
            "ux-designer-agent": "ux-researcher-agent",
            "web-designer-agent": "ui-designer-agent",
            
            # Testing mappings
            "testing-agent": "functional-tester-agent",
            "usability-tester-agent": "usability-heuristic-agent",
            "performance-tester-agent": "performance-load-tester-agent",
            "security-tester-agent": "security-penetration-tester-agent",
            "security-testing-agent": "security-penetration-tester-agent",
            "automation-testing-agent": "test-case-generator-agent",
            "AutomationEngineer": "test-case-generator-agent",
            
            # Content and Marketing mappings
            "content-marketing-agent": "content-strategy-agent",
            "social-media-agent": "social-media-setup-agent",
            "marketing-agent": "marketing-strategy-orchestrator",
            "copywriting-agent": "content-strategy-agent",
            
            # Data and Analytics mappings
            "data-scientist-agent": "analytics-setup-agent",
            "data-analyst-agent": "analytics-setup-agent",
            
            # Security and Compliance mappings
            "SecurityArchitect": "security-auditor-agent",
            "compliance-agent": "compliance-scope-agent",
            "legal-compliance-agent": "compliance-scope-agent",
            "ComplianceSpecialist": "compliance-scope-agent",
            
            # Requirements and Analysis mappings
            "RequirementsAnalyst": "elicitation-agent",
            "requirement-analysis-agent": "elicitation-agent",
            "requirement-elicitation-agent": "elicitation-agent",
            
            # Documentation mappings
            "technical-writer-agent": "documentation-agent",
            
            # Other specialized mappings
            "stakeholder-agent": "elicitation-agent",
            "api-design-agent": "tech-spec-agent",
            "conversion-optimization-agent": "growth-hacking-idea-agent",
            "accessibility-agent": "design-qa-analyst",
            "accessibility-testing-agent": "compliance-testing-agent"
        }
    
    def _build_invalid_references(self) -> List[str]:
        """Builds list of invalid references that should be removed."""
        return [
            # Generic references
            "Human stakeholders", "External systems and APIs", "Project management tools",
            "All technical and specialized agents", "All specialized agents", "AllSystemAgents",
            "All system agents", "Project stakeholders and users",
            "Documentation and knowledge systems", "Quality assurance and validation systems",
            
            # System/tool references
            "TaskManagementSystems", "ProjectManagementTools", "DatabaseSystems",
            "APIEndpoints", "FileSystemMonitors", "NotificationSystems",
            "AuditingSystems", "BackupSystems",
            
            # Team references
            "QualityAssuranceTeam", "StakeholderTeam", "StakeholderTeams",
            "AuditTeam", "IncidentResponseTeam",
            
            # Non-existent agents
            "optimization-agent", "performance-agent", "usability-agent", "ci-agent",
            "support-agent", "sales-agent", "email-marketing-agent", "creative-agent",
            "customer-success-agent", "event-marketing-agent", "influencer-marketing-agent",
            "data-privacy-agent", "risk-assessment-agent", "competitive-analysis-agent",
            "product-strategy-agent", "strategy-agent", "trend-analysis-agent",
            "database-administrator-agent", "cost-analyst-agent", "performance-engineer-agent",
            "data-governance-agent", "legal-advisor-agent", "knowledge-management-agent",
            "community-manager-agent", "customer-service-agent", "technical-seo-agent",
            "cost-optimization-agent", "TestDataManager", "RiskManager",
            "SecurityPenetrationTester", "DevOpsEngineer", "TechnologyAdvisor",
            "DataArchitect", "PerformanceEngineer", "TeamLead", "StakeholderRepresentative",
            "ComplianceSpecialist", "TrainingCoordinator", "KnowledgeManager",
            "CommunicationSpecialist", "audio-production-agent", "seo-agent",
            "team-coordinator-agent", "methodology-agent", "process-optimization-agent"
        ]
    
    def fix_groups_format(self, agent_files: List[Path]) -> int:
        """Fixes complex groups format to simple string format."""
        fixes_made = 0
        
        logger.info("🔧 Fixing groups format issues...")
        
        for agent_file in agent_files:
            agent_data = load_json_file(agent_file)
            if not agent_data or 'customModes' not in agent_data:
                continue
                
            mode = agent_data['customModes'][0]
            groups = mode.get('groups', [])
            
            # Check if groups need fixing
            needs_fixing = False
            fixed_groups = []
            
            for group in groups:
                if isinstance(group, list) and len(group) > 0 and group[0] == "edit":
                    # Convert complex ["edit", {...}] to simple "edit"
                    fixed_groups.append("edit")
                    needs_fixing = True
                else:
                    fixed_groups.append(group)
            
            if needs_fixing:
                # Create backup
                backup_path = create_backup(agent_file)
                logger.info(f"Created backup: {backup_path}")
                
                # Apply fix
                mode['groups'] = fixed_groups
                write_json_file(agent_file, agent_data)
                
                self.repairs_made.append(f"Fixed groups format in {agent_file.name}")
                fixes_made += 1
                logger.info(f"✓ Fixed groups format in {agent_file.name}")
        
        return fixes_made
    
    def fix_broken_references(self, agent_files: List[Path]) -> int:
        """Fixes broken interactsWith references."""
        fixes_made = 0
        
        logger.info("🔧 Fixing broken agent references...")
        
        for agent_file in agent_files:
            agent_data = load_json_file(agent_file)
            if not agent_data or 'customModes' not in agent_data:
                continue
                
            mode = agent_data['customModes'][0]
            connectivity = mode.get('connectivity', {})
            interacts_with = connectivity.get('interactsWith', [])
            
            if not isinstance(interacts_with, list):
                continue
                
            # Fix references
            fixed_references = []
            changes_made = False
            
            for ref in interacts_with:
                if isinstance(ref, str):
                    if ref in self.reference_mappings:
                        # Map to correct reference
                        fixed_references.append(self.reference_mappings[ref])
                        changes_made = True
                        logger.info(f"  Mapped {ref} → {self.reference_mappings[ref]} in {agent_file.name}")
                    elif ref in self.invalid_references:
                        # Remove invalid reference
                        changes_made = True
                        logger.info(f"  Removed invalid reference {ref} from {agent_file.name}")
                    else:
                        # Keep valid reference
                        fixed_references.append(ref)
                else:
                    # Log and skip non-string references
                    changes_made = True
                    logger.info(f"  Skipped non-string reference {ref} in {agent_file.name}")
            
            if changes_made:
                # Create backup
                backup_path = create_backup(agent_file)
                logger.info(f"Created backup: {backup_path}")
                
                # Apply fix
                connectivity['interactsWith'] = fixed_references
                mode['connectivity'] = connectivity
                write_json_file(agent_file, agent_data)
                
                self.repairs_made.append(f"Fixed references in {agent_file.name}")
                fixes_made += 1
                logger.info(f"✓ Fixed references in {agent_file.name}")
        
        return fixes_made
    
    def fix_empty_interactions(self, agent_files: List[Path]) -> int:
        """Automatically populates empty interactsWith arrays based on agent role and capabilities."""
        fixes_made = 0
        
        logger.info("🔧 Fixing empty interactsWith arrays...")
        
        # Define interaction patterns based on agent roles and capabilities
        interaction_patterns = {
            # Core orchestration agents
            'uber-orchestrator-agent': ['task-planning-agent', 'development-orchestrator-agent', 'marketing-strategy-orchestrator'],
            'task-deep-manager-agent': ['task-planning-agent', 'uber-orchestrator-agent', 'development-orchestrator-agent'],
            'task-sync-agent': ['task-planning-agent', 'uber-orchestrator-agent', 'task-deep-manager-agent'],
            
            # Planning and strategy agents
            'task-planning-agent': ['uber-orchestrator-agent', 'prd-architect-agent', 'development-orchestrator-agent'],
            'prd-architect-agent': ['task-planning-agent', 'system-architect-agent', 'tech-spec-agent'],
            'system-architect-agent': ['prd-architect-agent', 'tech-spec-agent', 'coding-agent'],
            
            # Development agents
            'development-orchestrator-agent': ['coding-agent', 'code-reviewer-agent', 'test-orchestrator-agent'],
            'coding-agent': ['development-orchestrator-agent', 'code-reviewer-agent', 'tech-spec-agent'],
            'code-reviewer-agent': ['coding-agent', 'development-orchestrator-agent', 'test-orchestrator-agent'],
            
            # Testing agents
            'test-orchestrator-agent': ['development-orchestrator-agent', 'functional-tester-agent', 'test-case-generator-agent'],
            'functional-tester-agent': ['test-orchestrator-agent', 'test-case-generator-agent', 'exploratory-tester-agent'],
            'test-case-generator-agent': ['test-orchestrator-agent', 'functional-tester-agent', 'coding-agent'],
            
            # Design agents
            'ui-designer-agent': ['design-system-agent', 'ux-researcher-agent', 'prototyping-agent'],
            'ux-researcher-agent': ['ui-designer-agent', 'design-system-agent', 'usability-heuristic-agent'],
            'design-system-agent': ['ui-designer-agent', 'branding-agent', 'prototyping-agent'],
            
            # Research and analysis agents
            'market-research-agent': ['idea-generation-agent', 'technology-advisor-agent', 'marketing-strategy-orchestrator'],
            'technology-advisor-agent': ['system-architect-agent', 'market-research-agent', 'mcp-researcher-agent'],
            'mcp-researcher-agent': ['technology-advisor-agent', 'mcp-configuration-agent', 'coding-agent'],
            
            # Marketing agents
            'marketing-strategy-orchestrator': ['campaign-manager-agent', 'content-strategy-agent', 'growth-hacking-idea-agent'],
            'campaign-manager-agent': ['marketing-strategy-orchestrator', 'content-strategy-agent', 'social-media-setup-agent'],
            'content-strategy-agent': ['campaign-manager-agent', 'graphic-design-agent', 'seo-sem-agent'],
            
            # Quality and compliance agents
            'design-qa-analyst': ['ui-designer-agent', 'ux-researcher-agent', 'compliance-testing-agent'],
            'security-auditor-agent': ['security-penetration-tester-agent', 'compliance-testing-agent', 'system-architect-agent'],
            'compliance-testing-agent': ['security-auditor-agent', 'test-orchestrator-agent', 'compliance-scope-agent'],
            
            # Deployment and operations agents
            'devops-agent': ['adaptive-deployment-strategist-agent', 'development-orchestrator-agent', 'security-auditor-agent'],
            'adaptive-deployment-strategist-agent': ['devops-agent', 'health-monitor-agent', 'efficiency-optimization-agent'],
            'health-monitor-agent': ['adaptive-deployment-strategist-agent', 'root-cause-analysis-agent', 'incident-learning-agent'],
            
            # Documentation and knowledge agents
            'documentation-agent': ['coding-agent', 'tech-spec-agent', 'knowledge-evolution-agent'],
            'knowledge-evolution-agent': ['documentation-agent', 'incident-learning-agent', 'efficiency-optimization-agent'],
            
            # User experience and feedback agents
            'user-feedback-collector-agent': ['ux-researcher-agent', 'usability-heuristic-agent', 'analytics-setup-agent'],
            'usability-heuristic-agent': ['user-feedback-collector-agent', 'ux-researcher-agent', 'design-qa-analyst'],
            
            # Analytics and optimization agents
            'analytics-setup-agent': ['user-feedback-collector-agent', 'seo-sem-agent', 'efficiency-optimization-agent'],
            'efficiency-optimization-agent': ['analytics-setup-agent', 'health-monitor-agent', 'knowledge-evolution-agent'],
            
            # Specialized workflow agents
            'elicitation-agent': ['nlu-processor-agent', 'compliance-scope-agent', 'idea-generation-agent'],
            'nlu-processor-agent': ['elicitation-agent', 'uber-orchestrator-agent', 'idea-generation-agent'],
            'compliance-scope-agent': ['elicitation-agent', 'compliance-testing-agent', 'security-auditor-agent']
        }
        
        for agent_file in agent_files:
            agent_data = load_json_file(agent_file)
            if not agent_data or 'customModes' not in agent_data:
                continue
                
            mode = agent_data['customModes'][0]
            agent_slug = mode.get('slug', agent_file.stem)
            connectivity = mode.get('connectivity', {})
            interacts_with = connectivity.get('interactsWith', [])
            
            # Check if interactsWith is empty or contains only invalid references
            if not interacts_with or len(interacts_with) == 0:
                # Get suggested interactions based on agent role
                suggested_interactions = interaction_patterns.get(agent_slug, [])
                
                if suggested_interactions:
                    # Verify that suggested agents actually exist
                    valid_interactions = []
                    for suggested_agent in suggested_interactions:
                        if (AGENTS_DIR / f"{suggested_agent}.json").exists():
                            valid_interactions.append(suggested_agent)
                    
                    if valid_interactions:
                        # Create backup
                        backup_path = create_backup(agent_file)
                        logger.info(f"Created backup: {backup_path}")
                        
                        # Apply fix
                        connectivity['interactsWith'] = valid_interactions
                        mode['connectivity'] = connectivity
                        write_json_file(agent_file, agent_data)
                        
                        self.repairs_made.append(f"Populated interactsWith in {agent_file.name} with {len(valid_interactions)} agents")
                        fixes_made += 1
                        logger.info(f"✓ Populated interactsWith in {agent_file.name} with: {', '.join(valid_interactions)}")
        
        return fixes_made
    
    def repair_all(self, agent_files: List[Path]) -> Dict[str, int]:
        """Runs all repair operations."""
        logger.info("🚀 Starting comprehensive agent repair...")
        
        results = {
            'groups_fixes': self.fix_groups_format(agent_files),
            'reference_fixes': self.fix_broken_references(agent_files),
            'interaction_fixes': self.fix_empty_interactions(agent_files)
        }
        
        total_fixes = sum(results.values())
        logger.info(f"✅ Repair complete! Made {total_fixes} total fixes")
        
        return results

# --- Enhanced Agent Validation ---

class AgentValidator:
    """Comprehensive agent validation combining format and loading tests."""
    
    def __init__(self, schema_path: Path):
        self.schema = load_json_file(schema_path)
        self.validation_errors = []
        self.validation_warnings = []
        
    def validate_agent_comprehensive(self, agent_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Performs comprehensive validation combining both approaches."""
        errors = []
        warnings = []
        
        # Load agent data
        agent_data = load_json_file(agent_path)
        if agent_data is None:
            return False, ["Failed to load or parse JSON"], []
            
        # Basic structure validation
        structure_errors = self._validate_basic_structure(agent_data, agent_path)
        errors.extend(structure_errors)
        
        if not structure_errors:  # Only continue if basic structure is valid
            # Detailed field validation
            field_errors, field_warnings = self._validate_detailed_fields(agent_data, agent_path)
            errors.extend(field_errors)
            warnings.extend(field_warnings)
            
            # Custom instructions validation
            instr_errors = self._validate_custom_instructions(agent_data)
            errors.extend(instr_errors)
            
            # Connectivity validation
            conn_warnings = self._validate_connectivity(agent_data, agent_path)
            warnings.extend(conn_warnings)
            
        return len(errors) == 0, errors, warnings
    
    def _validate_basic_structure(self, data: Dict[str, Any], agent_path: Path) -> List[str]:
        """Validates basic JSON structure."""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Root element must be a dictionary")
            return errors
            
        if "customModes" not in data:
            errors.append("Missing 'customModes' key")
            return errors
            
        custom_modes = data["customModes"]
        if not isinstance(custom_modes, list):
            errors.append("'customModes' must be a list")
            return errors
            
        if len(custom_modes) != 1:
            errors.append("'customModes' must contain exactly one element")
            return errors
            
        mode = custom_modes[0]
        if not isinstance(mode, dict):
            errors.append("customModes item must be a dictionary")
            return errors
            
        # Validate slug matches filename
        slug = mode.get("slug")
        if not slug or slug != agent_path.stem:
            errors.append(f"'slug' must match filename without extension (expected '{agent_path.stem}', got '{slug}')")
            
        return errors
    
    def _validate_detailed_fields(self, data: Dict[str, Any], agent_path: Path) -> Tuple[List[str], List[str]]:
        """Validates all required fields in detail."""
        errors = []
        warnings = []
        mode = data["customModes"][0]
        required_fields = ["slug", "name", "roleDefinition", "customInstructions", "groups"]
        extended_fields = ["whenToUse", "inputSpec", "outputSpec", "connectivity", "continuousLearning"]
        # Check required fields
        for field in required_fields:
            if field not in mode or not mode[field]:
                errors.append(f"Missing or empty required field: '{field}'")
        # Check extended fields (warnings if missing)
        for field in extended_fields:
            if field not in mode or not mode[field]:
                warnings.append(f"Missing extended field: '{field}' (recommended for complete agent definition)")
        # Deep checks for inputSpec/outputSpec
        for spec_name in ["inputSpec", "outputSpec"]:
            if spec_name in mode and mode[spec_name]:
                spec = mode[spec_name]
                for deep_field in ["example", "schema", "validationRules"]:
                    if deep_field not in spec or not spec[deep_field]:
                        errors.append(f"Missing {spec_name}.{deep_field}")
        # Check for errorHandling and healthCheck
        for deep_field in ["errorHandling", "healthCheck"]:
            if deep_field not in mode or not mode[deep_field]:
                errors.append(f"Missing or empty field: '{deep_field}'")
        # Ensure groups includes 'command'
        groups = mode.get("groups", [])
        if "command" not in groups:
            errors.append("'groups' must contain 'command'")
        # Validate nested structures if they exist
        if "inputSpec" in mode and mode["inputSpec"]:
            input_errors = self._validate_nested_object(mode["inputSpec"], "inputSpec", ["type", "format"])
            errors.extend(input_errors)
        if "outputSpec" in mode and mode["outputSpec"]:
            output_errors = self._validate_nested_object(mode["outputSpec"], "outputSpec", ["type", "format"])
            errors.extend(output_errors)
        if "connectivity" in mode and mode["connectivity"]:
            conn_errors = self._validate_nested_object(mode["connectivity"], "connectivity", ["interactsWith", "feedbackLoop"])
            errors.extend(conn_errors)
        if "continuousLearning" in mode and mode["continuousLearning"]:
            learn_errors = self._validate_nested_object(mode["continuousLearning"], "continuousLearning", ["enabled", "mechanism"])
            errors.extend(learn_errors)
        # Validate groups array
        groups_errors = self._validate_groups(mode.get("groups", []))
        errors.extend(groups_errors)
        return errors, warnings
    
    def _validate_nested_object(self, obj: Any, parent_name: str, required_fields: List[str]) -> List[str]:
        """Validates nested object structure."""
        errors = []
        
        if not isinstance(obj, dict):
            errors.append(f"'{parent_name}' must be an object")
            return errors
            
        for field in required_fields:
            if field not in obj or not obj[field]:
                errors.append(f"Missing or empty field: '{parent_name}.{field}'")
                
        return errors
    
    def _validate_groups(self, groups: Any) -> List[str]:
        """Validates groups array structure."""
        errors = []
        
        if not isinstance(groups, list):
            errors.append("'groups' must be a list")
            return errors
            
        if len(groups) < 2 or len(groups) > 5:
            errors.append(f"'groups' must have 2-5 elements (has {len(groups)})")
            
        if not groups or groups[0] != "read":
            errors.append("First element in 'groups' must be 'read'")
            
        has_edit = "edit" in groups
        has_mcp = "mcp" in groups
        has_interaction = "ask_followup_question" in groups or "command" in groups
        
        if not has_edit:
            errors.append("'groups' must contain 'edit'")
        if not has_mcp:
            errors.append("'groups' must contain 'mcp'")
        if not has_interaction:
            errors.append("'groups' must contain either 'ask_followup_question' or 'command'")
            
        # Check for invalid group items
        valid_groups = {"read", "edit", "mcp", "ask_followup_question", "command", "browser"}
        for group in groups:
            if group not in valid_groups:
                errors.append(f"Invalid group item: '{group}'")
                
        return errors
    
    def _validate_custom_instructions(self, data: Dict[str, Any]) -> List[str]:
        """Validates custom instructions structure."""
        errors = []
        mode = data["customModes"][0]
        instructions = mode.get("customInstructions", "")
        if not instructions:
            return ["customInstructions cannot be empty"]
        # Check for all required sections
        required_sections = [
            "Core Purpose", "Key Capabilities", "Operational Process", "Technical Outputs",
            "Domain Specializations", "Quality Standards", "MCP Tools"
        ]
        missing_sections = []
        for section in required_sections:
            if f"**{section}**" not in instructions:
                missing_sections.append(section)
        if missing_sections:
            errors.append(f"Missing customInstructions sections: {', '.join(missing_sections)}")
        return errors
    
    def _validate_connectivity(self, data: Dict[str, Any], agent_path: Path) -> List[str]:
        """Validates interactsWith references."""
        warnings = []
        mode = data["customModes"][0]
        
        connectivity = mode.get("connectivity", {})
        if not connectivity:
            return warnings
            
        interacts_with = connectivity.get("interactsWith", [])
        if not isinstance(interacts_with, list):
            return warnings
            
        invalid_refs = []
        non_string_refs = []
        for interaction in interacts_with:
            if isinstance(interaction, str):
                if interaction and not (AGENTS_DIR / f"{interaction}.json").exists():
                    invalid_refs.append(interaction)
            else:
                non_string_refs.append(str(interaction))

        if invalid_refs:
            warnings.append(f"Invalid interactsWith references: {', '.join(invalid_refs)}")
        if non_string_refs:
            warnings.append(f"Non-string interactsWith entries found: {', '.join(non_string_refs)}")
            
        return warnings

# --- Agent Loading Test ---

def agent_loading_test(agent_path: Path, auto_yes: bool = False) -> Tuple[bool, Optional[str]]:
    """Simulates loading an agent into .roomodes."""
    try:
        agent_data = load_json_file(agent_path)
        if agent_data is None:
            return False, f"Failed to load agent data: {agent_path.name}"

        if "customModes" not in agent_data or not agent_data["customModes"]:
            return False, "Missing or invalid 'customModes'"

        temp_roomodes_content = {"customModes": [agent_data["customModes"][0]]}
        write_json_file(ROOMODES_FILE, temp_roomodes_content)

        agent_slug = agent_data["customModes"][0].get("slug", agent_path.stem)

        if auto_yes:
            logger.info(f"Auto-confirming agent '{agent_slug}' loaded correctly")
            return True, None
        else:
            user_input = input(f"Did agent '{agent_slug}' load correctly in chat mode? (yes/no): ").strip().lower()
            return user_input in ("y", "yes"), None if user_input in ("y", "yes") else "User reported loading failure"

    except Exception as e:
        return False, f"Exception during loading test: {e}"

# --- System Initialization ---

class SystemInitializer:
    """System initialization and validation controller."""
    
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path if workspace_path else BASE_DIR
        self.dna_file = self.workspace_path / '01_Machine' / '03_Brain' / 'DNA.json'
        self.genesis_file = self.workspace_path / '01_Machine' / '03_Brain' / 'Genesis.json'
        self.step_file = self.workspace_path / '01_Machine' / '03_Brain' / 'Step.json'
        self.validation_errors = []
        self.validation_warnings = []
        self.system_status = "uninitialized"

    def initialize_system(self) -> Tuple[bool, Dict[str, Any]]:
        """Conducts complete system initialization."""
        logger.info("Starting DafnckMachine v3.1 System Initialization")

        # Validate core configs
        validation_results = self._validate_core_configs()
        if not validation_results['valid']:
            self.system_status = "failed"
            return False, {
                'status': 'failed',
                'stage': 'configuration_validation',
                'errors': self.validation_errors
            }

        # Load configurations
        configs = self._load_configurations()
        if not configs:
            self.system_status = "failed"
            return False, {
                'status': 'failed',
                'stage': 'configuration_loading',
                'errors': self.validation_errors
            }

        # Cross-validate
        if not self._validate_cross_references(configs):
            self.system_status = "failed"
            return False, {
                'status': 'failed',
                'stage': 'cross_validation',
                'errors': self.validation_errors
            }

        # Initialize agents
        if not self._initialize_agents(configs.get('dna', {})):
            self.system_status = "partial"

        # Setup workflow
        if not self._setup_workflow_orchestration(configs):
            self.system_status = "failed"
            return False, {
                'status': 'failed',
                'stage': 'workflow_setup',
                'errors': self.validation_errors
            }

        # Verify readiness
        readiness_check = self._verify_system_readiness(configs)
        self.system_status = "initialized" if readiness_check and not self.validation_errors else "partial"
        
        self._update_step_file_status(configs)

        return readiness_check and not self.validation_errors, {
            'status': 'success' if self.system_status == 'initialized' else 'partial',
            'stage': 'complete',
            'configs': configs,
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'system_status': self.system_status
        }

    def _validate_core_configs(self) -> Dict[str, Any]:
        """Validates core configuration files."""
        required_files = {
            'dna': self.dna_file,
            'genesis': self.genesis_file,
            'step': self.step_file
        }

        all_valid = True
        for config_type, file_path in required_files.items():
            if not file_path.exists():
                self.validation_errors.append(f"Missing config file: {file_path}")
                all_valid = False
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    logger.info(f"✓ {config_type.upper()} configuration valid")
                except json.JSONDecodeError as e:
                    self.validation_errors.append(f"Invalid JSON in {file_path}: {e}")
                    all_valid = False

        return {'valid': all_valid}

    def _load_configurations(self) -> Optional[Dict[str, Any]]:
        """Loads all core configuration files."""
        dna_config = load_json_file(self.dna_file)
        genesis_config = load_json_file(self.genesis_file)
        step_config = load_json_file(self.step_file)

        if None in [dna_config, genesis_config, step_config]:
            self.validation_errors.append("Failed to load core configuration files")
            return None

        return {
            'dna': dna_config,
            'genesis': genesis_config,
            'step': step_config
        }

    def _validate_cross_references(self, configs: Dict[str, Any]) -> bool:
        """Validates cross-references between configurations."""
        dna = configs.get('dna', {})
        genesis = configs.get('genesis', {})
        
        dna_agents = {agent.get('agentName') for agent in dna.get('agentRegistry', [])}
        genesis_phases = {phase.get('phaseID') for phase in genesis.get('workflowSequence', [])}

        for agent in dna.get('agentRegistry', []):
            agent_name = agent.get('agentName', 'UNKNOWN')
            for phase in agent.get('phases', []):
                if phase not in genesis_phases:
                    self.validation_errors.append(f"Agent '{agent_name}' references undefined phase: '{phase}'")

        return not self.validation_errors

    def _initialize_agents(self, dna_config: Dict[str, Any]) -> bool:
        """Validates agent configurations from DNA.json."""
        required_core_agents = ['uber-orchestrator-agent', 'scribe-agent', 'task-sync-agent']
        available_agents = {agent.get('agentName') for agent in dna_config.get('agentRegistry', [])}

        for required_agent in required_core_agents:
            if required_agent not in available_agents:
                self.validation_errors.append(f"Missing core agent: '{required_agent}'")

        return not self.validation_errors

    def _setup_workflow_orchestration(self, configs: Dict[str, Any]) -> bool:
        """Validates workflow sequence."""
        genesis = configs.get('genesis', {})
        workflow_sequence = genesis.get('workflowSequence', [])
        
        if not workflow_sequence:
            self.validation_errors.append("No workflow sequence defined")
            return False

        return not self.validation_errors

    def _verify_system_readiness(self, configs: Dict[str, Any]) -> bool:
        """Performs final readiness checks."""
        required_dirs = [
            self.workspace_path / '01_Machine' / '01_Workflow',
            self.workspace_path / '01_Machine' / '02_Agents',
            self.workspace_path / '01_Machine' / '03_Brain',
            self.workspace_path / '02_Vision'
        ]

        for dir_path in required_dirs:
            if not dir_path.exists():
                self.validation_warnings.append(f"Missing directory: {dir_path.relative_to(self.workspace_path)}")

        return not self.validation_errors

    def _update_step_file_status(self, configs: Optional[Dict[str, Any]] = None):
        """Updates system status in Step.json."""
        try:
            step_config = configs.get('step', {}) if configs else load_json_file(self.step_file) or {}
            
            step_config.update({
                'lastInitialization': datetime.now().isoformat(),
                'systemStatus': self.system_status,
                'validationResults': {
                    'errors': len(self.validation_errors),
                    'warnings': len(self.validation_warnings),
                    'timestamp': datetime.now().isoformat()
                }
            })

            write_json_file(self.step_file, step_config)
            logger.info(f"Updated system status in {self.step_file}")

        except Exception as e:
            logger.error(f"Failed to update system status: {e}")

# --- Synchronization Logic ---

def sync_modes_to_roomodes(results):
    """Synchronizes valid agent modes to .roomodes file."""
    logger.info("Starting mode synchronization to .roomodes...")
    existing_data = load_json_file(ROOMODES_FILE)
    existing_modes = []
    if existing_data and isinstance(existing_data.get('customModes'), list):
        existing_modes = existing_data['customModes']
    agent_defined_modes = []
    for fname, (passed_validation, _, _) in results.items():
        if passed_validation:
            agent_path = AGENTS_DIR / fname
            agent_config = load_json_file(agent_path)
            if agent_config and agent_config.get("customModes"):
                agent_defined_modes.extend(agent_config["customModes"])
    # Merge modes
    merged_modes_map = {mode['slug']: mode for mode in existing_modes if mode.get('slug')}
    for mode in agent_defined_modes:
        if mode.get('slug'):
            merged_modes_map[mode['slug']] = mode
    # Order according to workflow
    slug_to_mode = {m['slug']: m for m in merged_modes_map.values()}
    ordered_modes = []
    for slug in WORKFLOW_AGENT_ORDER:
        if slug in slug_to_mode:
            ordered_modes.append(slug_to_mode[slug])
            del slug_to_mode[slug]
    ordered_modes.extend(slug_to_mode.values())
    output_data = {"customModes": ordered_modes}
    write_json_file(ROOMODES_FILE, output_data)
    logger.info(f"Synced {len(ordered_modes)} modes to .roomodes")

# --- Interactive Menu ---

def print_menu(agent_files: List[Path]):
    """Prints interactive menu."""
    print("\n--- Unified Agent Validator Menu ---")
    for idx, fname in enumerate(agent_files):
        print(f"  [{idx+1}] {fname.name}")
    print("  [A] Test ALL agents")
    print("  [M] Test MULTIPLE agents (comma-separated)")
    print("  [T] Auto-yes mode (non-interactive)")
    print("  [S] System initialization only")
    print("  [R] Repair ALL agents (groups, references & interactions)")
    print("  [G] Fix groups format only")
    print("  [F] Fix broken references only")
    print("  [I] Fix empty interactions only")
    print("  [X] Sync ALL (both RooCode then Cursor)")
    print("  [Y] Sync to RooCode (.roomodes)")
    print("  [Z] Sync to Cursor (.cursorrules)")
    print("  [Q] Quit")
    print("------------------------------------")

def get_user_selection(agent_files: List[Path]) -> Tuple[List[Path], bool, bool, Optional[str]]:
    """Gets user selection for testing mode."""
    while True:
        print_menu(agent_files)
        choice = input("Select option: ").strip().lower()
        if choice == 'q':
            sys.exit(0)
        elif choice == 'a':
            return agent_files, False, False, None
        elif choice == 't':
            return agent_files, True, False, None
        elif choice == 's':
            return [], False, True, None
        elif choice == 'r':
            return agent_files, False, False, 'repair_all'
        elif choice == 'g':
            return agent_files, False, False, 'fix_groups'
        elif choice == 'f':
            return agent_files, False, False, 'fix_references'
        elif choice == 'i':
            return agent_files, False, False, 'fix_interactions'
        elif choice == 'x':
            return [], False, False, 'sync_all'
        elif choice == 'y':
            return [], False, False, 'sync_roomodes'
        elif choice == 'z':
            return [], False, False, 'sync_cursorrules'
        elif choice == 'm':
            indices = input("Enter comma-separated indices: ").strip()
            try:
                idxs = [int(i) - 1 for i in indices.split(',') if i.strip().isdigit()]
                selected = [agent_files[i] for i in idxs if 0 <= i < len(agent_files)]
                if selected:
                    return selected, False, False, None
            except Exception:
                pass
            print("Invalid input. Try again.")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(agent_files):
                return [agent_files[idx]], False, False, None
        print("Invalid selection. Try again.")

# --- Report Generation ---

def generate_comprehensive_report(agent_results: Dict[str, Tuple[bool, List[str], List[str]]], 
                                system_results: Optional[Dict[str, Any]] = None,
                                repair_results: Optional[Dict[str, int]] = None) -> str:
    """Generates comprehensive validation report."""
    timestamp = datetime.now().isoformat()
    
    report = f"""# Unified Agent Validation Report
Generated: {timestamp}

"""
    
    # Add repair results if available
    if repair_results:
        total_repairs = sum(repair_results.values())
        report += f"""## Repair Summary

- Total repairs made: {total_repairs}
"""
        for repair_type, count in repair_results.items():
            if count > 0:
                report += f"- {repair_type.replace('_', ' ').title()}: {count}\n"
        report += "\n"
    
    report += "## Agent Validation Summary\n"
    
    if agent_results:
        total_agents = len(agent_results)
        valid_agents = sum(1 for passed, _, _ in agent_results.values() if passed)
        
        report += f"""
- Total agents tested: {total_agents}
- Valid agents: {valid_agents}
- Failed agents: {total_agents - valid_agents}
- Success rate: {(valid_agents/total_agents)*100:.1f}%

## Detailed Agent Results
"""
        
        for fname, (passed, errors, warnings) in agent_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            report += f"\n### {fname} - {status}\n"
            
            if errors:
                report += "\n**Errors:**\n"
                for error in errors:
                    report += f"- {error}\n"
                    
            if warnings:
                report += "\n**Warnings:**\n"
                for warning in warnings:
                    report += f"- {warning}\n"
    else:
        report += "\nNo agents were tested.\n"
    
    if system_results:
        report += f"""
## System Initialization Results

- Status: {system_results.get('system_status', 'unknown').upper()}
- Stage: {system_results.get('stage', 'unknown')}
- Errors: {len(system_results.get('errors', []))}
- Warnings: {len(system_results.get('warnings', []))}

"""
        if system_results.get('errors'):
            report += "**System Errors:**\n"
            for error in system_results['errors']:
                report += f"- {error}\n"
                
        if system_results.get('warnings'):
            report += "\n**System Warnings:**\n"
            for warning in system_results['warnings']:
                report += f"- {warning}\n"
    
    # Add deep field issues
    deep_issues = []
    for fname, (passed, errors, warnings) in agent_results.items():
        for e in errors:
            if any(x in e for x in ["Missing inputSpec.example", "Missing inputSpec.schema", "Missing inputSpec.validationRules", "Missing outputSpec.example", "Missing outputSpec.schema", "Missing outputSpec.validationRules", "Missing or empty field: 'errorHandling'", "Missing or empty field: 'healthCheck'", "'groups' must contain 'command'", "Missing customInstructions sections"]):
                deep_issues.append(f"{fname}: {e}")
    if deep_issues:
        report += "\n## Deep Field Issues (Strict Mode)\n\n"
        for issue in deep_issues:
            report += f"- {issue}\n"
    
    return report

# --- Main Function ---

def main():
    """Main entry point for unified validation."""
    parser = argparse.ArgumentParser(description='Unified Agent Validator for DafnckMachine v3.1')
    parser.add_argument('--yes', '-y', action='store_true', help='Auto-yes mode (non-interactive)')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    parser.add_argument('--workspace', type=str, help='Workspace path', default=str(BASE_DIR))
    parser.add_argument('--agents-only', action='store_true', help='Test agents only, skip system init')
    parser.add_argument('--system-only', action='store_true', help='System initialization only')
    # Repair options
    parser.add_argument('--repair', action='store_true', help='Run all repair operations before validation')
    parser.add_argument('--fix-groups', action='store_true', help='Fix groups format issues only')
    parser.add_argument('--fix-references', action='store_true', help='Fix broken interactsWith references only')
    parser.add_argument('--fix-interactions', action='store_true', help='Fix empty interactsWith arrays only')
    parser.add_argument('--auto-repair', action='store_true', help='Automatically repair issues during validation')
    parser.add_argument('--repair-only', action='store_true', help='Run repairs only, skip validation')
    # Cursor options
    parser.add_argument('--cursor', action='store_true', help='Generate cursor configuration after validation')
    parser.add_argument('--cursor-only', action='store_true', help='Generate cursor configuration only, skip validation')
    parser.add_argument('--no-cursor', action='store_true', help='Skip cursor configuration generation')
    parser.add_argument('--cursor-backup', action='store_true', help='Backup existing cursor files before generation')
    # Template options
    parser.add_argument('--update-template', action='store_true', help='Update Template-Step-Structure.md with current agent list')
    parser.add_argument('--template-only', action='store_true', help='Update template only, skip validation')
    # New sync options
    parser.add_argument('--sync-all', action='store_true', help='Sync both .roomodes and .cursorrules')
    parser.add_argument('--sync-roomodes', action='store_true', help='Sync to .roomodes only')
    parser.add_argument('--sync-cursorrules', action='store_true', help='Sync to .cursorrules only')
    parser.add_argument('--strict', action='store_true', help='Enable strict mode: fail agents missing deep fields')
    parser.add_argument('--auto-fix', action='store_true', help='Auto-fix all agents to be fully spec-compliant before validation')
    args = parser.parse_args()
    strict_mode = args.strict
    # Handle new sync CLI flags
    if args.sync_all:
        sync_all()
        sys.exit(0)
    if args.sync_roomodes:
        sync_to_roomodes()
        sys.exit(0)
    if args.sync_cursorrules:
        sync_to_cursorrules()
        sys.exit(0)
    # Handle template-only mode
    if args.template_only or args.update_template:
        print("📝 DafnckMachine v3.1 - Template Update System")
        print("=" * 50)
        
        success = update_template_agent_list()
        
        if success:
            print("\n✅ Template updated successfully!")
            if args.template_only:
                sys.exit(0)
        else:
            print("\n❌ Failed to update template")
            if args.template_only:
                sys.exit(1)

    # Handle cursor-only mode
    if args.cursor_only:
        print("🎯 DafnckMachine v3.1 - Cursor Configuration Generator")
        print("=" * 55)
        
        success = sync_cursor_config(backup=args.cursor_backup)
        
        if success:
            print("\n🎉 Cursor configuration generated successfully!")
            sys.exit(0)
        else:
            print("\n❌ Failed to generate cursor configuration")
            sys.exit(1)

    print("🚀 DafnckMachine v3.1 Unified Agent Validator")
    print("=" * 50)

    # Initialize components
    initializer = SystemInitializer(Path(args.workspace))
    validator = AgentValidator(AGENT_FORMAT_SCHEMA_PATH)
    repairer = AgentRepairer()
    
    agent_results = {}
    system_results = None
    repair_results = None

    # Get agent files for repair/validation
    agent_files = list_agent_files()
    
    # Repair phase
    if args.repair or args.fix_groups or args.fix_references or args.fix_interactions or args.repair_only or args.auto_repair:
        print("\n🔧 Agent Repair Phase")
        print("-" * 25)
        
        if not agent_files:
            print("⚠️  No agent files found for repair")
        else:
            if args.repair or args.repair_only:
                repair_results = repairer.repair_all(agent_files)
            else:
                repair_results = {}
                if args.fix_groups:
                    repair_results['groups_fixes'] = repairer.fix_groups_format(agent_files)
                if args.fix_references:
                    repair_results['reference_fixes'] = repairer.fix_broken_references(agent_files)
                if args.fix_interactions:
                    repair_results['interaction_fixes'] = repairer.fix_empty_interactions(agent_files)
            
            total_repairs = sum(repair_results.values()) if repair_results else 0
            print(f"\n✅ Repair phase complete! Made {total_repairs} total repairs")
            
            if repair_results:
                for repair_type, count in repair_results.items():
                    if count > 0:
                        print(f"   - {repair_type.replace('_', ' ').title()}: {count}")
        
        if args.repair_only:
            print(f"\n📊 Repair summary saved to logs")
            return

    # Agent validation
    if not args.system_only and not args.repair_only:
        print("\n📋 Agent Validation Phase")
        print("-" * 30)
        
        if not agent_files:
            print("⚠️  No agent files found")
        else:
            if args.yes:
                selected_agents, auto_yes, system_only, repair_action = agent_files, True, False, None
            else:
                selected_agents, auto_yes, system_only, repair_action = get_user_selection(agent_files)
                
            # Handle interactive repair actions
            if repair_action:
                print(f"\n🔧 Running {repair_action.replace('_', ' ')}...")
                if repair_action == 'repair_all':
                    repair_results = repairer.repair_all(selected_agents)
                elif repair_action == 'fix_groups':
                    repair_results = {'groups_fixes': repairer.fix_groups_format(selected_agents)}
                elif repair_action == 'fix_references':
                    repair_results = {'reference_fixes': repairer.fix_broken_references(selected_agents)}
                elif repair_action == 'fix_interactions':
                    repair_results = {'interaction_fixes': repairer.fix_empty_interactions(selected_agents)}
                
                total_repairs = sum(repair_results.values()) if repair_results else 0
                print(f"✅ Completed! Made {total_repairs} repairs")
                return
                
            if not system_only:
                for agent_path in selected_agents:
                    print(f"\n🔍 Testing {agent_path.name}")
                    
                    # Auto-repair if enabled
                    if args.auto_repair:
                        print("   🔧 Auto-repairing...")
                        groups_fixes = repairer.fix_groups_format([agent_path])
                        ref_fixes = repairer.fix_broken_references([agent_path])
                        interaction_fixes = repairer.fix_empty_interactions([agent_path])
                        total_fixes = groups_fixes + ref_fixes + interaction_fixes
                        if total_fixes > 0:
                            print(f"   ✓ Applied {total_fixes} auto-repairs")
                    
                    # Comprehensive validation
                    passed, errors, warnings = validator.validate_agent_comprehensive(agent_path)
                    
                    # Strict mode: fail if any deep field errors
                    if strict_mode:
                        deep_errors = [e for e in errors if any(x in e for x in ["Missing inputSpec.example", "Missing inputSpec.schema", "Missing inputSpec.validationRules", "Missing outputSpec.example", "Missing outputSpec.schema", "Missing outputSpec.validationRules", "Missing or empty field: 'errorHandling'", "Missing or empty field: 'healthCheck'", "'groups' must contain 'command'", "Missing customInstructions sections"])]
                        if deep_errors:
                            passed = False
                            errors.extend([f"[STRICT] {err}" for err in deep_errors])
                    
                    agent_results[agent_path.name] = (passed, errors, warnings)
                    
                    # Print immediate results
                    status = "✅ PASS" if passed else "❌ FAIL"
                    print(f"   {status}")
                    if errors:
                        for error in errors[:3]:  # Show first 3 errors
                            print(f"   ❌ {error}")
                        if len(errors) > 3:
                            print(f"   ... and {len(errors) - 3} more errors")
                    if warnings:
                        for warning in warnings[:2]:  # Show first 2 warnings
                            print(f"   ⚠️  {warning}")

    # System initialization
    if not args.agents_only:
        print("\n🔧 System Initialization Phase")
        print("-" * 35)
        
        success, system_results = initializer.initialize_system()
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"System Status: {status}")
        print(f"Final State: {system_results.get('system_status', 'unknown').upper()}")

    # Synchronization
    if agent_results and any(passed for passed, _, _ in agent_results.values()):
        print("\n🔄 Synchronizing .roomodes")
        print("-" * 30)
        if strict_mode:
            sync_modes_to_roomodes(agent_results)
        else:
            sync_modes_to_roomodes(agent_results)
        print("✅ Synchronization complete")

    # Cursor configuration generation
    if (args.cursor or (not args.no_cursor and agent_results)) and not args.repair_only:
        print("\n🎯 Generating Cursor Configuration")
        print("-" * 40)
        
        cursor_success = sync_cursor_config(backup=args.cursor_backup)
        
        if cursor_success:
            print("✅ Cursor configuration generated successfully")
        else:
            print("❌ Failed to generate cursor configuration")

    # Template update generation
    if args.update_template and not args.repair_only:
        print("\n📝 Updating Template Documentation")
        print("-" * 40)
        
        template_success = update_template_agent_list()
        
        if template_success:
            print("✅ Template documentation updated successfully")
        else:
            print("❌ Failed to update template documentation")

    # Generate report
    report = generate_comprehensive_report(agent_results, system_results, repair_results)
    
    with open(AGENT_HEALTH_REPORT, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📊 Report saved to: {AGENT_HEALTH_REPORT.relative_to(BASE_DIR)}")
    
    if args.report:
        print("\n" + "=" * 50)
        print(report)

    # Exit with appropriate code
    agent_success = not agent_results or all(passed for passed, _, _ in agent_results.values())
    system_success = system_results is None or system_results.get('status') == 'success'
    
    if agent_success and system_success:
        print("\n🎉 All validations passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some validations failed. Check the report for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 