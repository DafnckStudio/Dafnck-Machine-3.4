"""
Performance Load Testing Framework for Rule Orchestration Platform

This module provides comprehensive performance and load testing capabilities for the
DhafnckMCP rule orchestration platform, building on existing performance monitoring
infrastructure to deliver enterprise-scale performance validation.

Author: Performance Load Tester Agent
Date: 2025-01-27
Task: 20250628008.002 - Performance and Load Testing
"""

import asyncio
import time
import threading
import psutil
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
from pathlib import Path
import json
import logging
from datetime import datetime, timedelta
from collections import deque, defaultdict
import sys
import os

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from src.fastmcp.task_management.infrastructure.services.performance_monitor import (
        PerformanceMonitor, BenchmarkConfig, BenchmarkResult, PerformanceSnapshot
    )
    from src.fastmcp.task_management.infrastructure.services.performance_cache_manager import (
        PerformanceMetrics
    )
except ImportError:
    # Fallback for testing without full infrastructure
    PerformanceMonitor = None
    BenchmarkConfig = None
    BenchmarkResult = None
    PerformanceSnapshot = None
    PerformanceMetrics = None

logger = logging.getLogger(__name__)


class LoadTestType(Enum):
    """Types of load tests supported"""
    BASELINE = "baseline"
    LOAD = "load"
    STRESS = "stress"
    SOAK = "soak"
    SPIKE = "spike"
    VOLUME = "volume"
    CONCURRENCY = "concurrency"


class LoadPattern(Enum):
    """Load generation patterns"""
    CONSTANT = "constant"
    RAMP_UP = "ramp_up"
    STEP_UP = "step_up"
    SPIKE = "spike"
    WAVE = "wave"


@dataclass
class LoadTestConfig:
    """Configuration for load testing scenarios"""
    test_type: LoadTestType
    test_name: str
    description: str
    
    # Load parameters
    target_rps: int = 100
    concurrent_users: int = 10
    test_duration_seconds: int = 300
    ramp_up_duration_seconds: int = 60
    
    # Load pattern
    load_pattern: LoadPattern = LoadPattern.CONSTANT
    spike_multiplier: float = 2.0
    wave_amplitude: float = 0.5
    
    # Performance criteria
    max_response_time_ms: float = 1000.0
    max_error_rate: float = 0.05
    min_throughput_rps: float = 50.0
    
    # Test configuration
    warmup_requests: int = 50
    cooldown_duration_seconds: int = 30
    think_time_ms: float = 100.0
    
    # Monitoring
    enable_resource_monitoring: bool = True
    monitoring_interval_seconds: float = 1.0
    
    # MCP specific
    mcp_tools_to_test: List[str] = field(default_factory=lambda: [
        "health_check", "get_server_capabilities", "manage_project", 
        "manage_task", "manage_agent", "call_agent"
    ])


@dataclass
class LoadTestResult:
    """Comprehensive load test results"""
    config: LoadTestConfig
    start_time: float
    end_time: float
    test_status: str = "completed"
    
    # Performance metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    actual_rps: float = 0.0
    
    # Response time metrics
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    
    # Error metrics
    error_rate: float = 0.0
    error_types: Dict[str, int] = field(default_factory=dict)
    timeout_count: int = 0
    
    # Resource utilization
    avg_cpu_usage: float = 0.0
    max_cpu_usage: float = 0.0
    avg_memory_usage_mb: float = 0.0
    max_memory_usage_mb: float = 0.0
    
    # MCP specific metrics
    tool_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Test verdict
    passed: bool = False
    failure_reasons: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ResourceMonitor:
    """System resource monitoring during tests"""
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Resource history
        self.cpu_usage_history: List[float] = []
        self.memory_usage_history: List[float] = []
        self.disk_io_history: List[Dict[str, float]] = []
        self.network_io_history: List[Dict[str, float]] = []
        
        # Process monitoring
        try:
            self.process = psutil.Process()
        except Exception:
            self.process = None
        
    async def start_monitoring(self):
        """Start resource monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Resource monitoring started")
    
    async def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Resource monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        try:
            while self.monitoring_active:
                # System-wide metrics
                try:
                    cpu_percent = psutil.cpu_percent(interval=None)
                    memory = psutil.virtual_memory()
                    
                    # Store metrics
                    self.cpu_usage_history.append(cpu_percent)
                    self.memory_usage_history.append(memory.used / (1024 * 1024))  # MB
                    
                except Exception as e:
                    logger.warning(f"Resource monitoring error: {e}")
                
                await asyncio.sleep(self.monitoring_interval)
                
        except asyncio.CancelledError:
            logger.info("Resource monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Resource monitoring error: {e}")
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get resource usage summary"""
        if not self.cpu_usage_history:
            return {"error": "No monitoring data available"}
        
        return {
            "cpu": {
                "avg_usage": statistics.mean(self.cpu_usage_history),
                "max_usage": max(self.cpu_usage_history),
                "min_usage": min(self.cpu_usage_history),
                "samples": len(self.cpu_usage_history)
            },
            "memory": {
                "avg_usage_mb": statistics.mean(self.memory_usage_history),
                "max_usage_mb": max(self.memory_usage_history),
                "min_usage_mb": min(self.memory_usage_history),
                "samples": len(self.memory_usage_history)
            },
            "monitoring_duration_seconds": len(self.cpu_usage_history) * self.monitoring_interval
        }


