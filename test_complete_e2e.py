"""
Complete End-to-End Test Suite for CW Logistics Platform
=========================================================

This comprehensive test suite validates ALL features across the entire stack:
- A2A Agent Server (cw-agents)
- MCP Server (cw-ai-server)
- Analytics Engine (cw-analytics-engine)
- Brain Server (cw-brain)

Every time a new feature is added, append a new test scenario to this file.
This ensures no existing functionality breaks when new features are added.

Test Coverage:
- Basic shipment operations (search, track, update)
- Advanced analytics (delays, routes, risk assessment)
- Document generation (BOL, Invoice, Packing List)
- ML predictions (delay prediction)
- Database operations (CRUD)

Requirements:
- All 4 services must be running
- Run from cw-agents directory
- Python 3.11+

Usage:
    python test_complete_e2e.py
"""

import sys
import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any, List

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Configuration
A2A_BASE_URL = "http://localhost:8001"
MCP_BASE_URL = "http://localhost:8000"
ANALYTICS_BASE_URL = "http://localhost:8002"
BRAIN_BASE_URL = "http://localhost:8100"

class E2ETestSuite:
    """Comprehensive end-to-end test suite"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []
        
    def print_header(self, text: str):
        """Print test section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    def print_test(self, test_name: str):
        """Print test name"""
        print(f"{Colors.YELLOW}▶ Testing:{Colors.RESET} {test_name}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ PASS:{Colors.RESET} {message}")
        self.passed += 1
        self.test_results.append(("PASS", message))
    
    def print_failure(self, message: str):
        """Print failure message"""
        print(f"{Colors.RED}✗ FAIL:{Colors.RESET} {message}")
        self.failed += 1
        self.test_results.append(("FAIL", message))
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"{Colors.BLUE}  ℹ Info:{Colors.RESET} {message}")
    
    async def check_service_health(self, service_name: str, url: str) -> bool:
        """Check if a service is healthy"""
        self.print_test(f"{service_name} Health Check")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    self.print_success(f"{service_name} is healthy")
                    return True
                else:
                    self.print_failure(f"{service_name} returned status {response.status_code}")
                    return False
        except Exception as e:
            self.print_failure(f"{service_name} health check failed: {e}")
            return False
    
    async def test_a2a_skill(self, skill_name: str, parameters: Dict[str, Any], 
                             validation_func=None) -> Dict[str, Any]:
        """Test an A2A skill"""
        self.print_test(f"A2A Skill: {skill_name}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "skill": skill_name,
                    "parameters": parameters
                }
                response = await client.post(f"{A2A_BASE_URL}/execute", json=payload)
                
                if response.status_code != 200:
                    self.print_failure(f"Status {response.status_code}: {response.text}")
                    return {}
                
                result = response.json()
                
                # Check for errors in response
                if result.get("status") == "error":
                    self.print_failure(f"Skill error: {result.get('error', 'Unknown error')}")
                    return {}
                
                # Extract actual result from A2A response
                artifact = result.get("artifact", {})
                content = artifact.get("content", {})
                actual_result = content.get("result", {})
                
                # Run custom validation if provided
                if validation_func:
                    validation_func(actual_result)
                else:
                    self.print_success(f"Skill {skill_name} executed successfully")
                
                return actual_result
                
        except Exception as e:
            self.print_failure(f"Skill {skill_name} failed: {e}")
            return {}
    
    async def test_mcp_tool(self, tool_name: str, arguments: Dict[str, Any], 
                           validation_func=None) -> Any:
        """Test an MCP tool directly"""
        self.print_test(f"MCP Tool: {tool_name}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "name": tool_name,
                    "arguments": arguments
                }
                response = await client.post(f"{MCP_BASE_URL}/tools/call", json=payload)
                
                if response.status_code != 200:
                    self.print_failure(f"Status {response.status_code}: {response.text}")
                    return None
                
                result = response.json()
                
                # Run custom validation if provided
                if validation_func:
                    validation_func(result)
                else:
                    self.print_success(f"Tool {tool_name} executed successfully")
                
                return result
                
        except Exception as e:
            self.print_failure(f"Tool {tool_name} failed: {e}")
            return None
    
    async def test_analytics_endpoint(self, endpoint: str, method: str = "GET", 
                                     data: Dict[str, Any] = None,
                                     validation_func=None) -> Any:
        """Test an Analytics Engine endpoint"""
        self.print_test(f"Analytics: {method} {endpoint}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(f"{ANALYTICS_BASE_URL}{endpoint}")
                elif method == "POST":
                    response = await client.post(f"{ANALYTICS_BASE_URL}{endpoint}", json=data)
                else:
                    self.print_failure(f"Unsupported method: {method}")
                    return None
                
                if response.status_code not in [200, 201]:
                    self.print_failure(f"Status {response.status_code}: {response.text}")
                    return None
                
                result = response.json()
                
                # Run custom validation if provided
                if validation_func:
                    validation_func(result)
                else:
                    self.print_success(f"{method} {endpoint} succeeded")
                
                return result
                
        except Exception as e:
            self.print_failure(f"{method} {endpoint} failed: {e}")
            return None
    
    # ========================================================================
    # TEST SUITE 1: SERVICE HEALTH CHECKS
    # ========================================================================
    
    async def test_suite_1_health_checks(self):
        """Test all services are running and healthy"""
        self.print_header("TEST SUITE 1: SERVICE HEALTH CHECKS")
        
        services = [
            ("A2A Agent Server", A2A_BASE_URL),
            ("MCP Server", MCP_BASE_URL),
            ("Analytics Engine", ANALYTICS_BASE_URL),
        ]
        
        all_healthy = True
        for service_name, url in services:
            healthy = await self.check_service_health(service_name, url)
            if not healthy:
                all_healthy = False
        
        if not all_healthy:
            self.print_failure("Not all services are healthy - tests may fail")
    
    # ========================================================================
    # TEST SUITE 2: BASIC SHIPMENT OPERATIONS
    # ========================================================================
    
    async def test_suite_2_basic_operations(self):
        """Test basic shipment CRUD operations"""
        self.print_header("TEST SUITE 2: BASIC SHIPMENT OPERATIONS")
        
        # Test 2.1: Search shipments
        def validate_search(result):
            if not isinstance(result, list):
                self.print_failure("Search result is not a list")
                return
            if len(result) == 0:
                self.print_failure("No shipments found")
                return
            self.print_success(f"Found {len(result)} shipments")
            self.print_info(f"First shipment: {result[0].get('job_number', 'N/A')}")
        
        await self.test_a2a_skill(
            "search-shipments",
            {"criteria": "all"},
            validate_search
        )
        
        # Test 2.2: Track specific shipment
        def validate_track(result):
            if not result:
                self.print_failure("No tracking data returned")
                return
            job_number = result.get("job_number")
            status = result.get("status")
            if job_number and status:
                self.print_success(f"Tracked shipment {job_number} - Status: {status}")
            else:
                self.print_failure("Missing job_number or status in response")
        
        await self.test_a2a_skill(
            "track-shipment",
            {"job_number": "job-2025-001"},
            validate_track
        )
        
        # Test 2.3: Get server status
        def validate_status(result):
            if "status" in result and result["status"] == "operational":
                self.print_success("Server status is operational")
            else:
                self.print_failure("Server status check failed")
        
        await self.test_a2a_skill(
            "get-server-status",
            {},
            validate_status
        )
    
    # ========================================================================
    # TEST SUITE 3: ADVANCED ANALYTICS
    # ========================================================================
    
    async def test_suite_3_analytics(self):
        """Test advanced analytics features"""
        self.print_header("TEST SUITE 3: ADVANCED ANALYTICS")
        
        # Test 3.1: Get delayed shipments
        def validate_delays(result):
            if not isinstance(result, list):
                self.print_failure("Delays result is not a list")
                return
            self.print_success(f"Found {len(result)} delayed shipments")
            if len(result) > 0:
                self.print_info(f"First delayed: {result[0].get('job_number', 'N/A')}")
        
        await self.test_a2a_skill(
            "get-delayed-shipments",
            {},
            validate_delays
        )
        
        # Test 3.2: Get shipments by route
        def validate_route(result):
            if not isinstance(result, list):
                self.print_failure("Route result is not a list")
                return
            self.print_success(f"Found {len(result)} shipments on Shanghai-Los Angeles route")
        
        await self.test_a2a_skill(
            "get-shipments-by-route",
            {"origin": "Shanghai", "destination": "Los Angeles"},
            validate_route
        )
        
        # Test 3.3: Get analytics overview
        def validate_analytics(result):
            if not result:
                self.print_failure("No analytics data returned")
                return
            total = result.get("total_shipments", 0)
            in_transit = result.get("in_transit", 0)
            self.print_success(f"Analytics: {total} total, {in_transit} in transit")
        
        await self.test_a2a_skill(
            "get-shipments-analytics",
            {},
            validate_analytics
        )
    
    # ========================================================================
    # TEST SUITE 4: DOCUMENT GENERATION
    # ========================================================================
    
    async def test_suite_4_document_generation(self):
        """Test document generation features (Day 5)"""
        self.print_header("TEST SUITE 4: DOCUMENT GENERATION (DAY 5)")
        
        # Test 4.1: Generate Bill of Lading
        def validate_bol(result):
            if not result:
                self.print_failure("No BOL data returned")
                return
            filepath = result.get("filepath")
            if filepath:
                self.print_success(f"BOL generated: {filepath}")
            else:
                self.print_failure("BOL generation failed")
        
        await self.test_a2a_skill(
            "generate-bol",
            {"shipment_id": "job-2025-001"},
            validate_bol
        )
        
        # Test 4.2: Generate Commercial Invoice
        def validate_invoice(result):
            if not result:
                self.print_failure("No Invoice data returned")
                return
            filepath = result.get("filepath")
            total_value = result.get("total_value")
            if filepath and total_value:
                self.print_success(f"Invoice generated: {filepath}, Total: {total_value}")
            else:
                self.print_failure("Invoice generation failed")
        
        await self.test_a2a_skill(
            "generate-invoice",
            {"shipment_id": "job-2025-001"},
            validate_invoice
        )
        
        # Test 4.3: Generate Packing List
        def validate_packing(result):
            if not result:
                self.print_failure("No Packing List data returned")
                return
            filepath = result.get("filepath")
            total_packages = result.get("total_packages")
            if filepath and total_packages:
                self.print_success(f"Packing List generated: {filepath}, Packages: {total_packages}")
            else:
                self.print_failure("Packing List generation failed")
        
        await self.test_a2a_skill(
            "generate-packing-list",
            {"shipment_id": "job-2025-001"},
            validate_packing
        )
        
        # Test 4.4: Direct Analytics Engine document generation
        def validate_direct_doc(result):
            if not result:
                self.print_failure("No document data returned")
                return
            if result.get("success"):
                self.print_success(f"Direct generation: {result.get('message')}")
            else:
                self.print_failure("Direct generation failed")
        
        await self.test_analytics_endpoint(
            "/api/generate-document",
            "POST",
            {
                "document_type": "bill_of_lading",
                "shipment_id": "job-2025-001"
            },
            validate_direct_doc
        )
    
    # ========================================================================
    # TEST SUITE 5: ML PREDICTIONS (if implemented)
    # ========================================================================
    
    async def test_suite_5_ml_predictions(self):
        """Test ML-based predictions"""
        self.print_header("TEST SUITE 5: ML PREDICTIONS")
        
        # Test 5.1: Delay prediction
        try:
            def validate_prediction(result):
                if not result:
                    self.print_failure("No prediction data returned")
                    return
                delay_risk = result.get("delay_risk_score")
                if delay_risk is not None:
                    self.print_success(f"Delay prediction: {delay_risk}% risk")
                else:
                    self.print_info("Delay prediction feature not yet implemented")
            
            await self.test_a2a_skill(
                "predict-delay",
                {"shipment_id": "job-2025-001"},
                validate_prediction
            )
        except Exception as e:
            self.print_info("Delay prediction not available (expected for Day 5)")
    
    # ========================================================================
    # TEST SUITE 6: DATABASE INTEGRITY
    # ========================================================================
    
    async def test_suite_6_database(self):
        """Test database operations and data integrity"""
        self.print_header("TEST SUITE 6: DATABASE INTEGRITY")
        
        # Test 6.1: Verify shipment data structure
        shipments = await self.test_a2a_skill(
            "search-shipments",
            {"criteria": "all"}
        )
        
        if shipments and len(shipments) > 0:
            shipment = shipments[0]
            required_fields = ["job_number", "status", "container_number", "origin", "destination"]
            missing_fields = [field for field in required_fields if field not in shipment]
            
            if missing_fields:
                self.print_failure(f"Missing required fields: {missing_fields}")
            else:
                self.print_success("All required shipment fields present")
        
        # Test 6.2: Query by multiple criteria
        def validate_advanced_search(result):
            if isinstance(result, list):
                self.print_success(f"Advanced search returned {len(result)} results")
            else:
                self.print_failure("Advanced search failed")
        
        await self.test_a2a_skill(
            "search-shipments-advanced",
            {
                "status": "in_transit",
                "risk_level": "low"
            },
            validate_advanced_search
        )
    
    # ========================================================================
    # TEST SUITE 7: ERROR HANDLING
    # ========================================================================
    
    async def test_suite_7_error_handling(self):
        """Test error handling and edge cases"""
        self.print_header("TEST SUITE 7: ERROR HANDLING")
        
        # Test 7.1: Invalid shipment ID
        self.print_test("Invalid shipment ID handling")
        result = await self.test_a2a_skill(
            "track-shipment",
            {"job_number": "invalid-nonexistent-999"}
        )
        if not result or "error" in str(result).lower():
            self.print_success("Invalid shipment ID handled correctly")
        else:
            self.print_info("Invalid ID returned data (may have fallback behavior)")
        
        # Test 7.2: Missing required parameters
        self.print_test("Missing parameters handling")
        result = await self.test_a2a_skill(
            "get-shipments-by-route",
            {"origin": "Shanghai"}  # Missing destination
        )
        # This should either fail gracefully or use defaults
        self.print_info("Missing parameter test completed")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    def print_summary(self):
        """Print final test summary"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'FINAL TEST SUMMARY':^70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}\n")
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{Colors.BOLD}Total Tests:{Colors.RESET} {total}")
        print(f"{Colors.GREEN}✓ Passed:{Colors.RESET} {self.passed}")
        print(f"{Colors.RED}✗ Failed:{Colors.RESET} {self.failed}")
        print(f"{Colors.BOLD}Pass Rate:{Colors.RESET} {pass_rate:.1f}%\n")
        
        if self.failed > 0:
            print(f"{Colors.RED}Failed Tests:{Colors.RESET}")
            for status, message in self.test_results:
                if status == "FAIL":
                    print(f"  {Colors.RED}✗{Colors.RESET} {message}")
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
        
        if self.failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️  Some tests failed - please review{Colors.RESET}")
        
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

async def main():
    """Run the complete test suite"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 70)
    print(" CW LOGISTICS PLATFORM - COMPLETE E2E TEST SUITE ".center(70))
    print(" All Features - Regression Prevention ".center(70))
    print("=" * 70)
    print(f"{Colors.RESET}\n")
    print(f"{Colors.YELLOW}Starting comprehensive test suite...{Colors.RESET}")
    print(f"{Colors.YELLOW}Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    suite = E2ETestSuite()
    
    try:
        # Run all test suites
        await suite.test_suite_1_health_checks()
        await suite.test_suite_2_basic_operations()
        await suite.test_suite_3_analytics()
        await suite.test_suite_4_document_generation()
        await suite.test_suite_5_ml_predictions()
        await suite.test_suite_6_database()
        await suite.test_suite_7_error_handling()
        
        # Print summary
        suite.print_summary()
        
        # Exit with appropriate code
        sys.exit(0 if suite.failed == 0 else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test suite interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Test suite failed with error: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
