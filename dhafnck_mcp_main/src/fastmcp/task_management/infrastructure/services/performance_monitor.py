"""
Performance Monitor for Rule Orchestration Platform

This module provides comprehensive performance monitoring and analysis tools for
the caching system, including real-time metrics, benchmarking, and optimization
recommendations.

Author: Coding Agent
Date: 2025-01-27
Task: 20250628006 - Phase 5: Performance Optimization & Caching
"""

import asyncio
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import logging
from datetime import datetime, timedelta
from collections import deque, defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PerformanceSnapshot:
    """Point-in-time performance metrics snapshot"""
    timestamp: float
    hit_rate: float
    miss_rate: float
    average_response_time_ms: float
    operations_per_second: float
    memory_usage_mb: float
    cache_size: int
    eviction_count: int


@dataclass
class BenchmarkConfig:
    """Configuration for performance benchmarks"""
    num_operations: int = 1000
    concurrent_operations: int = 10
    data_size_bytes: int = 1024
    test_duration_seconds: int = 60
    warmup_operations: int = 100
    include_stress_test: bool = True
    include_memory_test: bool = True
    include_concurrency_test: bool = True


@dataclass
class BenchmarkResult:
    """Comprehensive benchmark results"""
    config: BenchmarkConfig
    start_time: float
    end_time: float
    
    # Basic performance metrics
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    operations_per_second: float = 0.0
    
    # Response time metrics
    average_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    
    # Cache metrics
    final_hit_rate: float = 0.0
    final_cache_size: int = 0
    memory_usage_mb: float = 0.0
    eviction_count: int = 0
    
    # Concurrency metrics
    max_concurrent_operations: int = 0
    concurrent_performance_degradation: float = 0.0
    
    # Error metrics
    error_rate: float = 0.0
    timeout_count: int = 0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)


