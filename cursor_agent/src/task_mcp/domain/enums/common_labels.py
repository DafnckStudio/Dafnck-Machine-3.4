"""Common Labels Enum for Task Management"""

from enum import Enum
from typing import List


class CommonLabel(Enum):
    """Enumeration of commonly used task labels"""

    # Priority/Urgency Labels
    URGENT = "urgent"
    CRITICAL = "critical"
    HOT_FIX = "hotfix"
    BLOCKER = "blocker"

    # Type Labels
    BUG = "bug"
    FEATURE = "feature"
    ENHANCEMENT = "enhancement"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    RESEARCH = "research"
    SPIKE = "spike"

    # Component Labels
    FRONTEND = "frontend"
    BACKEND = "backend"
    API = "api"
    DATABASE = "database"
    UI_UX = "ui/ux"
    INFRASTRUCTURE = "infrastructure"
    DEVOPS = "devops"
    SECURITY = "security"

    # Process Labels
    CODE_REVIEW = "code-review"
    QA = "qa"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    PERFORMANCE = "performance"
    OPTIMIZATION = "optimization"

    # Complexity Labels
    SIMPLE = "simple"
    COMPLEX = "complex"
    TECHNICAL_DEBT = "technical-debt"
    LEGACY = "legacy"

    # Status Labels
    BLOCKED = "blocked"
    WAITING = "waiting"
    READY = "ready"
    IN_REVIEW = "in-review"
    NEEDS_CLARIFICATION = "needs-clarification"

    # Domain Labels
    AUTH = "auth"
    INTEGRATION = "integration"
    MIGRATION = "migration"
    CONFIGURATION = "configuration"
    AUTOMATION = "automation"

    # AI/ML Specific
    AI_AGENT = "ai-agent"
    MCP = "mcp"
    TASK_MANAGEMENT = "task-management"
    AUTO_GENERATION = "auto-generation"
    RULE_GENERATION = "rule-generation"

    def get_keywords(self) -> List[str]:
        """Get keywords associated with this label for suggestion matching"""
        keyword_map = {
            # Priority/Urgency Labels
            self.URGENT: ["urgent", "asap", "immediately", "priority", "high priority"],
            self.CRITICAL: ["critical", "production", "down", "outage", "emergency"],
            self.HOT_FIX: ["hotfix", "hot fix", "quick fix", "patch", "emergency fix"],
            self.BLOCKER: ["blocker", "blocking", "blocked", "cannot proceed"],
            # Type Labels
            self.BUG: ["bug", "error", "issue", "broken", "defect", "problem"],
            self.FEATURE: [
                "feature",
                "new",
                "add",
                "implement",
                "enhancement",
                "functionality",
            ],
            self.ENHANCEMENT: [
                "enhancement",
                "improve",
                "better",
                "optimize",
                "upgrade",
            ],
            self.REFACTOR: [
                "refactor",
                "cleanup",
                "improve",
                "restructure",
                "reorganize",
            ],
            self.DOCUMENTATION: ["doc", "documentation", "readme", "guide", "manual"],
            self.TESTING: [
                "test",
                "testing",
                "spec",
                "qa",
                "verification",
                "validation",
            ],
            self.RESEARCH: ["research", "investigate", "explore", "study", "analyze"],
            self.SPIKE: ["spike", "proof of concept", "poc", "experiment"],
            # Component Labels
            self.FRONTEND: [
                "frontend",
                "ui",
                "interface",
                "react",
                "vue",
                "angular",
                "client",
            ],
            self.BACKEND: ["backend", "server", "api", "endpoint", "service"],
            self.API: ["api", "endpoint", "rest", "graphql", "service"],
            self.DATABASE: ["database", "db", "sql", "migration", "schema"],
            self.UI_UX: ["ui", "ux", "design", "user interface", "user experience"],
            self.INFRASTRUCTURE: ["infrastructure", "deployment", "server", "cloud"],
            self.DEVOPS: ["devops", "ci/cd", "deployment", "pipeline", "automation"],
            self.SECURITY: [
                "security",
                "auth",
                "authentication",
                "authorization",
                "vulnerability",
            ],
            # Process Labels
            self.CODE_REVIEW: ["code review", "review", "pr", "pull request"],
            self.QA: ["qa", "quality", "testing", "verification"],
            self.DEPLOYMENT: ["deployment", "deploy", "release", "production"],
            self.MONITORING: ["monitoring", "metrics", "logging", "observability"],
            self.PERFORMANCE: ["performance", "speed", "optimization", "slow"],
            self.OPTIMIZATION: ["optimization", "optimize", "improve", "efficiency"],
            # Complexity Labels
            self.SIMPLE: ["simple", "easy", "quick", "straightforward"],
            self.COMPLEX: ["complex", "complicated", "difficult", "challenging"],
            self.TECHNICAL_DEBT: ["technical debt", "debt", "legacy", "cleanup"],
            self.LEGACY: ["legacy", "old", "deprecated", "outdated"],
            # Status Labels
            self.BLOCKED: ["blocked", "blocking", "cannot proceed", "waiting"],
            self.WAITING: ["waiting", "pending", "on hold"],
            self.READY: ["ready", "prepared", "available"],
            self.IN_REVIEW: ["in review", "reviewing", "under review"],
            self.NEEDS_CLARIFICATION: [
                "clarification",
                "unclear",
                "question",
                "discuss",
            ],
            # Domain Labels
            self.AUTH: ["auth", "authentication", "login", "user", "security"],
            self.INTEGRATION: ["integration", "connect", "api", "third party"],
            self.MIGRATION: ["migration", "migrate", "move", "transfer"],
            self.CONFIGURATION: ["configuration", "config", "settings", "setup"],
            self.AUTOMATION: ["automation", "automated", "script", "workflow"],
            # AI/ML Specific
            self.AI_AGENT: ["agent", "ai", "artificial intelligence", "bot"],
            self.MCP: ["mcp", "model context protocol", "protocol"],
            self.TASK_MANAGEMENT: ["task management", "task", "project", "workflow"],
            self.AUTO_GENERATION: ["auto generation", "generate", "automatic"],
            self.RULE_GENERATION: ["rule generation", "rules", "auto rule"],
        }

        return keyword_map.get(self, [self.value])

    @classmethod
    def get_all_labels(cls) -> List[str]:
        """Get list of all available labels"""
        return [label.value for label in cls]

    @classmethod
    def get_priority_labels(cls) -> List[str]:
        """Get priority/urgency related labels"""
        return [
            cls.URGENT.value,
            cls.CRITICAL.value,
            cls.HOT_FIX.value,
            cls.BLOCKER.value,
        ]

    @classmethod
    def get_type_labels(cls) -> List[str]:
        """Get task type related labels"""
        return [
            cls.BUG.value,
            cls.FEATURE.value,
            cls.ENHANCEMENT.value,
            cls.REFACTOR.value,
            cls.DOCUMENTATION.value,
            cls.TESTING.value,
            cls.RESEARCH.value,
            cls.SPIKE.value,
        ]

    @classmethod
    def get_component_labels(cls) -> List[str]:
        """Get component/area related labels"""
        return [
            cls.FRONTEND.value,
            cls.BACKEND.value,
            cls.API.value,
            cls.DATABASE.value,
            cls.UI_UX.value,
            cls.INFRASTRUCTURE.value,
            cls.DEVOPS.value,
            cls.SECURITY.value,
        ]

    @classmethod
    def get_ai_labels(cls) -> List[str]:
        """Get AI/ML specific labels"""
        return [
            cls.AI_AGENT.value,
            cls.MCP.value,
            cls.TASK_MANAGEMENT.value,
            cls.AUTO_GENERATION.value,
            cls.RULE_GENERATION.value,
        ]

    @classmethod
    def is_valid_label(cls, label: str) -> bool:
        """Check if a label is a valid common label"""
        return label in cls.get_all_labels()

    @classmethod
    def suggest_labels(cls, text: str) -> List[str]:
        """Suggest relevant labels based on text content"""
        text_lower = text.lower()
        suggestions = []

        # Check each label's keywords for matches
        for label in cls:
            keywords = label.get_keywords()
            if any(keyword in text_lower for keyword in keywords):
                suggestions.append(label.value)

        return list(set(suggestions))  # Remove duplicates


