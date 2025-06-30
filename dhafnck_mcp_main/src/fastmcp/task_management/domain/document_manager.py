"""
Document Manager - Core business logic for document management system
Handles document tracking, dependencies, location validation, and knowledge management.
"""

import json
import os
import fnmatch
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

from .document_entities import (
    DocumentEntity, DependencyEntity, KnowledgeEntry, LocationRule, DocumentIndex,
    DocumentType, DocumentCategory, DependencyType, DependencyStrength, DocumentMetadata
)

logger = logging.getLogger(__name__)


class DocumentManager:
    """Core document management system"""
    
    def __init__(self, base_path: str = None, config: Dict[str, Any] = None):
        """Initialize document manager"""
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.config = config or {}
        self.index = DocumentIndex()
        self._lock = threading.RLock()
        self._storage_path = self.base_path / ".cursor" / "documents"
        self._storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_index()
        self._setup_default_rules()
    
    def scan_directory(self, directory: str = None, project_id: str = "", recursive: bool = True) -> Dict[str, Any]:
        """Scan directory for documents and add them to index"""
        with self._lock:
            scan_path = Path(directory) if directory else self.base_path
            if not scan_path.exists():
                return {"success": False, "error": f"Directory {scan_path} does not exist"}
            
            added_count = 0
            updated_count = 0
            errors = []
            
            try:
                pattern = "**/*" if recursive else "*"
                for file_path in scan_path.glob(pattern):
                    if file_path.is_file():
                        try:
                            relative_path = str(file_path.relative_to(self.base_path))
                            existing_doc = self.index.find_by_path(relative_path)
                            
                            if existing_doc:
                                # Update existing document
                                metadata = self._extract_metadata(str(file_path))
                                if metadata and existing_doc.metadata and metadata.modified_at > existing_doc.metadata.modified_at:
                                    existing_doc.metadata = metadata
                                    existing_doc.content_hash = existing_doc._calculate_hash()
                                    updated_count += 1
                            else:
                                # Add new document
                                doc = self._create_document_from_path(relative_path, project_id)
                                if doc:
                                    self.index.add_document(doc)
                                    added_count += 1
                        
                        except Exception as e:
                            errors.append(f"Error processing {file_path}: {e}")
                
                self._save_index()
                
                return {
                    "success": True,
                    "added": added_count,
                    "updated": updated_count,
                    "errors": errors,
                    "total_documents": len(self.index.documents)
                }
            
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    def add_document(self, path: str, project_id: str = "", tags: List[str] = None, 
                    category: str = None) -> Dict[str, Any]:
        """Manually add a document to the index"""
        with self._lock:
            try:
                # Check if document already exists
                existing_doc = self.index.find_by_path(path)
                if existing_doc:
                    return {"success": False, "error": f"Document {path} already exists"}
                
                doc = self._create_document_from_path(path, project_id)
                if not doc:
                    return {"success": False, "error": f"Could not create document from path {path}"}
                
                # Override category if provided
                if category:
                    try:
                        doc.category = DocumentCategory(category)
                    except ValueError:
                        return {"success": False, "error": f"Invalid category: {category}"}
                
                # Add custom tags
                if tags:
                    doc.tags.update(tags)
                
                self.index.add_document(doc)
                self._save_index()
                
                return {
                    "success": True,
                    "document": doc.to_dict(),
                    "message": f"Document {path} added successfully"
                }
            
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    def get_document(self, document_id: str = None, path: str = None) -> Dict[str, Any]:
        """Get document by ID or path"""
        try:
            doc = None
            if document_id:
                doc = self.index.documents.get(document_id)
            elif path:
                doc = self.index.find_by_path(path)
            
            if not doc:
                return {"success": False, "error": "Document not found"}
            
            # Update access statistics
            doc.last_accessed = datetime.now()
            doc.access_count += 1
            self._save_index()
            
            return {
                "success": True,
                "document": doc.to_dict()
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_documents(self, project_id: str = None, category: str = None, 
                      tag: str = None, limit: int = None) -> Dict[str, Any]:
        """List documents with optional filtering"""
        try:
            documents = []
            
            if project_id:
                documents = self.index.find_by_project(project_id)
            elif category:
                try:
                    cat_enum = DocumentCategory(category)
                    documents = self.index.find_by_category(cat_enum)
                except ValueError:
                    return {"success": False, "error": f"Invalid category: {category}"}
            elif tag:
                documents = self.index.find_by_tag(tag)
            else:
                documents = list(self.index.documents.values())
            
            # Apply limit
            if limit and limit > 0:
                documents = documents[:limit]
            
            return {
                "success": True,
                "documents": [doc.to_dict() for doc in documents],
                "total": len(documents)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_dependency(self, source_id: str, target_id: str, dependency_type: str, 
                      relationship_nature: str, strength: str = "medium") -> Dict[str, Any]:
        """Add dependency between documents"""
        with self._lock:
            try:
                # Validate documents exist
                if source_id not in self.index.documents:
                    return {"success": False, "error": f"Source document {source_id} not found"}
                if target_id not in self.index.documents:
                    return {"success": False, "error": f"Target document {target_id} not found"}
                
                # Validate enums
                try:
                    dep_type = DependencyType(dependency_type)
                    dep_strength = DependencyStrength(strength)
                except ValueError as e:
                    return {"success": False, "error": f"Invalid enum value: {e}"}
                
                # Check for circular dependencies
                if self._would_create_cycle(source_id, target_id):
                    return {"success": False, "error": "Would create circular dependency"}
                
                # Create dependency
                dep = DependencyEntity(
                    id="",  # Auto-generated
                    source_document_id=source_id,
                    target_document_id=target_id,
                    dependency_type=dep_type,
                    relationship_nature=relationship_nature,
                    strength=dep_strength
                )
                
                self.index.dependencies[dep.id] = dep
                self._save_index()
                
                return {
                    "success": True,
                    "dependency": dep.to_dict(),
                    "message": "Dependency added successfully"
                }
            
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    def validate_locations(self, project_id: str = None) -> Dict[str, Any]:
        """Validate document locations against rules"""
        try:
            violations = []
            documents = (self.index.find_by_project(project_id) if project_id 
                        else list(self.index.documents.values()))
            
            for doc in documents:
                for rule in self.index.location_rules.values():
                    if not rule.active:
                        continue
                    
                    # Check if rule applies to this document
                    if rule.categories and doc.category not in rule.categories:
                        continue
                    
                    if rule.document_types and doc.type not in rule.document_types:
                        continue
                    
                    # Check pattern match
                    if not fnmatch.fnmatch(doc.name, rule.pattern):
                        continue
                    
                    # Check required path
                    if rule.required_path and not doc.path.startswith(rule.required_path):
                        violations.append({
                            "document_id": doc.id,
                            "document_path": doc.path,
                            "rule_id": rule.id,
                            "violation_type": "wrong_location",
                            "expected_path": rule.required_path,
                            "description": rule.description
                        })
                        doc.location_valid = False
                    
                    # Check forbidden paths
                    for forbidden in rule.forbidden_paths:
                        if doc.path.startswith(forbidden):
                            violations.append({
                                "document_id": doc.id,
                                "document_path": doc.path,
                                "rule_id": rule.id,
                                "violation_type": "forbidden_location",
                                "forbidden_path": forbidden,
                                "description": rule.description
                            })
                            doc.location_valid = False
            
            self._save_index()
            
            return {
                "success": True,
                "violations": violations,
                "total_violations": len(violations),
                "documents_checked": len(documents)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_knowledge(self, query: str, category: str = None, 
                        limit: int = 10) -> Dict[str, Any]:
        """Search knowledge entries"""
        try:
            results = []
            query_lower = query.lower()
            
            for entry in self.index.knowledge_entries.values():
                # Simple text search (can be enhanced with semantic search)
                score = 0.0
                
                if query_lower in entry.title.lower():
                    score += 2.0
                if query_lower in entry.content.lower():
                    score += 1.0
                if any(query_lower in tag.lower() for tag in entry.tags):
                    score += 1.5
                
                if score > 0:
                    if not category or entry.category == category:
                        entry_dict = entry.to_dict()
                        entry_dict["relevance_score"] = score
                        results.append(entry_dict)
            
            # Sort by relevance score
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # Apply limit
            if limit > 0:
                results = results[:limit]
            
            return {
                "success": True,
                "results": results,
                "total": len(results),
                "query": query
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_statistics(self, project_id: str = None) -> Dict[str, Any]:
        """Get document management statistics"""
        try:
            documents = (self.index.find_by_project(project_id) if project_id 
                        else list(self.index.documents.values()))
            
            stats = {
                "total_documents": len(documents),
                "total_dependencies": len(self.index.dependencies),
                "total_knowledge_entries": len(self.index.knowledge_entries),
                "total_location_rules": len(self.index.location_rules),
                "by_category": {},
                "by_type": {},
                "location_violations": 0,
                "most_accessed": [],
                "recent_documents": []
            }
            
            # Category and type statistics
            for doc in documents:
                cat = doc.category.value
                doc_type = doc.type.value
                
                stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
                stats["by_type"][doc_type] = stats["by_type"].get(doc_type, 0) + 1
                
                if not doc.location_valid:
                    stats["location_violations"] += 1
            
            # Most accessed documents
            sorted_docs = sorted(documents, key=lambda d: d.access_count, reverse=True)
            stats["most_accessed"] = [
                {"id": doc.id, "path": doc.path, "access_count": doc.access_count}
                for doc in sorted_docs[:5]
            ]
            
            # Recent documents
            sorted_recent = sorted(documents, key=lambda d: d.indexed_at or datetime.min, reverse=True)
            stats["recent_documents"] = [
                {"id": doc.id, "path": doc.path, "indexed_at": doc.indexed_at.isoformat() if doc.indexed_at else None}
                for doc in sorted_recent[:5]
            ]
            
            return {
                "success": True,
                "statistics": stats,
                "project_id": project_id
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Helper methods (simplified for this integration)
    
    def _get_storage_file(self, name: str) -> Path:
        """Get storage file path"""
        return self._storage_path / f"{name}.json"
    
    def _load_index(self):
        """Load document index from storage"""
        try:
            docs_file = self._get_storage_file("documents")
            if docs_file.exists():
                with open(docs_file, 'r', encoding='utf-8') as f:
                    docs_data = json.load(f)
                    for doc_data in docs_data.values():
                        doc = DocumentEntity.from_dict(doc_data)
                        self.index.add_document(doc)
            logger.info(f"Loaded {len(self.index.documents)} documents")
        except Exception as e:
            logger.error(f"Error loading document index: {e}")
    
    def _save_index(self):
        """Save document index to storage"""
        try:
            docs_data = {doc_id: doc.to_dict() for doc_id, doc in self.index.documents.items()}
            with open(self._get_storage_file("documents"), 'w', encoding='utf-8') as f:
                json.dump(docs_data, f, indent=2, ensure_ascii=False)
            logger.debug("Document index saved successfully")
        except Exception as e:
            logger.error(f"Error saving document index: {e}")
    
    def _setup_default_rules(self):
        """Setup default location rules"""
        default_rules = [
            {
                "id": "cursor_rules",
                "pattern": "*.mdc",
                "categories": ["rules"],
                "required_path": ".cursor/rules/",
                "description": "Cursor rules files should be in .cursor/rules/"
            },
            {
                "id": "documentation",
                "pattern": "*.md",
                "categories": ["documentation"],
                "required_path": "docs/",
                "description": "Documentation files should be in docs/"
            }
        ]
        
        for rule_data in default_rules:
            rule_id = rule_data["id"]
            if rule_id not in self.index.location_rules:
                rule = LocationRule(
                    id=rule_id,
                    pattern=rule_data["pattern"],
                    categories={DocumentCategory(cat) for cat in rule_data.get("categories", [])},
                    required_path=rule_data.get("required_path", ""),
                    forbidden_paths=set(),
                    description=rule_data["description"]
                )
                self.index.location_rules[rule_id] = rule
    
    def _detect_document_type(self, path: str) -> DocumentType:
        """Detect document type from file extension"""
        ext = Path(path).suffix.lower()
        type_mapping = {
            '.md': DocumentType.MARKDOWN,
            '.mdc': DocumentType.RULE,
            '.json': DocumentType.JSON,
            '.py': DocumentType.PYTHON,
            '.ts': DocumentType.TYPESCRIPT,
            '.js': DocumentType.TYPESCRIPT,
            '.yaml': DocumentType.YAML,
            '.yml': DocumentType.YAML,
            '.txt': DocumentType.TEXT,
            '.config': DocumentType.CONFIG
        }
        return type_mapping.get(ext, DocumentType.OTHER)
    
    def _detect_document_category(self, path: str, doc_type: DocumentType) -> DocumentCategory:
        """Detect document category from path and type"""
        path_lower = path.lower()
        
        if '.cursor/rules' in path_lower or doc_type == DocumentType.RULE:
            return DocumentCategory.RULES
        elif 'docs/' in path_lower or 'documentation/' in path_lower:
            return DocumentCategory.DOCUMENTATION
        elif 'test' in path_lower:
            return DocumentCategory.TESTS
        elif 'config' in path_lower or doc_type == DocumentType.CONFIG:
            return DocumentCategory.CONFIGURATION
        elif doc_type in [DocumentType.PYTHON, DocumentType.TYPESCRIPT]:
            return DocumentCategory.CODE
        else:
            return DocumentCategory.OTHER
    
    def _extract_metadata(self, path: str) -> Optional[DocumentMetadata]:
        """Extract metadata from file"""
        try:
            file_path = Path(path)
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            return DocumentMetadata(
                size=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                author=os.getenv('USER', 'unknown')
            )
        except Exception as e:
            logger.warning(f"Error extracting metadata for {path}: {e}")
            return None
    
    def _create_document_from_path(self, path: str, project_id: str = "") -> Optional[DocumentEntity]:
        """Create document entity from file path"""
        try:
            file_path = Path(path)
            doc_type = self._detect_document_type(path)
            category = self._detect_document_category(path, doc_type)
            metadata = self._extract_metadata(path)
            
            # Auto-generate tags based on path
            tags = set()
            path_parts = Path(path).parts
            for part in path_parts:
                if part not in {'.', '..', ''}:
                    tags.add(part)
            
            doc = DocumentEntity(
                id="",  # Will be auto-generated
                path=path,
                name=file_path.name,
                type=doc_type,
                category=category,
                tags=tags,
                metadata=metadata,
                project_id=project_id
            )
            
            return doc
            
        except Exception as e:
            logger.error(f"Error creating document from path {path}: {e}")
            return None
    
    def _would_create_cycle(self, source_id: str, target_id: str) -> bool:
        """Check if adding dependency would create a cycle"""
        visited = set()
        
        def has_path(start: str, end: str) -> bool:
            if start == end:
                return True
            if start in visited:
                return False
            
            visited.add(start)
            
            for dep in self.index.dependencies.values():
                if dep.source_document_id == start:
                    if has_path(dep.target_document_id, end):
                        return True
            
            return False
        
        return has_path(target_id, source_id) 