class LoadGenerator:
    """Generates load according to specified patterns"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.active_workers = 0
        self.request_count = 0
        self.response_times: List[float] = []
        self.errors: List[Dict[str, Any]] = []
        self.start_time = 0.0
        
    async def generate_load(self, target_function: Callable, *args, **kwargs) -> List[Dict[str, Any]]:
        """Generate load according to configuration"""
        logger.info(f"Starting load generation: {self.config.test_name}")
        
        self.start_time = time.time()
        results = []
        
        # Warmup phase
        if self.config.warmup_requests > 0:
            logger.info(f"Warmup phase: {self.config.warmup_requests} requests")
            await self._warmup_phase(target_function, *args, **kwargs)
        
        # Main load generation
        if self.config.load_pattern == LoadPattern.CONSTANT:
            results = await self._constant_load(target_function, *args, **kwargs)
        elif self.config.load_pattern == LoadPattern.RAMP_UP:
            results = await self._ramp_up_load(target_function, *args, **kwargs)
        elif self.config.load_pattern == LoadPattern.SPIKE:
            results = await self._spike_load(target_function, *args, **kwargs)
        elif self.config.load_pattern == LoadPattern.WAVE:
            results = await self._wave_load(target_function, *args, **kwargs)
        else:
            results = await self._constant_load(target_function, *args, **kwargs)
        
        # Cooldown phase
        if self.config.cooldown_duration_seconds > 0:
            logger.info(f"Cooldown phase: {self.config.cooldown_duration_seconds} seconds")
            await asyncio.sleep(self.config.cooldown_duration_seconds)
        
        return results
    
    async def _warmup_phase(self, target_function: Callable, *args, **kwargs):
        """Warmup phase to prepare system"""
        tasks = []
        for i in range(self.config.warmup_requests):
            task = asyncio.create_task(self._execute_request(target_function, *args, **kwargs))
            tasks.append(task)
            
            # Small delay between requests
            await asyncio.sleep(0.1)
        
        # Wait for warmup to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Clear warmup data
        self.response_times.clear()
        self.errors.clear()
        self.request_count = 0
    
    async def _constant_load(self, target_function: Callable, *args, **kwargs) -> List[Dict[str, Any]]:
        """Generate constant load"""
        tasks = []
        request_interval = 1.0 / self.config.target_rps if self.config.target_rps > 0 else 0.1
        
        end_time = time.time() + self.config.test_duration_seconds
        
        while time.time() < end_time:
            if len(tasks) < self.config.concurrent_users:
                task = asyncio.create_task(self._execute_request(target_function, *args, **kwargs))
                tasks.append(task)
            
            # Remove completed tasks
            tasks = [task for task in tasks if not task.done()]
            
            await asyncio.sleep(request_interval)
        
        # Wait for remaining tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        return []
    
    async def _ramp_up_load(self, target_function: Callable, *args, **kwargs) -> List[Dict[str, Any]]:
        """Generate ramping load"""
        ramp_steps = 10
        step_duration = self.config.ramp_up_duration_seconds / ramp_steps
        main_duration = self.config.test_duration_seconds - self.config.ramp_up_duration_seconds
        
        # Ramp up phase
        for step in range(ramp_steps):
            current_users = int((step + 1) * self.config.concurrent_users / ramp_steps)
            current_rps = int((step + 1) * self.config.target_rps / ramp_steps)
            
            logger.info(f"Ramp step {step + 1}/{ramp_steps}: {current_users} users, {current_rps} RPS")
            
            # Generate load for this step
            await self._generate_step_load(target_function, current_users, current_rps, step_duration, *args, **kwargs)
        
        # Sustained load phase
        if main_duration > 0:
            logger.info(f"Sustained load: {self.config.concurrent_users} users, {self.config.target_rps} RPS")
            await self._generate_step_load(
                target_function, 
                self.config.concurrent_users, 
                self.config.target_rps, 
                main_duration, 
                *args, **kwargs
            )
        
        return []
    
    async def _spike_load(self, target_function: Callable, *args, **kwargs) -> List[Dict[str, Any]]:
        """Generate spike load pattern"""
        normal_duration = self.config.test_duration_seconds * 0.4
        spike_duration = self.config.test_duration_seconds * 0.2
        recovery_duration = self.config.test_duration_seconds * 0.4
        
        # Normal load
        logger.info(f"Normal load phase: {normal_duration}s")
        await self._generate_step_load(
            target_function, 
            self.config.concurrent_users, 
            self.config.target_rps, 
            normal_duration, 
            *args, **kwargs
        )
        
        # Spike load
        spike_users = int(self.config.concurrent_users * self.config.spike_multiplier)
        spike_rps = int(self.config.target_rps * self.config.spike_multiplier)
        logger.info(f"Spike load phase: {spike_duration}s, {spike_users} users, {spike_rps} RPS")
        await self._generate_step_load(target_function, spike_users, spike_rps, spike_duration, *args, **kwargs)
        
        # Recovery phase
        logger.info(f"Recovery phase: {recovery_duration}s")
        await self._generate_step_load(
            target_function, 
            self.config.concurrent_users, 
            self.config.target_rps, 
            recovery_duration, 
            *args, **kwargs
        )
        
        return []
    
    async def _wave_load(self, target_function: Callable, *args, **kwargs) -> List[Dict[str, Any]]:
        """Generate wave load pattern"""
        import math
        
        step_duration = 30  # 30 second steps
        steps = int(self.config.test_duration_seconds / step_duration)
        
        for step in range(steps):
            # Calculate wave position (0 to 2*pi over the test duration)
            wave_position = (step / steps) * 2 * math.pi
            wave_factor = 1.0 + self.config.wave_amplitude * math.sin(wave_position)
            
            current_users = int(self.config.concurrent_users * wave_factor)
            current_rps = int(self.config.target_rps * wave_factor)
            
            logger.info(f"Wave step {step + 1}/{steps}: {current_users} users, {current_rps} RPS")
            
            await self._generate_step_load(target_function, current_users, current_rps, step_duration, *args, **kwargs)
        
        return []
    
    async def _generate_step_load(self, target_function: Callable, users: int, rps: int, duration: float, *args, **kwargs):
        """Generate load for a specific step"""
        tasks = []
        request_interval = 1.0 / rps if rps > 0 else 0.1
        end_time = time.time() + duration
        
        while time.time() < end_time:
            if len(tasks) < users:
                task = asyncio.create_task(self._execute_request(target_function, *args, **kwargs))
                tasks.append(task)
            
            # Remove completed tasks
            tasks = [task for task in tasks if not task.done()]
            
            await asyncio.sleep(request_interval)
        
        # Wait for remaining tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_request(self, target_function: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Execute a single request with timing and error handling"""
        start_time = time.time()
        self.active_workers += 1
        
        try:
            # Add think time before request
            if self.config.think_time_ms > 0:
                await asyncio.sleep(self.config.think_time_ms / 1000.0)
            
            # Execute the request
            result = await target_function(*args, **kwargs)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            self.response_times.append(response_time)
            self.request_count += 1
            
            return {
                "success": True,
                "response_time_ms": response_time,
                "result": result,
                "timestamp": end_time
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            error_info = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "response_time_ms": response_time,
                "timestamp": end_time
            }
            
            self.errors.append(error_info)
            self.request_count += 1
            
            return error_info
            
        finally:
            self.active_workers -= 1
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from load generation"""
        if not self.response_times and not self.errors:
            return {"error": "No performance data available"}
        
        total_requests = len(self.response_times) + len(self.errors)
        successful_requests = len(self.response_times)
        failed_requests = len(self.errors)
        
        # Calculate response time statistics
        if self.response_times:
            sorted_times = sorted(self.response_times)
            avg_response_time = statistics.mean(self.response_times)
            min_response_time = min(self.response_times)
            max_response_time = max(self.response_times)
            p50_response_time = sorted_times[int(len(sorted_times) * 0.5)]
            p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]
            p99_response_time = sorted_times[int(len(sorted_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
            p50_response_time = p95_response_time = p99_response_time = 0.0
        
        # Calculate error statistics
        error_types = defaultdict(int)
        for error in self.errors:
            error_types[error.get("error_type", "Unknown")] += 1
        
        # Calculate throughput
        test_duration = time.time() - self.start_time if self.start_time > 0 else 1.0
        actual_rps = total_requests / test_duration
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "error_rate": failed_requests / total_requests if total_requests > 0 else 0.0,
            "actual_rps": actual_rps,
            "response_times": {
                "avg_ms": avg_response_time,
                "min_ms": min_response_time,
                "max_ms": max_response_time,
                "p50_ms": p50_response_time,
                "p95_ms": p95_response_time,
                "p99_ms": p99_response_time
            },
            "error_types": dict(error_types),
            "test_duration_seconds": test_duration
        }


class PerformanceLoadTestingFramework:
    """Main framework for comprehensive performance and load testing"""
    
    def __init__(self):
        self.resource_monitor = ResourceMonitor()
        self.test_results: List[LoadTestResult] = []
        self.baseline_metrics: Optional[Dict[str, Any]] = None
        
    async def run_performance_test_suite(self, mcp_server, test_configs: List[LoadTestConfig]) -> Dict[str, Any]:
        """Run a complete performance test suite"""
        logger.info(f"Starting performance test suite with {len(test_configs)} test configurations")
        
        suite_start_time = time.time()
        suite_results = []
        
        try:
            for i, config in enumerate(test_configs):
                logger.info(f"Running test {i + 1}/{len(test_configs)}: {config.test_name}")
                
                test_result = await self.run_single_performance_test(mcp_server, config)
                suite_results.append(test_result)
                self.test_results.append(test_result)
                
                # Brief pause between tests
                await asyncio.sleep(10)
            
            suite_end_time = time.time()
            
            # Generate suite summary
            suite_summary = self._generate_suite_summary(suite_results, suite_start_time, suite_end_time)
            
            logger.info(f"Performance test suite completed in {suite_end_time - suite_start_time:.2f} seconds")
            
            return suite_summary
            
        except Exception as e:
            logger.error(f"Performance test suite failed: {e}")
            raise
    
    async def run_single_performance_test(self, mcp_server, config: LoadTestConfig) -> LoadTestResult:
        """Run a single performance test"""
        logger.info(f"Starting performance test: {config.test_name}")
        
        # Initialize result object
        result = LoadTestResult(
            config=config,
            start_time=time.time(),
            end_time=0.0
        )
        
        try:
            # Start resource monitoring
            if config.enable_resource_monitoring:
                await self.resource_monitor.start_monitoring()
            
            # Create load generator
            load_generator = LoadGenerator(config)
            
            # Create target function for MCP server testing
            async def mcp_test_function():
                # Test different MCP tools based on configuration
                tool_name = config.mcp_tools_to_test[0] if config.mcp_tools_to_test else "health_check"
                
                if tool_name == "health_check":
                    return await mcp_server._call_tool("health_check", {"random_string": "test"})
                elif tool_name == "get_server_capabilities":
                    return await mcp_server._call_tool("get_server_capabilities", {"random_string": "test"})
                elif tool_name == "manage_project":
                    return await mcp_server._call_tool("manage_project", {
                        "action": "list",
                        "project_id": "test_project"
                    })
                else:
                    # Default to health check
                    return await mcp_server._call_tool("health_check", {"random_string": "test"})
            
            # Generate load
            load_results = await load_generator.generate_load(mcp_test_function)
            
            # Stop resource monitoring
            if config.enable_resource_monitoring:
                await self.resource_monitor.stop_monitoring()
            
            # Collect metrics
            performance_metrics = load_generator.get_performance_metrics()
            resource_metrics = self.resource_monitor.get_resource_summary()
            
            # Populate result
            result.end_time = time.time()
            result.total_requests = performance_metrics["total_requests"]
            result.successful_requests = performance_metrics["successful_requests"]
            result.failed_requests = performance_metrics["failed_requests"]
            result.actual_rps = performance_metrics["actual_rps"]
            result.error_rate = performance_metrics["error_rate"]
            
            # Response time metrics
            result.avg_response_time_ms = performance_metrics["response_times"]["avg_ms"]
            result.min_response_time_ms = performance_metrics["response_times"]["min_ms"]
            result.max_response_time_ms = performance_metrics["response_times"]["max_ms"]
            result.p50_response_time_ms = performance_metrics["response_times"]["p50_ms"]
            result.p95_response_time_ms = performance_metrics["response_times"]["p95_ms"]
            result.p99_response_time_ms = performance_metrics["response_times"]["p99_ms"]
            
            # Resource metrics
            if "cpu" in resource_metrics:
                result.avg_cpu_usage = resource_metrics["cpu"]["avg_usage"]
                result.max_cpu_usage = resource_metrics["cpu"]["max_usage"]
            
            if "memory" in resource_metrics:
                result.avg_memory_usage_mb = resource_metrics["memory"]["avg_usage_mb"]
                result.max_memory_usage_mb = resource_metrics["memory"]["max_usage_mb"]
            
            # Error analysis
            result.error_types = performance_metrics["error_types"]
            
            # Evaluate test success
            result.passed, result.failure_reasons = self._evaluate_test_success(result, config)
            result.recommendations = self._generate_recommendations(result, config)
            
            logger.info(f"Performance test completed: {config.test_name} - {'PASSED' if result.passed else 'FAILED'}")
            
            return result
            
        except Exception as e:
            result.end_time = time.time()
            result.test_status = "failed"
            result.failure_reasons.append(f"Test execution failed: {str(e)}")
            
            logger.error(f"Performance test failed: {config.test_name} - {e}")
            
            # Stop monitoring if it was started
            if config.enable_resource_monitoring:
                try:
                    await self.resource_monitor.stop_monitoring()
                except Exception:
                    pass
            
            return result
    
    def _evaluate_test_success(self, result: LoadTestResult, config: LoadTestConfig) -> Tuple[bool, List[str]]:
        """Evaluate if test passed based on success criteria"""
        failure_reasons = []
        
        # Check response time criteria
        if result.p95_response_time_ms > config.max_response_time_ms:
            failure_reasons.append(
                f"P95 response time ({result.p95_response_time_ms:.2f}ms) exceeds limit ({config.max_response_time_ms}ms)"
            )
        
        # Check error rate criteria
        if result.error_rate > config.max_error_rate:
            failure_reasons.append(
                f"Error rate ({result.error_rate:.2%}) exceeds limit ({config.max_error_rate:.2%})"
            )
        
        # Check throughput criteria
        if result.actual_rps < config.min_throughput_rps:
            failure_reasons.append(
                f"Throughput ({result.actual_rps:.2f} RPS) below minimum ({config.min_throughput_rps} RPS)"
            )
        
        # Check if test completed
        if result.test_status != "completed":
            failure_reasons.append(f"Test did not complete successfully: {result.test_status}")
        
        return len(failure_reasons) == 0, failure_reasons
    
    def _generate_recommendations(self, result: LoadTestResult, config: LoadTestConfig) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Response time recommendations
        if result.p95_response_time_ms > 500:
            recommendations.append("High response times detected - consider implementing caching or optimizing database queries")
        
        if result.max_response_time_ms > result.avg_response_time_ms * 5:
            recommendations.append("High response time variance detected - investigate performance outliers")
        
        # Throughput recommendations
        if result.actual_rps < config.target_rps * 0.8:
            recommendations.append("Low throughput achieved - consider horizontal scaling or performance optimization")
        
        # Error rate recommendations
        if result.error_rate > 0.01:  # 1%
            recommendations.append("Elevated error rate detected - investigate error causes and implement better error handling")
        
        # Resource utilization recommendations
        if result.max_cpu_usage > 80:
            recommendations.append("High CPU usage detected - consider CPU optimization or scaling")
        
        if result.max_memory_usage_mb > 1000:  # 1GB
            recommendations.append("High memory usage detected - investigate memory leaks or optimize memory usage")
        
        # Load pattern specific recommendations
        if config.load_pattern == LoadPattern.SPIKE and result.p95_response_time_ms > config.max_response_time_ms:
            recommendations.append("Poor spike handling - implement auto-scaling or load shedding mechanisms")
        
        return recommendations
    
    def _generate_suite_summary(self, results: List[LoadTestResult], start_time: float, end_time: float) -> Dict[str, Any]:
        """Generate comprehensive test suite summary"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        
        # Calculate overall metrics
        total_requests = sum(r.total_requests for r in results)
        total_errors = sum(r.failed_requests for r in results)
        overall_error_rate = total_errors / total_requests if total_requests > 0 else 0.0
        
        # Response time analysis
        all_avg_times = [r.avg_response_time_ms for r in results if r.avg_response_time_ms > 0]
        all_p95_times = [r.p95_response_time_ms for r in results if r.p95_response_time_ms > 0]
        
        return {
            "suite_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
                "total_duration_seconds": end_time - start_time
            },
            "overall_performance": {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "overall_error_rate": overall_error_rate,
                "avg_response_time_ms": statistics.mean(all_avg_times) if all_avg_times else 0.0,
                "avg_p95_response_time_ms": statistics.mean(all_p95_times) if all_p95_times else 0.0
            },
            "test_results": [
                {
                    "test_name": r.config.test_name,
                    "test_type": r.config.test_type.value,
                    "passed": r.passed,
                    "actual_rps": r.actual_rps,
                    "p95_response_time_ms": r.p95_response_time_ms,
                    "error_rate": r.error_rate,
                    "failure_reasons": r.failure_reasons
                }
                for r in results
            ],
            "recommendations": self._generate_suite_recommendations(results)
        }
    
    def _generate_suite_recommendations(self, results: List[LoadTestResult]) -> List[str]:
        """Generate recommendations for the entire test suite"""
        recommendations = []
        
        # Analyze patterns across all tests
        failed_tests = [r for r in results if not r.passed]
        high_latency_tests = [r for r in results if r.p95_response_time_ms > 1000]
        high_error_tests = [r for r in results if r.error_rate > 0.05]
        
        if len(failed_tests) > len(results) * 0.5:
            recommendations.append("More than 50% of tests failed - system requires significant performance improvements")
        
        if high_latency_tests:
            recommendations.append("Multiple tests show high latency - implement comprehensive performance optimization")
        
        if high_error_tests:
            recommendations.append("Multiple tests show high error rates - improve error handling and system stability")
        
        # Scaling recommendations
        max_rps_achieved = max((r.actual_rps for r in results), default=0)
        if max_rps_achieved < 100:
            recommendations.append("System shows limited scaling capability - consider architectural improvements")
        elif max_rps_achieved < 1000:
            recommendations.append("System ready for Tier 1 scaling (1K RPS) - implement horizontal scaling for higher tiers")
        
        return recommendations


