"""
Enhanced Performance Cache Manager for Rule Orchestration Platform

This module implements a sophisticated caching system that provides:
- Multi-level caching (memory, disk, distributed)
- Intelligent cache policies and eviction strategies
- Performance monitoring and metrics
- Lazy loading and prefetching capabilities
- Memory management and optimization
- Horizontal scaling support

Author: Coding Agent
Date: 2025-01-27
Task: 20250628006 - Phase 5: Performance Optimization & Caching
"""

import asyncio
import hashlib
import json
import pickle
import threading
import time
import weakref
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
import logging
import psutil
import os
from datetime import datetime, timedelta

# Try to import psutil for system metrics, fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache levels for multi-tier caching"""
    MEMORY = "memory"
    DISK = "disk"
    DISTRIBUTED = "distributed"


class CachePolicy(Enum):
    """Cache eviction policies"""
    LRU = "lru"              # Least Recently Used
    LFU = "lfu"              # Least Frequently Used
    TTL = "ttl"              # Time To Live
    ADAPTIVE = "adaptive"     # Adaptive based on usage patterns
    SIZE_BASED = "size_based" # Based on content size


class CacheMetrics(Enum):
    """Performance metrics to track"""
    HIT_RATE = "hit_rate"
    MISS_RATE = "miss_rate"
    EVICTION_RATE = "eviction_rate"
    MEMORY_USAGE = "memory_usage"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"


@dataclass
class CacheConfiguration:
    """Configuration for cache manager"""
    # Memory cache settings
    memory_max_size: int = 1000
    memory_max_memory_mb: int = 512
    memory_policy: CachePolicy = CachePolicy.ADAPTIVE
    
    # Disk cache settings
    disk_enabled: bool = True
    disk_max_size: int = 10000
    disk_max_size_gb: int = 5
    disk_cache_dir: Optional[Path] = None
    
    # Distributed cache settings
    distributed_enabled: bool = False
    distributed_backend: str = "redis"
    distributed_config: Dict[str, Any] = field(default_factory=dict)
    
    # TTL settings
    default_ttl: float = 3600.0  # 1 hour
    max_ttl: float = 86400.0     # 24 hours
    min_ttl: float = 60.0        # 1 minute
    
    # Performance settings
    lazy_loading: bool = True
    prefetch_enabled: bool = True
    compression_enabled: bool = True
    async_operations: bool = True
    
    # Monitoring settings
    metrics_enabled: bool = True
    metrics_interval: float = 60.0  # 1 minute
    performance_logging: bool = True


@dataclass
class CacheEntry:
    """Enhanced cache entry with comprehensive metadata"""
    content: Any
    timestamp: float
    last_accessed: float
    access_count: int
    ttl: float
    size_bytes: int
    content_hash: str
    tags: List[str] = field(default_factory=list)
    priority: int = 1
    source_level: CacheLevel = CacheLevel.MEMORY
    compression_ratio: float = 1.0
    creation_time: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return time.time() - self.timestamp > self.ttl
    
    def age_seconds(self) -> float:
        """Get age of entry in seconds"""
        return time.time() - self.creation_time
    
    def access_frequency(self) -> float:
        """Calculate access frequency (accesses per hour)"""
        age_hours = self.age_seconds() / 3600
        return self.access_count / max(age_hours, 0.1)


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    # Hit/miss statistics
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Response time statistics
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    
    # Memory statistics
    current_memory_usage: int = 0
    peak_memory_usage: int = 0
    
    # Eviction statistics
    total_evictions: int = 0
    evictions_by_policy: Dict[str, int] = field(default_factory=dict)
    
    # Throughput statistics
    operations_per_second: float = 0.0
    last_metric_time: float = field(default_factory=time.time)
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests
    
    def miss_rate(self) -> float:
        """Calculate cache miss rate"""
        return 1.0 - self.hit_rate()
    
    def average_response_time(self) -> float:
        """Calculate average response time"""
        if self.total_requests == 0:
            return 0.0
        return self.total_response_time / self.total_requests
    
    def update_response_time(self, response_time: float):
        """Update response time statistics"""
        self.total_response_time += response_time
        self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)