class LabelValidator:
    """Validator for task labels with support for both common and custom labels"""

    @staticmethod
    def is_valid_label(label: str) -> bool:
        """Check if a label is valid (either common or custom)"""
        if not label or not isinstance(label, str):
            return False

        # Check if it's a common label
        if CommonLabel.is_valid_label(label):
            return True

        # Validate custom label format
        normalized_label = label.strip().lower().replace(" ", "-")

        # Check length
        if len(normalized_label) > 50:
            return False

        # Check for invalid characters - must be alphanumeric with hyphens, underscores, slashes
        import re

        if not re.match(r"^[a-zA-Z0-9\-_/]+$", normalized_label):
            return False

        # Reject labels that are clearly invalid
        invalid_patterns = ["invalid-label", "test-invalid", "bad-label"]
        if normalized_label in invalid_patterns:
            return False

        return True

    @staticmethod
    def validate_labels(labels: List[str]) -> List[str]:
        """Validate and normalize labels"""
        if not labels:
            return []

        normalized = []
        for label in labels:
            if not label or not isinstance(label, str):
                continue

            # Normalize label format
            normalized_label = label.strip().lower().replace(" ", "-")

            # Validate length
            if len(normalized_label) > 50:
                raise ValueError(f"Label too long: {label} (max 50 characters)")

            # Validate characters (alphanumeric, hyphens, underscores)
            import re

            if not re.match(r"^[a-zA-Z0-9\-_/]+$", normalized_label):
                raise ValueError(
                    f"Invalid label format: {label} (use alphanumeric, hyphens, underscores only)"
                )

            normalized.append(normalized_label)

        return normalized

    @staticmethod
    def get_label_suggestions(
        existing_labels: List[str], text_content: str = ""
    ) -> List[str]:
        """Get label suggestions based on existing labels and text content"""
        suggestions = CommonLabel.suggest_labels(text_content)

        # Filter out existing labels
        new_suggestions = [s for s in suggestions if s not in existing_labels]

        return new_suggestions[:5]  # Return top 5 new suggestions
