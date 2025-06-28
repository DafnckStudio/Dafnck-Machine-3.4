#!/usr/bin/env python3
"""
Simplified Performance Test for Rule Orchestration Platform

A streamlined version of the performance testing framework that focuses on
essential metrics without complex warmup phases that might cause hanging.

Author: Performance Load Tester Agent
Date: 2025-01-27
Task: 20250628008.002 - Performance and Load Testing
"""

import asyncio
import time
import json
import logging
import statistics
from pathlib import Path
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class SimplePerformanceResult:
    """Simple performance test result"""
    tool_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    throughput_rps: float = 0.0
    error_rate: float = 0.0
    test_duration_seconds: float = 0.0
    passed: bool = False
    failure_reasons: List[str] = field(default_factory=list)


class SimplePerformanceTester:
    """Simplified performance tester for MCP tools"""
    
    def __init__(self):
        self.results: Dict[str, SimplePerformanceResult] = {}
        
        # Expected performance characteristics for each tool
        self.tool_expectations = {
            "health_check": {
                "expected_response_time_ms": 50.0,
                "expected_throughput_rps": 100.0,
                "max_error_rate": 0.01,
                "description": "Health check endpoint"
            },
            "get_server_capabilities": {
                "expected_response_time_ms": 100.0,
                "expected_throughput_rps": 50.0,
                "max_error_rate": 0.01,
                "description": "Server capabilities"
            },
            "manage_project": {
                "expected_response_time_ms": 200.0,
                "expected_throughput_rps": 30.0,
                "max_error_rate": 0.02,
                "description": "Project management"
            },
            "manage_task": {
                "expected_response_time_ms": 300.0,
                "expected_throughput_rps": 25.0,
                "max_error_rate": 0.02,
                "description": "Task management"
            },
            "manage_agent": {
                "expected_response_time_ms": 150.0,
                "expected_throughput_rps": 40.0,
                "max_error_rate": 0.02,
                "description": "Agent management"
            }
        }
    
    async def run_simple_performance_test(self, mcp_server, tool_name: str, 
                                        num_requests: int = 50, 
                                        concurrent_requests: int = 5) -> SimplePerformanceResult:
        """Run a simple performance test for a specific tool"""
        logger.info(f"Testing {tool_name} with {num_requests} requests ({concurrent_requests} concurrent)")
        
        start_time = time.time()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        failure_reasons = []
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def single_request():
            async with semaphore:
                request_start = time.time()
                try:
                    result = await self._execute_tool_call(mcp_server, tool_name)
                    request_end = time.time()
                    response_time_ms = (request_end - request_start) * 1000
                    response_times.append(response_time_ms)
                    return True
                except Exception as e:
                    request_end = time.time()
                    response_time_ms = (request_end - request_start) * 1000
                    response_times.append(response_time_ms)
                    failure_reasons.append(str(e))
                    return False
        
        # Execute all requests
        tasks = [single_request() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Count successes and failures
        for result in results:
            if isinstance(result, Exception):
                failed_requests += 1
                failure_reasons.append(str(result))
            elif result:
                successful_requests += 1
            else:
                failed_requests += 1
        
        # Calculate metrics
        avg_response_time_ms = statistics.mean(response_times) if response_times else 0.0
        p95_response_time_ms = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0.0
        p99_response_time_ms = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times) if response_times else 0.0
        throughput_rps = successful_requests / test_duration if test_duration > 0 else 0.0
        error_rate = failed_requests / num_requests if num_requests > 0 else 0.0
        
        # Determine if test passed
        expectations = self.tool_expectations.get(tool_name, {})
        passed = True
        test_failure_reasons = []
        
        if avg_response_time_ms > expectations.get('expected_response_time_ms', 500) * 2:
            passed = False
            test_failure_reasons.append(f"Response time too high: {avg_response_time_ms:.2f}ms > {expectations.get('expected_response_time_ms', 500) * 2}ms")
        
        if error_rate > expectations.get('max_error_rate', 0.05):
            passed = False
            test_failure_reasons.append(f"Error rate too high: {error_rate:.2%} > {expectations.get('max_error_rate', 0.05):.2%}")
        
        if throughput_rps < expectations.get('expected_throughput_rps', 10) * 0.5:
            passed = False
            test_failure_reasons.append(f"Throughput too low: {throughput_rps:.2f} RPS < {expectations.get('expected_throughput_rps', 10) * 0.5:.2f} RPS")
        
        return SimplePerformanceResult(
            tool_name=tool_name,
            total_requests=num_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time_ms,
            p95_response_time_ms=p95_response_time_ms,
            p99_response_time_ms=p99_response_time_ms,
            throughput_rps=throughput_rps,
            error_rate=error_rate,
            test_duration_seconds=test_duration,
            passed=passed,
            failure_reasons=test_failure_reasons
        )
    
    async def _execute_tool_call(self, mcp_server, tool_name: str) -> Any:
        """Execute a specific tool call"""
        if tool_name == "health_check":
            result = await mcp_server._mcp_call_tool("health_check", {})
            return json.loads(result[0].text)
        
        elif tool_name == "get_server_capabilities":
            result = await mcp_server._mcp_call_tool("get_server_capabilities", {})
            return json.loads(result[0].text)
        
        elif tool_name == "manage_project":
            result = await mcp_server._mcp_call_tool("manage_project", {
                "action": "list"
            })
            return json.loads(result[0].text)
        
        elif tool_name == "manage_task":
            result = await mcp_server._mcp_call_tool("manage_task", {
                "action": "list",
                "project_id": "dhafnck_mcp_main"
            })
            return json.loads(result[0].text)
        
        elif tool_name == "manage_agent":
            result = await mcp_server._mcp_call_tool("manage_agent", {
                "action": "list",
                "project_id": "dhafnck_mcp_main"
            })
            return json.loads(result[0].text)
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def run_comprehensive_test_suite(self, mcp_server) -> Dict[str, Any]:
        """Run comprehensive performance tests for all tools"""
        logger.info("🚀 Starting Simple Performance Test Suite")
        print("\n" + "="*80)
        print("🏁 DHAFNCK MCP - SIMPLE PERFORMANCE TEST SUITE")
        print("="*80)
        
        start_time = time.time()
        tool_results = {}
        
        # Test each tool
        for tool_name in self.tool_expectations.keys():
            print(f"\n🔧 Testing {tool_name}...")
            try:
                result = await self.run_simple_performance_test(mcp_server, tool_name)
                tool_results[tool_name] = result
                self.results[tool_name] = result
                
                # Print immediate results
                status = "✅ PASSED" if result.passed else "❌ FAILED"
                print(f"   {status} - {result.successful_requests}/{result.total_requests} requests")
                print(f"   📊 Throughput: {result.throughput_rps:.2f} RPS")
                print(f"   ⏱️ Avg Response: {result.avg_response_time_ms:.2f}ms")
                print(f"   ❌ Error Rate: {result.error_rate:.2%}")
                
                if not result.passed:
                    for reason in result.failure_reasons:
                        print(f"   ⚠️ {reason}")
                
                # Brief pause between tests
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to test {tool_name}: {e}")
                tool_results[tool_name] = SimplePerformanceResult(
                    tool_name=tool_name,
                    passed=False,
                    failure_reasons=[f"Test execution failed: {str(e)}"]
                )
        
        end_time = time.time()
        
        # Generate summary report
        report = self._generate_summary_report(tool_results, start_time, end_time)
        
        # Save results
        await self._save_results(report)
        
        # Print summary
        self._print_summary(report)
        
        return report