# Predefined test configurations for different scenarios
def get_baseline_test_config() -> LoadTestConfig:
    """Get configuration for baseline performance test"""
    return LoadTestConfig(
        test_type=LoadTestType.BASELINE,
        test_name="Baseline Performance Test",
        description="Establish current system performance baseline",
        target_rps=50,
        concurrent_users=10,
        test_duration_seconds=300,  # 5 minutes
        load_pattern=LoadPattern.CONSTANT,
        max_response_time_ms=1000.0,
        max_error_rate=0.05,
        min_throughput_rps=25.0
    )


def get_load_test_config() -> LoadTestConfig:
    """Get configuration for standard load test"""
    return LoadTestConfig(
        test_type=LoadTestType.LOAD,
        test_name="Standard Load Test",
        description="Test system under expected production load",
        target_rps=200,
        concurrent_users=50,
        test_duration_seconds=600,  # 10 minutes
        ramp_up_duration_seconds=120,
        load_pattern=LoadPattern.RAMP_UP,
        max_response_time_ms=500.0,
        max_error_rate=0.02,
        min_throughput_rps=150.0
    )


def get_stress_test_config() -> LoadTestConfig:
    """Get configuration for stress test"""
    return LoadTestConfig(
        test_type=LoadTestType.STRESS,
        test_name="Stress Test",
        description="Test system beyond normal capacity to find breaking point",
        target_rps=500,
        concurrent_users=200,
        test_duration_seconds=300,  # 5 minutes
        ramp_up_duration_seconds=60,
        load_pattern=LoadPattern.RAMP_UP,
        max_response_time_ms=2000.0,
        max_error_rate=0.10,
        min_throughput_rps=200.0
    )


