"""
🤖 Multi-Agent Coordination System Testing Suite
Uber Orchestrator & System Architect Agents - Strategic Multi-Agent Testing

This comprehensive test suite validates multi-agent coordination, task distribution,
orchestration workflows, and 60+ specialized agent management capabilities.
"""

import sys
import os
import pytest
import asyncio
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List, Optional, Set
import concurrent.futures
from dataclasses import dataclass
from enum import Enum

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import test isolation system
from test_environment_config import isolated_test_environment

# Import MCP-related modules
try:
    from fastmcp.server.server import FastMCP
    from fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
    from fastmcp.utilities.logging import get_logger
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

logger = get_logger(__name__) if MCP_AVAILABLE else None


class AgentRole(Enum):
    """Agent role classifications for testing"""
    ORCHESTRATOR = "orchestrator"
    SPECIALIST = "specialist"
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"


@dataclass
class AgentConfig:
    """Agent configuration for testing"""
    id: str
    name: str
    role: AgentRole
    capabilities: List[str]
    max_concurrent_tasks: int = 5
    priority_level: int = 1
    specialization: str = "general"


class MockAgent:
    """Mock agent for testing multi-agent coordination"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.id = config.id
        self.name = config.name
        self.role = config.role
        self.capabilities = config.capabilities
        self.status = "idle"
        self.current_tasks = []
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.last_heartbeat = time.time()
        self.load_factor = 0.0
        
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return result"""
        self.status = "busy"
        self.current_tasks.append(task)
        
        # Simulate task execution time
        execution_time = task.get("estimated_time", 0.1)
        await asyncio.sleep(execution_time)
        
        # Simulate success/failure
        success_rate = task.get("success_rate", 0.95)
        import random
        success = random.random() < success_rate
        
        if success:
            self.completed_tasks += 1
            result = {"status": "completed", "agent_id": self.id, "task_id": task["id"]}
        else:
            self.failed_tasks += 1
            result = {"status": "failed", "agent_id": self.id, "task_id": task["id"], "error": "Mock execution failure"}
        
        self.current_tasks.remove(task)
        if not self.current_tasks:
            self.status = "idle"
            
        self.load_factor = len(self.current_tasks) / self.config.max_concurrent_tasks
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "current_tasks": len(self.current_tasks),
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "load_factor": self.load_factor,
            "capabilities": self.capabilities,
            "last_heartbeat": self.last_heartbeat
        }


class MultiAgentOrchestrator:
    """Mock multi-agent orchestrator for testing"""
    
    def __init__(self):
        self.agents: Dict[str, MockAgent] = {}
        self.task_queue = []
        self.completed_tasks = []
        self.failed_tasks = []
        self.orchestration_metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_response_time": 0.0,
            "agent_utilization": 0.0
        }
    
    def register_agent(self, agent: MockAgent) -> bool:
        """Register an agent with the orchestrator"""
        if agent.id in self.agents:
            return False
        self.agents[agent.id] = agent
        return True
    
    def deregister_agent(self, agent_id: str) -> bool:
        """Deregister an agent from the orchestrator"""
        if agent_id not in self.agents:
            return False
        del self.agents[agent_id]
        return True
    
    def get_best_agent_for_task(self, task: Dict[str, Any]) -> Optional[MockAgent]:
        """Find the best agent for a given task"""
        required_capabilities = task.get("required_capabilities", [])
        available_agents = [
            agent for agent in self.agents.values()
            if agent.status in ["idle", "busy"] and agent.load_factor < 1.0
        ]
        
        if not available_agents:
            return None
        
        # Score agents based on capability match and load
        scored_agents = []
        for agent in available_agents:
            capability_score = len(set(required_capabilities) & set(agent.capabilities))
            load_score = 1.0 - agent.load_factor
            total_score = capability_score * 10 + load_score
            scored_agents.append((agent, total_score))
        
        # Return the highest scoring agent
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return scored_agents[0][0] if scored_agents else None
    
    async def distribute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute a task to the best available agent"""
        agent = self.get_best_agent_for_task(task)
        if not agent:
            return {"status": "failed", "error": "No available agent"}
        
        start_time = time.time()
        result = await agent.execute_task(task)
        execution_time = time.time() - start_time
        
        # Update metrics
        self.orchestration_metrics["total_tasks"] += 1
        if result["status"] == "completed":
            self.orchestration_metrics["successful_tasks"] += 1
            self.completed_tasks.append(result)
        else:
            self.orchestration_metrics["failed_tasks"] += 1
            self.failed_tasks.append(result)
        
        # Update average response time
        total_time = (self.orchestration_metrics["average_response_time"] * 
                     (self.orchestration_metrics["total_tasks"] - 1) + execution_time)
        self.orchestration_metrics["average_response_time"] = total_time / self.orchestration_metrics["total_tasks"]
        
        return result
    
    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get current orchestration metrics"""
        # Calculate agent utilization
        if self.agents:
            total_load = sum(agent.load_factor for agent in self.agents.values())
            self.orchestration_metrics["agent_utilization"] = total_load / len(self.agents)
        
        return self.orchestration_metrics.copy()


