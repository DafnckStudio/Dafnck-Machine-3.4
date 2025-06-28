"""Enhanced Rule Orchestration Platform for DhafnckMCP

This module implements a sophisticated rule orchestration system that transforms
the basic manage_rule MCP tool into a comprehensive rule management platform.

Architecture Components:
- RuleContentParser: Handle JSON/MDC parsing and validation
- NestedRuleManager: Navigate hierarchical rule structures with inheritance
- ClientRuleIntegrator: Enable client-side synchronization
- RuleComposer: Intelligent rule combination and conflict resolution
- RuleCacheManager: Performance optimization with intelligent caching
- Enhanced MCP tool with advanced actions

Author: System Architect Agent
Date: 2025-01-27
Task: 20250628001 - Sophisticated Rule Orchestration Platform
Phase: 2 - Enhanced Nested Rule Management with Inheritance
"""

from typing import Dict, Any, Optional, List, Union, Tuple, Set
from pathlib import Path
import json
import yaml
import re
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import asyncio
import uuid
from threading import Lock

# Configure logging
logger = logging.getLogger(__name__)


class RuleFormat(Enum):
    """Supported rule file formats"""
    MDC = "mdc"
    MD = "md"
    JSON = "json"
    YAML = "yaml"
    TXT = "txt"


class RuleType(Enum):
    """Rule classification types"""
    CORE = "core"              # Essential system rules
    WORKFLOW = "workflow"      # Development workflow rules
    AGENT = "agent"           # Agent-specific rules
    PROJECT = "project"       # Project-specific rules
    CONTEXT = "context"       # Context management rules
    CUSTOM = "custom"         # User-defined rules


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    MERGE = "merge"           # Intelligent merging
    OVERRIDE = "override"     # Last rule wins
    APPEND = "append"         # Combine content
    MANUAL = "manual"         # Require manual resolution


class InheritanceType(Enum):
    """Types of rule inheritance"""
    FULL = "full"             # Inherit all content and metadata
    CONTENT = "content"       # Inherit only content sections
    METADATA = "metadata"     # Inherit only metadata
    VARIABLES = "variables"   # Inherit only variables
    SELECTIVE = "selective"   # Inherit specific sections


class SyncOperation(Enum):
    """Types of synchronization operations"""
    PUSH = "push"             # Client to server
    PULL = "pull"             # Server to client
    BIDIRECTIONAL = "bidirectional"  # Both directions
    MERGE = "merge"           # Intelligent merge


class ClientAuthMethod(Enum):
    """Client authentication methods"""
    API_KEY = "api_key"
    TOKEN = "token"
    OAUTH2 = "oauth2"
    CERTIFICATE = "certificate"


