"""Agent Converter Service"""

from typing import Dict, List, Optional, Set
from datetime import datetime
import logging

from ...domain.entities.agent import Agent, AgentCapability, AgentStatus
from ...domain.enums.agent_roles import AgentRole


class AgentConverter:
    """Service to convert simplified agent data to full Agent entities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def convert_simplified_agent_to_entity(self, agent_data: Dict, project_id: str) -> Agent:
        """Convert simplified agent data from projects.json to full Agent entity"""
        agent_id = agent_data.get("id")
        name = agent_data.get("name")
        call_agent = agent_data.get("call_agent", f"@{agent_id.replace('_', '-')}-agent")
        
        # Extract capabilities and specializations from call_agent reference
        capabilities, specializations, preferred_languages = self._extract_agent_details(call_agent)
        
        # Create full Agent entity
        agent = Agent(
            id=agent_id,
            name=name,
            description=f"Agent {name} - {call_agent}",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            capabilities=capabilities,
            specializations=specializations,
            preferred_languages=preferred_languages,
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=3,  # Default reasonable value
            current_workload=0,
            priority_preference="high",
            assigned_projects={project_id}
        )
        
        return agent
    
    def _extract_agent_details(self, call_agent: str) -> tuple[Set[AgentCapability], List[str], List[str]]:
        """Extract agent capabilities and details from call_agent reference"""
        capabilities = set()
        specializations = []
        preferred_languages = []
        
        # Remove @ prefix if present
        agent_name = call_agent.lstrip('@').replace('-', '_')
        
        # Map common agent types to capabilities and specializations
        agent_mappings = {
            'system_architect_agent': {
                'capabilities': [AgentCapability.ARCHITECTURE, AgentCapability.BACKEND_DEVELOPMENT],
                'specializations': ['system_design', 'architecture_patterns', 'scalability'],
                'languages': ['python', 'java', 'typescript']
            },
            'coding_agent': {
                'capabilities': [AgentCapability.FRONTEND_DEVELOPMENT, AgentCapability.BACKEND_DEVELOPMENT],
                'specializations': ['full_stack_development', 'api_development', 'web_development'],
                'languages': ['python', 'javascript', 'typescript', 'html', 'css']
            },
            'documentation_agent': {
                'capabilities': [AgentCapability.DOCUMENTATION],
                'specializations': ['technical_writing', 'api_documentation', 'user_guides'],
                'languages': ['markdown', 'html']
            },
            'test_orchestrator_agent': {
                'capabilities': [AgentCapability.TESTING],
                'specializations': ['test_automation', 'quality_assurance', 'integration_testing'],
                'languages': ['python', 'javascript', 'typescript']
            },
            'devops_agent': {
                'capabilities': [AgentCapability.DEVOPS],
                'specializations': ['ci_cd', 'deployment', 'infrastructure', 'containerization'],
                'languages': ['bash', 'yaml', 'python']
            },
            'security_auditor_agent': {
                'capabilities': [AgentCapability.SECURITY],
                'specializations': ['security_audit', 'vulnerability_assessment', 'secure_coding'],
                'languages': ['python', 'bash']
            }
        }
        
        # Get mapping for this agent type or use defaults
        mapping = agent_mappings.get(agent_name, {
            'capabilities': [AgentCapability.BACKEND_DEVELOPMENT],
            'specializations': ['general_development'],
            'languages': ['python']
        })
        
        capabilities = set(mapping.get('capabilities', []))
        specializations = mapping.get('specializations', [])
        preferred_languages = mapping.get('languages', [])
        
        return capabilities, specializations, preferred_languages
    
    def convert_project_agents_to_entities(self, project_data: Dict) -> Dict[str, Agent]:
        """Convert all agents in a project to Agent entities"""
        project_id = project_data.get("id")
        registered_agents_data = project_data.get("registered_agents", {})
        
        agent_entities = {}
        for agent_id, agent_data in registered_agents_data.items():
            try:
                agent_entity = self.convert_simplified_agent_to_entity(agent_data, project_id)
                agent_entities[agent_id] = agent_entity
            except Exception as e:
                self.logger.error(f"Failed to convert agent {agent_id}: {str(e)}")
                # Create minimal fallback agent
                agent_entities[agent_id] = self._create_fallback_agent(agent_id, agent_data, project_id)
        
        return agent_entities
    
    def _create_fallback_agent(self, agent_id: str, agent_data: Dict, project_id: str) -> Agent:
        """Create a minimal fallback agent when conversion fails"""
        return Agent(
            id=agent_id,
            name=agent_data.get("name", agent_id),
            description=f"Fallback agent for {agent_id}",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            capabilities={AgentCapability.BACKEND_DEVELOPMENT},
            specializations=["general_development"],
            preferred_languages=["python"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=1,
            current_workload=0,
            assigned_projects={project_id}
        )
    
    def update_agent_assignments(self, agent_entities: Dict[str, Agent], agent_assignments: Dict[str, str]) -> None:
        """Update agent entities with their tree assignments"""
        for tree_id, agent_id in agent_assignments.items():
            if agent_id in agent_entities:
                agent_entities[agent_id].assign_to_tree(tree_id) 