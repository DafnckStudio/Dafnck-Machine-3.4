"""
Document Management Domain Entities
Defines the core data structures for document tracking, dependencies, and knowledge management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from pathlib import Path
import hashlib
import json


class DependencyType(Enum):
    """Types of dependencies between documents"""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


class DependencyStrength(Enum):
    """Strength of dependency relationship"""
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"


class DocumentType(Enum):
    """Types of documents in the system"""
    MARKDOWN = "markdown"
    JSON = "json"
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    YAML = "yaml"
    TEXT = "text"
    RULE = "rule"
    CONFIG = "config"
    DOCUMENTATION = "documentation"
    OTHER = "other"


class DocumentCategory(Enum):
    """Categories for document organization"""
    RULES = "rules"
    DOCUMENTATION = "documentation"
    CODE = "code"
    CONFIGURATION = "configuration"
    TEMPLATES = "templates"
    TESTS = "tests"
    ASSETS = "assets"
    GENERATED = "generated"
    OTHER = "other"


@dataclass
class DocumentMetadata:
    """Metadata for a document"""
    size: int
    created_at: datetime
    modified_at: datetime
    author: str
    version: str = "1.0"
    encoding: str = "utf-8"
    line_count: int = 0
    word_count: int = 0


@dataclass
class DocumentEntity:
    """Core document entity with all properties"""
    id: str
    path: str
    name: str
    type: DocumentType
    category: DocumentCategory
    tags: Set[str] = field(default_factory=set)
    metadata: Optional[DocumentMetadata] = None
    content_hash: str = ""
    location_valid: bool = True
    project_id: str = ""
    indexed_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    
    def __post_init__(self):
        """Post-initialization processing"""
        if not self.id:
            self.id = self._generate_id()
        if not self.content_hash:
            self.content_hash = self._calculate_hash()
        if self.indexed_at is None:
            self.indexed_at = datetime.now()
    
    def _generate_id(self) -> str:
        """Generate unique ID based on path"""
        return hashlib.md5(self.path.encode()).hexdigest()[:12]
    
    def _calculate_hash(self) -> str:
        """Calculate content hash for the document"""
        try:
            if Path(self.path).exists():
                with open(self.path, 'rb') as f:
                    return hashlib.sha256(f.read()).hexdigest()[:16]
        except Exception:
            pass
        return hashlib.md5(self.path.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "path": self.path,
            "name": self.name,
            "type": self.type.value,
            "category": self.category.value,
            "tags": list(self.tags),
            "metadata": self.metadata.__dict__ if self.metadata else None,
            "content_hash": self.content_hash,
            "location_valid": self.location_valid,
            "project_id": self.project_id,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "access_count": self.access_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentEntity':
        """Create from dictionary representation"""
        metadata = None
        if data.get('metadata'):
            metadata = DocumentMetadata(**data['metadata'])
        
        return cls(
            id=data['id'],
            path=data['path'],
            name=data['name'],
            type=DocumentType(data['type']),
            category=DocumentCategory(data['category']),
            tags=set(data.get('tags', [])),
            metadata=metadata,
            content_hash=data.get('content_hash', ''),
            location_valid=data.get('location_valid', True),
            project_id=data.get('project_id', ''),
            indexed_at=datetime.fromisoformat(data['indexed_at']) if data.get('indexed_at') else None,
            last_accessed=datetime.fromisoformat(data['last_accessed']) if data.get('last_accessed') else None,
            access_count=data.get('access_count', 0)
        )


@dataclass
class DependencyEntity:
    """Represents a dependency relationship between documents"""
    id: str
    source_document_id: str
    target_document_id: str
    dependency_type: DependencyType
    relationship_nature: str
    strength: DependencyStrength = DependencyStrength.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing"""
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for dependency"""
        combined = f"{self.source_document_id}-{self.target_document_id}-{self.dependency_type.value}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "source_document_id": self.source_document_id,
            "target_document_id": self.target_document_id,
            "dependency_type": self.dependency_type.value,
            "relationship_nature": self.relationship_nature,
            "strength": self.strength.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DependencyEntity':
        """Create from dictionary representation"""
        return cls(
            id=data['id'],
            source_document_id=data['source_document_id'],
            target_document_id=data['target_document_id'],
            dependency_type=DependencyType(data['dependency_type']),
            relationship_nature=data['relationship_nature'],
            strength=DependencyStrength(data['strength']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            metadata=data.get('metadata', {})
        )


@dataclass
class KnowledgeEntry:
    """Represents a knowledge entry in the library"""
    id: str
    title: str
    content: str
    category: str
    tags: Set[str] = field(default_factory=set)
    related_documents: Set[str] = field(default_factory=set)
    usage_count: int = 0
    relevance_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing"""
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for knowledge entry"""
        combined = f"{self.title}-{self.category}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": list(self.tags),
            "related_documents": list(self.related_documents),
            "usage_count": self.usage_count,
            "relevance_score": self.relevance_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "author": self.author,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeEntry':
        """Create from dictionary representation"""
        return cls(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            category=data['category'],
            tags=set(data.get('tags', [])),
            related_documents=set(data.get('related_documents', [])),
            usage_count=data.get('usage_count', 0),
            relevance_score=data.get('relevance_score', 1.0),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            author=data.get('author', ''),
            metadata=data.get('metadata', {})
        )


@dataclass
class LocationRule:
    """Rules for document location validation"""
    id: str
    pattern: str  # Glob pattern or regex
    document_types: Set[DocumentType] = field(default_factory=set)
    categories: Set[DocumentCategory] = field(default_factory=set)
    required_path: str = ""
    forbidden_paths: Set[str] = field(default_factory=set)
    description: str = ""
    priority: int = 1
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "pattern": self.pattern,
            "document_types": [t.value for t in self.document_types],
            "categories": [c.value for c in self.categories],
            "required_path": self.required_path,
            "forbidden_paths": list(self.forbidden_paths),
            "description": self.description,
            "priority": self.priority,
            "active": self.active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LocationRule':
        """Create from dictionary representation"""
        return cls(
            id=data['id'],
            pattern=data['pattern'],
            document_types={DocumentType(t) for t in data.get('document_types', [])},
            categories={DocumentCategory(c) for c in data.get('categories', [])},
            required_path=data.get('required_path', ''),
            forbidden_paths=set(data.get('forbidden_paths', [])),
            description=data.get('description', ''),
            priority=data.get('priority', 1),
            active=data.get('active', True)
        )


@dataclass
class DocumentIndex:
    """Index for fast document lookup and search"""
    documents: Dict[str, DocumentEntity] = field(default_factory=dict)
    dependencies: Dict[str, DependencyEntity] = field(default_factory=dict)
    knowledge_entries: Dict[str, KnowledgeEntry] = field(default_factory=dict)
    location_rules: Dict[str, LocationRule] = field(default_factory=dict)
    
    # Indexes for fast lookup
    by_path: Dict[str, str] = field(default_factory=dict)  # path -> document_id
    by_category: Dict[DocumentCategory, Set[str]] = field(default_factory=dict)  # category -> document_ids
    by_type: Dict[DocumentType, Set[str]] = field(default_factory=dict)  # type -> document_ids
    by_tag: Dict[str, Set[str]] = field(default_factory=dict)  # tag -> document_ids
    by_project: Dict[str, Set[str]] = field(default_factory=dict)  # project_id -> document_ids
    
    def add_document(self, document: DocumentEntity):
        """Add document to index"""
        self.documents[document.id] = document
        self.by_path[document.path] = document.id
        
        # Update category index
        if document.category not in self.by_category:
            self.by_category[document.category] = set()
        self.by_category[document.category].add(document.id)
        
        # Update type index
        if document.type not in self.by_type:
            self.by_type[document.type] = set()
        self.by_type[document.type].add(document.id)
        
        # Update tag index
        for tag in document.tags:
            if tag not in self.by_tag:
                self.by_tag[tag] = set()
            self.by_tag[tag].add(document.id)
        
        # Update project index
        if document.project_id:
            if document.project_id not in self.by_project:
                self.by_project[document.project_id] = set()
            self.by_project[document.project_id].add(document.id)
    
    def remove_document(self, document_id: str):
        """Remove document from index"""
        if document_id not in self.documents:
            return
        
        document = self.documents[document_id]
        
        # Remove from path index
        if document.path in self.by_path:
            del self.by_path[document.path]
        
        # Remove from category index
        if document.category in self.by_category:
            self.by_category[document.category].discard(document_id)
            if not self.by_category[document.category]:
                del self.by_category[document.category]
        
        # Remove from type index
        if document.type in self.by_type:
            self.by_type[document.type].discard(document_id)
            if not self.by_type[document.type]:
                del self.by_type[document.type]
        
        # Remove from tag index
        for tag in document.tags:
            if tag in self.by_tag:
                self.by_tag[tag].discard(document_id)
                if not self.by_tag[tag]:
                    del self.by_tag[tag]
        
        # Remove from project index
        if document.project_id and document.project_id in self.by_project:
            self.by_project[document.project_id].discard(document_id)
            if not self.by_project[document.project_id]:
                del self.by_project[document.project_id]
        
        # Remove document
        del self.documents[document_id]
    
    def find_by_path(self, path: str) -> Optional[DocumentEntity]:
        """Find document by path"""
        doc_id = self.by_path.get(path)
        return self.documents.get(doc_id) if doc_id else None
    
    def find_by_category(self, category: DocumentCategory) -> List[DocumentEntity]:
        """Find documents by category"""
        doc_ids = self.by_category.get(category, set())
        return [self.documents[doc_id] for doc_id in doc_ids if doc_id in self.documents]
    
    def find_by_tag(self, tag: str) -> List[DocumentEntity]:
        """Find documents by tag"""
        doc_ids = self.by_tag.get(tag, set())
        return [self.documents[doc_id] for doc_id in doc_ids if doc_id in self.documents]
    
    def find_by_project(self, project_id: str) -> List[DocumentEntity]:
        """Find documents by project"""
        doc_ids = self.by_project.get(project_id, set())
        return [self.documents[doc_id] for doc_id in doc_ids if doc_id in self.documents] 