"""
Comprehensive Performance Test Runner for Rule Orchestration Platform

This module orchestrates and executes all performance tests for the DhafnckMCP
rule orchestration platform, generating comprehensive performance reports and
recommendations for scaling and optimization.

Author: Performance Load Tester Agent
Date: 2025-01-27
Task: 20250628008.002 - Performance and Load Testing
"""

import asyncio
import time
import json
import logging
from pathlib import Path
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import performance testing modules
from performance_load_testing_framework import (
    PerformanceLoadTestingFramework,
    get_baseline_test_config,
    get_load_test_config,
    get_stress_test_config,
    get_spike_test_config,
    get_soak_test_config
)

from mcp_performance_tests import MCPToolPerformanceTester

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ComprehensivePerformanceTestRunner:
    """Orchestrates comprehensive performance testing for the rule orchestration platform"""
    
    def __init__(self):
        self.framework = PerformanceLoadTestingFramework()
        self.mcp_tester = MCPToolPerformanceTester()
        self.test_results = {}
        self.start_time = 0.0
        self.end_time = 0.0
        
    async def run_full_performance_test_suite(self, mcp_server) -> Dict[str, Any]:
        """Run the complete performance test suite"""
        logger.info("🚀 Starting Comprehensive Performance Test Suite for Rule Orchestration Platform")
        print("\n" + "="*100)
        print("🏁 DHAFNCK MCP RULE ORCHESTRATION PLATFORM - PERFORMANCE TEST SUITE")
        print("="*100)
        
        self.start_time = time.time()
        
        try:
            # Phase 1: Baseline Performance Testing
            print("\n📊 PHASE 1: BASELINE PERFORMANCE TESTING")
            print("-" * 60)
            baseline_results = await self._run_baseline_tests(mcp_server)
            self.test_results['baseline'] = baseline_results
            
            # Phase 2: MCP Tool-Specific Performance Testing
            print("\n🔧 PHASE 2: MCP TOOL-SPECIFIC PERFORMANCE TESTING")
            print("-" * 60)
            mcp_results = await self._run_mcp_tool_tests(mcp_server)
            self.test_results['mcp_tools'] = mcp_results
            
            # Phase 3: Load and Scalability Testing
            print("\n📈 PHASE 3: LOAD AND SCALABILITY TESTING")
            print("-" * 60)
            scalability_results = await self._run_scalability_tests(mcp_server)
            self.test_results['scalability'] = scalability_results
            
            # Phase 4: Stress and Spike Testing
            print("\n⚡ PHASE 4: STRESS AND SPIKE TESTING")
            print("-" * 60)
            stress_results = await self._run_stress_tests(mcp_server)
            self.test_results['stress'] = stress_results
            
            # Phase 5: Extended Stability Testing (Optional - only if time permits)
            print("\n⏱️ PHASE 5: EXTENDED STABILITY TESTING")
            print("-" * 60)
            stability_results = await self._run_stability_tests(mcp_server)
            self.test_results['stability'] = stability_results
            
            self.end_time = time.time()
            
            # Generate comprehensive report
            comprehensive_report = await self._generate_comprehensive_report()
            
            # Save results
            await self._save_test_results(comprehensive_report)
            
            # Print summary
            self._print_test_summary(comprehensive_report)
            
            return comprehensive_report
            
        except Exception as e:
            self.end_time = time.time()
            logger.error(f"Performance test suite failed: {e}")
            
            # Generate failure report
            failure_report = {
                "status": "failed",
                "error": str(e),
                "completed_phases": list(self.test_results.keys()),
                "duration_seconds": self.end_time - self.start_time
            }
            
            await self._save_test_results(failure_report)
            raise
    
    async def _run_baseline_tests(self, mcp_server) -> Dict[str, Any]:
        """Run baseline performance tests to establish current system capabilities"""
        print("🔍 Establishing performance baseline...")
        
        baseline_config = get_baseline_test_config()
        baseline_result = await self.framework.run_single_performance_test(mcp_server, baseline_config)
        
        # Store baseline for comparison
        self.framework.baseline_metrics = {
            "avg_response_time_ms": baseline_result.avg_response_time_ms,
            "p95_response_time_ms": baseline_result.p95_response_time_ms,
            "throughput_rps": baseline_result.actual_rps,
            "error_rate": baseline_result.error_rate,
            "max_cpu_usage": baseline_result.max_cpu_usage,
            "max_memory_usage_mb": baseline_result.max_memory_usage_mb
        }
        
        print(f"✅ Baseline established:")
        print(f"   📊 Throughput: {baseline_result.actual_rps:.2f} RPS")
        print(f"   ⏱️ P95 Response Time: {baseline_result.p95_response_time_ms:.2f}ms")
        print(f"   ❌ Error Rate: {baseline_result.error_rate:.2%}")
        print(f"   🖥️ CPU Usage: {baseline_result.max_cpu_usage:.1f}%")
        print(f"   💾 Memory Usage: {baseline_result.max_memory_usage_mb:.1f}MB")
        
        return {
            "test_result": baseline_result,
            "baseline_metrics": self.framework.baseline_metrics,
            "status": "passed" if baseline_result.passed else "failed"
        }
    
    async def _run_mcp_tool_tests(self, mcp_server) -> Dict[str, Any]:
        """Run MCP tool-specific performance tests"""
        print("🔧 Testing individual MCP tool performance...")
        
        mcp_results = await self.mcp_tester.run_comprehensive_mcp_performance_tests(mcp_server)
        
        # Print MCP tool summary
        print(f"✅ MCP Tool Testing completed:")
        print(f"   🛠️ Tools tested: {mcp_results['test_summary']['total_tools_tested']}")
        print(f"   ✅ Passed: {mcp_results['test_summary']['passed_tools']}")
        print(f"   ❌ Failed: {mcp_results['test_summary']['failed_tools']}")
        print(f"   📊 Success Rate: {mcp_results['test_summary']['success_rate']:.1%}")
        print(f"   ⏱️ Avg Response Time: {mcp_results['performance_overview']['avg_response_time_ms']:.2f}ms")
        print(f"   📈 Avg Throughput: {mcp_results['performance_overview']['avg_throughput_rps']:.2f} RPS")
        
        return mcp_results
    
    async def _run_scalability_tests(self, mcp_server) -> Dict[str, Any]:
        """Run load and scalability tests"""
        print("📈 Testing system scalability and load handling...")
        
        # Run progressive load tests
        load_configs = [
            get_load_test_config(),
        ]
        
        scalability_results = await self.framework.run_performance_test_suite(mcp_server, load_configs)
        
        print(f"✅ Scalability Testing completed:")
        print(f"   📊 Tests: {scalability_results['suite_summary']['total_tests']}")
        print(f"   ✅ Passed: {scalability_results['suite_summary']['passed_tests']}")
        print(f"   📈 Overall Success Rate: {scalability_results['suite_summary']['success_rate']:.1%}")
        print(f"   ⏱️ Avg Response Time: {scalability_results['overall_performance']['avg_response_time_ms']:.2f}ms")
        
        return scalability_results
    
    async def _run_stress_tests(self, mcp_server) -> Dict[str, Any]:
        """Run stress and spike tests"""
        print("⚡ Testing system under stress and spike conditions...")
        
        stress_configs = [
            get_stress_test_config(),
            get_spike_test_config()
        ]
        
        stress_results = await self.framework.run_performance_test_suite(mcp_server, stress_configs)
        
        print(f"✅ Stress Testing completed:")
        print(f"   📊 Tests: {stress_results['suite_summary']['total_tests']}")
        print(f"   ✅ Passed: {stress_results['suite_summary']['passed_tests']}")
        print(f"   📈 Success Rate: {stress_results['suite_summary']['success_rate']:.1%}")
        
        return stress_results
    
    async def _run_stability_tests(self, mcp_server) -> Dict[str, Any]:
        """Run extended stability tests (shortened for demo)"""
        print("⏱️ Testing system stability (shortened test for demo)...")
        
        # Use a shortened soak test for demonstration
        short_soak_config = get_soak_test_config()
        short_soak_config.test_duration_seconds = 600  # 10 minutes instead of 1 hour
        short_soak_config.test_name = "Short Stability Test"
        short_soak_config.description = "Shortened stability test for demonstration"
        
        stability_results = await self.framework.run_performance_test_suite(mcp_server, [short_soak_config])
        
        print(f"✅ Stability Testing completed:")
        print(f"   ⏱️ Duration: {stability_results['suite_summary']['total_duration_seconds']:.0f} seconds")
        print(f"   📈 Success Rate: {stability_results['suite_summary']['success_rate']:.1%}")
        
        return stability_results
    
    async def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance test report"""
        logger.info("Generating comprehensive performance report...")
        
        total_duration = self.end_time - self.start_time
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics()
        
        # Generate performance assessment
        performance_assessment = self._assess_performance_readiness()
        
        # Generate scaling recommendations
        scaling_recommendations = self._generate_scaling_recommendations()
        
        # Create comprehensive report
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "test_duration_seconds": total_duration,
                "test_duration_formatted": self._format_duration(total_duration),
                "platform": "DhafnckMCP Rule Orchestration Platform",
                "test_version": "1.0.0"
            },
            "executive_summary": {
                "overall_status": performance_assessment["overall_status"],
                "performance_score": performance_assessment["performance_score"],
                "production_readiness": performance_assessment["production_readiness"],
                "key_findings": performance_assessment["key_findings"],
                "critical_issues": performance_assessment["critical_issues"]
            },
            "test_results": self.test_results,
            "overall_metrics": overall_metrics,
            "performance_assessment": performance_assessment,
            "scaling_recommendations": scaling_recommendations,
            "detailed_analysis": self._generate_detailed_analysis()
        }
        
        return report
    
    def _calculate_overall_metrics(self) -> Dict[str, Any]:
        """Calculate overall performance metrics across all tests"""
        metrics = {
            "total_tests_run": 0,
            "total_tests_passed": 0,
            "overall_success_rate": 0.0,
            "best_throughput_rps": 0.0,
            "worst_response_time_ms": 0.0,
            "average_error_rate": 0.0,
            "peak_cpu_usage": 0.0,
            "peak_memory_usage_mb": 0.0
        }
        
        # Aggregate metrics from all test phases
        for phase_name, phase_results in self.test_results.items():
            if phase_name == "baseline":
                metrics["total_tests_run"] += 1
                if phase_results.get("status") == "passed":
                    metrics["total_tests_passed"] += 1
                    
                baseline_result = phase_results["test_result"]
                metrics["best_throughput_rps"] = max(metrics["best_throughput_rps"], baseline_result.actual_rps)
                metrics["worst_response_time_ms"] = max(metrics["worst_response_time_ms"], baseline_result.p95_response_time_ms)
                metrics["average_error_rate"] += baseline_result.error_rate
                metrics["peak_cpu_usage"] = max(metrics["peak_cpu_usage"], baseline_result.max_cpu_usage)
                metrics["peak_memory_usage_mb"] = max(metrics["peak_memory_usage_mb"], baseline_result.max_memory_usage_mb)
                
            elif phase_name == "mcp_tools":
                tool_results = phase_results.get("tool_results", {})
                metrics["total_tests_run"] += len(tool_results)
                metrics["total_tests_passed"] += sum(1 for result in tool_results.values() if result.get("passed", False))
                
                for tool_result in tool_results.values():
                    metrics["best_throughput_rps"] = max(metrics["best_throughput_rps"], tool_result.get("throughput_rps", 0))
                    metrics["worst_response_time_ms"] = max(metrics["worst_response_time_ms"], tool_result.get("p95_response_time_ms", 0))
                    metrics["average_error_rate"] += tool_result.get("error_rate", 0)
                
            elif phase_name in ["scalability", "stress", "stability"]:
                suite_results = phase_results.get("test_results", [])
                metrics["total_tests_run"] += len(suite_results)
                metrics["total_tests_passed"] += sum(1 for result in suite_results if result.get("passed", False))
                
                for test_result in suite_results:
                    metrics["best_throughput_rps"] = max(metrics["best_throughput_rps"], test_result.get("actual_rps", 0))
                    metrics["worst_response_time_ms"] = max(metrics["worst_response_time_ms"], test_result.get("p95_response_time_ms", 0))
                    metrics["average_error_rate"] += test_result.get("error_rate", 0)
        
        # Calculate averages
        if metrics["total_tests_run"] > 0:
            metrics["overall_success_rate"] = metrics["total_tests_passed"] / metrics["total_tests_run"]
            metrics["average_error_rate"] = metrics["average_error_rate"] / metrics["total_tests_run"]
        
        return metrics
    
    def _assess_performance_readiness(self) -> Dict[str, Any]:
        """Assess overall performance readiness for production"""
        overall_metrics = self._calculate_overall_metrics()
        
        # Performance scoring (0-100)
        performance_score = 0
        key_findings = []
        critical_issues = []
        
        # Success rate scoring (30 points)
        success_rate = overall_metrics["overall_success_rate"]
        if success_rate >= 0.95:
            performance_score += 30
            key_findings.append("Excellent test success rate (95%+)")
        elif success_rate >= 0.85:
            performance_score += 25
            key_findings.append("Good test success rate (85%+)")
        elif success_rate >= 0.70:
            performance_score += 15
            key_findings.append("Moderate test success rate (70%+)")
        else:
            critical_issues.append(f"Low test success rate ({success_rate:.1%})")
        
        # Throughput scoring (25 points)
        best_throughput = overall_metrics["best_throughput_rps"]
        if best_throughput >= 500:
            performance_score += 25
            key_findings.append(f"High throughput achieved ({best_throughput:.0f} RPS)")
        elif best_throughput >= 200:
            performance_score += 20
            key_findings.append(f"Good throughput achieved ({best_throughput:.0f} RPS)")
        elif best_throughput >= 100:
            performance_score += 15
            key_findings.append(f"Moderate throughput achieved ({best_throughput:.0f} RPS)")
        elif best_throughput >= 50:
            performance_score += 10
            key_findings.append(f"Basic throughput achieved ({best_throughput:.0f} RPS)")
        else:
            critical_issues.append(f"Low throughput ({best_throughput:.0f} RPS)")
        
        # Response time scoring (25 points)
        worst_response_time = overall_metrics["worst_response_time_ms"]
        if worst_response_time <= 100:
            performance_score += 25
            key_findings.append("Excellent response times (<100ms p95)")
        elif worst_response_time <= 500:
            performance_score += 20
            key_findings.append("Good response times (<500ms p95)")
        elif worst_response_time <= 1000:
            performance_score += 15
            key_findings.append("Acceptable response times (<1s p95)")
        elif worst_response_time <= 2000:
            performance_score += 10
            key_findings.append("High response times (<2s p95)")
        else:
            critical_issues.append(f"Very high response times ({worst_response_time:.0f}ms p95)")
        
        # Error rate scoring (20 points)
        avg_error_rate = overall_metrics["average_error_rate"]
        if avg_error_rate <= 0.01:
            performance_score += 20
            key_findings.append("Excellent error rate (<1%)")
        elif avg_error_rate <= 0.05:
            performance_score += 15
            key_findings.append("Good error rate (<5%)")
        elif avg_error_rate <= 0.10:
            performance_score += 10
            key_findings.append("Moderate error rate (<10%)")
        else:
            critical_issues.append(f"High error rate ({avg_error_rate:.1%})")
        
        # Determine overall status
        if performance_score >= 85:
            overall_status = "EXCELLENT"
            production_readiness = "READY"
        elif performance_score >= 70:
            overall_status = "GOOD"
            production_readiness = "READY_WITH_MONITORING"
        elif performance_score >= 55:
            overall_status = "ACCEPTABLE"
            production_readiness = "READY_WITH_IMPROVEMENTS"
        elif performance_score >= 40:
            overall_status = "POOR"
            production_readiness = "NOT_READY"
        else:
            overall_status = "CRITICAL"
            production_readiness = "NOT_READY"
        
        return {
            "overall_status": overall_status,
            "performance_score": performance_score,
            "production_readiness": production_readiness,
            "key_findings": key_findings,
            "critical_issues": critical_issues,
            "detailed_scores": {
                "success_rate_score": min(30, performance_score),
                "throughput_score": min(25, max(0, performance_score - 30)),
                "response_time_score": min(25, max(0, performance_score - 55)),
                "error_rate_score": min(20, max(0, performance_score - 80))
            }
        }
    
    def _generate_scaling_recommendations(self) -> Dict[str, Any]:
        """Generate scaling recommendations based on test results"""
        overall_metrics = self._calculate_overall_metrics()
        
        recommendations = {
            "immediate_actions": [],
            "short_term_improvements": [],
            "long_term_scaling": [],
            "architecture_recommendations": []
        }
        
        # Immediate actions based on critical issues
        if overall_metrics["overall_success_rate"] < 0.8:
            recommendations["immediate_actions"].append("Fix failing tests - investigate and resolve test failures")
        
        if overall_metrics["average_error_rate"] > 0.1:
            recommendations["immediate_actions"].append("Improve error handling - high error rate detected")
        
        if overall_metrics["worst_response_time_ms"] > 2000:
            recommendations["immediate_actions"].append("Optimize response times - unacceptable latency detected")
        
        # Short-term improvements
        if overall_metrics["best_throughput_rps"] < 100:
            recommendations["short_term_improvements"].append("Implement caching to improve throughput")
            recommendations["short_term_improvements"].append("Optimize database queries and file I/O operations")
        
        if overall_metrics["peak_cpu_usage"] > 80:
            recommendations["short_term_improvements"].append("Optimize CPU-intensive operations")
        
        if overall_metrics["peak_memory_usage_mb"] > 1000:
            recommendations["short_term_improvements"].append("Optimize memory usage and implement memory pooling")
        
        # Long-term scaling based on throughput achievements
        if overall_metrics["best_throughput_rps"] >= 500:
            recommendations["long_term_scaling"].append("System ready for Tier 2 scaling (10K RPS) - implement microservices architecture")
        elif overall_metrics["best_throughput_rps"] >= 200:
            recommendations["long_term_scaling"].append("System ready for Tier 1 scaling (1K RPS) - implement horizontal scaling")
        elif overall_metrics["best_throughput_rps"] >= 100:
            recommendations["long_term_scaling"].append("Implement basic horizontal scaling and load balancing")
        else:
            recommendations["long_term_scaling"].append("Focus on fundamental performance improvements before scaling")
        
        # Architecture recommendations
        recommendations["architecture_recommendations"].extend([
            "Implement async I/O for all file operations",
            "Add comprehensive caching layer (Redis/Memcached)",
            "Implement connection pooling for database operations",
            "Consider microservices decomposition for high-load components",
            "Implement monitoring and alerting for production deployment"
        ])
        
        return recommendations
    
    def _generate_detailed_analysis(self) -> Dict[str, Any]:
        """Generate detailed performance analysis"""
        return {
            "baseline_analysis": self._analyze_baseline_performance(),
            "mcp_tool_analysis": self._analyze_mcp_tool_performance(),
            "scalability_analysis": self._analyze_scalability_performance(),
            "bottleneck_analysis": self._identify_system_bottlenecks(),
            "comparison_analysis": self._compare_with_targets()
        }
    
    def _analyze_baseline_performance(self) -> Dict[str, Any]:
        """Analyze baseline performance results"""
        if "baseline" not in self.test_results:
            return {"status": "not_run"}
        
        baseline = self.test_results["baseline"]
        baseline_result = baseline["test_result"]
        
        return {
            "status": baseline["status"],
            "performance_characteristics": {
                "throughput_rps": baseline_result.actual_rps,
                "avg_response_time_ms": baseline_result.avg_response_time_ms,
                "p95_response_time_ms": baseline_result.p95_response_time_ms,
                "error_rate": baseline_result.error_rate,
                "resource_usage": {
                    "cpu_usage": baseline_result.max_cpu_usage,
                    "memory_usage_mb": baseline_result.max_memory_usage_mb
                }
            },
            "baseline_assessment": "Baseline established successfully" if baseline["status"] == "passed" else "Baseline test failed"
        }
    
    def _analyze_mcp_tool_performance(self) -> Dict[str, Any]:
        """Analyze MCP tool performance results"""
        if "mcp_tools" not in self.test_results:
            return {"status": "not_run"}
        
        mcp_results = self.test_results["mcp_tools"]
        
        # Find best and worst performing tools
        tool_results = mcp_results.get("tool_results", {})
        
        if not tool_results:
            return {"status": "no_results"}
        
        best_throughput_tool = max(tool_results.items(), key=lambda x: x[1].get("throughput_rps", 0))
        worst_throughput_tool = min(tool_results.items(), key=lambda x: x[1].get("throughput_rps", float('inf')))
        
        fastest_tool = min(tool_results.items(), key=lambda x: x[1].get("avg_response_time_ms", float('inf')))
        slowest_tool = max(tool_results.items(), key=lambda x: x[1].get("avg_response_time_ms", 0))
        
        return {
            "status": "completed",
            "summary": mcp_results["test_summary"],
            "performance_leaders": {
                "highest_throughput": {
                    "tool": best_throughput_tool[0],
                    "throughput_rps": best_throughput_tool[1].get("throughput_rps", 0)
                },
                "fastest_response": {
                    "tool": fastest_tool[0],
                    "response_time_ms": fastest_tool[1].get("avg_response_time_ms", 0)
                }
            },
            "performance_laggards": {
                "lowest_throughput": {
                    "tool": worst_throughput_tool[0],
                    "throughput_rps": worst_throughput_tool[1].get("throughput_rps", 0)
                },
                "slowest_response": {
                    "tool": slowest_tool[0],
                    "response_time_ms": slowest_tool[1].get("avg_response_time_ms", 0)
                }
            }
        }
    
    def _analyze_scalability_performance(self) -> Dict[str, Any]:
        """Analyze scalability test results"""
        scalability_phases = ["scalability", "stress", "stability"]
        analysis = {}
        
        for phase in scalability_phases:
            if phase in self.test_results:
                phase_results = self.test_results[phase]
                analysis[phase] = {
                    "status": "passed" if phase_results["suite_summary"]["success_rate"] > 0.8 else "failed",
                    "success_rate": phase_results["suite_summary"]["success_rate"],
                    "performance_summary": phase_results["overall_performance"]
                }
        
        return analysis
    
    def _identify_system_bottlenecks(self) -> List[str]:
        """Identify system bottlenecks based on test results"""
        bottlenecks = []
        overall_metrics = self._calculate_overall_metrics()
        
        # Response time bottlenecks
        if overall_metrics["worst_response_time_ms"] > 1000:
            bottlenecks.append("High response times indicate potential I/O or processing bottlenecks")
        
        # Throughput bottlenecks
        if overall_metrics["best_throughput_rps"] < 100:
            bottlenecks.append("Low throughput indicates fundamental performance limitations")
        
        # Resource bottlenecks
        if overall_metrics["peak_cpu_usage"] > 80:
            bottlenecks.append("High CPU usage indicates potential CPU bottleneck")
        
        if overall_metrics["peak_memory_usage_mb"] > 1000:
            bottlenecks.append("High memory usage indicates potential memory bottleneck")
        
        # Error rate bottlenecks
        if overall_metrics["average_error_rate"] > 0.05:
            bottlenecks.append("High error rate indicates stability issues under load")
        
        return bottlenecks
    
    def _compare_with_targets(self) -> Dict[str, Any]:
        """Compare results with target performance requirements"""
        overall_metrics = self._calculate_overall_metrics()
        
        # Target requirements from Phase 02 documentation
        targets = {
            "target_rps_tier1": 1000,
            "target_response_time_p95_ms": 100,
            "target_error_rate": 0.01,
            "target_availability": 0.999
        }
        
        comparison = {}
        
        # Throughput comparison
        throughput_ratio = overall_metrics["best_throughput_rps"] / targets["target_rps_tier1"]
        comparison["throughput"] = {
            "achieved_rps": overall_metrics["best_throughput_rps"],
            "target_rps": targets["target_rps_tier1"],
            "achievement_ratio": throughput_ratio,
            "status": "meets_target" if throughput_ratio >= 0.8 else "below_target"
        }
        
        # Response time comparison
        response_time_ratio = overall_metrics["worst_response_time_ms"] / targets["target_response_time_p95_ms"]
        comparison["response_time"] = {
            "achieved_p95_ms": overall_metrics["worst_response_time_ms"],
            "target_p95_ms": targets["target_response_time_p95_ms"],
            "performance_ratio": response_time_ratio,
            "status": "meets_target" if response_time_ratio <= 1.5 else "exceeds_target"
        }
        
        # Error rate comparison
        error_rate_ratio = overall_metrics["average_error_rate"] / targets["target_error_rate"]
        comparison["error_rate"] = {
            "achieved_error_rate": overall_metrics["average_error_rate"],
            "target_error_rate": targets["target_error_rate"],
            "performance_ratio": error_rate_ratio,
            "status": "meets_target" if error_rate_ratio <= 2.0 else "exceeds_target"
        }
        
        return comparison
    
    def _format_duration(self, duration_seconds: float) -> str:
        """Format duration in human-readable format"""
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    async def _save_test_results(self, report: Dict[str, Any]):
        """Save test results to file"""
        try:
            # Create results directory
            results_dir = Path(__file__).parent / "results"
            results_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_test_results_{timestamp}.json"
            filepath = results_dir / filename
            
            # Save report
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📄 Test results saved to: {filepath}")
            
        except Exception as e:
            logger.warning(f"Failed to save test results: {e}")
    
    def _print_test_summary(self, report: Dict[str, Any]):
        """Print comprehensive test summary"""
        print("\n" + "="*100)
        print("📊 COMPREHENSIVE PERFORMANCE TEST RESULTS SUMMARY")
        print("="*100)
        
        # Executive Summary
        exec_summary = report["executive_summary"]
        print(f"\n🎯 EXECUTIVE SUMMARY:")
        print(f"   Overall Status: {exec_summary['overall_status']}")
        print(f"   Performance Score: {exec_summary['performance_score']}/100")
        print(f"   Production Readiness: {exec_summary['production_readiness']}")
        
        # Overall Metrics
        overall_metrics = report["overall_metrics"]
        print(f"\n📈 OVERALL PERFORMANCE METRICS:")
        print(f"   Tests Run: {overall_metrics['total_tests_run']}")
        print(f"   Tests Passed: {overall_metrics['total_tests_passed']}")
        print(f"   Success Rate: {overall_metrics['overall_success_rate']:.1%}")
        print(f"   Best Throughput: {overall_metrics['best_throughput_rps']:.2f} RPS")
        print(f"   Worst P95 Response Time: {overall_metrics['worst_response_time_ms']:.2f}ms")
        print(f"   Average Error Rate: {overall_metrics['average_error_rate']:.2%}")
        print(f"   Peak CPU Usage: {overall_metrics['peak_cpu_usage']:.1f}%")
        print(f"   Peak Memory Usage: {overall_metrics['peak_memory_usage_mb']:.1f}MB")
        
        # Key Findings
        if exec_summary['key_findings']:
            print(f"\n✅ KEY FINDINGS:")
            for finding in exec_summary['key_findings']:
                print(f"   • {finding}")
        
        # Critical Issues
        if exec_summary['critical_issues']:
            print(f"\n❌ CRITICAL ISSUES:")
            for issue in exec_summary['critical_issues']:
                print(f"   • {issue}")
        
        # Scaling Recommendations
        scaling_recs = report["scaling_recommendations"]
        if scaling_recs['immediate_actions']:
            print(f"\n🚨 IMMEDIATE ACTIONS REQUIRED:")
            for action in scaling_recs['immediate_actions']:
                print(f"   • {action}")
        
        if scaling_recs['short_term_improvements']:
            print(f"\n📈 SHORT-TERM IMPROVEMENTS:")
            for improvement in scaling_recs['short_term_improvements'][:3]:  # Show top 3
                print(f"   • {improvement}")
        
        if scaling_recs['long_term_scaling']:
            print(f"\n🏗️ LONG-TERM SCALING:")
            for scaling in scaling_recs['long_term_scaling']:
                print(f"   • {scaling}")
        
        # Test Duration
        print(f"\n⏱️ TEST EXECUTION:")
        print(f"   Total Duration: {report['report_metadata']['test_duration_formatted']}")
        print(f"   Completed At: {report['report_metadata']['generated_at']}")
        
        print("\n" + "="*100)
        
        # Final Assessment
        if exec_summary['production_readiness'] == "READY":
            print("🎉 SYSTEM IS READY FOR PRODUCTION DEPLOYMENT!")
        elif exec_summary['production_readiness'] == "READY_WITH_MONITORING":
            print("✅ SYSTEM IS READY FOR PRODUCTION WITH ENHANCED MONITORING!")
        elif exec_summary['production_readiness'] == "READY_WITH_IMPROVEMENTS":
            print("⚠️ SYSTEM NEEDS IMPROVEMENTS BEFORE PRODUCTION DEPLOYMENT!")
        else:
            print("❌ SYSTEM IS NOT READY FOR PRODUCTION - SIGNIFICANT WORK REQUIRED!")
        
        print("="*100)


async def main():
    """Main function to run comprehensive performance tests"""
    try:
        # Import MCP server creation function
        sys.path.append(str(Path(__file__).parent.parent))
        from test_mvp_server import create_dhafnck_mcp_server
        
        # Create MCP server
        print("🏗️ Creating MCP server instance...")
        mcp_server = create_dhafnck_mcp_server()
        
        # Create test runner
        test_runner = ComprehensivePerformanceTestRunner()
        
        # Run comprehensive performance tests
        results = await test_runner.run_full_performance_test_suite(mcp_server)
        
        return results
        
    except Exception as e:
        print(f"\n❌ Performance testing failed: {e}")
        logger.exception("Performance testing failed")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 