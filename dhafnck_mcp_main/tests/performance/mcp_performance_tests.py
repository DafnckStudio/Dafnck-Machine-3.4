"""
MCP Performance Tests for Rule Orchestration Platform

This module provides MCP tool-specific performance testing capabilities,
testing each MCP tool under various load conditions and measuring tool-specific
performance characteristics.

Author: Performance Load Tester Agent
Date: 2025-01-27
Task: 20250628008.002 - Performance and Load Testing
"""

import asyncio
import time
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from performance_load_testing_framework import (
    LoadTestConfig, LoadTestResult, LoadTestType, LoadPattern,
    PerformanceLoadTestingFramework
)

logger = logging.getLogger(__name__)


@dataclass
class MCPToolPerformanceResult:
    """Performance results for a specific MCP tool"""
    tool_name: str
    test_config: LoadTestConfig
    
    # Performance metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    throughput_rps: float = 0.0
    error_rate: float = 0.0
    
    # Tool-specific metrics
    tool_specific_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Success criteria
    passed: bool = False
    failure_reasons: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class MCPToolPerformanceTester:
    """Performance tester for individual MCP tools"""
    
    def __init__(self):
        self.framework = PerformanceLoadTestingFramework()
        self.tool_results: Dict[str, MCPToolPerformanceResult] = {}
        
        # MCP tool configurations with expected performance characteristics
        self.tool_configs = {
            "health_check": {
                "expected_response_time_ms": 50.0,
                "expected_throughput_rps": 1000.0,
                "max_error_rate": 0.001,
                "description": "Health check endpoint - should be fastest"
            },
            "get_server_capabilities": {
                "expected_response_time_ms": 100.0,
                "expected_throughput_rps": 500.0,
                "max_error_rate": 0.001,
                "description": "Server capabilities - lightweight metadata"
            },
            "manage_project": {
                "expected_response_time_ms": 200.0,
                "expected_throughput_rps": 200.0,
                "max_error_rate": 0.01,
                "description": "Project management operations"
            },
            "manage_task": {
                "expected_response_time_ms": 300.0,
                "expected_throughput_rps": 150.0,
                "max_error_rate": 0.01,
                "description": "Task management operations"
            },
            "manage_agent": {
                "expected_response_time_ms": 150.0,
                "expected_throughput_rps": 300.0,
                "max_error_rate": 0.01,
                "description": "Agent management operations"
            },
            "manage_subtask": {
                "expected_response_time_ms": 250.0,
                "expected_throughput_rps": 200.0,
                "max_error_rate": 0.01,
                "description": "Subtask management operations"
            },
            "manage_context": {
                "expected_response_time_ms": 400.0,
                "expected_throughput_rps": 100.0,
                "max_error_rate": 0.02,
                "description": "Context management - most complex operations"
            },
            "call_agent": {
                "expected_response_time_ms": 500.0,
                "expected_throughput_rps": 50.0,
                "max_error_rate": 0.02,
                "description": "Agent calling - involves YAML loading"
            }
        }
    
    async def run_comprehensive_mcp_performance_tests(self, mcp_server) -> Dict[str, Any]:
        """Run comprehensive performance tests for all MCP tools"""
        logger.info("Starting comprehensive MCP tool performance testing")
        
        start_time = time.time()
        tool_results = {}
        
        # Test each MCP tool individually
        for tool_name in self.tool_configs.keys():
            logger.info(f"Testing MCP tool: {tool_name}")
            
            try:
                result = await self.test_mcp_tool_performance(mcp_server, tool_name)
                tool_results[tool_name] = result
                self.tool_results[tool_name] = result
                
                # Brief pause between tool tests
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Failed to test MCP tool {tool_name}: {e}")
                tool_results[tool_name] = self._create_failed_result(tool_name, str(e))
        
        # Run concurrent tool testing
        logger.info("Testing concurrent MCP tool usage")
        concurrent_result = await self.test_concurrent_mcp_tools(mcp_server)
        
        end_time = time.time()
        
        # Generate comprehensive report
        report = self._generate_mcp_performance_report(tool_results, concurrent_result, start_time, end_time)
        
        logger.info(f"MCP performance testing completed in {end_time - start_time:.2f} seconds")
        
        return report
    
    async def test_mcp_tool_performance(self, mcp_server, tool_name: str) -> MCPToolPerformanceResult:
        """Test performance of a specific MCP tool"""
        tool_config = self.tool_configs.get(tool_name, {})
        
        # Create test configuration based on tool characteristics
        test_config = LoadTestConfig(
            test_type=LoadTestType.LOAD,
            test_name=f"{tool_name} Performance Test",
            description=f"Performance test for {tool_name}: {tool_config.get('description', '')}",
            target_rps=int(tool_config.get('expected_throughput_rps', 100) * 0.8),  # Test at 80% of expected
            concurrent_users=20,
            test_duration_seconds=180,  # 3 minutes
            ramp_up_duration_seconds=30,
            load_pattern=LoadPattern.RAMP_UP,
            max_response_time_ms=tool_config.get('expected_response_time_ms', 500) * 2,  # 2x expected
            max_error_rate=tool_config.get('max_error_rate', 0.02),
            min_throughput_rps=tool_config.get('expected_throughput_rps', 100) * 0.5,  # 50% of expected
            mcp_tools_to_test=[tool_name]
        )
        
        # Create tool-specific test function
        async def tool_test_function():
            return await self._execute_mcp_tool_call(mcp_server, tool_name)
        
        # Run performance test
        load_result = await self.framework.run_single_performance_test(mcp_server, test_config)
        
        # Convert to MCP tool result
        mcp_result = MCPToolPerformanceResult(
            tool_name=tool_name,
            test_config=test_config,
            total_requests=load_result.total_requests,
            successful_requests=load_result.successful_requests,
            failed_requests=load_result.failed_requests,
            avg_response_time_ms=load_result.avg_response_time_ms,
            p95_response_time_ms=load_result.p95_response_time_ms,
            p99_response_time_ms=load_result.p99_response_time_ms,
            throughput_rps=load_result.actual_rps,
            error_rate=load_result.error_rate,
            passed=load_result.passed,
            failure_reasons=load_result.failure_reasons
        )
        
        # Add tool-specific analysis
        mcp_result.tool_specific_metrics = self._analyze_tool_specific_metrics(tool_name, load_result)
        mcp_result.recommendations = self._generate_tool_specific_recommendations(tool_name, mcp_result)
        
        return mcp_result
    
    async def test_concurrent_mcp_tools(self, mcp_server) -> Dict[str, Any]:
        """Test concurrent usage of multiple MCP tools"""
        logger.info("Testing concurrent MCP tool usage")
        
        # Test configuration for concurrent tool usage
        test_config = LoadTestConfig(
            test_type=LoadTestType.CONCURRENCY,
            test_name="Concurrent MCP Tools Test",
            description="Test multiple MCP tools running concurrently",
            target_rps=100,
            concurrent_users=50,
            test_duration_seconds=300,  # 5 minutes
            load_pattern=LoadPattern.CONSTANT,
            max_response_time_ms=1000.0,
            max_error_rate=0.05,
            min_throughput_rps=75.0,
            mcp_tools_to_test=list(self.tool_configs.keys())
        )
        
        # Create concurrent test function that randomly selects tools
        import random
        
        async def concurrent_tool_test():
            tool_name = random.choice(test_config.mcp_tools_to_test)
            return await self._execute_mcp_tool_call(mcp_server, tool_name)
        
        # Run concurrent test
        start_time = time.time()
        
        # Create load generator for concurrent testing
        from .performance_load_testing_framework import LoadGenerator
        load_generator = LoadGenerator(test_config)
        
        # Generate concurrent load
        await load_generator.generate_load(concurrent_tool_test)
        
        # Collect metrics
        performance_metrics = load_generator.get_performance_metrics()
        
        end_time = time.time()
        
        return {
            "test_name": "Concurrent MCP Tools",
            "duration_seconds": end_time - start_time,
            "total_requests": performance_metrics["total_requests"],
            "successful_requests": performance_metrics["successful_requests"],
            "failed_requests": performance_metrics["failed_requests"],
            "avg_response_time_ms": performance_metrics["response_times"]["avg_ms"],
            "p95_response_time_ms": performance_metrics["response_times"]["p95_ms"],
            "throughput_rps": performance_metrics["actual_rps"],
            "error_rate": performance_metrics["error_rate"],
            "error_types": performance_metrics["error_types"]
        }
    
    async def _execute_mcp_tool_call(self, mcp_server, tool_name: str) -> Any:
        """Execute a specific MCP tool call with appropriate parameters"""
        try:
            if tool_name == "health_check":
                return await mcp_server._call_tool("health_check", {"random_string": "test"})
            
            elif tool_name == "get_server_capabilities":
                return await mcp_server._call_tool("get_server_capabilities", {"random_string": "test"})
            
            elif tool_name == "manage_project":
                # Test different project operations
                import random
                actions = ["list", "get"]
                action = random.choice(actions)
                
                if action == "list":
                    return await mcp_server._call_tool("manage_project", {"action": "list"})
                else:
                    return await mcp_server._call_tool("manage_project", {
                        "action": "get",
                        "project_id": "dhafnck_mcp_main"
                    })
            
            elif tool_name == "manage_task":
                # Test task operations (read-only for performance testing)
                return await mcp_server._call_tool("manage_task", {
                    "action": "next",
                    "project_id": "dhafnck_mcp_main",
                    "task_tree_id": "sophisticated-rule-orchestration-platform"
                })
            
            elif tool_name == "manage_agent":
                # Test agent operations
                return await mcp_server._call_tool("manage_agent", {
                    "action": "list",
                    "project_id": "dhafnck_mcp_main"
                })
            
            elif tool_name == "manage_subtask":
                # Test subtask operations
                return await mcp_server._call_tool("manage_subtask", {
                    "action": "list",
                    "task_id": "20250628008",
                    "project_id": "dhafnck_mcp_main",
                    "task_tree_id": "sophisticated-rule-orchestration-platform"
                })
            
            elif tool_name == "manage_context":
                # Test context operations
                return await mcp_server._call_tool("manage_context", {
                    "action": "get",
                    "task_id": "20250628008",
                    "project_id": "dhafnck_mcp_main",
                    "task_tree_id": "sophisticated-rule-orchestration-platform"
                })
            
            elif tool_name == "call_agent":
                # Test agent calling
                return await mcp_server._call_tool("call_agent", {
                    "name_agent": "performance_load_tester_agent"
                })
            
            else:
                # Default to health check
                return await mcp_server._call_tool("health_check", {"random_string": "test"})
                
        except Exception as e:
            logger.warning(f"MCP tool call failed for {tool_name}: {e}")
            raise
    
    def _analyze_tool_specific_metrics(self, tool_name: str, load_result: LoadTestResult) -> Dict[str, Any]:
        """Analyze tool-specific performance metrics"""
        tool_config = self.tool_configs.get(tool_name, {})
        expected_response_time = tool_config.get('expected_response_time_ms', 500)
        expected_throughput = tool_config.get('expected_throughput_rps', 100)
        
        metrics = {
            "performance_vs_expected": {
                "response_time_ratio": load_result.avg_response_time_ms / expected_response_time,
                "throughput_ratio": load_result.actual_rps / expected_throughput,
                "meets_response_time_target": load_result.p95_response_time_ms <= expected_response_time * 1.5,
                "meets_throughput_target": load_result.actual_rps >= expected_throughput * 0.8
            },
            "performance_characteristics": {
                "response_time_consistency": load_result.max_response_time_ms / load_result.avg_response_time_ms,
                "error_stability": load_result.error_rate < tool_config.get('max_error_rate', 0.02),
                "scalability_indicator": load_result.actual_rps / load_result.config.concurrent_users
            },
            "bottleneck_analysis": self._identify_tool_bottlenecks(tool_name, load_result)
        }
        
        return metrics
    
    def _identify_tool_bottlenecks(self, tool_name: str, load_result: LoadTestResult) -> Dict[str, Any]:
        """Identify potential bottlenecks for specific tools"""
        bottlenecks = {
            "identified_bottlenecks": [],
            "performance_indicators": {}
        }
        
        # High response time variance indicates inconsistent performance
        if load_result.max_response_time_ms > load_result.avg_response_time_ms * 3:
            bottlenecks["identified_bottlenecks"].append("High response time variance - potential resource contention")
        
        # Tool-specific bottleneck analysis
        if tool_name in ["manage_context", "call_agent"]:
            # These tools involve file I/O and should be monitored for I/O bottlenecks
            if load_result.p95_response_time_ms > 1000:
                bottlenecks["identified_bottlenecks"].append("High latency for I/O intensive operation - potential disk bottleneck")
        
        elif tool_name in ["manage_task", "manage_project"]:
            # These tools involve JSON processing
            if load_result.avg_response_time_ms > 200:
                bottlenecks["identified_bottlenecks"].append("High latency for data processing - potential JSON serialization bottleneck")
        
        elif tool_name in ["health_check", "get_server_capabilities"]:
            # These should be very fast
            if load_result.avg_response_time_ms > 100:
                bottlenecks["identified_bottlenecks"].append("Unexpectedly high latency for lightweight operation")
        
        # CPU utilization analysis
        if load_result.max_cpu_usage > 80:
            bottlenecks["identified_bottlenecks"].append("High CPU usage - potential CPU bottleneck")
        
        # Memory utilization analysis
        if load_result.max_memory_usage_mb > 500:
            bottlenecks["identified_bottlenecks"].append("High memory usage - potential memory bottleneck")
        
        return bottlenecks
    
    def _generate_tool_specific_recommendations(self, tool_name: str, result: MCPToolPerformanceResult) -> List[str]:
        """Generate tool-specific performance recommendations"""
        recommendations = []
        tool_config = self.tool_configs.get(tool_name, {})
        
        # Response time recommendations
        expected_response_time = tool_config.get('expected_response_time_ms', 500)
        if result.p95_response_time_ms > expected_response_time * 2:
            recommendations.append(f"{tool_name}: Response time significantly above expected - investigate tool-specific optimizations")
        
        # Throughput recommendations
        expected_throughput = tool_config.get('expected_throughput_rps', 100)
        if result.throughput_rps < expected_throughput * 0.5:
            recommendations.append(f"{tool_name}: Throughput well below expected - consider tool-specific performance tuning")
        
        # Tool-specific recommendations
        if tool_name == "call_agent" and result.avg_response_time_ms > 1000:
            recommendations.append("call_agent: High latency detected - consider caching YAML configurations")
        
        elif tool_name == "manage_context" and result.avg_response_time_ms > 500:
            recommendations.append("manage_context: High latency detected - consider context caching or database optimization")
        
        elif tool_name in ["manage_task", "manage_project"] and result.avg_response_time_ms > 300:
            recommendations.append(f"{tool_name}: Consider implementing data caching or optimizing JSON processing")
        
        elif tool_name in ["health_check", "get_server_capabilities"] and result.avg_response_time_ms > 50:
            recommendations.append(f"{tool_name}: Lightweight operation showing high latency - investigate basic infrastructure")
        
        # Error rate recommendations
        if result.error_rate > tool_config.get('max_error_rate', 0.02):
            recommendations.append(f"{tool_name}: High error rate - improve error handling and stability")
        
        return recommendations
    
    def _create_failed_result(self, tool_name: str, error_message: str) -> MCPToolPerformanceResult:
        """Create a failed test result"""
        return MCPToolPerformanceResult(
            tool_name=tool_name,
            test_config=LoadTestConfig(
                test_type=LoadTestType.LOAD,
                test_name=f"{tool_name} Performance Test",
                description="Failed test"
            ),
            passed=False,
            failure_reasons=[f"Test execution failed: {error_message}"]
        )
    
    def _generate_mcp_performance_report(self, tool_results: Dict[str, MCPToolPerformanceResult], 
                                       concurrent_result: Dict[str, Any], start_time: float, end_time: float) -> Dict[str, Any]:
        """Generate comprehensive MCP performance report"""
        
        # Calculate summary statistics
        total_tools_tested = len(tool_results)
        passed_tools = sum(1 for result in tool_results.values() if result.passed)
        failed_tools = total_tools_tested - passed_tools
        
        # Performance analysis
        avg_response_times = [r.avg_response_time_ms for r in tool_results.values() if r.avg_response_time_ms > 0]
        avg_throughputs = [r.throughput_rps for r in tool_results.values() if r.throughput_rps > 0]
        
        # Tool rankings
        fastest_tools = sorted(tool_results.items(), key=lambda x: x[1].avg_response_time_ms)[:3]
        highest_throughput_tools = sorted(tool_results.items(), key=lambda x: x[1].throughput_rps, reverse=True)[:3]
        
        return {
            "test_summary": {
                "total_tools_tested": total_tools_tested,
                "passed_tools": passed_tools,
                "failed_tools": failed_tools,
                "success_rate": passed_tools / total_tools_tested if total_tools_tested > 0 else 0.0,
                "total_test_duration_seconds": end_time - start_time
            },
            "performance_overview": {
                "avg_response_time_ms": sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0.0,
                "avg_throughput_rps": sum(avg_throughputs) / len(avg_throughputs) if avg_throughputs else 0.0,
                "fastest_tools": [{"tool": name, "response_time_ms": result.avg_response_time_ms} 
                                for name, result in fastest_tools],
                "highest_throughput_tools": [{"tool": name, "throughput_rps": result.throughput_rps} 
                                           for name, result in highest_throughput_tools]
            },
            "tool_results": {
                name: {
                    "passed": result.passed,
                    "avg_response_time_ms": result.avg_response_time_ms,
                    "p95_response_time_ms": result.p95_response_time_ms,
                    "throughput_rps": result.throughput_rps,
                    "error_rate": result.error_rate,
                    "total_requests": result.total_requests,
                    "failure_reasons": result.failure_reasons,
                    "recommendations": result.recommendations,
                    "tool_specific_metrics": result.tool_specific_metrics
                }
                for name, result in tool_results.items()
            },
            "concurrent_testing": concurrent_result,
            "overall_recommendations": self._generate_overall_mcp_recommendations(tool_results, concurrent_result)
        }
    
    def _generate_overall_mcp_recommendations(self, tool_results: Dict[str, MCPToolPerformanceResult], 
                                            concurrent_result: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations for MCP performance"""
        recommendations = []
        
        # Analyze overall patterns
        high_latency_tools = [name for name, result in tool_results.items() if result.avg_response_time_ms > 500]
        low_throughput_tools = [name for name, result in tool_results.items() if result.throughput_rps < 50]
        high_error_tools = [name for name, result in tool_results.items() if result.error_rate > 0.05]
        
        # Overall system recommendations
        if len(high_latency_tools) > len(tool_results) * 0.5:
            recommendations.append("More than 50% of MCP tools show high latency - consider system-wide performance optimization")
        
        if low_throughput_tools:
            recommendations.append(f"Low throughput detected in tools: {', '.join(low_throughput_tools)} - investigate scaling limitations")
        
        if high_error_tools:
            recommendations.append(f"High error rates in tools: {', '.join(high_error_tools)} - improve error handling and stability")
        
        # Concurrent performance analysis
        if concurrent_result.get("error_rate", 0) > 0.1:
            recommendations.append("High error rate during concurrent tool usage - implement better resource management")
        
        if concurrent_result.get("p95_response_time_ms", 0) > 2000:
            recommendations.append("High latency during concurrent usage - consider connection pooling and resource optimization")
        
        # Scaling recommendations
        avg_throughput = sum(r.throughput_rps for r in tool_results.values()) / len(tool_results)
        if avg_throughput < 100:
            recommendations.append("Overall low throughput - system needs significant performance improvements for production scale")
        elif avg_throughput < 500:
            recommendations.append("Moderate throughput achieved - ready for small-scale production, implement caching for higher scale")
        else:
            recommendations.append("Good throughput achieved - system ready for production scale")
        
        return recommendations


# Example usage
async def main():
    """Example usage of MCP performance testing"""
    try:
        # Import MCP server creation function
        sys.path.append(str(Path(__file__).parent.parent))
        from test_mvp_server import create_dhafnck_mcp_server
        
        # Create MCP server
        mcp_server = create_dhafnck_mcp_server()
        
        # Create MCP performance tester
        tester = MCPToolPerformanceTester()
        
        # Run comprehensive MCP performance tests
        results = await tester.run_comprehensive_mcp_performance_tests(mcp_server)
        
        # Print results
        print("\n" + "="*80)
        print("MCP TOOL PERFORMANCE TEST RESULTS")
        print("="*80)
        
        print(f"Tools Tested: {results['test_summary']['total_tools_tested']}")
        print(f"Passed: {results['test_summary']['passed_tools']}")
        print(f"Failed: {results['test_summary']['failed_tools']}")
        print(f"Success Rate: {results['test_summary']['success_rate']:.1%}")
        
        print(f"\nPerformance Overview:")
        print(f"Average Response Time: {results['performance_overview']['avg_response_time_ms']:.2f}ms")
        print(f"Average Throughput: {results['performance_overview']['avg_throughput_rps']:.2f} RPS")
        
        print(f"\nFastest Tools:")
        for tool_info in results['performance_overview']['fastest_tools']:
            print(f"  {tool_info['tool']}: {tool_info['response_time_ms']:.2f}ms")
        
        print(f"\nHighest Throughput Tools:")
        for tool_info in results['performance_overview']['highest_throughput_tools']:
            print(f"  {tool_info['tool']}: {tool_info['throughput_rps']:.2f} RPS")
        
        if results['overall_recommendations']:
            print(f"\nRecommendations:")
            for i, rec in enumerate(results['overall_recommendations'], 1):
                print(f"{i}. {rec}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"MCP performance testing failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 