class PerformanceMonitor:
    """Real-time performance monitoring for cache system"""
    
    def __init__(self, cache_manager, monitoring_interval: float = 1.0, history_size: int = 3600):
        self.cache_manager = cache_manager
        self.monitoring_interval = monitoring_interval
        self.history_size = history_size
        
        # Performance history
        self.performance_history: deque[PerformanceSnapshot] = deque(maxlen=history_size)
        self.alert_thresholds = {
            "hit_rate_min": 0.7,
            "response_time_max_ms": 100.0,
            "memory_usage_max_mb": 1024.0,
            "error_rate_max": 0.05
        }
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.alert_callbacks: List[Callable] = []
        
        # Performance tracking
        self.operation_times: deque[float] = deque(maxlen=1000)
        self.error_count = 0
        self.last_snapshot_time = time.time()
        
        logger.info("Performance monitor initialized")
    
    async def start_monitoring(self):
        """Start real-time performance monitoring"""
        if self.monitoring_active:
            logger.warning("Performance monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        try:
            while self.monitoring_active:
                await self._capture_snapshot()
                await self._check_alerts()
                await asyncio.sleep(self.monitoring_interval)
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
    
    async def _capture_snapshot(self):
        """Capture current performance snapshot"""
        try:
            metrics = self.cache_manager.get_performance_metrics()
            
            snapshot = PerformanceSnapshot(
                timestamp=time.time(),
                hit_rate=metrics["cache_statistics"]["hit_rate"],
                miss_rate=metrics["cache_statistics"]["miss_rate"],
                average_response_time_ms=metrics["performance_metrics"]["average_response_time_ms"],
                operations_per_second=metrics["performance_metrics"].get("operations_per_second", 0.0),
                memory_usage_mb=metrics["cache_levels"].get("memory_size_bytes", 0) / (1024 * 1024),
                cache_size=metrics["cache_levels"]["memory_entries"],
                eviction_count=metrics["eviction_statistics"]["total_evictions"]
            )
            
            self.performance_history.append(snapshot)
            
        except Exception as e:
            logger.error(f"Failed to capture performance snapshot: {e}")
    
    async def _check_alerts(self):
        """Check for performance alerts"""
        if not self.performance_history:
            return
        
        latest = self.performance_history[-1]
        alerts = []
        
        # Check hit rate
        if latest.hit_rate < self.alert_thresholds["hit_rate_min"]:
            alerts.append(f"Low hit rate: {latest.hit_rate:.2%}")
        
        # Check response time
        if latest.average_response_time_ms > self.alert_thresholds["response_time_max_ms"]:
            alerts.append(f"High response time: {latest.average_response_time_ms:.2f}ms")
        
        # Check memory usage
        if latest.memory_usage_mb > self.alert_thresholds["memory_usage_max_mb"]:
            alerts.append(f"High memory usage: {latest.memory_usage_mb:.2f}MB")
        
        # Trigger alert callbacks
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    await callback(alert, latest)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    def get_performance_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for specified time window"""
        cutoff_time = time.time() - (time_window_minutes * 60)
        recent_snapshots = [s for s in self.performance_history if s.timestamp >= cutoff_time]
        
        if not recent_snapshots:
            return {"error": "No data available for specified time window"}
        
        # Calculate averages
        avg_hit_rate = sum(s.hit_rate for s in recent_snapshots) / len(recent_snapshots)
        avg_response_time = sum(s.average_response_time_ms for s in recent_snapshots) / len(recent_snapshots)
        avg_ops_per_sec = sum(s.operations_per_second for s in recent_snapshots) / len(recent_snapshots)
        avg_memory_usage = sum(s.memory_usage_mb for s in recent_snapshots) / len(recent_snapshots)
        
        # Calculate trends
        if len(recent_snapshots) >= 2:
            hit_rate_trend = recent_snapshots[-1].hit_rate - recent_snapshots[0].hit_rate
            response_time_trend = recent_snapshots[-1].average_response_time_ms - recent_snapshots[0].average_response_time_ms
        else:
            hit_rate_trend = 0.0
            response_time_trend = 0.0
        
        return {
            "time_window_minutes": time_window_minutes,
            "data_points": len(recent_snapshots),
            "averages": {
                "hit_rate": avg_hit_rate,
                "response_time_ms": avg_response_time,
                "operations_per_second": avg_ops_per_sec,
                "memory_usage_mb": avg_memory_usage
            },
            "trends": {
                "hit_rate_change": hit_rate_trend,
                "response_time_change_ms": response_time_trend
            },
            "current": {
                "hit_rate": recent_snapshots[-1].hit_rate,
                "response_time_ms": recent_snapshots[-1].average_response_time_ms,
                "cache_size": recent_snapshots[-1].cache_size,
                "memory_usage_mb": recent_snapshots[-1].memory_usage_mb
            }
        }
    
    def export_performance_data(self, file_path: Path, format: str = "json") -> bool:
        """Export performance history to file"""
        try:
            data = [
                {
                    "timestamp": s.timestamp,
                    "datetime": datetime.fromtimestamp(s.timestamp).isoformat(),
                    "hit_rate": s.hit_rate,
                    "miss_rate": s.miss_rate,
                    "average_response_time_ms": s.average_response_time_ms,
                    "operations_per_second": s.operations_per_second,
                    "memory_usage_mb": s.memory_usage_mb,
                    "cache_size": s.cache_size,
                    "eviction_count": s.eviction_count
                }
                for s in self.performance_history
            ]
            
            if format.lower() == "json":
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Performance data exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export performance data: {e}")
            return False


class CacheBenchmark:
    """Comprehensive cache performance benchmarking"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.response_times: List[float] = []
        
    async def run_basic_benchmark(self, num_operations: int = 1000) -> Dict[str, Any]:
        """Run basic performance benchmark"""
        logger.info(f"Starting basic benchmark with {num_operations} operations")
        
        start_time = time.time()
        
        # Test data
        test_data = {f"test_key_{i}": f"test_content_{i}" * 100 for i in range(num_operations)}
        
        # Benchmark put operations
        put_start = time.time()
        put_success = 0
        for key, content in test_data.items():
            if await self.cache_manager.put(key, content):
                put_success += 1
        put_time = time.time() - put_start
        
        # Benchmark get operations
        get_start = time.time()
        get_success = 0
        for key in test_data.keys():
            if await self.cache_manager.get(key) is not None:
                get_success += 1
        get_time = time.time() - get_start
        
        total_time = time.time() - start_time
        
        # Get final metrics
        final_metrics = self.cache_manager.get_performance_metrics()
        
        benchmark_results = {
            "configuration": {
                "num_operations": num_operations,
                "data_size_per_item": 100 * len(f"test_content_0")
            },
            "performance": {
                "total_operations": num_operations * 2,
                "total_time_seconds": total_time,
                "operations_per_second": (num_operations * 2) / total_time,
                "put_operations_per_second": num_operations / put_time,
                "get_operations_per_second": num_operations / get_time,
                "put_success_rate": put_success / num_operations,
                "get_success_rate": get_success / num_operations
            },
            "timing": {
                "average_put_time_ms": (put_time / num_operations) * 1000,
                "average_get_time_ms": (get_time / num_operations) * 1000,
                "total_put_time_seconds": put_time,
                "total_get_time_seconds": get_time
            },
            "cache_metrics": {
                "final_hit_rate": final_metrics["cache_statistics"]["hit_rate"],
                "final_cache_size": final_metrics["cache_levels"]["memory_entries"],
                "memory_usage_mb": final_metrics["cache_levels"].get("memory_size_bytes", 0) / (1024 * 1024),
                "total_evictions": final_metrics["eviction_statistics"]["total_evictions"]
            }
        }
        
        # Generate recommendations
        recommendations = []
        if benchmark_results["performance"]["operations_per_second"] < 1000:
            recommendations.append("Low throughput detected - consider performance optimizations")
        if benchmark_results["cache_metrics"]["final_hit_rate"] < 0.8:
            recommendations.append("Low hit rate - consider increasing cache size or adjusting TTL")
        if benchmark_results["performance"]["put_success_rate"] < 0.95:
            recommendations.append("High put failure rate - investigate cache capacity issues")
        
        benchmark_results["recommendations"] = recommendations
        
        logger.info(f"Benchmark completed: {benchmark_results['performance']['operations_per_second']:.2f} ops/sec")
        
        # Clean up test data
        for key in test_data.keys():
            await self.cache_manager.invalidate(key)
        
        return benchmark_results 