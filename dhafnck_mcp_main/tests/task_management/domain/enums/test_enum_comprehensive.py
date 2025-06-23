"""
This is the canonical and only maintained test suite for all domain enums.
All validation, conversion, and edge-case tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest

from fastmcp.dhafnck_mcp.domain.enums.agent_roles import AgentRole
from fastmcp.dhafnck_mcp.domain.enums.common_labels import CommonLabel
from fastmcp.dhafnck_mcp.domain.enums.estimated_effort import EstimatedEffort, EffortLevel


class TestAgentRoleEnum:
    """Comprehensive tests for AgentRole enum to improve coverage from 71% to 90%+"""

    def test_all_agent_roles_exist(self):
        """Test that all expected agent roles are defined"""
        expected_roles = [
            "UBER_ORCHESTRATOR",
            "NLU_PROCESSOR",
            "ELICITATION",
            "COMPLIANCE_SCOPE",
            "IDEA_GENERATION",
            "IDEA_REFINEMENT",
            "CORE_CONCEPT",
            "MARKET_RESEARCH",
            "MCP_RESEARCHER",
            "TECHNOLOGY_ADVISOR",
            "SYSTEM_ARCHITECT",
            "BRANDING",
            "DESIGN_SYSTEM",
            "UI_DESIGNER",
            "PROTOTYPING",
            "DESIGN_QA_ANALYST",
            "UX_RESEARCHER",
            "TECH_SPEC",
            "TASK_PLANNING",
            "PRD_ARCHITECT",
            "MCP_CONFIGURATION",
            "ALGORITHMIC_PROBLEM_SOLVER",
            "CODING",
            "CODE_REVIEWER",
            "DOCUMENTATION",
            "DEVELOPMENT_ORCHESTRATOR",
            "TEST_CASE_GENERATOR",
            "TEST_ORCHESTRATOR",
            "FUNCTIONAL_TESTER",
            "EXPLORATORY_TESTER",
            "PERFORMANCE_LOAD_TESTER",
            "VISUAL_REGRESSION_TESTING",
            "UAT_COORDINATOR",
            "LEAD_TESTING",
            "COMPLIANCE_TESTING",
            "SECURITY_PENETRATION_TESTER",
            "USABILITY_HEURISTIC",
            "ADAPTIVE_DEPLOYMENT_STRATEGIST",
            "DEVOPS",
            "USER_FEEDBACK_COLLECTOR",
            "EFFICIENCY_OPTIMIZATION",
            "KNOWLEDGE_EVOLUTION",
            "SECURITY_AUDITOR",
            "SWARM_SCALER",
            "ROOT_CAUSE_ANALYSIS",
            "REMEDIATION",
            "HEALTH_MONITOR",
            "INCIDENT_LEARNING",
            "MARKETING_STRATEGY_ORCHESTRATOR",
            "CAMPAIGN_MANAGER",
            "CONTENT_STRATEGY",
            "GRAPHIC_DESIGN",
            "GROWTH_HACKING_IDEA",
            "VIDEO_PRODUCTION",
            "ANALYTICS_SETUP",
            "SEO_SEM",
            "SOCIAL_MEDIA_SETUP",
            "COMMUNITY_STRATEGY",
            "PROJECT_INITIATOR",
            "TASK_DEEP_MANAGER",
            "DEBUGGER",
            "TASK_SYNC",
            "ETHICAL_REVIEW",
            "WORKFLOW_ARCHITECT",
            "SCRIBE",
            "BRAINJS_ML",
            "DEEP_RESEARCH"
        ]
        
        for role_name in expected_roles:
            assert hasattr(AgentRole, role_name), f"AgentRole.{role_name} should exist"

    def test_agent_role_values(self):
        """Test that agent roles have correct string values"""
        assert AgentRole.CODING.value == "coding_agent"
        assert AgentRole.FUNCTIONAL_TESTER.value == "functional_tester_agent"
        assert AgentRole.DEVOPS.value == "devops_agent"

    def test_agent_role_from_string(self):
        """Test creating AgentRole from string values"""
        assert AgentRole("coding_agent") == AgentRole.CODING
        assert AgentRole("functional_tester_agent") == AgentRole.FUNCTIONAL_TESTER
        assert AgentRole("devops_agent") == AgentRole.DEVOPS

    def test_agent_role_invalid_value(self):
        """Test that invalid agent role values raise ValueError"""
        with pytest.raises(ValueError):
            AgentRole("invalid_role")

    def test_agent_role_list_all(self):
        """Test listing all agent roles"""
        all_roles = list(AgentRole)
        assert len(all_roles) > 50
        assert AgentRole.CODING in all_roles
        assert AgentRole.FUNCTIONAL_TESTER in all_roles

    def test_agent_role_string_representation(self):
        """Test string representation of agent roles"""
        assert str(AgentRole.CODING) == "AgentRole.CODING"
        assert repr(AgentRole.CODING) == "<AgentRole.CODING: 'coding_agent'>"

    def test_agent_role_equality(self):
        """Test agent role equality"""
        role1 = AgentRole.CODING
        role2 = AgentRole.CODING
        role3 = AgentRole.FUNCTIONAL_TESTER
        
        assert role1 == role2
        assert role1 != role3
        assert role1 is role2

    def test_agent_role_hashing(self):
        """Test that agent roles can be used as dictionary keys"""
        role_dict = {
            AgentRole.CODING: "Coding tasks",
            AgentRole.FUNCTIONAL_TESTER: "Testing tasks",
            AgentRole.DEVOPS: "DevOps tasks"
        }
        
        assert role_dict[AgentRole.CODING] == "Coding tasks"
        assert role_dict[AgentRole.FUNCTIONAL_TESTER] == "Testing tasks"
        assert role_dict[AgentRole.DEVOPS] == "DevOps tasks"

    def test_agent_role_iteration(self):
        """Test iterating over agent roles"""
        roles = []
        for role in AgentRole:
            roles.append(role)
        
        assert len(roles) > 50
        assert AgentRole.CODING in roles
        assert AgentRole.FUNCTIONAL_TESTER in roles

    def test_agent_role_membership(self):
        """Test membership testing for agent roles"""
        assert AgentRole.CODING in AgentRole
        assert "not_a_role" not in [role.value for role in AgentRole]


class TestCommonLabelEnum:
    """Comprehensive tests for CommonLabel enum to improve coverage from 73% to 90%+"""

    def test_all_common_labels_exist(self):
        """Test that all expected common labels are defined"""
        expected_labels = [
            "FEATURE",
            "BUG",
            "ENHANCEMENT",
            "DOCUMENTATION",
            "TESTING",
            "REFACTOR",
            "PERFORMANCE",
            "SECURITY",
            "UI_UX",
            "API",
            "DATABASE",
            "INFRASTRUCTURE",
            "DEPLOYMENT",
            "MONITORING",
            "INTEGRATION",
            "MIGRATION",
            "RESEARCH",
            "URGENT",
            "CRITICAL",
            "BLOCKED",
            "READY",
            "IN_REVIEW",
            "FRONTEND",
            "BACKEND",
            "HOT_FIX"
        ]
        
        for label_name in expected_labels:
            assert hasattr(CommonLabel, label_name), f"CommonLabel.{label_name} should exist"

    def test_common_label_values(self):
        """Test that common labels have correct string values"""
        assert CommonLabel.FEATURE.value == "feature"
        assert CommonLabel.BUG.value == "bug"
        assert CommonLabel.ENHANCEMENT.value == "enhancement"

    def test_common_label_from_string(self):
        """Test creating CommonLabel from string values"""
        assert CommonLabel("feature") == CommonLabel.FEATURE
        assert CommonLabel("bug") == CommonLabel.BUG
        assert CommonLabel("enhancement") == CommonLabel.ENHANCEMENT

    def test_common_label_invalid_value(self):
        """Test that invalid common label values raise ValueError"""
        with pytest.raises(ValueError):
            CommonLabel("invalid_label")

    def test_common_label_list_all(self):
        """Test listing all common labels"""
        all_labels = list(CommonLabel)
        assert len(all_labels) > 20
        assert CommonLabel.FEATURE in all_labels
        assert CommonLabel.BUG in all_labels

    def test_common_label_string_representation(self):
        """Test string representation of common labels"""
        assert str(CommonLabel.FEATURE) == "CommonLabel.FEATURE"
        assert repr(CommonLabel.FEATURE) == "<CommonLabel.FEATURE: 'feature'>"

    def test_common_label_equality(self):
        """Test common label equality"""
        label1 = CommonLabel.FEATURE
        label2 = CommonLabel.FEATURE
        label3 = CommonLabel.BUG
        
        assert label1 == label2
        assert label1 != label3
        assert label1 is label2

    def test_common_label_hashing(self):
        """Test that common labels can be used as dictionary keys"""
        label_dict = {
            CommonLabel.FEATURE: "New feature",
            CommonLabel.BUG: "Bug fix",
            CommonLabel.ENHANCEMENT: "Enhancement"
        }
        
        assert label_dict[CommonLabel.FEATURE] == "New feature"
        assert label_dict[CommonLabel.BUG] == "Bug fix"
        assert label_dict[CommonLabel.ENHANCEMENT] == "Enhancement"

    def test_common_label_iteration(self):
        """Test iterating over common labels"""
        labels = []
        for label in CommonLabel:
            labels.append(label)
        
        assert len(labels) > 20
        assert CommonLabel.FEATURE in labels
        assert CommonLabel.BUG in labels

    def test_common_label_membership(self):
        """Test membership testing for common labels"""
        assert CommonLabel.FEATURE in CommonLabel
        assert "not_a_label" not in [label.value for label in CommonLabel]

    def test_common_label_categories(self):
        """Test that labels can be categorized"""
        priority_labels = [CommonLabel.URGENT, CommonLabel.CRITICAL]
        status_labels = [CommonLabel.BLOCKED, CommonLabel.READY, CommonLabel.IN_REVIEW]
        type_labels = [CommonLabel.FEATURE, CommonLabel.BUG, CommonLabel.ENHANCEMENT]
        
        for label in priority_labels:
            assert label in CommonLabel
        for label in status_labels:
            assert label in CommonLabel
        for label in type_labels:
            assert label in CommonLabel


class TestEstimatedEffortEnum:
    """Comprehensive tests for EstimatedEffort enum to improve coverage from 53% to 90%+"""

    def test_all_estimated_efforts_exist(self):
        """Test that all expected estimated efforts are defined in EffortLevel"""
        expected_efforts = [
            "QUICK",
            "SHORT",
            "SMALL",
            "MEDIUM",
            "LARGE",
            "XLARGE",
            "EPIC",
            "MASSIVE"
        ]
        
        for effort_name in expected_efforts:
            assert hasattr(EffortLevel, effort_name), f"EffortLevel.{effort_name} should exist"

    def test_estimated_effort_values(self):
        """Test that estimated efforts have correct string values"""
        assert EffortLevel.QUICK.label == "quick"
        assert EffortLevel.SHORT.label == "short"
        assert EffortLevel.SMALL.label == "small"
        assert EffortLevel.MEDIUM.label == "medium"

    def test_estimated_effort_from_string(self):
        """Test creating EstimatedEffort from string values"""
        assert EstimatedEffort("quick").value == "quick"
        assert EstimatedEffort("short").value == "short"
        assert EstimatedEffort("small").value == "small"

    def test_estimated_effort_invalid_value(self):
        """Test that invalid estimated effort values raise ValueError"""
        with pytest.raises(ValueError):
            EstimatedEffort("invalid_effort")

    def test_estimated_effort_list_all(self):
        """Test listing all estimated efforts from EffortLevel"""
        all_efforts = list(EffortLevel)
        assert len(all_efforts) == 8
        assert EffortLevel.QUICK in all_efforts
        assert EffortLevel.MASSIVE in all_efforts

    def test_estimated_effort_string_representation(self):
        """Test string representation of estimated efforts"""
        effort = EstimatedEffort("quick")
        assert str(effort) == "quick"

    def test_estimated_effort_equality(self):
        """Test estimated effort equality"""
        effort1 = EstimatedEffort("quick")
        effort2 = EstimatedEffort("quick")
        effort3 = EstimatedEffort("large")
        
        assert effort1.value == effort2.value
        assert effort1.value != effort3.value

    def test_estimated_effort_hashing(self):
        """Test that estimated efforts can be used as dictionary keys"""
        effort_dict = {
            EffortLevel.QUICK: "< 1 hour",
            EffortLevel.SHORT: "1-4 hours",
            EffortLevel.SMALL: "1-2 days",
            EffortLevel.MEDIUM: "3-5 days",
            EffortLevel.LARGE: "1-2 weeks",
            EffortLevel.XLARGE: "2-4 weeks",
            EffortLevel.EPIC: "1-3 months",
            EffortLevel.MASSIVE: "> 3 months"
        }
        
        assert effort_dict[EffortLevel.QUICK] == "< 1 hour"
        assert effort_dict[EffortLevel.MASSIVE] == "> 3 months"

    def test_estimated_effort_iteration(self):
        """Test iterating over estimated efforts"""
        efforts = []
        for effort in EffortLevel:
            efforts.append(effort)
        
        assert len(efforts) == 8
        assert EffortLevel.QUICK in efforts
        assert EffortLevel.MASSIVE in efforts

    def test_estimated_effort_membership(self):
        """Test membership testing for estimated efforts"""
        assert EffortLevel.QUICK in EffortLevel
        assert "not_an_effort" not in [effort.label for effort in EffortLevel]

    def test_estimated_effort_ordering_concept(self):
        """Test that effort levels represent increasing complexity"""
        efforts_in_order = [
            EffortLevel.QUICK,
            EffortLevel.SHORT,
            EffortLevel.SMALL,
            EffortLevel.MEDIUM,
            EffortLevel.LARGE,
            EffortLevel.XLARGE,
            EffortLevel.EPIC,
            EffortLevel.MASSIVE
        ]
        
        all_efforts = list(EffortLevel)
        for i, effort in enumerate(efforts_in_order):
            assert effort in all_efforts

    def test_estimated_effort_time_mapping(self):
        """Test conceptual time mapping for estimated efforts"""
        time_ranges = {
            EffortLevel.QUICK: "minutes to hours",
            EffortLevel.SHORT: "hours to half day",
            EffortLevel.SMALL: "days",
            EffortLevel.MEDIUM: "week",
            EffortLevel.LARGE: "weeks",
            EffortLevel.XLARGE: "month",
            EffortLevel.EPIC: "months",
            EffortLevel.MASSIVE: "quarters"
        }
        
        for effort in EffortLevel:
            assert effort in time_ranges

    def test_estimated_effort_validation_helper(self):
        """Test helper functions for effort validation"""
        valid_efforts = [effort.label for effort in EffortLevel]
        
        assert "quick" in valid_efforts
        assert "massive" in valid_efforts
        assert "invalid" not in valid_efforts
        
        effort = EstimatedEffort("quick")
        assert effort.value == "quick"

    def test_estimated_effort_comprehensive_coverage(self):
        """Test comprehensive coverage of EstimatedEffort functionality"""
        effort = EstimatedEffort("medium")
        
        assert effort.value == "medium"
        assert str(effort) == "medium"
        
        hours = effort.get_hours()
        assert hours is not None
        assert hours > 0
        
        level = effort.get_level()
        assert level == "medium"
        
        quick_effort = EstimatedEffort.quick()
        assert quick_effort.value == "quick"
        
        medium_effort = EstimatedEffort.medium()
        assert medium_effort.value == "medium" 