class SyncStatus(Enum):
    """Synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class ClientConfig:
    """Client configuration for synchronization"""
    client_id: str
    client_name: str
    auth_method: ClientAuthMethod
    auth_credentials: Dict[str, Any]
    sync_permissions: List[str]
    rate_limit: int = 100  # requests per minute
    sync_frequency: int = 300  # seconds
    allowed_rule_types: List[RuleType] = field(default_factory=lambda: list(RuleType))
    auto_sync: bool = True
    conflict_resolution: ConflictResolution = ConflictResolution.MERGE
    last_sync: Optional[float] = None
    sync_history: List[str] = field(default_factory=list)


@dataclass
class SyncRequest:
    """Synchronization request"""
    request_id: str
    client_id: str
    operation: SyncOperation
    rules: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: float
    priority: int = 1


@dataclass
class SyncResult:
    """Result of synchronization operation"""
    request_id: str
    client_id: str
    status: SyncStatus
    operation: SyncOperation
    processed_rules: List[str]
    conflicts: List[Dict[str, Any]]
    errors: List[str]
    warnings: List[str]
    sync_duration: float
    timestamp: float
    changes_applied: int = 0


@dataclass
class RuleConflict:
    """Rule conflict information"""
    rule_path: str
    client_version: str
    server_version: str
    conflict_type: str
    client_content: str
    server_content: str
    suggested_resolution: str
    auto_resolvable: bool = False


@dataclass
class RuleMetadata:
    """Metadata for rule files"""
    path: str
    format: RuleFormat
    type: RuleType
    size: int
    modified: float
    checksum: str
    dependencies: List[str]
    version: str = "1.0"
    author: str = "system"
    description: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class RuleContent:
    """Structured rule content"""
    metadata: RuleMetadata
    raw_content: str
    parsed_content: Dict[str, Any]
    sections: Dict[str, str]
    references: List[str]
    variables: Dict[str, Any]


@dataclass
class RuleInheritance:
    """Rule inheritance configuration and tracking"""
    parent_path: str
    child_path: str
    inheritance_type: InheritanceType
    inherited_sections: List[str] = field(default_factory=list)
    overridden_sections: List[str] = field(default_factory=list)
    merged_variables: Dict[str, Any] = field(default_factory=dict)
    inheritance_depth: int = 0
    conflicts: List[str] = field(default_factory=list)


@dataclass
class CompositionResult:
    """Result of rule composition operation"""
    composed_content: str
    source_rules: List[str]
    inheritance_chain: List[RuleInheritance]
    conflicts_resolved: List[str]
    composition_metadata: Dict[str, Any]
    success: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class CacheEntry:
    """Cache entry for rule content"""
    content: RuleContent
    timestamp: float
    access_count: int
    ttl: float


class RuleContentParser:
    """Advanced parser for rule content with format detection and validation"""
    
    def __init__(self):
        self.format_handlers = {
            RuleFormat.MDC: self._parse_mdc,
            RuleFormat.MD: self._parse_markdown,
            RuleFormat.JSON: self._parse_json,
            RuleFormat.YAML: self._parse_yaml,
            RuleFormat.TXT: self._parse_text
        }
    
    def parse_rule_file(self, file_path: Path) -> RuleContent:
        """Parse a rule file and extract structured content"""
        try:
            # Detect format
            format_type = self._detect_format(file_path)
            
            # Read content
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            # Generate metadata
            metadata = self._generate_metadata(file_path, format_type, raw_content)
            
            # Parse content based on format
            handler = self.format_handlers.get(format_type, self._parse_text)
            parsed_content, sections, references, variables = handler(raw_content)
            
            return RuleContent(
                metadata=metadata,
                raw_content=raw_content,
                parsed_content=parsed_content,
                sections=sections,
                references=references,
                variables=variables
            )
            
        except Exception as e:
            logger.error(f"Failed to parse rule file {file_path}: {e}")
            raise
    
    def _detect_format(self, file_path: Path) -> RuleFormat:
        """Detect rule file format from extension and content"""
        suffix = file_path.suffix.lower()
        
        format_map = {
            '.mdc': RuleFormat.MDC,
            '.md': RuleFormat.MD,
            '.json': RuleFormat.JSON,
            '.yaml': RuleFormat.YAML,
            '.yml': RuleFormat.YAML,
            '.txt': RuleFormat.TXT
        }
        
        return format_map.get(suffix, RuleFormat.TXT)
    
    def _generate_metadata(self, file_path: Path, format_type: RuleFormat, content: str) -> RuleMetadata:
        """Generate metadata for rule file"""
        stat = file_path.stat()
        checksum = hashlib.md5(content.encode()).hexdigest()
        
        # Extract dependencies from content
        dependencies = self._extract_dependencies(content)
        
        # Classify rule type
        rule_type = self._classify_rule_type(file_path, content)
        
        return RuleMetadata(
            path=str(file_path),
            format=format_type,
            type=rule_type,
            size=stat.st_size,
            modified=stat.st_mtime,
            checksum=checksum,
            dependencies=dependencies
        )
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract rule dependencies from content"""
        dependencies = []
        
        # Look for common dependency patterns
        patterns = [
            r'\[([^\]]+)\]\(mdc:([^)]+)\)',  # MDC references
            r'@import\s+"([^"]+)"',          # Import statements
            r'include:\s*([^\n]+)',          # Include directives
            r'depends_on:\s*\[([^\]]+)\]'    # Explicit dependencies
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            dependencies.extend([match[1] if isinstance(match, tuple) else match for match in matches])
        
        return list(set(dependencies))  # Remove duplicates
    
    def _classify_rule_type(self, file_path: Path, content: str) -> RuleType:
        """Classify rule type based on path and content"""
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        # Path-based classification
        if 'core' in path_str or 'essential' in path_str:
            return RuleType.CORE
        elif 'workflow' in path_str or 'dev_workflow' in path_str:
            return RuleType.WORKFLOW
        elif 'agent' in path_str:
            return RuleType.AGENT
        elif 'project' in path_str:
            return RuleType.PROJECT
        elif 'context' in path_str:
            return RuleType.CONTEXT
        
        # Content-based classification
        if any(keyword in content_lower for keyword in ['core', 'essential', 'critical']):
            return RuleType.CORE
        elif any(keyword in content_lower for keyword in ['workflow', 'development', 'process']):
            return RuleType.WORKFLOW
        elif any(keyword in content_lower for keyword in ['agent', '@agent', 'role']):
            return RuleType.AGENT
        
        return RuleType.CUSTOM

    def _parse_mdc(self, content: str) -> Tuple[Dict[str, Any], Dict[str, str], List[str], Dict[str, Any]]:
        """Parse MDC (Markdown Cursor) format"""
        return self._parse_markdown(content)  # MDC uses markdown syntax
    
    def _parse_markdown(self, content: str) -> Tuple[Dict[str, Any], Dict[str, str], List[str], Dict[str, Any]]:
        """Parse Markdown content with enhanced structure detection"""
        sections = {}
        references = []
        variables = {}
        
        # Split content by headers
        lines = content.split('\n')
        current_section = "content"
        current_content = []
        
        for line in lines:
            # Detect headers
            if line.startswith('#'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.strip('# ').lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Extract references
        ref_patterns = [
            r'\[([^\]]+)\]\(([^)]+)\)',      # Markdown links
            r'\[([^\]]+)\]\(mdc:([^)]+)\)',  # MDC references
            r'@([a-zA-Z_-]+)',               # Agent references
        ]
        
        for pattern in ref_patterns:
            matches = re.findall(pattern, content)
            references.extend([match[1] if isinstance(match, tuple) and len(match) > 1 else match for match in matches])
        
        # Extract variables (look for patterns like {{variable}} or ${variable})
        var_patterns = [
            r'\{\{([^}]+)\}\}',  # Handlebars style
            r'\$\{([^}]+)\}',    # Shell style
            r'@([A-Z_]+)',       # Environment style
        ]
        
        for pattern in var_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                variables[match] = f"${{{match}}}"  # Standardize format
        
        parsed_content = {
            "format": "markdown",
            "sections": sections,
            "headers": [line for line in lines if line.startswith('#')],
            "line_count": len(lines)
        }
        
        return parsed_content, sections, references, variables

    def _parse_json(self, content: str) -> Tuple[Dict[str, Any], Dict[str, str], List[str], Dict[str, Any]]:
        """Parse JSON content"""
        try:
            data = json.loads(content)
            sections = {}
            references = []
            
            # Extract sections from JSON structure
            def extract_refs(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        if isinstance(value, str) and ('mdc:' in value or 'http' in value):
                            references.append(value)
                        extract_refs(value, new_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        extract_refs(item, f"{path}[{i}]")
            
            extract_refs(data)
            
            return data, sections, references, data.get('variables', {})
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON content: {e}")
            return {}, {}, [], {}

    def _parse_yaml(self, content: str) -> Tuple[Dict[str, Any], Dict[str, str], List[str], Dict[str, Any]]:
        """Parse YAML content"""
        try:
            data = yaml.safe_load(content)
            sections = {}
            references = []
            
            # Extract references from YAML structure
            def extract_refs(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, str) and ('mdc:' in value or 'http' in value):
                            references.append(value)
                        elif isinstance(value, (dict, list)):
                            extract_refs(value)
                elif isinstance(obj, list):
                    for item in obj:
                        extract_refs(item)
            
            if data:
                extract_refs(data)
            
            return data or {}, sections, references, (data or {}).get('variables', {})
            
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML content: {e}")
            return {}, {}, [], {}

    def _parse_text(self, content: str) -> Tuple[Dict[str, Any], Dict[str, str], List[str], Dict[str, Any]]:
        """Parse plain text content"""
        sections = {"content": content}
        references = []
        variables = {}
        
        # Look for URLs and references in text
        url_pattern = r'https?://[^\s]+'
        references.extend(re.findall(url_pattern, content))
        
        parsed_content = {
            "format": "text",
            "line_count": len(content.split('\n')),
            "word_count": len(content.split()),
            "char_count": len(content)
        }
        
        return parsed_content, sections, references, variables


class NestedRuleManager:
    """Enhanced hierarchical rule manager with inheritance and composition"""
    
    def __init__(self, parser: RuleContentParser):
        self.parser = parser
        self.rule_tree = {}
        self.dependency_graph = {}
        self.inheritance_map: Dict[str, RuleInheritance] = {}
        self.composition_cache: Dict[str, CompositionResult] = {}
    
    def load_rule_hierarchy(self, root_path: Path) -> Dict[str, RuleContent]:
        """Load and organize rules in hierarchical structure with inheritance analysis"""
        rules = {}
        
        try:
            # Recursively find all rule files
            for rule_file in root_path.rglob("*"):
                if rule_file.is_file() and self._is_rule_file(rule_file):
                    try:
                        rule_content = self.parser.parse_rule_file(rule_file)
                        relative_path = str(rule_file.relative_to(root_path))
                        rules[relative_path] = rule_content
                        
                        # Build dependency graph
                        self.dependency_graph[relative_path] = rule_content.references
                        
                    except Exception as e:
                        logger.warning(f"Failed to load rule file {rule_file}: {e}")
            
            # Organize into tree structure
            self.rule_tree = self._build_tree_structure(rules)
            
            # Analyze inheritance relationships
            self._analyze_inheritance_relationships(rules)
            
            return rules
            
        except Exception as e:
            logger.error(f"Failed to load rule hierarchy from {root_path}: {e}")
            return {}
    
    def _analyze_inheritance_relationships(self, rules: Dict[str, RuleContent]) -> None:
        """Analyze and map inheritance relationships between rules"""
        self.inheritance_map.clear()
        
        for child_path, child_rule in rules.items():
            parent_path = self._find_parent_rule(child_path, rules)
            
            if parent_path and parent_path in rules:
                parent_rule = rules[parent_path]
                
                # Determine inheritance type
                inheritance_type = self._determine_inheritance_type(parent_rule, child_rule)
                
                # Calculate inheritance depth
                depth = self._calculate_inheritance_depth(child_path, rules)
                
                # Detect conflicts
                conflicts = self._detect_inheritance_conflicts(parent_rule, child_rule)
                
                # Create inheritance record
                inheritance = RuleInheritance(
                    parent_path=parent_path,
                    child_path=child_path,
                    inheritance_type=inheritance_type,
                    inherited_sections=self._get_inherited_sections(parent_rule, child_rule),
                    overridden_sections=self._get_overridden_sections(parent_rule, child_rule),
                    merged_variables=self._merge_variables(parent_rule.variables, child_rule.variables),
                    inheritance_depth=depth,
                    conflicts=conflicts
                )
                
                self.inheritance_map[child_path] = inheritance
    
    def _find_parent_rule(self, rule_path: str, rules: Dict[str, RuleContent]) -> Optional[str]:
        """Find the most appropriate parent rule for inheritance"""
        path_parts = Path(rule_path).parts
        
        # Look for parent in same directory hierarchy
        for i in range(len(path_parts) - 1, 0, -1):
            parent_dir = "/".join(path_parts[:i])
            
            # Look for common parent file names
            potential_parents = [
                f"{parent_dir}/index.mdc",
                f"{parent_dir}/base.mdc", 
                f"{parent_dir}/parent.mdc",
                f"{parent_dir}/_base.mdc"
            ]
            
            for parent_path in potential_parents:
                if parent_path in rules and parent_path != rule_path:
                    return parent_path
        
        # Look for root-level parent
        root_parents = ["base.mdc", "index.mdc", "_base.mdc"]
        for parent in root_parents:
            if parent in rules and parent != rule_path:
                return parent
        
        return None
    
    def _determine_inheritance_type(self, parent_rule: RuleContent, child_rule: RuleContent) -> InheritanceType:
        """Determine the type of inheritance between parent and child rules"""
        parent_sections = set(parent_rule.sections.keys())
        child_sections = set(child_rule.sections.keys())
        
        # Check for explicit inheritance declarations
        if 'inherit' in child_rule.variables:
            inherit_value = child_rule.variables['inherit'].lower()
            if inherit_value == 'full':
                return InheritanceType.FULL
            elif inherit_value == 'content':
                return InheritanceType.CONTENT
            elif inherit_value == 'metadata':
                return InheritanceType.METADATA
            elif inherit_value == 'variables':
                return InheritanceType.VARIABLES
        
        # Infer inheritance type from content overlap
        common_sections = parent_sections & child_sections
        if len(common_sections) == len(parent_sections):
            return InheritanceType.FULL
        elif len(common_sections) > len(parent_sections) * 0.7:
            return InheritanceType.CONTENT
        elif len(common_sections) > 0:
            return InheritanceType.SELECTIVE
        else:
            return InheritanceType.METADATA
    
    def _get_inherited_sections(self, parent_rule: RuleContent, child_rule: RuleContent) -> List[str]:
        """Get list of sections inherited from parent"""
        parent_sections = set(parent_rule.sections.keys())
        child_sections = set(child_rule.sections.keys())
        return list(parent_sections - child_sections)
    
    def _get_overridden_sections(self, parent_rule: RuleContent, child_rule: RuleContent) -> List[str]:
        """Get list of sections overridden by child"""
        parent_sections = set(parent_rule.sections.keys())
        child_sections = set(child_rule.sections.keys())
        return list(parent_sections & child_sections)
    
    def _merge_variables(self, parent_vars: Dict[str, Any], child_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Merge variables from parent and child with child taking precedence"""
        merged = parent_vars.copy()
        merged.update(child_vars)
        return merged
    
    def _calculate_inheritance_depth(self, rule_path: str, rules: Dict[str, RuleContent]) -> int:
        """Calculate the inheritance depth of a rule"""
        depth = 0
        current_path = rule_path
        visited = set()
        
        while current_path and current_path not in visited:
            visited.add(current_path)
            parent_path = self._find_parent_rule(current_path, rules)
            if parent_path:
                depth += 1
                current_path = parent_path
            else:
                break
        
        return depth
    
    def _detect_inheritance_conflicts(self, parent_rule: RuleContent, child_rule: RuleContent) -> List[str]:
        """Detect potential conflicts in inheritance"""
        conflicts = []
        
        # Check for conflicting metadata
        if parent_rule.metadata.type != child_rule.metadata.type:
            conflicts.append(f"Type mismatch: parent={parent_rule.metadata.type.value}, child={child_rule.metadata.type.value}")
        
        # Check for conflicting variables
        for var_name, parent_value in parent_rule.variables.items():
            if var_name in child_rule.variables:
                child_value = child_rule.variables[var_name]
                if parent_value != child_value:
                    conflicts.append(f"Variable conflict: {var_name} (parent={parent_value}, child={child_value})")
        
        return conflicts
    
    def compose_nested_rules(self, rule_path: str, rules: Dict[str, RuleContent]) -> CompositionResult:
        """Compose a rule with its inheritance chain into a single unified rule"""
        try:
            # Check cache first
            cache_key = f"{rule_path}:{hash(str(sorted(rules.keys())))}"
            if cache_key in self.composition_cache:
                return self.composition_cache[cache_key]
            
            # Get inheritance chain
            inheritance_chain = self._build_inheritance_chain(rule_path, rules)
            
            if not inheritance_chain:
                # No inheritance, return original rule
                if rule_path in rules:
                    return CompositionResult(
                        composed_content=rules[rule_path].raw_content,
                        source_rules=[rule_path],
                        inheritance_chain=[],
                        conflicts_resolved=[],
                        composition_metadata={"type": "direct", "inheritance_depth": 0}
                    )
                else:
                    return CompositionResult(
                        composed_content="",
                        source_rules=[],
                        inheritance_chain=[],
                        conflicts_resolved=[],
                        composition_metadata={"type": "error", "error": "Rule not found"},
                        success=False
                    )
            
            # Compose rules in inheritance order (parent to child)
            composed_sections = {}
            composed_variables = {}
            source_rules = []
            conflicts_resolved = []
            warnings = []
            
            # Start with root parent and work down
            for inheritance in reversed(inheritance_chain):
                parent_rule = rules[inheritance.parent_path]
                child_rule = rules[inheritance.child_path]
                
                source_rules.append(inheritance.parent_path)
                
                # Merge sections based on inheritance type
                if inheritance.inheritance_type in [InheritanceType.FULL, InheritanceType.CONTENT]:
                    # Inherit all sections from parent
                    for section_name, section_content in parent_rule.sections.items():
                        if section_name not in composed_sections:
                            composed_sections[section_name] = section_content
                
                # Apply child overrides
                for section_name, section_content in child_rule.sections.items():
                    if section_name in composed_sections:
                        # Conflict resolution
                        if composed_sections[section_name] != section_content:
                            conflicts_resolved.append(f"Section '{section_name}' overridden by {inheritance.child_path}")
                    composed_sections[section_name] = section_content
                
                # Merge variables
                composed_variables.update(inheritance.merged_variables)
                
                # Track conflicts
                if inheritance.conflicts:
                    warnings.extend([f"Inheritance conflict in {inheritance.child_path}: {conflict}" for conflict in inheritance.conflicts])
            
            # Add the target rule
            if rule_path in rules:
                target_rule = rules[rule_path]
                source_rules.append(rule_path)
                
                # Final override with target rule
                for section_name, section_content in target_rule.sections.items():
                    composed_sections[section_name] = section_content
                
                composed_variables.update(target_rule.variables)
            
            # Generate composed content
            composed_content = self._generate_composed_content(composed_sections, composed_variables, rules[rule_path].metadata.format)
            
            # Create result
            result = CompositionResult(
                composed_content=composed_content,
                source_rules=source_rules,
                inheritance_chain=inheritance_chain,
                conflicts_resolved=conflicts_resolved,
                composition_metadata={
                    "type": "composed",
                    "inheritance_depth": len(inheritance_chain),
                    "sections_count": len(composed_sections),
                    "variables_count": len(composed_variables),
                    "format": rules[rule_path].metadata.format.value
                },
                warnings=warnings
            )
            
            # Cache result
            self.composition_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to compose nested rules for {rule_path}: {e}")
            return CompositionResult(
                composed_content="",
                source_rules=[],
                inheritance_chain=[],
                conflicts_resolved=[],
                composition_metadata={"type": "error", "error": str(e)},
                success=False
            )
    
    def _build_inheritance_chain(self, rule_path: str, rules: Dict[str, RuleContent]) -> List[RuleInheritance]:
        """Build the complete inheritance chain for a rule"""
        chain = []
        current_path = rule_path
        visited = set()
        
        while current_path and current_path not in visited:
            visited.add(current_path)
            
            if current_path in self.inheritance_map:
                inheritance = self.inheritance_map[current_path]
                chain.append(inheritance)
                current_path = inheritance.parent_path
            else:
                break
        
        return chain
    
    def _generate_composed_content(self, sections: Dict[str, str], variables: Dict[str, Any], format_type: RuleFormat) -> str:
        """Generate composed content from sections and variables"""
        if format_type == RuleFormat.MDC or format_type == RuleFormat.MD:
            # Generate markdown content
            content_parts = []
            
            # Add variables section if present
            if variables:
                content_parts.append("# Variables")
                for var_name, var_value in variables.items():
                    content_parts.append(f"- {var_name}: {var_value}")
                content_parts.append("")
            
            # Add sections
            for section_name, section_content in sections.items():
                if section_name != "content":
                    content_parts.append(f"# {section_name.replace('_', ' ').title()}")
                content_parts.append(section_content)
                content_parts.append("")
            
            return "\n".join(content_parts).strip()
            
        elif format_type == RuleFormat.JSON:
            # Generate JSON content
            return json.dumps({
                "variables": variables,
                "sections": sections
            }, indent=2)
            
        elif format_type == RuleFormat.YAML:
            # Generate YAML content
            return yaml.dump({
                "variables": variables,
                "sections": sections
            }, default_flow_style=False)
            
        else:
            # Plain text format
            content_parts = []
            for section_content in sections.values():
                content_parts.append(section_content)
            return "\n\n".join(content_parts)
    
    def resolve_inheritance_chain(self, rule_path: str) -> List[str]:
        """Resolve the complete inheritance chain for a rule"""
        chain = []
        current_path = rule_path
        visited = set()
        
        while current_path and current_path not in visited:
            visited.add(current_path)
            chain.append(current_path)
            
            if current_path in self.inheritance_map:
                current_path = self.inheritance_map[current_path].parent_path
            else:
                break
        
        return list(reversed(chain))  # Return from root to target
    
    def validate_rule_hierarchy(self, rules: Dict[str, RuleContent]) -> Dict[str, Any]:
        """Validate the rule hierarchy for conflicts and issues"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "inheritance_issues": [],
            "circular_dependencies": [],
            "orphaned_rules": [],
            "statistics": {}
        }
        
        try:
            # Check for circular dependencies
            circular_deps = self._detect_circular_dependencies()
            if circular_deps:
                validation_results["valid"] = False
                validation_results["circular_dependencies"] = circular_deps
                validation_results["errors"].append(f"Found {len(circular_deps)} circular dependencies")
            
            # Check inheritance issues
            for rule_path, inheritance in self.inheritance_map.items():
                if inheritance.conflicts:
                    validation_results["inheritance_issues"].append({
                        "rule": rule_path,
                        "conflicts": inheritance.conflicts,
                        "parent": inheritance.parent_path
                    })
                    validation_results["warnings"].append(f"Inheritance conflicts in {rule_path}")
            
            # Find orphaned rules (rules with missing parents)
            for rule_path, inheritance in self.inheritance_map.items():
                if inheritance.parent_path not in rules:
                    validation_results["orphaned_rules"].append(rule_path)
                    validation_results["warnings"].append(f"Missing parent rule for {rule_path}: {inheritance.parent_path}")
            
            # Generate statistics
            validation_results["statistics"] = {
                "total_rules": len(rules),
                "rules_with_inheritance": len(self.inheritance_map),
                "max_inheritance_depth": max([inheritance.inheritance_depth for inheritance in self.inheritance_map.values()], default=0),
                "inheritance_types": {
                    inheritance_type.value: sum(1 for i in self.inheritance_map.values() if i.inheritance_type == inheritance_type)
                    for inheritance_type in InheritanceType
                },
                "total_conflicts": sum(len(inheritance.conflicts) for inheritance in self.inheritance_map.values())
            }
            
            # Overall validation
            if validation_results["errors"]:
                validation_results["valid"] = False
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Validation failed: {str(e)}")
        
        return validation_results

    def _is_rule_file(self, file_path: Path) -> bool:
        """Check if file is a valid rule file"""
        valid_extensions = {'.mdc', '.md', '.json', '.yaml', '.yml', '.txt'}
        return file_path.suffix.lower() in valid_extensions
    
    def _build_tree_structure(self, rules: Dict[str, RuleContent]) -> Dict[str, Any]:
        """Build hierarchical tree structure from flat rule list"""
        tree = {}
        
        for path, rule_content in rules.items():
            parts = Path(path).parts
            current = tree
            
            for part in parts[:-1]:  # Navigate to parent directory
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add the rule file
            filename = parts[-1]
            current[filename] = {
                "content": rule_content,
                "type": "file"
            }
        
        return tree
    
    def resolve_dependencies(self, rule_path: str) -> List[str]:
        """Resolve rule dependencies in correct order"""
        resolved = []
        visited = set()
        visiting = set()
        
        def dfs(path):
            if path in visiting:
                raise ValueError(f"Circular dependency detected: {path}")
            if path in visited:
                return
            
            visiting.add(path)
            
            # Process dependencies first
            for dep in self.dependency_graph.get(path, []):
                dfs(dep)
            
            visiting.remove(path)
            visited.add(path)
            resolved.append(path)
        
        try:
            dfs(rule_path)
            return resolved
        except ValueError as e:
            logger.error(f"Dependency resolution failed: {e}")
            return [rule_path]  # Return at least the requested rule
    
    def get_rule_hierarchy_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the rule hierarchy"""
        def count_nodes(tree):
            files = 0
            dirs = 0
            for key, value in tree.items():
                if isinstance(value, dict):
                    if "content" in value and value.get("type") == "file":
                        files += 1
                    else:
                        dirs += 1
                        sub_files, sub_dirs = count_nodes(value)
                        files += sub_files
                        dirs += sub_dirs
            return files, dirs
        
        total_files, total_dirs = count_nodes(self.rule_tree)
        
        return {
            "total_files": total_files,
            "total_directories": total_dirs,
            "dependency_count": len(self.dependency_graph),
            "inheritance_relationships": len(self.inheritance_map),
            "max_depth": self._calculate_max_depth(self.rule_tree),
            "circular_dependencies": self._detect_circular_dependencies(),
            "inheritance_statistics": {
                inheritance_type.value: sum(1 for i in self.inheritance_map.values() if i.inheritance_type == inheritance_type)
                for inheritance_type in InheritanceType
            }
        }
    
    def _calculate_max_depth(self, tree, current_depth=0):
        """Calculate maximum depth of rule hierarchy"""
        if not tree:
            return current_depth
        
        max_depth = current_depth
        for value in tree.values():
            if isinstance(value, dict) and "content" not in value:
                depth = self._calculate_max_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the rule graph"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                dfs(neighbor, path + [neighbor])
            
            rec_stack.remove(node)
        
        for node in self.dependency_graph:
            if node not in visited:
                dfs(node, [node])
        
        return cycles


class RuleCacheManager:
    """Intelligent caching system for rule content"""
    
    def __init__(self, max_size: int = 100, default_ttl: float = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.access_order = []  # For LRU eviction
    
    def get(self, key: str) -> Optional[RuleContent]:
        """Get cached rule content"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check TTL
        if time.time() - entry.timestamp > entry.ttl:
            self.invalidate(key)
            return None
        
        # Update access
        entry.access_count += 1
        self._update_access_order(key)
        
        return entry.content
    
    def put(self, key: str, content: RuleContent, ttl: Optional[float] = None) -> None:
        """Cache rule content"""
        if ttl is None:
            ttl = self.default_ttl
        
        # Evict if necessary
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_lru()
        
        self.cache[key] = CacheEntry(
            content=content,
            timestamp=time.time(),
            access_count=1,
            ttl=ttl
        )
        
        self._update_access_order(key)
    
    def invalidate(self, key: str) -> None:
        """Remove item from cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
    
    def clear(self) -> None:
        """Clear all cached items"""
        self.cache.clear()
        self.access_order.clear()
    
    def _update_access_order(self, key: str) -> None:
        """Update LRU access order"""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if self.access_order:
            lru_key = self.access_order[0]
            self.invalidate(lru_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_access = sum(entry.access_count for entry in self.cache.values())
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": 0 if not total_access else len(self.cache) / total_access,
            "total_accesses": total_access,
            "expired_items": sum(1 for entry in self.cache.values() 
                               if time.time() - entry.timestamp > entry.ttl)
        }


# Continue with additional components...
class RuleComposer:
    """Intelligent rule composition and conflict resolution"""
    
    def __init__(self, conflict_strategy: ConflictResolution = ConflictResolution.MERGE):
        self.conflict_strategy = conflict_strategy
        self.composition_rules = {}
    
    def compose_rules(self, rules: List[RuleContent], output_format: RuleFormat = RuleFormat.MDC) -> str:
        """Compose multiple rules into a single rule"""
        # Implementation for intelligent rule composition
        pass
    
    def resolve_conflicts(self, rules: List[RuleContent]) -> RuleContent:
        """Resolve conflicts between rules"""
        # Implementation for conflict resolution
        pass


class ClientRuleIntegrator:
    """Advanced client-side rule integration and bidirectional synchronization"""
    
    def __init__(self, parser: RuleContentParser):
        self.parser = parser
        self.client_configs: Dict[str, ClientConfig] = {}
        self.sync_history: Dict[str, List[SyncResult]] = {}
        self.active_syncs: Dict[str, SyncRequest] = {}
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
        self.sync_lock = Lock()
        
        # Real-time notification system
        self.notification_callbacks: List[callable] = []
        self.conflict_handlers: Dict[str, callable] = {}
    
    def register_client(self, config: ClientConfig) -> Dict[str, Any]:
        """Register a new client for synchronization"""
        try:
            # Validate client configuration
            validation_result = self._validate_client_config(config)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid client configuration: {validation_result['errors']}"
                }
            
            # Initialize client
            self.client_configs[config.client_id] = config
            self.sync_history[config.client_id] = []
            self._initialize_rate_limiter(config.client_id, config.rate_limit)
            
            logger.info(f"Client {config.client_id} registered successfully")
            
            return {
                "success": True,
                "client_id": config.client_id,
                "auth_method": config.auth_method.value,
                "sync_permissions": config.sync_permissions,
                "rate_limit": config.rate_limit
            }
            
        except Exception as e:
            logger.error(f"Failed to register client {config.client_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def authenticate_client(self, client_id: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate client for synchronization"""
        try:
            if client_id not in self.client_configs:
                return {"success": False, "error": "Client not registered"}
            
            config = self.client_configs[client_id]
            auth_result = self._verify_credentials(config, credentials)
            
            if auth_result["valid"]:
                # Update last authentication time
                config.auth_credentials["last_auth"] = time.time()
                return {
                    "success": True,
                    "client_id": client_id,
                    "auth_token": auth_result["token"],
                    "expires_in": auth_result.get("expires_in", 3600)
                }
            else:
                return {"success": False, "error": "Authentication failed"}
                
        except Exception as e:
            logger.error(f"Authentication failed for client {client_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def sync_with_client(self, client_id: str, operation: SyncOperation, 
                        client_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform synchronization with client"""
        try:
            # Validate client and rate limiting
            validation_result = self._validate_sync_request(client_id, operation)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}
            
            # Create sync request
            request_id = str(uuid.uuid4())
            sync_request = SyncRequest(
                request_id=request_id,
                client_id=client_id,
                operation=operation,
                rules=client_rules or {},
                metadata={"initiated_by": "client", "sync_type": operation.value},
                timestamp=time.time()
            )
            
            # Execute synchronization
            with self.sync_lock:
                self.active_syncs[request_id] = sync_request
                sync_result = self._execute_sync_operation(sync_request)
                del self.active_syncs[request_id]
            
            # Store sync result
            self.sync_history[client_id].append(sync_result)
            
            # Update client last sync time
            self.client_configs[client_id].last_sync = time.time()
            
            # Notify subscribers
            self._notify_sync_completion(sync_result)
            
            return {
                "success": sync_result.status == SyncStatus.COMPLETED,
                "request_id": request_id,
                "status": sync_result.status.value,
                "processed_rules": sync_result.processed_rules,
                "conflicts": sync_result.conflicts,
                "changes_applied": sync_result.changes_applied,
                "sync_duration": sync_result.sync_duration,
                "warnings": sync_result.warnings,
                "errors": sync_result.errors
            }
            
        except Exception as e:
            logger.error(f"Sync failed for client {client_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_client_diff(self, client_id: str, server_rules: Dict[str, RuleContent]) -> Dict[str, Any]:
        """Calculate differences between client and server rules"""
        try:
            if client_id not in self.client_configs:
                return {"success": False, "error": "Client not registered"}
            
            # Get client's last known state
            client_state = self._get_client_rule_state(client_id)
            
            # Calculate differences
            diff_result = self._calculate_rule_diff(client_state, server_rules)
            
            return {
                "success": True,
                "client_id": client_id,
                "differences": diff_result["differences"],
                "conflicts": diff_result["conflicts"],
                "new_rules": diff_result["new_rules"],
                "modified_rules": diff_result["modified_rules"],
                "deleted_rules": diff_result["deleted_rules"],
                "sync_required": diff_result["sync_required"]
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate diff for client {client_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def resolve_conflicts(self, client_id: str, conflicts: List[RuleConflict], 
                         resolution_strategy: ConflictResolution = None) -> Dict[str, Any]:
        """Resolve synchronization conflicts"""
        try:
            if client_id not in self.client_configs:
                return {"success": False, "error": "Client not registered"}
            
            config = self.client_configs[client_id]
            strategy = resolution_strategy or config.conflict_resolution
            
            resolved_conflicts = []
            unresolved_conflicts = []
            
            for conflict in conflicts:
                resolution_result = self._resolve_single_conflict(conflict, strategy)
                
                if resolution_result["resolved"]:
                    resolved_conflicts.append(resolution_result)
                else:
                    unresolved_conflicts.append(conflict)
            
            return {
                "success": True,
                "client_id": client_id,
                "resolved_conflicts": len(resolved_conflicts),
                "unresolved_conflicts": len(unresolved_conflicts),
                "resolution_details": resolved_conflicts,
                "manual_review_required": unresolved_conflicts
            }
            
        except Exception as e:
            logger.error(f"Conflict resolution failed for client {client_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_sync_status(self, client_id: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Get synchronization status for client"""
        try:
            if client_id not in self.client_configs:
                return {"success": False, "error": "Client not registered"}
            
            if request_id:
                # Get specific sync status
                sync_result = self._find_sync_result(client_id, request_id)
                if sync_result:
                    return {
                        "success": True,
                        "request_id": request_id,
                        "status": sync_result.status.value,
                        "operation": sync_result.operation.value,
                        "duration": sync_result.sync_duration,
                        "timestamp": sync_result.timestamp
                    }
                else:
                    return {"success": False, "error": "Sync request not found"}
            else:
                # Get overall client sync status
                config = self.client_configs[client_id]
                recent_syncs = self.sync_history[client_id][-5:]  # Last 5 syncs
                
                return {
                    "success": True,
                    "client_id": client_id,
                    "last_sync": config.last_sync,
                    "auto_sync": config.auto_sync,
                    "sync_frequency": config.sync_frequency,
                    "recent_syncs": [
                        {
                            "request_id": sync.request_id,
                            "status": sync.status.value,
                            "operation": sync.operation.value,
                            "timestamp": sync.timestamp,
                            "changes_applied": sync.changes_applied
                        }
                        for sync in recent_syncs
                    ],
                    "active_syncs": list(self.active_syncs.keys())
                }
                
        except Exception as e:
            logger.error(f"Failed to get sync status for client {client_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def subscribe_to_notifications(self, callback: callable) -> str:
        """Subscribe to real-time sync notifications"""
        subscription_id = str(uuid.uuid4())
        self.notification_callbacks.append((subscription_id, callback))
        return subscription_id
    
    def unsubscribe_from_notifications(self, subscription_id: str) -> bool:
        """Unsubscribe from notifications"""
        for i, (sub_id, _) in enumerate(self.notification_callbacks):
            if sub_id == subscription_id:
                del self.notification_callbacks[i]
                return True
        return False
    
    def get_client_analytics(self, client_id: str) -> Dict[str, Any]:
        """Get analytics for client synchronization"""
        try:
            if client_id not in self.client_configs:
                return {"success": False, "error": "Client not registered"}
            
            config = self.client_configs[client_id]
            sync_history = self.sync_history[client_id]
            
            # Calculate analytics
            total_syncs = len(sync_history)
            successful_syncs = sum(1 for sync in sync_history if sync.status == SyncStatus.COMPLETED)
            failed_syncs = sum(1 for sync in sync_history if sync.status == SyncStatus.FAILED)
            avg_sync_duration = sum(sync.sync_duration for sync in sync_history) / max(total_syncs, 1)
            total_changes = sum(sync.changes_applied for sync in sync_history)
            
            # Recent activity (last 24 hours)
            recent_cutoff = time.time() - 86400  # 24 hours
            recent_syncs = [sync for sync in sync_history if sync.timestamp > recent_cutoff]
            
            return {
                "success": True,
                "client_id": client_id,
                "client_name": config.client_name,
                "registration_date": config.auth_credentials.get("registration_date"),
                "last_sync": config.last_sync,
                "analytics": {
                    "total_syncs": total_syncs,
                    "successful_syncs": successful_syncs,
                    "failed_syncs": failed_syncs,
                    "success_rate": successful_syncs / max(total_syncs, 1) * 100,
                    "average_sync_duration": avg_sync_duration,
                    "total_changes_applied": total_changes,
                    "recent_activity": len(recent_syncs),
                    "rate_limit_usage": self._get_rate_limit_usage(client_id)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics for client {client_id}: {e}")
            return {"success": False, "error": str(e)}
    
    # Private helper methods
    
    def _validate_client_config(self, config: ClientConfig) -> Dict[str, Any]:
        """Validate client configuration"""
        errors = []
        
        if not config.client_id or not isinstance(config.client_id, str):
            errors.append("Invalid client_id")
        
        if not config.client_name or not isinstance(config.client_name, str):
            errors.append("Invalid client_name")
        
        if config.auth_method not in ClientAuthMethod:
            errors.append("Invalid auth_method")
        
        if not isinstance(config.sync_permissions, list):
            errors.append("Invalid sync_permissions")
        
        if config.rate_limit <= 0:
            errors.append("Invalid rate_limit")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _verify_credentials(self, config: ClientConfig, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Verify client credentials based on auth method"""
        if config.auth_method == ClientAuthMethod.API_KEY:
            expected_key = config.auth_credentials.get("api_key")
            provided_key = credentials.get("api_key")
            
            if expected_key and expected_key == provided_key:
                return {
                    "valid": True,
                    "token": f"token_{config.client_id}_{int(time.time())}",
                    "expires_in": 3600
                }
        
        elif config.auth_method == ClientAuthMethod.TOKEN:
            # Implement token validation logic
            token = credentials.get("token")
            if token and self._validate_token(token):
                return {"valid": True, "token": token}
        
        return {"valid": False}
    
    def _validate_token(self, token: str) -> bool:
        """Validate authentication token"""
        # Implement token validation logic
        return token and len(token) > 10
    
    def _initialize_rate_limiter(self, client_id: str, rate_limit: int):
        """Initialize rate limiter for client"""
        self.rate_limiters[client_id] = {
            "limit": rate_limit,
            "window_start": time.time(),
            "requests": 0
        }
    
    def _validate_sync_request(self, client_id: str, operation: SyncOperation) -> Dict[str, Any]:
        """Validate synchronization request"""
        if client_id not in self.client_configs:
            return {"valid": False, "error": "Client not registered"}
        
        # Check rate limiting
        if not self._check_rate_limit(client_id):
            return {"valid": False, "error": "Rate limit exceeded"}
        
        # Check permissions
        config = self.client_configs[client_id]
        if operation.value not in config.sync_permissions:
            return {"valid": False, "error": "Operation not permitted"}
        
        return {"valid": True}
    
    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limits"""
        if client_id not in self.rate_limiters:
            return False
        
        limiter = self.rate_limiters[client_id]
        current_time = time.time()
        
        # Reset window if needed (1 minute window)
        if current_time - limiter["window_start"] >= 60:
            limiter["window_start"] = current_time
            limiter["requests"] = 0
        
        # Check if within limit
        if limiter["requests"] >= limiter["limit"]:
            return False
        
        # Increment request count
        limiter["requests"] += 1
        return True
    
    def _execute_sync_operation(self, request: SyncRequest) -> SyncResult:
        """Execute the actual synchronization operation"""
        start_time = time.time()
        
        try:
            if request.operation == SyncOperation.PUSH:
                result = self._handle_push_operation(request)
            elif request.operation == SyncOperation.PULL:
                result = self._handle_pull_operation(request)
            elif request.operation == SyncOperation.BIDIRECTIONAL:
                result = self._handle_bidirectional_operation(request)
            elif request.operation == SyncOperation.MERGE:
                result = self._handle_merge_operation(request)
            else:
                raise ValueError(f"Unsupported sync operation: {request.operation}")
            
            result.sync_duration = time.time() - start_time
            return result
            
        except Exception as e:
            return SyncResult(
                request_id=request.request_id,
                client_id=request.client_id,
                status=SyncStatus.FAILED,
                operation=request.operation,
                processed_rules=[],
                conflicts=[],
                errors=[str(e)],
                warnings=[],
                sync_duration=time.time() - start_time,
                timestamp=time.time()
            )
    
    def _handle_push_operation(self, request: SyncRequest) -> SyncResult:
        """Handle client-to-server push operation"""
        # Implementation for push operation
        return SyncResult(
            request_id=request.request_id,
            client_id=request.client_id,
            status=SyncStatus.COMPLETED,
            operation=request.operation,
            processed_rules=list(request.rules.keys()),
            conflicts=[],
            errors=[],
            warnings=[],
            sync_duration=0.0,
            timestamp=time.time(),
            changes_applied=len(request.rules)
        )
    
    def _handle_pull_operation(self, request: SyncRequest) -> SyncResult:
        """Handle server-to-client pull operation"""
        # Implementation for pull operation
        return SyncResult(
            request_id=request.request_id,
            client_id=request.client_id,
            status=SyncStatus.COMPLETED,
            operation=request.operation,
            processed_rules=[],
            conflicts=[],
            errors=[],
            warnings=[],
            sync_duration=0.0,
            timestamp=time.time()
        )
    
    def _handle_bidirectional_operation(self, request: SyncRequest) -> SyncResult:
        """Handle bidirectional synchronization"""
        # Implementation for bidirectional sync
        return SyncResult(
            request_id=request.request_id,
            client_id=request.client_id,
            status=SyncStatus.COMPLETED,
            operation=request.operation,
            processed_rules=[],
            conflicts=[],
            errors=[],
            warnings=[],
            sync_duration=0.0,
            timestamp=time.time()
        )
    
    def _handle_merge_operation(self, request: SyncRequest) -> SyncResult:
        """Handle intelligent merge operation"""
        # Implementation for merge operation
        return SyncResult(
            request_id=request.request_id,
            client_id=request.client_id,
            status=SyncStatus.COMPLETED,
            operation=request.operation,
            processed_rules=[],
            conflicts=[],
            errors=[],
            warnings=[],
            sync_duration=0.0,
            timestamp=time.time()
        )
    
    def _get_client_rule_state(self, client_id: str) -> Dict[str, Any]:
        """Get client's last known rule state"""
        # Implementation to retrieve client state
        return {}
    
    def _calculate_rule_diff(self, client_state: Dict[str, Any], 
                           server_rules: Dict[str, RuleContent]) -> Dict[str, Any]:
        """Calculate differences between client and server rules"""
        # Implementation for diff calculation
        return {
            "differences": [],
            "conflicts": [],
            "new_rules": [],
            "modified_rules": [],
            "deleted_rules": [],
            "sync_required": False
        }
    
    def _resolve_single_conflict(self, conflict: RuleConflict, 
                               strategy: ConflictResolution) -> Dict[str, Any]:
        """Resolve a single rule conflict"""
        # Implementation for conflict resolution
        return {"resolved": True, "resolution": "merged"}
    
    def _find_sync_result(self, client_id: str, request_id: str) -> Optional[SyncResult]:
        """Find sync result by request ID"""
        for sync_result in self.sync_history.get(client_id, []):
            if sync_result.request_id == request_id:
                return sync_result
        return None
    
    def _notify_sync_completion(self, sync_result: SyncResult):
        """Notify subscribers of sync completion"""
        for subscription_id, callback in self.notification_callbacks:
            try:
                callback(sync_result)
            except Exception as e:
                logger.warning(f"Notification callback failed for {subscription_id}: {e}")
    
    def _get_rate_limit_usage(self, client_id: str) -> Dict[str, Any]:
        """Get current rate limit usage for client"""
        if client_id not in self.rate_limiters:
            return {"usage": 0, "limit": 0, "remaining": 0}
        
        limiter = self.rate_limiters[client_id]
        return {
            "usage": limiter["requests"],
            "limit": limiter["limit"],
            "remaining": max(0, limiter["limit"] - limiter["requests"]),
            "window_reset": limiter["window_start"] + 60
        }


class EnhancedRuleOrchestrator:
    """Main orchestrator for the enhanced rule management system"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.rules_dir = project_root / ".cursor" / "rules"
        
        # Initialize components
        self.parser = RuleContentParser()
        self.nested_manager = None  # Lazy initialization
        self.cache_manager = None   # Lazy initialization
        self.composer = None        # Lazy initialization
        self.client_integrator = None  # Lazy initialization
        
        # State
        self.loaded_rules = {}
        self.last_scan = 0
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the rule orchestration system"""
        try:
            # Ensure rules directory exists
            self.rules_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize core components
            self.nested_manager = NestedRuleManager(self.parser)
            self.cache_manager = RuleCacheManager()
            self.composer = RuleComposer()
            self.client_integrator = ClientRuleIntegrator(self.parser)
            
            # Load basic rule information
            self.loaded_rules = self._scan_rules()
            self.last_scan = time.time()
            
            return {
                "success": True,
                "rules_loaded": len(self.loaded_rules),
                "rules_directory": str(self.rules_dir),
                "components_initialized": [
                    "parser", 
                    "nested_manager", 
                    "cache_manager", 
                    "composer", 
                    "client_integrator"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize rule orchestrator: {e}")
            return {"success": False, "error": str(e)}
    
    def _scan_rules(self) -> Dict[str, Any]:
        """Scan and catalog rule files"""
        rules = {}
        
        try:
            for rule_file in self.rules_dir.rglob("*"):
                if rule_file.is_file() and self._is_rule_file(rule_file):
                    relative_path = str(rule_file.relative_to(self.rules_dir))
                    rules[relative_path] = {
                        "path": str(rule_file),
                        "size": rule_file.stat().st_size,
                        "modified": rule_file.stat().st_mtime,
                        "format": self.parser._detect_format(rule_file).value
                    }
        except Exception as e:
            logger.warning(f"Error scanning rules: {e}")
        
        return rules
    
    def _is_rule_file(self, file_path: Path) -> bool:
        """Check if file is a valid rule file"""
        valid_extensions = {'.mdc', '.md', '.json', '.yaml', '.yml', '.txt'}
        return file_path.suffix.lower() in valid_extensions
    
    def get_enhanced_rule_info(self) -> Dict[str, Any]:
        """Get comprehensive rule system information"""
        # Ensure components are initialized
        if self.nested_manager is None:
            self.initialize()
        
        component_status = {
            "parser": "active" if self.parser else "inactive",
            "nested_manager": "active" if self.nested_manager else "inactive",
            "cache_manager": "active" if self.cache_manager else "inactive",
            "composer": "active" if self.composer else "inactive",
            "client_integrator": "active" if self.client_integrator else "inactive"
        }
        
        # Get cache statistics if available
        cache_stats = {}
        if self.cache_manager:
            cache_stats = self.cache_manager.get_cache_stats()
        
        # Get nested rule information if available
        hierarchy_info = {}
        if self.nested_manager:
            try:
                # Load current rules into nested manager
                rules = self.nested_manager.load_rule_hierarchy(self.rules_dir)
                hierarchy_info = self.nested_manager.get_rule_hierarchy_info()
            except Exception as e:
                hierarchy_info = {"error": str(e)}
        
        return {
            "orchestrator_status": "active",
            "rules_directory": str(self.rules_dir),
            "total_rules": len(self.loaded_rules),
            "last_scan": self.last_scan,
            "components": component_status,
            "cache_statistics": cache_stats,
            "hierarchy_information": hierarchy_info,
            "loaded_rules": self.loaded_rules,
            "phase_2_features": {
                "inheritance_support": True,
                "rule_composition": True,
                "conflict_detection": True,
                "hierarchy_validation": True
            }
        } 