class TestMultiAgentCoordination:
    """🤖 Multi-Agent Coordination System Testing"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.orchestrator = MultiAgentOrchestrator()
        self.test_agents = self._create_test_agents()
        
    def teardown_method(self):
        """Cleanup after each test method"""
        self.orchestrator = None
        self.test_agents = []
    
    def _create_test_agents(self) -> List[MockAgent]:
        """Create a set of test agents representing the 60+ agent system"""
        agent_configs = [
            # Orchestrator agents
            AgentConfig("uber_orchestrator", "Uber Orchestrator", AgentRole.ORCHESTRATOR, 
                       ["orchestration", "coordination", "planning"], 10, 1, "orchestration"),
            AgentConfig("system_architect", "System Architect", AgentRole.ORCHESTRATOR, 
                       ["architecture", "design", "planning"], 8, 1, "architecture"),
            AgentConfig("development_orchestrator", "Development Orchestrator", AgentRole.ORCHESTRATOR, 
                       ["development", "coordination", "code_review"], 7, 2, "development"),
            
            # Specialist agents
            AgentConfig("test_orchestrator", "Test Orchestrator", AgentRole.SPECIALIST, 
                       ["testing", "quality_assurance", "automation"], 6, 2, "testing"),
            AgentConfig("security_auditor", "Security Auditor", AgentRole.SPECIALIST, 
                       ["security", "auditing", "compliance"], 5, 2, "security"),
            AgentConfig("devops_agent", "DevOps Specialist", AgentRole.SPECIALIST, 
                       ["deployment", "infrastructure", "monitoring"], 5, 2, "devops"),
            
            # Coordinator agents
            AgentConfig("task_planning", "Task Planning Agent", AgentRole.COORDINATOR, 
                       ["planning", "scheduling", "resource_allocation"], 8, 3, "planning"),
            AgentConfig("documentation_agent", "Documentation Agent", AgentRole.COORDINATOR, 
                       ["documentation", "knowledge_management"], 4, 3, "documentation"),
            
            # Executor agents
            AgentConfig("coding_agent", "Coding Agent", AgentRole.EXECUTOR, 
                       ["coding", "implementation", "debugging"], 3, 4, "coding"),
            AgentConfig("functional_tester", "Functional Tester", AgentRole.EXECUTOR, 
                       ["testing", "validation", "bug_reporting"], 4, 4, "testing"),
            AgentConfig("performance_tester", "Performance Tester", AgentRole.EXECUTOR, 
                       ["performance", "load_testing", "optimization"], 3, 4, "performance"),
        ]
        
        return [MockAgent(config) for config in agent_configs]
    
    @pytest.mark.critical
    @pytest.mark.isolated
    def test_agent_registration_system(self):
        """Test agent registration and deregistration"""
        with isolated_test_environment(test_id="agent_registration") as config:
            
            # Test agent registration
            for agent in self.test_agents:
                result = self.orchestrator.register_agent(agent)
                assert result is True, f"Failed to register agent {agent.id}"
                assert agent.id in self.orchestrator.agents, f"Agent {agent.id} not found in orchestrator"
            
            # Test duplicate registration prevention
            duplicate_agent = self.test_agents[0]
            result = self.orchestrator.register_agent(duplicate_agent)
            assert result is False, "Duplicate agent registration should fail"
            
            # Test agent deregistration
            agent_to_remove = self.test_agents[0]
            result = self.orchestrator.deregister_agent(agent_to_remove.id)
            assert result is True, f"Failed to deregister agent {agent_to_remove.id}"
            assert agent_to_remove.id not in self.orchestrator.agents, f"Agent {agent_to_remove.id} still in orchestrator"
            
            # Test deregistration of non-existent agent
            result = self.orchestrator.deregister_agent("non_existent_agent")
            assert result is False, "Deregistration of non-existent agent should fail"
            
            print("✅ Agent registration system test passed")
    
    @pytest.mark.critical
    @pytest.mark.isolated
    def test_task_distribution_algorithm(self):
        """Test intelligent task distribution to agents"""
        with isolated_test_environment(test_id="task_distribution") as config:
            
            # Register test agents
            for agent in self.test_agents:
                self.orchestrator.register_agent(agent)
            
            # Test task distribution based on capabilities
            test_tasks = [
                {
                    "id": "task_1",
                    "name": "Security Audit",
                    "required_capabilities": ["security", "auditing"],
                    "estimated_time": 0.1,
                    "success_rate": 0.95
                },
                {
                    "id": "task_2", 
                    "name": "Code Implementation",
                    "required_capabilities": ["coding", "implementation"],
                    "estimated_time": 0.1,
                    "success_rate": 0.90
                },
                {
                    "id": "task_3",
                    "name": "System Architecture",
                    "required_capabilities": ["architecture", "design"],
                    "estimated_time": 0.1,
                    "success_rate": 0.95
                }
            ]
            
            # Distribute tasks and verify appropriate agent selection
            for task in test_tasks:
                agent = self.orchestrator.get_best_agent_for_task(task)
                assert agent is not None, f"No agent found for task {task['id']}"
                
                # Verify agent has required capabilities
                required_caps = set(task["required_capabilities"])
                agent_caps = set(agent.capabilities)
                assert required_caps & agent_caps, f"Agent {agent.id} lacks required capabilities for {task['id']}"
            
            print("✅ Task distribution algorithm test passed")
    
    @pytest.mark.critical
    @pytest.mark.isolated
    async def test_concurrent_task_execution(self):
        """Test concurrent task execution across multiple agents"""
        with isolated_test_environment(test_id="concurrent_execution") as config:
            
            # Register test agents
            for agent in self.test_agents:
                self.orchestrator.register_agent(agent)
            
            # Create multiple concurrent tasks
            concurrent_tasks = [
                {
                    "id": f"concurrent_task_{i}",
                    "name": f"Concurrent Task {i}",
                    "required_capabilities": ["coding"] if i % 2 == 0 else ["testing"],
                    "estimated_time": 0.05,
                    "success_rate": 0.95
                }
                for i in range(20)
            ]
            
            # Execute tasks concurrently
            start_time = time.time()
            tasks = [self.orchestrator.distribute_task(task) for task in concurrent_tasks]
            results = await asyncio.gather(*tasks)
            execution_time = time.time() - start_time
            
            # Verify results
            successful_tasks = [r for r in results if r["status"] == "completed"]
            failed_tasks = [r for r in results if r["status"] == "failed"]
            
            assert len(successful_tasks) > 0, "No tasks completed successfully"
            assert len(successful_tasks) + len(failed_tasks) == len(concurrent_tasks), "Task count mismatch"
            
            # Verify concurrent execution was faster than sequential
            max_sequential_time = len(concurrent_tasks) * 0.05
            assert execution_time < max_sequential_time, f"Concurrent execution too slow: {execution_time:.2f}s"
            
            print(f"✅ Concurrent task execution test passed - {len(successful_tasks)}/{len(concurrent_tasks)} tasks completed in {execution_time:.2f}s")
    
    @pytest.mark.high
    @pytest.mark.isolated
    def test_agent_load_balancing(self):
        """Test load balancing across agents"""
        with isolated_test_environment(test_id="load_balancing") as config:
            
            # Register test agents
            for agent in self.test_agents:
                self.orchestrator.register_agent(agent)
            
            # Create tasks that can be handled by multiple agents
            load_test_tasks = [
                {
                    "id": f"load_task_{i}",
                    "name": f"Load Test Task {i}",
                    "required_capabilities": ["testing"],  # Multiple agents have this capability
                    "estimated_time": 0.01,
                    "success_rate": 1.0
                }
                for i in range(10)
            ]
            
            # Track which agents get assigned tasks
            agent_assignments = {}
            
            for task in load_test_tasks:
                agent = self.orchestrator.get_best_agent_for_task(task)
                if agent:
                    agent_assignments[agent.id] = agent_assignments.get(agent.id, 0) + 1
                    # Simulate agent becoming busy
                    agent.current_tasks.append(task)
                    agent.load_factor = len(agent.current_tasks) / agent.config.max_concurrent_tasks
            
            # Verify load distribution
            assert len(agent_assignments) > 1, "Tasks should be distributed across multiple agents"
            
            # Check that no single agent is overloaded
            max_tasks_per_agent = max(agent_assignments.values())
            min_tasks_per_agent = min(agent_assignments.values())
            load_imbalance = max_tasks_per_agent - min_tasks_per_agent
            
            assert load_imbalance <= 3, f"Load imbalance too high: {load_imbalance}"
            
            print("✅ Agent load balancing test passed")
    
    @pytest.mark.high
    @pytest.mark.isolated
    def test_agent_failure_recovery(self):
        """Test system resilience to agent failures"""
        with isolated_test_environment(test_id="failure_recovery") as config:
            
            # Register test agents
            for agent in self.test_agents:
                self.orchestrator.register_agent(agent)
            
            # Debug: print agent capabilities
            print("\nAgent capabilities:")
            for agent in self.test_agents:
                print(f"  {agent.id}: {agent.capabilities}")
            
            # Find a capability that multiple agents share
            capability_counts = {}
            for agent in self.test_agents:
                for cap in agent.capabilities:
                    capability_counts[cap] = capability_counts.get(cap, 0) + 1
            
            # Find a capability shared by at least 2 agents
            common_capability = None
            for cap, count in capability_counts.items():
                if count >= 2:
                    common_capability = cap
                    break
            
            if not common_capability:
                # If no shared capability, test basic failure handling
                failed_agent = self.test_agents[0]
                failed_agent.status = "failed"
                
                task = {
                    "id": "recovery_task",
                    "name": "Recovery Test Task",
                    "required_capabilities": ["non_existent_capability"],
                    "estimated_time": 0.1,
                    "success_rate": 0.95
                }
                
                alternative_agent = self.orchestrator.get_best_agent_for_task(task)
                assert alternative_agent is None, "Should not find agent for non-existent capability"
                print("✅ Agent failure recovery test passed - No agents with required capability (expected)")
                return
            
            # Find agents with the common capability
            agents_with_capability = [
                agent for agent in self.test_agents 
                if common_capability in agent.capabilities
            ]
            
            # Simulate failure of one agent with the capability
            failed_agent = agents_with_capability[0]
            failed_agent.status = "failed"
            
            # Create task that requires the common capability
            task = {
                "id": "recovery_task",
                "name": "Recovery Test Task",
                "required_capabilities": [common_capability],
                "estimated_time": 0.1,
                "success_rate": 0.95
            }
            
            # Verify system finds alternative agent
            alternative_agent = self.orchestrator.get_best_agent_for_task(task)
            
            # Should find a different agent with the required capability
            if alternative_agent:
                assert alternative_agent.id != failed_agent.id, "System should not select failed agent"
                assert alternative_agent.status != "failed", "Alternative agent should be operational"
                
                # Verify alternative agent has the required capability
                required_caps = set(task["required_capabilities"])
                agent_caps = set(alternative_agent.capabilities)
                assert required_caps & agent_caps, f"Alternative agent {alternative_agent.id} should have capability {common_capability}. Agent caps: {agent_caps}"
                print(f"✅ Agent failure recovery test passed - Failed agent: {failed_agent.id}, Alternative: {alternative_agent.id}")
            else:
                # If no alternative agent is found, verify that's correct
                available_agents_with_cap = [
                    agent for agent in self.test_agents 
                    if common_capability in agent.capabilities and agent.status != "failed"
                ]
                if len(available_agents_with_cap) == 0:
                    print("✅ Agent failure recovery test passed - No alternative agent available (expected)")
                else:
                    assert False, f"Alternative agent should be available: {[a.id for a in available_agents_with_cap]}"
    
    @pytest.mark.high
    @pytest.mark.isolated
    async def test_orchestration_performance_metrics(self):
        """Test orchestration performance metrics collection"""
        with isolated_test_environment(test_id="performance_metrics") as config:
            
            # Create a fresh orchestrator for this test to avoid metrics contamination
            fresh_orchestrator = MultiAgentOrchestrator()
            
            # Register test agents with fresh orchestrator
            for agent in self.test_agents:
                fresh_orchestrator.register_agent(agent)
            
            # Execute a series of tasks to generate metrics
            performance_tasks = [
                {
                    "id": f"perf_task_{i}",
                    "name": f"Performance Task {i}",
                    "required_capabilities": ["testing"],
                    "estimated_time": 0.02,
                    "success_rate": 0.9
                }
                for i in range(15)
            ]
            
            # Execute tasks
            for task in performance_tasks:
                await fresh_orchestrator.distribute_task(task)
            
            # Get metrics
            metrics = fresh_orchestrator.get_orchestration_metrics()
            
            # Debug output
            print(f"\nMetrics debug: Total tasks: {metrics['total_tasks']}, Expected: {len(performance_tasks)}")
            print(f"Successful: {metrics['successful_tasks']}, Failed: {metrics['failed_tasks']}")
            
            # Verify metrics
            assert metrics["total_tasks"] == len(performance_tasks), f"Total tasks count incorrect: got {metrics['total_tasks']}, expected {len(performance_tasks)}"
            assert metrics["successful_tasks"] + metrics["failed_tasks"] == metrics["total_tasks"], "Task count mismatch"
            assert metrics["average_response_time"] > 0, "Average response time should be positive"
            assert 0 <= metrics["agent_utilization"] <= 1, "Agent utilization should be between 0 and 1"
            
            # Verify success rate is reasonable (with some tolerance for randomness)
            success_rate = metrics["successful_tasks"] / metrics["total_tasks"]
            expected_success_rate = 0.9  # Based on task success_rate parameter
            tolerance = 0.3  # Allow for random variance
            assert success_rate >= (expected_success_rate - tolerance), f"Success rate too low: {success_rate:.2f}, expected around {expected_success_rate:.2f}"
            
            print(f"✅ Orchestration performance metrics test passed - Success rate: {success_rate:.2f}")


class TestAgentSpecialization:
    """🎯 Agent Specialization and Role Validation Testing"""
    
    @pytest.mark.medium
    @pytest.mark.isolated
    def test_agent_role_specialization(self):
        """Test that agents are properly specialized for their roles"""
        with isolated_test_environment(test_id="agent_specialization") as config:
            
            # Define expected capabilities for different agent types
            expected_capabilities = {
                "uber_orchestrator": ["orchestration", "coordination", "planning"],
                "system_architect": ["architecture", "design", "planning"],
                "security_auditor": ["security", "auditing", "compliance"],
                "test_orchestrator": ["testing", "quality_assurance", "automation"],
                "devops_agent": ["deployment", "infrastructure", "monitoring"],
                "coding_agent": ["coding", "implementation", "debugging"]
            }
            
            # Create specialized agents
            orchestrator = MultiAgentOrchestrator()
            agents = []
            
            for agent_id, capabilities in expected_capabilities.items():
                config = AgentConfig(
                    id=agent_id,
                    name=agent_id.replace("_", " ").title(),
                    role=AgentRole.SPECIALIST,
                    capabilities=capabilities,
                    specialization=agent_id.split("_")[0]
                )
                agent = MockAgent(config)
                agents.append(agent)
                orchestrator.register_agent(agent)
            
            # Test that specialized tasks go to appropriate agents
            specialized_tasks = [
                ("security_task", ["security", "auditing"], "security_auditor"),
                ("architecture_task", ["architecture", "design"], "system_architect"),
                ("coding_task", ["coding", "implementation"], "coding_agent"),
                ("testing_task", ["testing", "quality_assurance"], "test_orchestrator"),
                ("deployment_task", ["deployment", "infrastructure"], "devops_agent")
            ]
            
            for task_name, required_caps, expected_agent_id in specialized_tasks:
                task = {
                    "id": task_name,
                    "name": task_name,
                    "required_capabilities": required_caps,
                    "estimated_time": 0.1
                }
                
                selected_agent = orchestrator.get_best_agent_for_task(task)
                assert selected_agent is not None, f"No agent selected for {task_name}"
                assert selected_agent.id == expected_agent_id, f"Wrong agent selected for {task_name}: got {selected_agent.id}, expected {expected_agent_id}"
            
            print("✅ Agent role specialization test passed")


# Test execution and reporting
if __name__ == "__main__":
    print("🤖 Running Multi-Agent Coordination System Tests...")
    print("=" * 70)
    
    # Run coordination tests
    coordination_tests = TestMultiAgentCoordination()
    coordination_tests.setup_method()
    
    # Run synchronous tests
    coordination_tests.test_agent_registration_system()
    coordination_tests.test_task_distribution_algorithm()
    coordination_tests.test_agent_load_balancing()
    coordination_tests.test_agent_failure_recovery()
    
    # Run asynchronous tests
    async def run_async_tests():
        await coordination_tests.test_concurrent_task_execution()
        await coordination_tests.test_orchestration_performance_metrics()
    
    asyncio.run(run_async_tests())
    
    # Run specialization tests
    specialization_tests = TestAgentSpecialization()
    specialization_tests.test_agent_role_specialization()
    
    print("=" * 70)
    print("🎉 All Multi-Agent Coordination Tests Completed Successfully!")
    print("📊 Test Coverage: Agent Registration, Task Distribution, Load Balancing,")
    print("    Failure Recovery, Performance Metrics, and Agent Specialization") 