async def main():
    """Main function to run simple performance tests"""
    try:
        # Import MCP server creation function
        from tests.test_mvp_server import create_dhafnck_mcp_server
        
        print("🏗️ Creating MCP server...")
        mcp_server = create_dhafnck_mcp_server()
        print(f"✅ Server created: {mcp_server.name}")
        
        # Create tester
        tester = SimplePerformanceTester()
        
        # Run tests
        results = await tester.run_comprehensive_test_suite(mcp_server)
        
        return results
        
    except Exception as e:
        print(f"\n❌ Performance testing failed: {e}")
        logger.exception("Performance testing failed")
        raise


if __name__ == "__main__":
    asyncio.run(main())
    
    def _generate_summary_report(self, tool_results: Dict[str, SimplePerformanceResult], 
                                start_time: float, end_time: float) -> Dict[str, Any]:
        """Generate a summary report"""
        total_tests = len(tool_results)
        passed_tests = sum(1 for result in tool_results.values() if result.passed)
        failed_tests = total_tests - passed_tests
        
        # Overall metrics
        all_throughputs = [r.throughput_rps for r in tool_results.values() if r.throughput_rps > 0]
        all_response_times = [r.avg_response_time_ms for r in tool_results.values() if r.avg_response_time_ms > 0]
        all_error_rates = [r.error_rate for r in tool_results.values()]
        
        avg_throughput = statistics.mean(all_throughputs) if all_throughputs else 0.0
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0.0
        avg_error_rate = statistics.mean(all_error_rates) if all_error_rates else 0.0
        
        # Performance assessment
        performance_score = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        if performance_score >= 90:
            readiness = "READY"
        elif performance_score >= 75:
            readiness = "READY_WITH_MONITORING"
        elif performance_score >= 50:
            readiness = "NEEDS_IMPROVEMENT"
        else:
            readiness = "NOT_READY"
        
        return {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "test_duration_seconds": end_time - start_time
            },
            "performance_overview": {
                "avg_throughput_rps": avg_throughput,
                "avg_response_time_ms": avg_response_time,
                "avg_error_rate": avg_error_rate,
                "performance_score": performance_score,
                "production_readiness": readiness
            },
            "tool_results": {name: {
                "passed": result.passed,
                "throughput_rps": result.throughput_rps,
                "avg_response_time_ms": result.avg_response_time_ms,
                "error_rate": result.error_rate,
                "failure_reasons": result.failure_reasons
            } for name, result in tool_results.items()},
            "recommendations": self._generate_recommendations(tool_results, performance_score),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, tool_results: Dict[str, SimplePerformanceResult], 
                                performance_score: float) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Analyze failed tests
        failed_tools = [name for name, result in tool_results.items() if not result.passed]
        if failed_tools:
            recommendations.append(f"Address performance issues in: {', '.join(failed_tools)}")
        
        # Response time analysis
        slow_tools = [name for name, result in tool_results.items() 
                     if result.avg_response_time_ms > 500]
        if slow_tools:
            recommendations.append(f"Optimize response times for: {', '.join(slow_tools)}")
        
        # Throughput analysis
        low_throughput_tools = [name for name, result in tool_results.items() 
                              if result.throughput_rps < 10]
        if low_throughput_tools:
            recommendations.append(f"Improve throughput for: {', '.join(low_throughput_tools)}")
        
        # Overall recommendations
        if performance_score < 75:
            recommendations.append("Consider implementing caching mechanisms")
            recommendations.append("Review database query optimization")
            recommendations.append("Consider connection pooling")
        
        if performance_score < 50:
            recommendations.append("Major performance optimization required before production")
            recommendations.append("Consider architectural changes")
        
        return recommendations
    
    async def _save_results(self, report: Dict[str, Any]):
        """Save test results to file"""
        try:
            results_dir = Path(__file__).parent / "results"
            results_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simple_performance_results_{timestamp}.json"
            filepath = results_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"\n📄 Results saved to: {filepath}")
            
        except Exception as e:
            logger.warning(f"Failed to save results: {e}")
    
    def _print_summary(self, report: Dict[str, Any]):
        """Print test summary"""
        print("\n" + "="*80)
        print("📊 PERFORMANCE TEST RESULTS SUMMARY")
        print("="*80)
        
        summary = report["test_summary"]
        overview = report["performance_overview"]
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Tests Run: {summary['total_tests']}")
        print(f"   Tests Passed: {summary['passed_tests']}")
        print(f"   Tests Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1%}")
        print(f"   Test Duration: {summary['test_duration_seconds']:.1f}s")
        
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   Average Throughput: {overview['avg_throughput_rps']:.2f} RPS")
        print(f"   Average Response Time: {overview['avg_response_time_ms']:.2f}ms")
        print(f"   Average Error Rate: {overview['avg_error_rate']:.2%}")
        print(f"   Performance Score: {overview['performance_score']:.1f}/100")
        print(f"   Production Readiness: {overview['production_readiness']}")
        
        if report["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        print("\n" + "="*80)
        
        # Final assessment
        if overview['production_readiness'] == "READY":
            print("🎉 SYSTEM IS READY FOR PRODUCTION!")
        elif overview['production_readiness'] == "READY_WITH_MONITORING":
            print("✅ SYSTEM IS READY WITH ENHANCED MONITORING!")
        elif overview['production_readiness'] == "NEEDS_IMPROVEMENT":
            print("⚠️ SYSTEM NEEDS IMPROVEMENT BEFORE PRODUCTION!")
        else:
            print("❌ SYSTEM IS NOT READY FOR PRODUCTION!")
        
        print("="*80)