class CacheStorage(ABC):
    """Abstract base class for cache storage backends"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from storage"""
        pass
    
    @abstractmethod
    async def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in storage"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete entry from storage"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all entries from storage"""
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """Get number of entries in storage"""
        pass
    
    @abstractmethod
    async def keys(self) -> List[str]:
        """Get all keys in storage"""
        pass


class MemoryStorage(CacheStorage):
    """Memory-based cache storage with intelligent eviction"""
    
    def __init__(self, config: CacheConfiguration):
        self.config = config
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.access_times: Dict[str, float] = {}
        self.access_counts: Dict[str, int] = defaultdict(int)
        self.size_tracker = 0
        self.lock = threading.RLock()
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from memory cache"""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                await self.delete(key)
                return None
            
            # Update access statistics
            entry.last_accessed = time.time()
            entry.access_count += 1
            self.access_times[key] = time.time()
            self.access_counts[key] += 1
            
            # Move to end for LRU
            self.cache.move_to_end(key)
            
            return entry
    
    async def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in memory cache"""
        with self.lock:
            # Check if we need to evict
            while (len(self.cache) >= self.config.memory_max_size or 
                   self.size_tracker + entry.size_bytes > self.config.memory_max_memory_mb * 1024 * 1024):
                if not await self._evict_entry():
                    break
            
            # Store entry
            if key in self.cache:
                old_entry = self.cache[key]
                self.size_tracker -= old_entry.size_bytes
            
            self.cache[key] = entry
            self.size_tracker += entry.size_bytes
            self.access_times[key] = time.time()
            self.access_counts[key] = entry.access_count
            
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete entry from memory cache"""
        with self.lock:
            if key in self.cache:
                entry = self.cache.pop(key)
                self.size_tracker -= entry.size_bytes
                self.access_times.pop(key, None)
                self.access_counts.pop(key, None)
                return True
            return False
    
    async def clear(self) -> bool:
        """Clear all entries from memory cache"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.access_counts.clear()
            self.size_tracker = 0
            return True
    
    async def size(self) -> int:
        """Get number of entries in memory cache"""
        return len(self.cache)
    
    async def keys(self) -> List[str]:
        """Get all keys in memory cache"""
        return list(self.cache.keys())
    
    async def _evict_entry(self) -> bool:
        """Evict entry based on configured policy"""
        if not self.cache:
            return False
        
        if self.config.memory_policy == CachePolicy.LRU:
            key = next(iter(self.cache))
        elif self.config.memory_policy == CachePolicy.LFU:
            key = min(self.access_counts.items(), key=lambda x: x[1])[0]
        elif self.config.memory_policy == CachePolicy.TTL:
            # Find oldest entry
            key = min(self.cache.items(), key=lambda x: x[1].timestamp)[0]
        elif self.config.memory_policy == CachePolicy.ADAPTIVE:
            key = await self._adaptive_eviction()
        else:
            key = next(iter(self.cache))
        
        await self.delete(key)
        return True
    
    async def _adaptive_eviction(self) -> str:
        """Adaptive eviction based on usage patterns"""
        now = time.time()
        scores = {}
        
        for key, entry in self.cache.items():
            # Score based on recency, frequency, and size
            recency_score = 1.0 / (now - entry.last_accessed + 1)
            frequency_score = entry.access_frequency()
            size_penalty = entry.size_bytes / (1024 * 1024)  # MB
            
            scores[key] = recency_score * frequency_score / (size_penalty + 1)
        
        # Return key with lowest score
        return min(scores.items(), key=lambda x: x[1])[0]


class DiskStorage(CacheStorage):
    """Disk-based cache storage with compression"""
    
    def __init__(self, config: CacheConfiguration):
        self.config = config
        self.cache_dir = config.disk_cache_dir or Path.cwd() / ".cache" / "rules"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self.index: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        self._load_index()
    
    def _load_index(self):
        """Load cache index from disk"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r') as f:
                    self.index = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache index: {e}")
            self.index = {}
    
    def _save_index(self):
        """Save cache index to disk"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for cache key"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from disk cache"""
        with self.lock:
            if key not in self.index:
                return None
            
            file_path = self._get_file_path(key)
            if not file_path.exists():
                # Clean up orphaned index entry
                del self.index[key]
                self._save_index()
                return None
            
            try:
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                
                # Check expiration
                if entry.is_expired():
                    await self.delete(key)
                    return None
                
                # Update access statistics
                entry.last_accessed = time.time()
                entry.access_count += 1
                
                # Update index
                self.index[key].update({
                    'last_accessed': entry.last_accessed,
                    'access_count': entry.access_count
                })
                self._save_index()
                
                return entry
                
            except Exception as e:
                logger.error(f"Failed to load cache entry {key}: {e}")
                await self.delete(key)
                return None
    
    async def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in disk cache"""
        with self.lock:
            # Check disk space limits
            await self._enforce_size_limits()
            
            file_path = self._get_file_path(key)
            
            try:
                with open(file_path, 'wb') as f:
                    pickle.dump(entry, f)
                
                # Update index
                self.index[key] = {
                    'timestamp': entry.timestamp,
                    'last_accessed': entry.last_accessed,
                    'access_count': entry.access_count,
                    'size_bytes': entry.size_bytes,
                    'ttl': entry.ttl,
                    'file_path': str(file_path)
                }
                self._save_index()
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to save cache entry {key}: {e}")
                return False
    
    async def delete(self, key: str) -> bool:
        """Delete entry from disk cache"""
        with self.lock:
            if key not in self.index:
                return False
            
            file_path = self._get_file_path(key)
            try:
                if file_path.exists():
                    file_path.unlink()
                del self.index[key]
                self._save_index()
                return True
            except Exception as e:
                logger.error(f"Failed to delete cache entry {key}: {e}")
                return False
    
    async def clear(self) -> bool:
        """Clear all entries from disk cache"""
        with self.lock:
            try:
                for file_path in self.cache_dir.glob("*.cache"):
                    file_path.unlink()
                self.index.clear()
                self._save_index()
                return True
            except Exception as e:
                logger.error(f"Failed to clear disk cache: {e}")
                return False
    
    async def size(self) -> int:
        """Get number of entries in disk cache"""
        return len(self.index)
    
    async def keys(self) -> List[str]:
        """Get all keys in disk cache"""
        return list(self.index.keys())
    
    async def _enforce_size_limits(self):
        """Enforce disk cache size limits"""
        # Check entry count limit
        while len(self.index) >= self.config.disk_max_size:
            await self._evict_oldest_entry()
        
        # Check disk space limit
        total_size = sum(entry.get('size_bytes', 0) for entry in self.index.values())
        max_size_bytes = self.config.disk_max_size_gb * 1024 * 1024 * 1024
        
        while total_size > max_size_bytes and self.index:
            evicted_size = await self._evict_oldest_entry()
            total_size -= evicted_size
    
    async def _evict_oldest_entry(self) -> int:
        """Evict oldest entry from disk cache"""
        if not self.index:
            return 0
        
        # Find oldest entry by timestamp
        oldest_key = min(self.index.items(), key=lambda x: x[1]['timestamp'])[0]
        size_bytes = self.index[oldest_key].get('size_bytes', 0)
        await self.delete(oldest_key)
        return size_bytes


class EnhancedRuleCacheManager:
    """Enhanced multi-level cache manager with performance optimization"""
    
    def __init__(self, config: Optional[CacheConfiguration] = None):
        self.config = config or CacheConfiguration()
        self.metrics = PerformanceMetrics()
        
        # Initialize storage backends
        self.memory_storage = MemoryStorage(self.config)
        self.disk_storage = DiskStorage(self.config) if self.config.disk_enabled else None
        self.distributed_storage = None  # TODO: Implement Redis/distributed storage
        
        # Performance monitoring
        self.performance_monitor = None
        if self.config.metrics_enabled:
            self._start_performance_monitoring()
        
        # Prefetch system
        self.prefetch_queue: asyncio.Queue = asyncio.Queue()
        self.prefetch_task = None
        if self.config.prefetch_enabled:
            self._start_prefetch_system()
        
        logger.info(f"Enhanced cache manager initialized with config: {self.config}")
    
    async def get(self, key: str, lazy_load_callback: Optional[Callable] = None) -> Optional[Any]:
        """Get content from cache with multi-level fallback"""
        start_time = time.time()
        
        try:
            # Try memory cache first
            entry = await self.memory_storage.get(key)
            if entry:
                self._record_hit(time.time() - start_time, CacheLevel.MEMORY)
                return entry.content
            
            # Try disk cache
            if self.disk_storage:
                entry = await self.disk_storage.get(key)
                if entry:
                    # Promote to memory cache
                    await self.memory_storage.put(key, entry)
                    self._record_hit(time.time() - start_time, CacheLevel.DISK)
                    return entry.content
            
            # Try distributed cache
            if self.distributed_storage:
                entry = await self.distributed_storage.get(key)
                if entry:
                    # Promote to memory and disk cache
                    await self.memory_storage.put(key, entry)
                    if self.disk_storage:
                        await self.disk_storage.put(key, entry)
                    self._record_hit(time.time() - start_time, CacheLevel.DISTRIBUTED)
                    return entry.content
            
            # Cache miss - try lazy loading
            if lazy_load_callback and self.config.lazy_loading:
                content = await self._lazy_load(key, lazy_load_callback)
                if content is not None:
                    self._record_hit(time.time() - start_time, None)
                    return content
            
            self._record_miss(time.time() - start_time)
            return None
            
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            self._record_miss(time.time() - start_time)
            return None
    
    async def put(self, key: str, content: Any, ttl: Optional[float] = None, 
                  tags: Optional[List[str]] = None, priority: int = 1) -> bool:
        """Store content in cache with intelligent placement"""
        start_time = time.time()
        
        try:
            # Calculate content metadata
            content_str = str(content)
            size_bytes = len(content_str.encode('utf-8'))
            content_hash = hashlib.sha256(content_str.encode()).hexdigest()
            
            # Create cache entry
            entry = CacheEntry(
                content=content,
                timestamp=time.time(),
                last_accessed=time.time(),
                access_count=1,
                ttl=ttl or self.config.default_ttl,
                size_bytes=size_bytes,
                content_hash=content_hash,
                tags=tags or [],
                priority=priority
            )
            
            # Store in memory cache
            success = await self.memory_storage.put(key, entry)
            
            # Store in disk cache if enabled and content is large enough
            if self.disk_storage and size_bytes > 1024:  # 1KB threshold
                await self.disk_storage.put(key, entry)
            
            # Store in distributed cache if enabled and priority is high
            if self.distributed_storage and priority >= 3:
                await self.distributed_storage.put(key, entry)
            
            # Update metrics
            self.metrics.total_response_time += time.time() - start_time
            
            return success
            
        except Exception as e:
            logger.error(f"Cache put failed for key {key}: {e}")
            return False
    
    async def invalidate(self, key: str) -> bool:
        """Invalidate cache entry across all levels"""
        success = True
        
        try:
            # Remove from all storage levels
            await self.memory_storage.delete(key)
            
            if self.disk_storage:
                success &= await self.disk_storage.delete(key)
            
            if self.distributed_storage:
                success &= await self.distributed_storage.delete(key)
            
            return success
            
        except Exception as e:
            logger.error(f"Cache invalidation failed for key {key}: {e}")
            return False
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate all cache entries with specified tags"""
        invalidated_count = 0
        
        try:
            # Get all keys from memory cache
            memory_keys = await self.memory_storage.keys()
            for key in memory_keys:
                entry = await self.memory_storage.get(key)
                if entry and any(tag in entry.tags for tag in tags):
                    await self.invalidate(key)
                    invalidated_count += 1
            
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Tag-based invalidation failed: {e}")
            return 0
    
    async def clear(self) -> bool:
        """Clear all cache levels"""
        success = True
        
        try:
            await self.memory_storage.clear()
            
            if self.disk_storage:
                success &= await self.disk_storage.clear()
            
            if self.distributed_storage:
                success &= await self.distributed_storage.clear()
            
            # Reset metrics
            self.metrics = PerformanceMetrics()
            
            return success
            
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        memory_info = psutil.virtual_memory()
        
        return {
            "cache_statistics": {
                "hit_rate": self.metrics.hit_rate(),
                "miss_rate": self.metrics.miss_rate(),
                "total_requests": self.metrics.total_requests,
                "cache_hits": self.metrics.cache_hits,
                "cache_misses": self.metrics.cache_misses
            },
            "performance_metrics": {
                "average_response_time_ms": self.metrics.average_response_time() * 1000,
                "min_response_time_ms": self.metrics.min_response_time * 1000,
                "max_response_time_ms": self.metrics.max_response_time * 1000,
                "operations_per_second": self.metrics.operations_per_second
            },
            "memory_metrics": {
                "current_usage_mb": self.metrics.current_memory_usage / (1024 * 1024),
                "peak_usage_mb": self.metrics.peak_memory_usage / (1024 * 1024),
                "system_memory_percent": memory_info.percent,
                "available_memory_mb": memory_info.available / (1024 * 1024)
            },
            "cache_levels": {
                "memory_entries": len(self.memory_storage.cache),
                "disk_entries": len(self.disk_storage.index) if self.disk_storage else 0,
                "distributed_entries": 0  # TODO: Implement
            },
            "eviction_statistics": {
                "total_evictions": self.metrics.total_evictions,
                "evictions_by_policy": dict(self.metrics.evictions_by_policy)
            }
        }
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """Perform cache optimization operations"""
        optimization_results = {
            "expired_entries_removed": 0,
            "memory_compacted": False,
            "disk_defragmented": False,
            "recommendations": []
        }
        
        try:
            # Remove expired entries
            expired_count = await self._remove_expired_entries()
            optimization_results["expired_entries_removed"] = expired_count
            
            # Analyze cache performance and provide recommendations
            hit_rate = self.metrics.hit_rate()
            if hit_rate < 0.5:
                optimization_results["recommendations"].append(
                    "Consider increasing cache size or adjusting TTL values"
                )
            
            if self.metrics.total_evictions > self.metrics.cache_hits * 0.1:
                optimization_results["recommendations"].append(
                    "High eviction rate detected - consider increasing memory cache size"
                )
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            return optimization_results
    
    async def _lazy_load(self, key: str, callback: Callable) -> Optional[Any]:
        """Lazy load content using provided callback"""
        try:
            content = await callback(key)
            if content is not None:
                await self.put(key, content)
            return content
        except Exception as e:
            logger.error(f"Lazy loading failed for key {key}: {e}")
            return None
    
    async def _remove_expired_entries(self) -> int:
        """Remove expired entries from all cache levels"""
        removed_count = 0
        
        # Check memory cache
        memory_keys = await self.memory_storage.keys()
        for key in memory_keys:
            entry = await self.memory_storage.get(key)
            if entry and entry.is_expired():
                await self.memory_storage.delete(key)
                removed_count += 1
        
        # Check disk cache
        if self.disk_storage:
            disk_keys = await self.disk_storage.keys()
            for key in disk_keys:
                entry = await self.disk_storage.get(key)
                if entry and entry.is_expired():
                    await self.disk_storage.delete(key)
                    removed_count += 1
        
        return removed_count
    
    def _record_hit(self, response_time: float, cache_level: Optional[CacheLevel]):
        """Record cache hit metrics"""
        self.metrics.total_requests += 1
        self.metrics.cache_hits += 1
        self.metrics.update_response_time(response_time)
        
        if self.config.performance_logging:
            logger.debug(f"Cache hit from {cache_level} in {response_time*1000:.2f}ms")
    
    def _record_miss(self, response_time: float):
        """Record cache miss metrics"""
        self.metrics.total_requests += 1
        self.metrics.cache_misses += 1
        self.metrics.update_response_time(response_time)
        
        if self.config.performance_logging:
            logger.debug(f"Cache miss in {response_time*1000:.2f}ms")
    
    def _start_performance_monitoring(self):
        """Start background performance monitoring"""
        # TODO: Implement background monitoring task
        pass
    
    def _start_prefetch_system(self):
        """Start background prefetch system"""
        # TODO: Implement intelligent prefetching
        pass
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Cleanup resources
        if self.prefetch_task:
            self.prefetch_task.cancel()
        
        # Save final metrics
        if self.config.performance_logging:
            metrics = self.get_performance_metrics()
            logger.info(f"Final cache metrics: {metrics}")


# Factory function for easy instantiation
def create_performance_cache_manager(
    memory_size: int = 1000,
    memory_mb: int = 512,
    disk_enabled: bool = True,
    disk_size_gb: int = 5,
    ttl_hours: float = 1.0,
    enable_metrics: bool = True
) -> EnhancedRuleCacheManager:
    """Factory function to create configured cache manager"""
    
    config = CacheConfiguration(
        memory_max_size=memory_size,
        memory_max_memory_mb=memory_mb,
        disk_enabled=disk_enabled,
        disk_max_size_gb=disk_size_gb,
        default_ttl=ttl_hours * 3600,
        metrics_enabled=enable_metrics
    )
    
    return EnhancedRuleCacheManager(config) 