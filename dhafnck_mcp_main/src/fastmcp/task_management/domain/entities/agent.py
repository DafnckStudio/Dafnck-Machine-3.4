"""Agent Domain Entity"""

from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class AgentStatus(Enum):
    """Agent status enumeration"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    PAUSED = "paused"


class AgentCapability(Enum):
    """Agent capability enumeration"""
    FRONTEND_DEVELOPMENT = "frontend_development"
    BACKEND_DEVELOPMENT = "backend_development"
    DEVOPS = "devops"
    TESTING = "testing"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    CODE_REVIEW = "code_review"
    PROJECT_MANAGEMENT = "project_management"
    DATA_ANALYSIS = "data_analysis"


@dataclass
class Agent:
    """Agent entity representing an AI agent that can work on tasks"""
    
    id: str
    name: str
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Agent capabilities and preferences
    capabilities: Set[AgentCapability] = field(default_factory=set)
    specializations: List[str] = field(default_factory=list)  # More specific specializations
    preferred_languages: List[str] = field(default_factory=list)  # Programming languages
    preferred_frameworks: List[str] = field(default_factory=list)  # Frameworks/tools
    
    # Agent status and availability
    status: AgentStatus = AgentStatus.AVAILABLE
    max_concurrent_tasks: int = 1
    current_workload: int = 0
    
    # Work preferences and constraints
    work_hours: Optional[Dict[str, str]] = None  # {"start": "09:00", "end": "17:00"}
    timezone: str = "UTC"
    priority_preference: str = "high"  # Prefers high, medium, or low priority tasks
    
    # Performance metrics
    completed_tasks: int = 0
    average_task_duration: Optional[float] = None  # Hours
    success_rate: float = 100.0  # Percentage
    
    # Current assignments
    assigned_projects: Set[str] = field(default_factory=set)
    assigned_trees: Set[str] = field(default_factory=set)
    active_tasks: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Set default values after initialization"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def add_capability(self, capability: AgentCapability) -> None:
        """Add a capability to the agent"""
        self.capabilities.add(capability)
        self.updated_at = datetime.now()
    
    def remove_capability(self, capability: AgentCapability) -> None:
        """Remove a capability from the agent"""
        self.capabilities.discard(capability)
        self.updated_at = datetime.now()
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities
    
    def can_handle_task(self, task_requirements: Dict) -> bool:
        """Check if agent can handle a task based on requirements"""
        # Check capabilities
        required_capabilities = task_requirements.get("capabilities", [])
        for req_cap in required_capabilities:
            if isinstance(req_cap, str):
                try:
                    req_cap = AgentCapability(req_cap)
                except ValueError:
                    continue  # Skip unknown capabilities
            
            if req_cap not in self.capabilities:
                return False
        
        # Check programming languages
        required_languages = task_requirements.get("languages", [])
        if required_languages:
            if not any(lang in self.preferred_languages for lang in required_languages):
                return False
        
        # Check frameworks
        required_frameworks = task_requirements.get("frameworks", [])
        if required_frameworks:
            if not any(fw in self.preferred_frameworks for fw in required_frameworks):
                return False
        
        return True
    
    def is_available(self) -> bool:
        """Check if agent is available for new work"""
        return (self.status == AgentStatus.AVAILABLE and 
                self.current_workload < self.max_concurrent_tasks)
    
    def assign_to_project(self, project_id: str) -> None:
        """Assign agent to a project"""
        self.assigned_projects.add(project_id)
        self.updated_at = datetime.now()
    
    def assign_to_tree(self, tree_id: str) -> None:
        """Assign agent to a task tree"""
        self.assigned_trees.add(tree_id)
        self.updated_at = datetime.now()
    
    def start_task(self, task_id: str) -> None:
        """Start working on a task"""
        if not self.is_available():
            raise ValueError(f"Agent {self.id} is not available for new tasks")
        
        self.active_tasks.add(task_id)
        self.current_workload += 1
        
        if self.current_workload >= self.max_concurrent_tasks:
            self.status = AgentStatus.BUSY
        
        self.updated_at = datetime.now()
    
    def complete_task(self, task_id: str, success: bool = True) -> None:
        """Complete a task and update metrics"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not assigned to agent {self.id}")
        
        self.active_tasks.remove(task_id)
        self.current_workload = max(0, self.current_workload - 1)
        self.completed_tasks += 1
        
        # Update success rate
        if success:
            # Weighted average favoring recent performance
            self.success_rate = (self.success_rate * 0.9) + (100.0 * 0.1)
        else:
            self.success_rate = (self.success_rate * 0.9) + (0.0 * 0.1)
        
        # Update status if no longer busy
        if self.current_workload < self.max_concurrent_tasks and self.status == AgentStatus.BUSY:
            self.status = AgentStatus.AVAILABLE
        
        self.updated_at = datetime.now()
    
    def pause_work(self) -> None:
        """Pause agent work"""
        self.status = AgentStatus.PAUSED
        self.updated_at = datetime.now()
    
    def resume_work(self) -> None:
        """Resume agent work"""
        if self.current_workload >= self.max_concurrent_tasks:
            self.status = AgentStatus.BUSY
        else:
            self.status = AgentStatus.AVAILABLE
        self.updated_at = datetime.now()
    
    def go_offline(self) -> None:
        """Set agent offline"""
        self.status = AgentStatus.OFFLINE
        self.updated_at = datetime.now()
    
    def go_online(self) -> None:
        """Set agent online and available"""
        self.status = AgentStatus.AVAILABLE
        self.updated_at = datetime.now()
    
    def get_workload_percentage(self) -> float:
        """Get current workload as percentage of capacity"""
        if self.max_concurrent_tasks == 0:
            return 100.0
        return (self.current_workload / self.max_concurrent_tasks) * 100.0
    
    def get_agent_profile(self) -> Dict:
        """Get comprehensive agent profile"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "specializations": self.specializations,
            "preferred_languages": self.preferred_languages,
            "preferred_frameworks": self.preferred_frameworks,
            "workload": {
                "current": self.current_workload,
                "max": self.max_concurrent_tasks,
                "percentage": self.get_workload_percentage(),
                "available": self.is_available()
            },
            "performance": {
                "completed_tasks": self.completed_tasks,
                "success_rate": self.success_rate,
                "average_duration": self.average_task_duration
            },
            "assignments": {
                "projects": list(self.assigned_projects),
                "trees": list(self.assigned_trees),
                "active_tasks": list(self.active_tasks)
            },
            "preferences": {
                "work_hours": self.work_hours,
                "timezone": self.timezone,
                "priority_preference": self.priority_preference
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def calculate_task_suitability_score(self, task_requirements: Dict) -> float:
        """Calculate how suitable this agent is for a specific task (0-100)"""
        if not self.can_handle_task(task_requirements):
            return 0.0
        
        score = 50.0  # Base score for meeting requirements
        
        # Bonus for availability
        if self.is_available():
            score += 20.0
        
        # Bonus for low workload
        workload_bonus = (1.0 - (self.current_workload / self.max_concurrent_tasks)) * 10.0
        score += workload_bonus
        
        # Bonus for high success rate
        success_bonus = (self.success_rate / 100.0) * 10.0
        score += success_bonus
        
        # Bonus for matching priority preference
        task_priority = task_requirements.get("priority", "medium")
        if task_priority == self.priority_preference:
            score += 10.0
        
        return min(100.0, score)
    
    @classmethod
    def create_agent(
        cls,
        agent_id: str,
        name: str,
        description: str,
        capabilities: List[AgentCapability] = None,
        specializations: List[str] = None,
        preferred_languages: List[str] = None
    ) -> 'Agent':
        """Factory method to create a new agent"""
        agent = cls(
            id=agent_id,
            name=name,
            description=description,
            created_at=datetime.now(),
            capabilities=set(capabilities or []),
            specializations=specializations or [],
            preferred_languages=preferred_languages or []
        )
        return agent 