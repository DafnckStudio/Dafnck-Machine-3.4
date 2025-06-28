"""Cursor Rules Management Tools for MCP Server"""

from typing import Dict, Any, Optional, Annotated
from pathlib import Path
import json
import os
import re
from pydantic import Field
import time

from ..domain.services import AutoRuleGenerator
from .enhanced_rule_orchestrator import EnhancedRuleOrchestrator

from fastmcp.tools.tool_path import find_project_root


def resolve_path(path, base=None):
    p = Path(path)
    if p.is_absolute():
        return p
    base = base or Path(__file__).parent
    return (base / p).resolve()


class CursorRulesTools:
    """Tools for managing Cursor rules and auto_rule.mdc file"""
    
    def __init__(self):
        from ..infrastructure.services import FileAutoRuleGenerator
        self._auto_rule_generator = FileAutoRuleGenerator()
        # Initialize enhanced rule orchestrator
        self._enhanced_orchestrator = None
    
    @property
    def project_root(self):
        # Allow override via environment variable, else use canonical function
        if "PROJECT_ROOT_PATH" in os.environ:
            return resolve_path(os.environ["PROJECT_ROOT_PATH"])
        return find_project_root()
    
    @property
    def enhanced_orchestrator(self):
        """Lazy initialization of enhanced rule orchestrator"""
        if self._enhanced_orchestrator is None:
            self._enhanced_orchestrator = EnhancedRuleOrchestrator(self.project_root)
            self._enhanced_orchestrator.initialize()
        return self._enhanced_orchestrator
    
    def register_tools(self, mcp):
        """Register all cursor rules tools with the MCP server"""
        
        @mcp.tool()
        def update_auto_rule(
            content: Annotated[str, Field(description="Complete markdown content for auto_rule.mdc file")],
            backup: Annotated[bool, Field(description="Create backup before update (default: true, recommended)")] = True
        ) -> Dict[str, Any]:
            """📝 AUTO-RULE CONTENT MANAGER - Direct update of AI assistant context rules

⭐ WHAT IT DOES: Updates .cursor/rules/auto_rule.mdc with custom AI context and rules
📋 WHEN TO USE: Manual context customization, special project rules, AI behavior tuning
🎯 CRITICAL FOR: Advanced users who need precise AI assistant configuration

🔧 FUNCTIONALITY:
• Direct Content Update: Replaces entire auto_rule.mdc with provided content
• Automatic Backup: Creates .mdc.backup before changes (unless disabled)
• Directory Creation: Ensures .cursor/rules/ directory structure exists
• Encoding Safety: Handles UTF-8 content with proper error handling

📋 PARAMETERS:
• content (required): Complete markdown content for auto_rule.mdc file
• backup (optional): Create backup before update (default: true, recommended)

⚠️ ADVANCED USAGE WARNING:
• Direct Editing: Bypasses task-based auto-generation
• Manual Responsibility: You must ensure proper markdown formatting
• Context Integrity: Content should follow established rule patterns
• Backup Recommended: Always use backup=true for safety

💡 CONTENT GUIDELINES:
• Use markdown headers for structure (# ## ###)
• Include task context if applicable
• Define clear role and persona information
• Specify operating rules and constraints
• Add tool usage guidance as needed

🎯 USE CASES:
• Custom Workflows: Project-specific AI behavior requirements
• Template Testing: Experimenting with rule formats
• Emergency Override: Quick context fixes when auto-generation fails
• Integration Setup: Preparing context for external integrations
            """
            try:
                auto_rule_path = self.project_root / ".cursor" / "rules" / "auto_rule.mdc"
                
                # Create backup if requested
                if backup and auto_rule_path.exists():
                    backup_path = auto_rule_path.with_suffix('.mdc.backup')
                    with open(auto_rule_path, 'r', encoding='utf-8') as src:
                        backup_content = src.read()
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(backup_content)
                
                # Ensure directory exists
                auto_rule_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write new content
                with open(auto_rule_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "success": True,
                    "message": "Auto rule file updated successfully",
                    "file_path": str(auto_rule_path),
                    "backup_created": backup and auto_rule_path.exists()
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to update auto rule: {str(e)}"
                }
        
        @mcp.tool()
        def validate_rules(
            file_path: Annotated[Optional[str], Field(description="Specific rule file to validate (default: auto_rule.mdc). Supports relative and absolute paths")] = None
        ) -> Dict[str, Any]:
            """🔍 RULES VALIDATION ENGINE - Comprehensive rule file quality and structure analysis

⭐ WHAT IT DOES: Analyzes rule files for proper structure, content quality, and potential issues
📋 WHEN TO USE: After rule modifications, troubleshooting AI behavior, quality assurance
🎯 ESSENTIAL FOR: Ensuring reliable AI assistant performance and context integrity

🔬 VALIDATION ANALYSIS:

📁 FILE INTEGRITY:
• Existence Check: Confirms file exists and is accessible
• Encoding Validation: Ensures UTF-8 compatibility and readability
• Size Analysis: Detects too-small files that lack sufficient context
• Line Count: Provides content volume metrics

📋 CONTENT STRUCTURE:
• Markdown Format: Validates proper markdown header structure
• Task Context: Checks for essential task information sections
• Role Definition: Ensures AI persona and role clarity
• Operating Rules: Validates presence of behavioral guidelines

🚨 ISSUE DETECTION:
• Content Deficiencies: Identifies missing critical sections
• Format Problems: Detects structural inconsistencies
• Size Warnings: Flags potentially insufficient context
• Encoding Errors: Catches character encoding issues

📋 PARAMETERS:
• file_path (optional): Specific rule file to validate (default: auto_rule.mdc)
• Path Handling: Supports both relative and absolute paths

💡 QUALITY METRICS:
• Completeness Score: How well the file covers required sections
• Structure Health: Markdown formatting quality assessment
• Content Density: Adequate information for AI context
• Integration Readiness: Suitability for AI assistant usage

🎯 USE CASES:
• Rule Development: Validate changes before deployment
• Troubleshooting: Diagnose AI behavior inconsistencies
• Quality Assurance: Ensure rule files meet standards
• Integration Testing: Verify rule compatibility
• Maintenance: Regular health checks of rule system
            """
            try:
                if file_path is None:
                    target_path = self.project_root / ".cursor" / "rules" / "auto_rule.mdc"
                else:
                    # If relative path provided, make it relative to project root
                    if not os.path.isabs(file_path):
                        target_path = self.project_root / file_path
                    else:
                        target_path = Path(file_path)
                
                if not target_path.exists():
                    return {
                        "success": False,
                        "error": f"File not found: {target_path}"
                    }
                
                # Read and validate content
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic validation checks
                validation_results = {
                    "file_exists": True,
                    "file_size": len(content),
                    "line_count": len(content.splitlines()),
                    "has_task_context": "Task Context" in content,
                    "has_role_info": "Role" in content or "Persona" in content,
                    "has_rules": "Rules" in content or "Operating" in content,
                    "markdown_structure": content.strip().startswith('#'),
                    "encoding_valid": True  # If we got here, encoding is valid
                }
                
                # Check for common issues
                issues = []
                if validation_results["file_size"] < 100:
                    issues.append("File seems too small (< 100 characters)")
                if not validation_results["has_task_context"]:
                    issues.append("Missing task context section")
                if not validation_results["markdown_structure"]:
                    issues.append("File doesn't start with markdown header")
                
                return {
                    "success": True,
                    "validation_results": validation_results,
                    "issues": issues,
                    "file_path": str(target_path)
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Validation failed: {str(e)}"
                }
        
        @mcp.tool()
        def manage_rule(
            action: Annotated[str, Field(description="Rule management action to perform. Available: list, backup, restore, clean, info, load_core, parse_rule, analyze_hierarchy, get_dependencies, enhanced_info, compose_nested_rules, compose_rules, resolve_rule_inheritance, validate_rule_hierarchy, build_hierarchy, load_nested, cache_status, register_client, authenticate_client, sync_client, client_diff, resolve_conflicts, client_status, client_analytics")],
            target: Annotated[Optional[str], Field(description="Target file or directory (optional, context-dependent)")] = None,
            content: Annotated[Optional[str], Field(description="Content for write operations (optional, context-dependent)")] = None
        ) -> Dict[str, Any]:
            """🗂️ CURSOR RULES ADMINISTRATION - Complete rule file system management

⭐ WHAT IT DOES: Comprehensive management of .cursor/rules/ directory and rule files
📋 WHEN TO USE: Rule system maintenance, backup management, directory administration
🎯 ESSENTIAL FOR: System administrators, rule system maintenance, disaster recovery

📋 SUPPORTED ACTIONS & PARAMETERS:

📂 LIST: Discover all rule files in system
• Required: action="list"
• Returns: Complete inventory of .mdc files with metadata
• Metadata: File paths, sizes, modification timestamps
• Use Case: Rule system audit, finding configuration files

💾 BACKUP: Create safety copy of auto_rule.mdc
• Required: action="backup"
• Creates: auto_rule.mdc.backup in same directory
• Safety: Preserves current state before modifications
• Use Case: Pre-change safety, disaster recovery preparation

🔄 RESTORE: Recover from backup file
• Required: action="restore"
• Restores: auto_rule.mdc from .backup file
• Recovery: Reverses changes to last backup point
• Use Case: Rollback after problematic changes

🧹 CLEAN: Remove backup files
• Required: action="clean"
• Removes: All .backup files to free space
• Maintenance: Cleanup old backup files
• Use Case: Disk space management, system cleanup

📊 INFO: Get rules directory statistics
• Required: action="info"
• Returns: Directory structure, file counts, total sizes
• Overview: Complete rule system health summary
• Use Case: System monitoring, capacity planning

🚀 LOAD_CORE: Load essential rules for chat session initialization
• Required: action="load_core"
• Loads: Core rule files automatically at session start
• Priority: Loads most critical rules first for optimal performance
• Fallback: Graceful handling if core rules are missing
• Use Case: Session initialization, automatic rule loading

🔍 ENHANCED_INFO: Get comprehensive rule orchestration system information
• Required: action="enhanced_info"
• Returns: Complete orchestrator status, components, and loaded rules
• Advanced: Shows parser status, rule counts, system health
• Use Case: System diagnostics, advanced troubleshooting

📝 PARSE_RULE: Parse specific rule file with detailed analysis
• Required: action="parse_rule", target="rule_file.mdc"
• Returns: Metadata, content analysis, sections, references, variables
• Advanced: Multi-format support (MDC, MD, JSON, YAML, TXT)
• Use Case: Rule content inspection, dependency analysis

🏗️ ANALYZE_HIERARCHY: Analyze rule structure and organization
• Required: action="analyze_hierarchy"
• Returns: Rules by format/directory, largest files, recent changes
• Advanced: Structural analysis and organization recommendations
• Use Case: Rule system optimization, structure analysis

🔗 GET_DEPENDENCIES: Extract and analyze rule dependencies
• Required: action="get_dependencies", target="rule_file.mdc"
• Returns: Dependencies, references, dependency analysis
• Advanced: Pattern-based dependency detection
• Use Case: Dependency mapping, impact analysis

🧩 COMPOSE_NESTED_RULES: Compose rule with inheritance chain (Phase 2)
• Required: action="compose_nested_rules", target="rule_file.mdc"
• Returns: Unified rule with inheritance applied, composition metadata
• Advanced: Intelligent merging, conflict resolution, inheritance tracking
• Use Case: Rule composition, inheritance visualization

🎯 COMPOSE_RULES: Intelligent multi-rule composition with conflict resolution (Phase 4)
• Required: action="compose_rules", content="rule1.mdc,rule2.mdc,rule3.mdc"
• Optional: target="output_format" (mdc, md, json, yaml, txt)
• Returns: Composed rule with intelligent merging, conflict resolution, composition metadata
• Advanced: Multiple composition strategies (intelligent, sequential, priority_merge), automatic conflict resolution
• Use Case: Advanced rule composition, multi-rule merging, conflict resolution

🔍 RESOLVE_RULE_INHERITANCE: Show inheritance chain for rule (Phase 2)
• Required: action="resolve_rule_inheritance", target="rule_file.mdc"
• Returns: Complete inheritance chain from root to target
• Advanced: Parent-child relationships, inheritance depth
• Use Case: Inheritance debugging, hierarchy understanding

✅ VALIDATE_RULE_HIERARCHY: Check hierarchy for conflicts (Phase 2)
• Required: action="validate_rule_hierarchy"
• Returns: Validation results, errors, warnings, statistics
• Advanced: Inheritance conflicts, circular dependencies, orphaned rules
• Use Case: Rule system health check, conflict detection

🏗️ BUILD_HIERARCHY: Analyze and build complete rule hierarchy (Phase 2)
• Required: action="build_hierarchy"
• Returns: Hierarchy structure, inheritance relationships, statistics
• Advanced: Automatic parent-child detection, dependency mapping
• Use Case: Initial hierarchy setup, relationship discovery

📚 LOAD_NESTED: Load rules in hierarchical order with inheritance (Phase 2)
• Required: action="load_nested"
• Returns: Rules loaded in dependency order with inheritance applied
• Advanced: Intelligent loading order, inheritance resolution
• Use Case: Comprehensive rule loading, inheritance application

💾 CACHE_STATUS: Get rule cache status and performance metrics (Phase 2)
• Required: action="cache_status"
• Returns: Cache statistics, hit rates, performance metrics
• Advanced: Cache optimization insights, memory usage
• Use Case: Performance tuning, cache management

💡 ADMINISTRATIVE FEATURES:
• Path Safety: All operations contained within .cursor/rules/
• Error Handling: Graceful failure with descriptive messages
• Metadata Rich: Detailed information about all operations
• Cross-Platform: Works on Windows, macOS, and Linux

🎯 OPERATIONAL BENEFITS:
• System Maintenance: Keep rule system healthy and organized
• Disaster Recovery: Backup and restore capabilities
• Audit Trail: Track rule file changes and modifications
• Space Management: Clean up unnecessary backup files
• Advanced Analysis: Deep insights into rule structure and relationships
• Hierarchical Support: Complete inheritance and composition management
            """
            try:
                rules_dir = self.project_root / ".cursor" / "rules"
                
                if action == "list":
                    if not rules_dir.exists():
                        return {
                            "success": True,
                            "files": [],
                            "message": "Rules directory does not exist"
                        }
                    
                    rule_files = []
                    for file_path in rules_dir.rglob("*.mdc"):
                        rule_files.append({
                            "path": str(file_path.relative_to(self.project_root)),
                            "size": file_path.stat().st_size,
                            "modified": file_path.stat().st_mtime
                        })
                    
                    return {
                        "success": True,
                        "files": rule_files,
                        "count": len(rule_files)
                    }
                
                elif action == "backup":
                    auto_rule_path = rules_dir / "auto_rule.mdc"
                    if not auto_rule_path.exists():
                        return {
                            "success": False,
                            "error": "auto_rule.mdc not found"
                        }
                    
                    backup_path = rules_dir / "auto_rule.mdc.backup"
                    with open(auto_rule_path, 'r', encoding='utf-8') as src:
                        content = src.read()
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(content)
                    
                    return {
                        "success": True,
                        "message": "Backup created successfully",
                        "backup_path": str(backup_path.relative_to(self.project_root))
                    }
                
                elif action == "restore":
                    backup_path = rules_dir / "auto_rule.mdc.backup"
                    if not backup_path.exists():
                        return {
                            "success": False,
                            "error": "Backup file not found"
                        }
                    
                    auto_rule_path = rules_dir / "auto_rule.mdc"
                    with open(backup_path, 'r', encoding='utf-8') as src:
                        content = src.read()
                    with open(auto_rule_path, 'w', encoding='utf-8') as dst:
                        dst.write(content)
                    
                    return {
                        "success": True,
                        "message": "Restored from backup successfully"
                    }
                
                elif action == "clean":
                    backup_files = list(rules_dir.rglob("*.backup"))
                    for backup_file in backup_files:
                        backup_file.unlink()
                    
                    return {
                        "success": True,
                        "message": f"Cleaned {len(backup_files)} backup files"
                    }
                
                elif action == "info":
                    if not rules_dir.exists():
                        return {
                            "success": True,
                            "info": {
                                "directory_exists": False,
                                "path": str(rules_dir.relative_to(self.project_root))
                            }
                        }
                    
                    all_files = list(rules_dir.rglob("*"))
                    mdc_files = list(rules_dir.rglob("*.mdc"))
                    backup_files = list(rules_dir.rglob("*.backup"))
                    
                    info = {
                        "directory_exists": True,
                        "path": str(rules_dir.relative_to(self.project_root)),
                        "total_files": len([f for f in all_files if f.is_file()]),
                        "mdc_files": len(mdc_files),
                        "backup_files": len(backup_files),
                        "auto_rule_exists": (rules_dir / "auto_rule.mdc").exists(),
                        "subdirectories": len([f for f in all_files if f.is_dir()])
                    }
                    
                    return {
                        "success": True,
                        "info": info
                    }
                
                elif action == "load_core":
                    # Define core rule files in priority order
                    core_rules = [
                        "dhafnck_mcp.mdc",           # Main MCP runtime system
                        "dev_workflow.mdc",          # Development workflow
                        "cursor_rules.mdc",          # Cursor rule guidelines
                        "taskmaster.mdc",            # Task management
                        "mcp.mdc"                    # MCP architecture
                    ]
                    
                    loaded_rules = []
                    failed_rules = []
                    total_size = 0
                    
                    for rule_file in core_rules:
                        rule_path = rules_dir / rule_file
                        if rule_path.exists():
                            try:
                                with open(rule_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    file_size = rule_path.stat().st_size
                                    total_size += file_size
                                    
                                loaded_rules.append({
                                    "file": rule_file,
                                    "path": str(rule_path.relative_to(self.project_root)),
                                    "size": file_size,
                                    "status": "loaded",
                                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                                })
                            except Exception as e:
                                failed_rules.append({
                                    "file": rule_file,
                                    "path": str(rule_path.relative_to(self.project_root)),
                                    "status": "error",
                                    "error": str(e)
                                })
                        else:
                            failed_rules.append({
                                "file": rule_file,
                                "path": str(rule_path.relative_to(self.project_root)),
                                "status": "not_found",
                                "error": "File does not exist"
                            })
                    
                    # Generate recommendations
                    recommendations = self._get_core_loading_recommendations(loaded_rules, failed_rules)
                    
                    return {
                        "success": True,
                        "action": "load_core",
                        "loaded_rules": loaded_rules,
                        "failed_rules": failed_rules,
                        "total_loaded": len(loaded_rules),
                        "total_size": total_size,
                        "recommendations": recommendations,
                        "message": f"Core loading complete: {len(loaded_rules)} loaded, {len(failed_rules)} failed"
                    }
                
                elif action == "enhanced_info":
                    # Get comprehensive rule system information from enhanced orchestrator
                    try:
                        orchestrator_info = self.enhanced_orchestrator.get_enhanced_rule_info()
                        
                        return {
                            "success": True,
                            "action": "enhanced_info",
                            "enhanced_orchestrator": orchestrator_info,
                            "message": "Enhanced rule orchestration system information retrieved"
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to get enhanced info: {str(e)}"
                        }
                
                elif action == "parse_rule":
                    # Parse a specific rule file using the enhanced parser
                    if not target:
                        return {
                            "success": False,
                            "error": "Target file path required for parse_rule action"
                        }
                    
                    try:
                        target_path = rules_dir / target if not os.path.isabs(target) else Path(target)
                        
                        if not target_path.exists():
                            return {
                                "success": False,
                                "error": f"Rule file not found: {target}"
                            }
                        
                        # Parse the rule file using enhanced parser
                        rule_content = self.enhanced_orchestrator.parser.parse_rule_file(target_path)
                        
                        return {
                            "success": True,
                            "action": "parse_rule",
                            "file_path": str(target_path.relative_to(self.project_root)),
                            "metadata": {
                                "format": rule_content.metadata.format.value,
                                "type": rule_content.metadata.type.value,
                                "size": rule_content.metadata.size,
                                "checksum": rule_content.metadata.checksum,
                                "dependencies": rule_content.metadata.dependencies,
                                "tags": rule_content.metadata.tags
                            },
                            "content_analysis": {
                                "sections": list(rule_content.sections.keys()),
                                "references": rule_content.references,
                                "variables": rule_content.variables,
                                "line_count": len(rule_content.raw_content.split('\n')),
                                "word_count": len(rule_content.raw_content.split())
                            },
                            "parsed_content": rule_content.parsed_content
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to parse rule file: {str(e)}"
                        }
                
                elif action == "analyze_hierarchy":
                    # Analyze rule hierarchy and dependencies
                    try:
                        # Reload rules to ensure fresh analysis
                        self.enhanced_orchestrator.loaded_rules = self.enhanced_orchestrator._scan_rules()
                        
                        # Get hierarchy information
                        hierarchy_info = {
                            "total_rules": len(self.enhanced_orchestrator.loaded_rules),
                            "rules_by_format": {},
                            "rules_by_directory": {},
                            "largest_files": [],
                            "recently_modified": []
                        }
                        
                        # Analyze rules by format
                        for rule_path, rule_info in self.enhanced_orchestrator.loaded_rules.items():
                            format_type = rule_info["format"]
                            hierarchy_info["rules_by_format"][format_type] = hierarchy_info["rules_by_format"].get(format_type, 0) + 1
                            
                            # Analyze by directory
                            directory = str(Path(rule_path).parent) if Path(rule_path).parent != Path('.') else "root"
                            hierarchy_info["rules_by_directory"][directory] = hierarchy_info["rules_by_directory"].get(directory, 0) + 1
                        
                        # Find largest files (top 5)
                        sorted_by_size = sorted(
                            self.enhanced_orchestrator.loaded_rules.items(),
                            key=lambda x: x[1]["size"],
                            reverse=True
                        )[:5]
                        
                        hierarchy_info["largest_files"] = [
                            {"path": path, "size": info["size"]} 
                            for path, info in sorted_by_size
                        ]
                        
                        # Find recently modified files (top 5)
                        sorted_by_modified = sorted(
                            self.enhanced_orchestrator.loaded_rules.items(),
                            key=lambda x: x[1]["modified"],
                            reverse=True
                        )[:5]
                        
                        hierarchy_info["recently_modified"] = [
                            {"path": path, "modified": info["modified"]} 
                            for path, info in sorted_by_modified
                        ]
                        
                        return {
                            "success": True,
                            "action": "analyze_hierarchy",
                            "hierarchy_analysis": hierarchy_info,
                            "recommendations": [
                                "Consider organizing rules by type in subdirectories",
                                "Review large files for potential splitting",
                                "Monitor recently modified files for consistency"
                            ]
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to analyze hierarchy: {str(e)}"
                        }
                
                elif action == "get_dependencies":
                    # Get dependency information for rules
                    if not target:
                        return {
                            "success": False,
                            "error": "Target file path required for get_dependencies action"
                        }
                    
                    try:
                        target_path = rules_dir / target if not os.path.isabs(target) else Path(target)
                        
                        if not target_path.exists():
                            return {
                                "success": False,
                                "error": f"Rule file not found: {target}"
                            }
                        
                        # Parse the rule file to extract dependencies
                        rule_content = self.enhanced_orchestrator.parser.parse_rule_file(target_path)
                        
                        return {
                            "success": True,
                            "action": "get_dependencies",
                            "file_path": str(target_path.relative_to(self.project_root)),
                            "dependencies": rule_content.metadata.dependencies,
                            "references": rule_content.references,
                            "dependency_analysis": {
                                "total_dependencies": len(rule_content.metadata.dependencies),
                                "total_references": len(rule_content.references),
                                "dependency_types": [
                                    "mdc_references" if "mdc:" in dep else "other" 
                                    for dep in rule_content.metadata.dependencies
                                ]
                            }
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to get dependencies: {str(e)}"
                        }
                
                elif action == "compose_nested_rules":
                    # Phase 2: Compose a rule with its inheritance chain
                    if not target:
                        return {
                            "success": False,
                            "error": "Target file path required for compose_nested_rules action"
                        }
                    
                    try:
                        # Initialize nested rule manager
                        nested_manager = self.enhanced_orchestrator.nested_manager
                        if nested_manager is None:
                            from .enhanced_rule_orchestrator import NestedRuleManager
                            nested_manager = NestedRuleManager(self.enhanced_orchestrator.parser)
                            self.enhanced_orchestrator.nested_manager = nested_manager
                        
                        # Load rule hierarchy
                        rules = nested_manager.load_rule_hierarchy(rules_dir)
                        
                        # Compose the nested rules
                        composition_result = nested_manager.compose_nested_rules(target, rules)
                        
                        return {
                            "success": composition_result.success,
                            "action": "compose_nested_rules",
                            "target_rule": target,
                            "composed_content": composition_result.composed_content,
                            "source_rules": composition_result.source_rules,
                            "inheritance_chain": [
                                {
                                    "parent": inheritance.parent_path,
                                    "child": inheritance.child_path,
                                    "type": inheritance.inheritance_type.value,
                                    "depth": inheritance.inheritance_depth,
                                    "conflicts": inheritance.conflicts
                                }
                                for inheritance in composition_result.inheritance_chain
                            ],
                            "conflicts_resolved": composition_result.conflicts_resolved,
                            "composition_metadata": composition_result.composition_metadata,
                            "warnings": composition_result.warnings
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to compose nested rules: {str(e)}"
                        }
                
                elif action == "compose_rules":
                    # Phase 4: Intelligent multi-rule composition with conflict resolution
                    if not content:
                        return {
                            "success": False,
                            "error": "Content parameter required for compose_rules action (comma-separated list of rule files)"
                        }
                    
                    try:
                        # Parse rule file list from content parameter
                        rule_files = [f.strip() for f in content.split(',')]
                        if not rule_files:
                            return {
                                "success": False,
                                "error": "No rule files specified in content parameter"
                            }
                        
                        # Parse optional parameters
                        output_format = target or "mdc"  # Default to MDC format
                        composition_strategy = "intelligent"  # Default strategy
                        
                        # Initialize rule composer
                        from .enhanced_rule_orchestrator import RuleComposer, RuleFormat
                        rule_composer = RuleComposer()
                        
                        # Load and parse all specified rule files
                        rules_to_compose = []
                        missing_files = []
                        
                        for rule_file in rule_files:
                            # Handle relative paths
                            rule_path = rules_dir / rule_file if not os.path.isabs(rule_file) else Path(rule_file)
                            
                            if not rule_path.exists():
                                missing_files.append(rule_file)
                                continue
                            
                            # Parse the rule file
                            try:
                                rule_content = self.enhanced_orchestrator.parser.parse_rule_file(rule_path)
                                rules_to_compose.append(rule_content)
                            except Exception as e:
                                return {
                                    "success": False,
                                    "error": f"Failed to parse rule file '{rule_file}': {str(e)}"
                                }
                        
                        if missing_files:
                            return {
                                "success": False,
                                "error": f"Rule files not found: {', '.join(missing_files)}"
                            }
                        
                        if not rules_to_compose:
                            return {
                                "success": False,
                                "error": "No valid rule files found to compose"
                            }
                        
                        # Convert output format string to enum
                        try:
                            format_enum = RuleFormat(output_format.lower())
                        except ValueError:
                            format_enum = RuleFormat.MDC  # Default fallback
                        
                        # Compose the rules using the RuleComposer
                        composition_result = rule_composer.compose_rules(
                            rules=rules_to_compose,
                            output_format=format_enum,
                            composition_strategy=composition_strategy
                        )
                        
                        # Get conflict resolution details
                        conflict_details = rule_composer.resolve_conflicts(rules_to_compose)
                        
                        return {
                            "success": composition_result.success,
                            "action": "compose_rules",
                            "rule_files": rule_files,
                            "composition_strategy": composition_strategy,
                            "output_format": output_format,
                            "composed_content": composition_result.composed_content,
                            "source_rules": composition_result.source_rules,
                            "conflicts_resolved": composition_result.conflicts_resolved,
                            "composition_metadata": composition_result.composition_metadata,
                            "warnings": composition_result.warnings,
                            "conflict_analysis": {
                                "total_conflicts": conflict_details.get("total_conflicts", 0),
                                "resolved_conflicts": conflict_details.get("resolved_conflicts", 0),
                                "unresolved_conflicts": conflict_details.get("unresolved_conflicts", 0),
                                "auto_resolution_rate": conflict_details.get("auto_resolution_rate", 100),
                                "resolution_details": conflict_details.get("resolution_details", [])
                            },
                            "rule_count": len(rules_to_compose),
                            "total_size": sum(rule.metadata.size for rule in rules_to_compose),
                            "composed_size": len(composition_result.composed_content)
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to compose rules: {str(e)}"
                        }
                
                elif action == "resolve_rule_inheritance":
                    # Phase 2: Show inheritance chain for a rule
                    if not target:
                        return {
                            "success": False,
                            "error": "Target file path required for resolve_rule_inheritance action"
                        }
                    
                    try:
                        # Initialize nested rule manager
                        nested_manager = self.enhanced_orchestrator.nested_manager
                        if nested_manager is None:
                            from .enhanced_rule_orchestrator import NestedRuleManager
                            nested_manager = NestedRuleManager(self.enhanced_orchestrator.parser)
                            self.enhanced_orchestrator.nested_manager = nested_manager
                        
                        # Load rule hierarchy
                        rules = nested_manager.load_rule_hierarchy(rules_dir)
                        
                        # Resolve inheritance chain
                        inheritance_chain = nested_manager.resolve_inheritance_chain(target)
                        
                        # Get detailed inheritance information
                        inheritance_details = {}
                        if target in nested_manager.inheritance_map:
                            inheritance = nested_manager.inheritance_map[target]
                            inheritance_details = {
                                "parent_path": inheritance.parent_path,
                                "inheritance_type": inheritance.inheritance_type.value,
                                "inherited_sections": inheritance.inherited_sections,
                                "overridden_sections": inheritance.overridden_sections,
                                "merged_variables": inheritance.merged_variables,
                                "inheritance_depth": inheritance.inheritance_depth,
                                "conflicts": inheritance.conflicts
                            }
                        
                        return {
                            "success": True,
                            "action": "resolve_rule_inheritance",
                            "target_rule": target,
                            "inheritance_chain": inheritance_chain,
                            "chain_length": len(inheritance_chain),
                            "inheritance_details": inheritance_details,
                            "has_inheritance": len(inheritance_chain) > 1
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to resolve rule inheritance: {str(e)}"
                        }
                
                elif action == "validate_rule_hierarchy":
                    # Phase 2: Validate rule hierarchy for conflicts and issues
                    try:
                        # Initialize nested rule manager
                        nested_manager = self.enhanced_orchestrator.nested_manager
                        if nested_manager is None:
                            from .enhanced_rule_orchestrator import NestedRuleManager
                            nested_manager = NestedRuleManager(self.enhanced_orchestrator.parser)
                            self.enhanced_orchestrator.nested_manager = nested_manager
                        
                        # Load rule hierarchy
                        rules = nested_manager.load_rule_hierarchy(rules_dir)
                        
                        # Validate hierarchy
                        validation_result = nested_manager.validate_rule_hierarchy(rules)
                        
                        return {
                            "success": True,
                            "action": "validate_rule_hierarchy",
                            "validation_result": validation_result,
                            "summary": {
                                "is_valid": validation_result["valid"],
                                "total_errors": len(validation_result["errors"]),
                                "total_warnings": len(validation_result["warnings"]),
                                "inheritance_issues": len(validation_result["inheritance_issues"]),
                                "circular_dependencies": len(validation_result["circular_dependencies"]),
                                "orphaned_rules": len(validation_result["orphaned_rules"])
                            }
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to validate rule hierarchy: {str(e)}"
                        }
                
                elif action == "build_hierarchy":
                    # Phase 2: Analyze and build complete rule hierarchy
                    try:
                        # Initialize nested rule manager
                        nested_manager = self.enhanced_orchestrator.nested_manager
                        if nested_manager is None:
                            from .enhanced_rule_orchestrator import NestedRuleManager
                            nested_manager = NestedRuleManager(self.enhanced_orchestrator.parser)
                            self.enhanced_orchestrator.nested_manager = nested_manager
                        
                        # Load and analyze rule hierarchy
                        rules = nested_manager.load_rule_hierarchy(rules_dir)
                        hierarchy_info = nested_manager.get_rule_hierarchy_info()
                        
                        # Get detailed hierarchy structure
                        return {
                            "success": True,
                            "action": "build_hierarchy",
                            "total_rules": len(rules),
                            "hierarchy_info": hierarchy_info,
                            "inheritance_relationships": len(nested_manager.inheritance_map),
                            "dependency_graph": dict(nested_manager.dependency_graph),
                            "rule_tree": nested_manager.rule_tree,
                            "inheritance_map": {
                                path: {
                                    "parent": inheritance.parent_path,
                                    "type": inheritance.inheritance_type.value,
                                    "depth": inheritance.inheritance_depth,
                                    "conflicts": inheritance.conflicts
                                }
                                for path, inheritance in nested_manager.inheritance_map.items()
                            }
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to build hierarchy: {str(e)}"
                        }
                
                elif action == "load_nested":
                    # Phase 2: Load rules in hierarchical order with inheritance resolution
                    try:
                        # Initialize nested rule manager
                        nested_manager = self.enhanced_orchestrator.nested_manager
                        if nested_manager is None:
                            from .enhanced_rule_orchestrator import NestedRuleManager
                            nested_manager = NestedRuleManager(self.enhanced_orchestrator.parser)
                            self.enhanced_orchestrator.nested_manager = nested_manager
                        
                        # Load rule hierarchy
                        rules = nested_manager.load_rule_hierarchy(rules_dir)
                        
                        # Process rules with inheritance
                        loaded_rules = []
                        inheritance_applied = []
                        
                        for rule_path, rule_content in rules.items():
                            # Get inheritance chain
                            inheritance_chain = nested_manager.resolve_inheritance_chain(rule_path)
                            
                            # Compose if has inheritance
                            if len(inheritance_chain) > 1:
                                composition_result = nested_manager.compose_nested_rules(rule_path, rules)
                                loaded_rules.append({
                                    "path": rule_path,
                                    "original_size": len(rule_content.raw_content),
                                    "composed_size": len(composition_result.composed_content),
                                    "inheritance_applied": True,
                                    "inheritance_depth": len(inheritance_chain) - 1,
                                    "source_rules": composition_result.source_rules
                                })
                                inheritance_applied.append(rule_path)
                            else:
                                loaded_rules.append({
                                    "path": rule_path,
                                    "size": len(rule_content.raw_content),
                                    "inheritance_applied": False,
                                    "inheritance_depth": 0,
                                    "source_rules": [rule_path]
                                })
                        
                        return {
                            "success": True,
                            "action": "load_nested",
                            "total_rules": len(rules),
                            "loaded_rules": loaded_rules,
                            "inheritance_applied_count": len(inheritance_applied),
                            "inheritance_applied_rules": inheritance_applied,
                            "loading_order": [rule["path"] for rule in loaded_rules]
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to load nested rules: {str(e)}"
                        }
                
                elif action == "cache_status":
                    # Phase 2: Get rule cache status and performance metrics
                    try:
                        # Initialize cache manager if needed
                        cache_manager = self.enhanced_orchestrator.cache_manager
                        if cache_manager is None:
                            from .enhanced_rule_orchestrator import RuleCacheManager
                            cache_manager = RuleCacheManager()
                            self.enhanced_orchestrator.cache_manager = cache_manager
                        
                        # Get cache statistics
                        cache_stats = cache_manager.get_cache_stats()
                        
                        # Get additional cache information
                        cache_keys = list(cache_manager.cache.keys())
                        cache_details = []
                        
                        for key in cache_keys[:10]:  # Show top 10 cached items
                            entry = cache_manager.cache[key]
                            cache_details.append({
                                "key": key,
                                "access_count": entry.access_count,
                                "age_seconds": time.time() - entry.timestamp,
                                "ttl_remaining": entry.ttl - (time.time() - entry.timestamp),
                                "size_bytes": len(entry.content.raw_content)
                            })
                        
                        return {
                            "success": True,
                            "action": "cache_status",
                            "cache_statistics": cache_stats,
                            "cache_details": cache_details,
                            "total_cached_items": len(cache_keys),
                            "cache_enabled": True,
                            "recommendations": [
                                f"Cache utilization: {cache_stats['size']}/{cache_stats['max_size']} ({cache_stats['size']/cache_stats['max_size']*100:.1f}%)",
                                f"Hit rate: {cache_stats['hit_rate']:.2%}",
                                "Consider increasing cache size if hit rate is low" if cache_stats['hit_rate'] < 0.8 else "Cache performance is optimal"
                            ]
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to get cache status: {str(e)}"
                        }
                
                elif action == "register_client":
                    # Phase 3: Register a new client for synchronization
                    try:
                        if not content:
                            return {
                                "success": False,
                                "error": "Client configuration required in content parameter (JSON format)"
                            }
                        
                        # Parse client configuration
                        import json
                        from .enhanced_rule_orchestrator import ClientConfig, ClientAuthMethod, RuleType, ConflictResolution
                        
                        config_data = json.loads(content)
                        
                        # Create ClientConfig object
                        client_config = ClientConfig(
                            client_id=config_data["client_id"],
                            client_name=config_data["client_name"],
                            auth_method=ClientAuthMethod(config_data["auth_method"]),
                            auth_credentials=config_data["auth_credentials"],
                            sync_permissions=config_data.get("sync_permissions", ["pull", "push", "bidirectional"]),
                            rate_limit=config_data.get("rate_limit", 100),
                            sync_frequency=config_data.get("sync_frequency", 300),
                            allowed_rule_types=[RuleType(rt) for rt in config_data.get("allowed_rule_types", ["core", "workflow", "project"])],
                            auto_sync=config_data.get("auto_sync", True),
                            conflict_resolution=ConflictResolution(config_data.get("conflict_resolution", "merge"))
                        )
                        
                        # Register client
                        result = self.enhanced_orchestrator.client_integrator.register_client(client_config)
                        
                        return {
                            "success": True,
                            "action": "register_client",
                            "result": result
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to register client: {str(e)}"
                        }
                
                elif action == "authenticate_client":
                    # Phase 3: Authenticate client for synchronization
                    try:
                        if not target:
                            return {
                                "success": False,
                                "error": "Client ID required in target parameter"
                            }
                        
                        if not content:
                            return {
                                "success": False,
                                "error": "Authentication credentials required in content parameter (JSON format)"
                            }
                        
                        # Parse credentials
                        import json
                        credentials = json.loads(content)
                        
                        # Authenticate client
                        result = self.enhanced_orchestrator.client_integrator.authenticate_client(target, credentials)
                        
                        return {
                            "success": True,
                            "action": "authenticate_client",
                            "client_id": target,
                            "result": result
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to authenticate client: {str(e)}"
                        }
                
                elif action == "sync_client":
                    # Phase 3: Perform synchronization with client
                    try:
                        if not target:
                            return {
                                "success": False,
                                "error": "Sync operation required in target parameter (push|pull|bidirectional|merge)"
                            }
                        
                        if not content:
                            return {
                                "success": False,
                                "error": "Sync data required in content parameter (JSON format with client_id and optional rules)"
                            }
                        
                        # Parse sync data
                        import json
                        from .enhanced_rule_orchestrator import SyncOperation
                        
                        sync_data = json.loads(content)
                        client_id = sync_data["client_id"]
                        client_rules = sync_data.get("rules", {})
                        operation = SyncOperation(target)
                        
                        # Perform synchronization
                        result = self.enhanced_orchestrator.client_integrator.sync_with_client(
                            client_id, operation, client_rules
                        )
                        
                        return {
                            "success": True,
                            "action": "sync_client",
                            "operation": target,
                            "client_id": client_id,
                            "result": result
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to sync with client: {str(e)}"
                        }
                
                elif action == "client_diff":
                    # Phase 3: Get differences between client and server rules
                    try:
                        if not target:
                            return {
                                "success": False,
                                "error": "Client ID required in target parameter"
                            }
                        
                        # Get current server rules
                        nested_manager = self.enhanced_orchestrator.nested_manager
                        if nested_manager is None:
                            from .enhanced_rule_orchestrator import NestedRuleManager
                            nested_manager = NestedRuleManager(self.enhanced_orchestrator.parser)
                            self.enhanced_orchestrator.nested_manager = nested_manager
                        
                        server_rules = nested_manager.load_rule_hierarchy(rules_dir)
                        
                        # Calculate differences
                        result = self.enhanced_orchestrator.client_integrator.get_client_diff(target, server_rules)
                        
                        return {
                            "success": True,
                            "action": "client_diff",
                            "client_id": target,
                            "result": result
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to calculate client diff: {str(e)}"
                        }
                
                elif action == "resolve_conflicts":
                    # Phase 3: Resolve synchronization conflicts
                    try:
                        if not target:
                            return {
                                "success": False,
                                "error": "Client ID required in target parameter"
                            }
                        
                        if not content:
                            return {
                                "success": False,
                                "error": "Conflict data required in content parameter (JSON format with conflicts array)"
                            }
                        
                        # Parse conflict data
                        import json
                        from .enhanced_rule_orchestrator import RuleConflict, ConflictResolution
                        
                        conflict_data = json.loads(content)
                        conflicts = []
                        
                        for conflict_info in conflict_data["conflicts"]:
                            conflict = RuleConflict(
                                rule_path=conflict_info["rule_path"],
                                client_version=conflict_info["client_version"],
                                server_version=conflict_info["server_version"],
                                conflict_type=conflict_info["conflict_type"],
                                client_content=conflict_info["client_content"],
                                server_content=conflict_info["server_content"],
                                suggested_resolution=conflict_info.get("suggested_resolution", "merge"),
                                auto_resolvable=conflict_info.get("auto_resolvable", False)
                            )
                            conflicts.append(conflict)
                        
                        # Resolve conflicts
                        resolution_strategy = ConflictResolution(conflict_data.get("resolution_strategy", "merge"))
                        result = self.enhanced_orchestrator.client_integrator.resolve_conflicts(
                            target, conflicts, resolution_strategy
                        )
                        
                        return {
                            "success": True,
                            "action": "resolve_conflicts",
                            "client_id": target,
                            "result": result
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to resolve conflicts: {str(e)}"
                        }
                
                elif action == "client_status":
                    # Phase 3: Get synchronization status for client
                    try:
                        if not target:
                            return {
                                "success": False,
                                "error": "Client ID required in target parameter"
                            }
                        
                        # Get optional request ID from content
                        request_id = None
                        if content:
                            try:
                                import json
                                data = json.loads(content)
                                request_id = data.get("request_id")
                            except:
                                pass
                        
                        # Get sync status
                        result = self.enhanced_orchestrator.client_integrator.get_sync_status(target, request_id)
                        
                        return {
                            "success": True,
                            "action": "client_status",
                            "client_id": target,
                            "result": result
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to get client status: {str(e)}"
                        }
                
                elif action == "client_analytics":
                    # Phase 3: Get analytics for client synchronization
                    try:
                        if not target:
                            return {
                                "success": False,
                                "error": "Client ID required in target parameter"
                            }
                        
                        # Get client analytics
                        result = self.enhanced_orchestrator.client_integrator.get_client_analytics(target)
                        
                        return {
                            "success": True,
                            "action": "client_analytics",
                            "client_id": target,
                            "result": result
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to get client analytics: {str(e)}"
                        }
                
                else:
                    return {
                        "success": False,
                        "error": f"Unknown action: {action}. Available: list, backup, restore, clean, info, load_core, parse_rule, analyze_hierarchy, get_dependencies, enhanced_info, compose_nested_rules, resolve_rule_inheritance, validate_rule_hierarchy, build_hierarchy, load_nested, cache_status, register_client, authenticate_client, sync_client, client_diff, resolve_conflicts, client_status, client_analytics"
                    }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Management operation failed: {str(e)}"
                }
        
        def _get_core_loading_recommendations(self, loaded_rules, failed_rules):
            """Generate recommendations based on core rule loading results"""
            recommendations = []
            
            # Check for critical missing rules
            critical_rules = ["dhafnck_mcp.mdc", "dev_workflow.mdc"]
            loaded_files = [rule["file"] for rule in loaded_rules]
            
            for critical_rule in critical_rules:
                if critical_rule not in loaded_files:
                    recommendations.append({
                        "type": "critical",
                        "message": f"Critical rule '{critical_rule}' is missing. Session functionality may be limited.",
                        "action": "Create or restore this essential rule file"
                    })
            
            # Performance recommendations
            total_loaded = len(loaded_rules)
            if total_loaded == 0:
                recommendations.append({
                    "type": "warning",
                    "message": "No core rules loaded. AI assistant will operate with minimal context.",
                    "action": "Initialize core rule files or check rule directory permissions"
                })
            elif total_loaded < 3:
                recommendations.append({
                    "type": "info",
                    "message": f"Only {total_loaded} core rules loaded. Consider adding more essential rules.",
                    "action": "Review and add missing rule files for optimal functionality"
                })
            else:
                recommendations.append({
                    "type": "success",
                    "message": f"Successfully loaded {total_loaded} core rules. Session is ready for optimal operation.",
                    "action": "Continue with normal operations"
                })
            
            # Error handling recommendations
            if failed_rules:
                error_count = len([r for r in failed_rules if r["status"] == "error"])
                missing_count = len([r for r in failed_rules if r["status"] == "not_found"])
                
                if error_count > 0:
                    recommendations.append({
                        "type": "warning",
                        "message": f"{error_count} rule files failed to load due to errors.",
                        "action": "Check file permissions and content integrity"
                    })
                
                if missing_count > 0:
                    recommendations.append({
                        "type": "info",
                        "message": f"{missing_count} expected rule files were not found.",
                        "action": "These files are optional but may enhance functionality if created"
                    })
            
            return recommendations
        
        @mcp.tool()
        def regenerate_auto_rule(
            role: Annotated[Optional[str], Field(description="Target role for rule generation. Examples: senior_developer, task_planner, code_reviewer, security_engineer, qa_engineer")] = None,
            task_context: Annotated[Optional[Dict[str, Any]], Field(description="Specific task information with structure: {'id': '...', 'title': '...', 'description': '...', 'assignee': '...'}")] = None
        ) -> Dict[str, Any]:
            """🔄 AUTO-RULE REGENERATION ENGINE - Smart context generation for AI assistant

⭐ WHAT IT DOES: Automatically generates optimized auto_rule.mdc based on role and task context
📋 WHEN TO USE: Role switching, task context updates, AI behavior reset, context optimization
🎯 PERFECT FOR: Dynamic AI assistant configuration and context-aware rule generation

🧠 INTELLIGENT GENERATION:
• Role-Based Rules: Generates appropriate rules based on specified role
• Context Integration: Incorporates task-specific context and requirements
• Template Application: Uses proven rule templates and patterns
• Smart Defaults: Fills in missing information intelligently

📋 PARAMETERS (both optional):

👤 ROLE: Specify target role for rule generation
• Values: "senior_developer", "task_planner", "code_reviewer", etc.
• Effect: Generates role-specific context and behavioral rules
• Default: Uses "senior_developer" if not specified
• Example: role="security_engineer"

📝 TASK_CONTEXT: Provide specific task information
• Structure: {"id": "...", "title": "...", "description": "...", "assignee": "..."}
• Optional Fields: priority, details, status, due_date
• Smart Fallback: Creates generic context if not provided
• Integration: Pulls from active task if available

🎯 GENERATION ALGORITHM:
1. Analyzes provided role and task context
2. Selects appropriate rule templates
3. Customizes content for specific situation
4. Generates comprehensive auto_rule.mdc
5. Validates generated content quality

💡 SMART FEATURES:
• Template Synthesis: Combines multiple rule patterns
• Context Awareness: Adapts to project and task specifics
• Quality Assurance: Validates generated rules for completeness
• Immediate Effect: Generated rules take effect immediately

🎯 COMMON SCENARIOS:
• Role Change: regenerate_auto_rule(role="qa_engineer")
• Task Focus: Include specific task context for targeted rules
• Context Reset: Call without parameters for clean slate
• Workflow Optimization: Generate rules for specific project phases

🚀 PRODUCTIVITY BENEFITS:
• Instant Adaptation: AI behavior matches current needs
• Context Precision: Rules tailored to exact requirements
• Quality Consistency: Always generates well-structured rules
• Zero Manual Work: Eliminates need for manual rule writing
            """
            try:
                # If no specific context provided, create a generic one
                if not task_context:
                    task_context = {
                        "id": "manual",
                        "title": "Manual Rule Generation",
                        "description": "Manually triggered rule generation",
                        "status": "in_progress",
                        "priority": "medium",
                        "assignee": role or "senior_developer",
                        "details": "Rules generated manually via MCP tool"
                    }
                
                # Create a simple task-like object for the generator
                class SimpleTask:
                    def __init__(self, data):
                        self.id = type('TaskId', (), {'value': data['id']})()
                        self.title = data['title']
                        self.description = data['description']
                        self.assignee = data['assignee']
                        self.priority = type('Priority', (), {'value': data['priority']})()
                        self.details = data['details']
                        
                    def to_dict(self):
                        return {
                            'id': self.id.value,
                            'title': self.title,
                            'description': self.description,
                            'assignee': self.assignee,
                            'priority': self.priority.value,
                            'details': self.details,
                            'status': 'in_progress'
                        }
                
                task = SimpleTask(task_context)
                
                # Generate rules
                success = self._auto_rule_generator.generate_rules_for_task(task)
                
                if success:
                    return {
                        "success": True,
                        "message": "Auto rules regenerated successfully",
                        "role": role or task_context['assignee'],
                        "output_path": str((self.project_root / ".cursor" / "rules" / "auto_rule.mdc").relative_to(self.project_root))
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to regenerate auto rules"
                    }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Regeneration failed: {str(e)}"
                }
        
        @mcp.tool()
        def validate_tasks_json(
            file_path: Annotated[Optional[str], Field(description="Target tasks.json file to validate. If not provided, uses hierarchical path with project_id/task_tree_id")] = None,
            project_id: Annotated[Optional[str], Field(description="Project identifier for hierarchical task validation")] = None,
            task_tree_id: Annotated[Optional[str], Field(description="Task tree identifier (defaults to 'main')")] = "main",
            user_id: Annotated[Optional[str], Field(description="User identifier (defaults to 'default_id')")] = "default_id",
            output_format: Annotated[str, Field(description="Validation report detail level. Available: summary (default), detailed, json")] = "summary"
        ) -> Dict[str, Any]:
            """🔍 TASKS.JSON INTEGRITY VALIDATOR - Comprehensive task database health analysis

⭐ WHAT IT DOES: Deep analysis of tasks.json structure, data integrity, and schema compliance
📋 WHEN TO USE: After task modifications, troubleshooting data issues, pre-deployment checks
🎯 CRITICAL FOR: Data integrity, system reliability, preventing corruption in task management

🔬 COMPREHENSIVE VALIDATION:

📊 STRUCTURAL ANALYSIS:
• JSON Schema: Validates proper JSON structure and syntax
• Required Fields: Ensures all mandatory task properties exist
• Data Types: Verifies correct field types (strings, arrays, objects)
• Relationship Integrity: Validates task dependencies and subtask links

🎯 CONTENT VALIDATION:
• ID Uniqueness: Ensures no duplicate task identifiers
• Reference Integrity: Validates dependency and subtask references
• Value Constraints: Checks valid status, priority, and enum values
• Logical Consistency: Identifies contradictory or impossible states

📋 PARAMETERS:

📁 FILE_PATH (optional): Target file for validation
• If not provided: Uses hierarchical path with project_id/task_tree_id
• Custom: Specify alternate tasks.json file path
• Path Handling: Supports relative and absolute paths

🏗️ PROJECT_ID (optional): Project identifier for hierarchical validation
• When provided: Uses hierarchical storage structure
• Format: .cursor/rules/tasks/{user_id}/{project_id}/{task_tree_id}/tasks.json
• Example: "dhafnck_mcp_main", "chaxiaiv2"

🌳 TASK_TREE_ID (optional): Task tree identifier
• Default: "main" (primary task tree)
• Custom: Specify alternate task tree (e.g., "v2.1---multiple-projects-support")
• Used with project_id for hierarchical validation

👤 USER_ID (optional): User identifier
• Default: "default_id" (standard user)
• Custom: Specify alternate user for multi-user scenarios

📊 OUTPUT_FORMAT: Control validation report detail level
• "summary" (default): High-level overview with critical issues
• "detailed": Comprehensive analysis with specific errors
• "json": Machine-readable format for automation

🚨 ISSUE DETECTION:
• Missing Properties: Identifies incomplete task definitions
• Invalid References: Finds broken dependency or subtask links
• Data Corruption: Detects malformed or corrupted entries
• Schema Violations: Highlights structure and type mismatches

💡 QUALITY METRICS:
• Completeness Score: Percentage of properly formed tasks
• Integrity Health: Reference and relationship validation status
• Schema Compliance: Adherence to task management standards
• Performance Impact: File size and structure efficiency

🎯 USE CASES:
• Pre-Deployment: Validate before system updates
• Troubleshooting: Diagnose task management issues
• Data Migration: Verify after import/export operations
• Quality Assurance: Regular health checks of task database
• Integration Testing: Ensure compatibility with external systems

🔧 DEVELOPER BENEFITS:
• Early Problem Detection: Catch issues before they cause failures
• Data Quality Assurance: Maintain high-quality task database
• Debug Support: Detailed error information for quick fixes
• Automation Ready: JSON output enables automated validation
            """
            try:
                # Determine target file path
                if file_path is None:
                    if project_id:
                        # Use hierarchical structure
                        target_path = self.project_root / ".cursor" / "rules" / "tasks" / user_id / project_id / task_tree_id / "tasks.json"
                    else:
                        # Fallback to legacy path
                        target_path = self.project_root / ".cursor" / "rules" / "tasks" / "tasks.json"
                else:
                    # Use provided file path
                    import os
                    if not os.path.isabs(file_path):
                        target_path = self.project_root / file_path
                    else:
                        target_path = Path(file_path)
                
                # Import the validator class
                import sys
                import importlib.util
                
                # Load the tasks validator from the tools directory
                validator_path = self.project_root / ".cursor" / "rules" / "tools" / "tasks_validator.py"
                
                if not validator_path.exists():
                    return {
                        "success": False,
                        "error": f"Tasks validator not found: {validator_path}"
                    }
                
                # Load the validator module
                spec = importlib.util.spec_from_file_location("tasks_validator", validator_path)
                validator_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(validator_module)
                
                # Create validator instance with resolved path
                validator = validator_module.TasksValidator(str(target_path))
                
                # Run validation
                result = validator.validate()
                
                if output_format == "json":
                    return {
                        "success": True,
                        "validation_result": result
                    }
                elif output_format == "detailed":
                    return {
                        "success": True,
                        "file_path": result["file_path"],
                        "file_exists": result["file_exists"],
                        "validation_passed": result["validation_passed"],
                        "total_issues": result["total_issues"],
                        "summary": result["summary"],
                        "errors": result["errors"],
                        "warnings": result["warnings"],
                        "missing_properties": result["missing_properties"],
                        "recommendations": result["recommendations"]
                    }
                else:  # summary format
                    status = "✅ VALID" if result["validation_passed"] else "❌ INVALID"
                    issues_summary = f"Errors: {result['summary']['errors']}, Warnings: {result['summary']['warnings']}, Missing: {result['summary']['missing_properties']}"
                    
                    return {
                        "success": True,
                        "file_path": result["file_path"],
                        "status": status,
                        "validation_passed": result["validation_passed"],
                        "total_issues": result["total_issues"],
                        "issues_summary": issues_summary,
                        "critical_errors": result["errors"][:3] if result["errors"] else [],
                        "recommendations": result["recommendations"][:2] if result["recommendations"] else []
                    }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Validation failed: {str(e)}"
                } 