def get_spike_test_config() -> LoadTestConfig:
    """Get configuration for spike test"""
    return LoadTestConfig(
        test_type=LoadTestType.SPIKE,
        test_name="Spike Test",
        description="Test system response to sudden traffic spikes",
        target_rps=100,
        concurrent_users=25,
        test_duration_seconds=300,  # 5 minutes
        load_pattern=LoadPattern.SPIKE,
        spike_multiplier=5.0,
        max_response_time_ms=1500.0,
        max_error_rate=0.05,
        min_throughput_rps=75.0
    )


def get_soak_test_config() -> LoadTestConfig:
    """Get configuration for soak test"""
    return LoadTestConfig(
        test_type=LoadTestType.SOAK,
        test_name="Soak Test",
        description="Test system stability over extended period",
        target_rps=100,
        concurrent_users=25,
        test_duration_seconds=3600,  # 1 hour
        load_pattern=LoadPattern.CONSTANT,
        max_response_time_ms=800.0,
        max_error_rate=0.02,
        min_throughput_rps=80.0
    )


# Example usage and test runner
async def main():
    """Example usage of the performance testing framework"""
    from tests.test_mvp_server import create_dhafnck_mcp_server
    
    # Create MCP server instance
    mcp_server = create_dhafnck_mcp_server()
    
    # Create test framework
    framework = PerformanceLoadTestingFramework()
    
    # Define test configurations
    test_configs = [
        get_baseline_test_config(),
        get_load_test_config(),
        get_spike_test_config()
    ]
    
    # Run test suite
    try:
        results = await framework.run_performance_test_suite(mcp_server, test_configs)
        
        print("\n" + "="*80)
        print("PERFORMANCE TEST SUITE RESULTS")
        print("="*80)
        print(f"Total Tests: {results['suite_summary']['total_tests']}")
        print(f"Passed: {results['suite_summary']['passed_tests']}")
        print(f"Failed: {results['suite_summary']['failed_tests']}")
        print(f"Success Rate: {results['suite_summary']['success_rate']:.1%}")
        print(f"Total Duration: {results['suite_summary']['total_duration_seconds']:.2f} seconds")
        
        print(f"\nOverall Performance:")
        print(f"Total Requests: {results['overall_performance']['total_requests']}")
        print(f"Error Rate: {results['overall_performance']['overall_error_rate']:.2%}")
        print(f"Avg Response Time: {results['overall_performance']['avg_response_time_ms']:.2f}ms")
        print(f"Avg P95 Response Time: {results['overall_performance']['avg_p95_response_time_ms']:.2f}ms")
        
        if results['recommendations']:
            print(f"\nRecommendations:")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"{i}. {rec}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"Performance test suite failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 