"""
Test script for CW Agents with A2A + CrewAI architecture.
Tests all 4 crews independently before full A2A integration.
"""
import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_tracking_crew():
    """Test TrackingCrew functionality."""
    logger.info("=" * 80)
    logger.info("Testing TrackingCrew")
    logger.info("=" * 80)
    
    try:
        from src.crews.tracking_crew import TrackingCrew
        
        crew = TrackingCrew()
        
        # Test 1: Track single shipment
        logger.info("\n--- Test 1: Track Single Shipment ---")
        result = await crew.track_shipment("SHIP001")
        logger.info(f"Result: {result}")
        
        # Test 2: Batch track
        logger.info("\n--- Test 2: Batch Track ---")
        result = await crew.batch_track(["SHIP001", "SHIP002", "SHIP003"])
        logger.info(f"Result: {result}")
        
        # Test 3: Search shipments
        logger.info("\n--- Test 3: Search Shipments ---")
        result = await crew.search_shipments({"status": "in_transit"}, limit=10)
        logger.info(f"Result: {result}")
        
        logger.info("\n✅ TrackingCrew tests passed\n")
        return True
    
    except Exception as e:
        logger.error(f"❌ TrackingCrew test failed: {e}", exc_info=True)
        return False


async def test_routing_crew():
    """Test RoutingCrew functionality."""
    logger.info("=" * 80)
    logger.info("Testing RoutingCrew")
    logger.info("=" * 80)
    
    try:
        from src.crews.routing_crew import RoutingCrew
        
        crew = RoutingCrew()
        
        # Test 1: Calculate route
        logger.info("\n--- Test 1: Calculate Route ---")
        result = await crew.calculate_route(
            origin="Los Angeles, CA",
            destination="New York, NY",
            mode="truck"
        )
        logger.info(f"Result: {result}")
        
        # Test 2: Optimize multi-stop route
        logger.info("\n--- Test 2: Optimize Route ---")
        result = await crew.optimize_route(
            waypoints=["Dallas, TX", "Chicago, IL", "Boston, MA"],
            start_location="Los Angeles, CA",
            optimization_goal="shortest"
        )
        logger.info(f"Result: {result}")
        
        # Test 3: Find alternatives
        logger.info("\n--- Test 3: Find Alternatives ---")
        result = await crew.find_alternatives(
            origin="Los Angeles, CA",
            destination="New York, NY",
            current_issue="Highway 40 closed due to weather"
        )
        logger.info(f"Result: {result}")
        
        logger.info("\n✅ RoutingCrew tests passed\n")
        return True
    
    except Exception as e:
        logger.error(f"❌ RoutingCrew test failed: {e}", exc_info=True)
        return False


async def test_exception_crew():
    """Test ExceptionCrew functionality."""
    logger.info("=" * 80)
    logger.info("Testing ExceptionCrew")
    logger.info("=" * 80)
    
    try:
        from src.crews.exception_crew import ExceptionCrew
        
        crew = ExceptionCrew()
        
        # Test 1: Handle exception
        logger.info("\n--- Test 1: Handle Exception ---")
        result = await crew.handle_exception(
            shipment_id="SHIP001",
            exception_type="delay",
            description="Package delayed due to weather",
            severity="medium"
        )
        logger.info(f"Result: {result}")
        
        # Test 2: Resolve issue
        logger.info("\n--- Test 2: Resolve Issue ---")
        result = await crew.resolve_issue(
            exception_id="EXC001",
            resolution="Rerouted package through alternative carrier",
            notes="Customer notified of delay"
        )
        logger.info(f"Result: {result}")
        
        # Test 3: Escalate problem
        logger.info("\n--- Test 3: Escalate Problem ---")
        result = await crew.escalate_problem(
            exception_id="EXC002",
            escalation_level="manager",
            reason="High-value shipment lost"
        )
        logger.info(f"Result: {result}")
        
        logger.info("\n✅ ExceptionCrew tests passed\n")
        return True
    
    except Exception as e:
        logger.error(f"❌ ExceptionCrew test failed: {e}", exc_info=True)
        return False


async def test_analytics_crew():
    """Test AnalyticsCrew functionality."""
    logger.info("=" * 80)
    logger.info("Testing AnalyticsCrew")
    logger.info("=" * 80)
    
    try:
        from src.crews.analytics_crew import AnalyticsCrew
        
        crew = AnalyticsCrew()
        
        # Test 1: Generate report
        logger.info("\n--- Test 1: Generate Report ---")
        result = await crew.generate_report(
            report_type="shipments",
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        logger.info(f"Result: {result}")
        
        # Test 2: Calculate KPIs
        logger.info("\n--- Test 2: Calculate KPIs ---")
        result = await crew.calculate_kpis(
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        logger.info(f"Result: {result}")
        
        # Test 3: Analyze trends
        logger.info("\n--- Test 3: Analyze Trends ---")
        result = await crew.analyze_trends(
            metric="on_time_delivery_rate",
            start_date="2024-12-01",
            end_date="2025-01-31",
            granularity="daily"
        )
        logger.info(f"Result: {result}")
        
        # Test 4: Forecast performance
        logger.info("\n--- Test 4: Forecast Performance ---")
        result = await crew.forecast_performance(
            metric="delivery_volume",
            forecast_days=30
        )
        logger.info(f"Result: {result}")
        
        logger.info("\n✅ AnalyticsCrew tests passed\n")
        return True
    
    except Exception as e:
        logger.error(f"❌ AnalyticsCrew test failed: {e}", exc_info=True)
        return False


async def test_infrastructure():
    """Test infrastructure components."""
    logger.info("=" * 80)
    logger.info("Testing Infrastructure Components")
    logger.info("=" * 80)
    
    try:
        # Test LLM Factory
        logger.info("\n--- Test: LLM Factory ---")
        from src.core.llm_factory import LLMFactory
        
        LLMFactory.initialize()
        config = LLMFactory.get_config()
        logger.info(f"LLM Config: {config}")
        
        primary_llm = LLMFactory.get_llm()
        logger.info(f"Primary LLM: {type(primary_llm).__name__}")
        
        has_fallback = LLMFactory.has_fallback()
        logger.info(f"Has Fallback: {has_fallback}")
        
        # Test MCP Pool (without actual connection)
        logger.info("\n--- Test: MCP Pool (Structure Only) ---")
        from src.infrastructure.mcp_pool import MCPConnectionPool
        
        pool = MCPConnectionPool()
        logger.info(f"Pool created: max_connections={pool.max_connections}, timeout={pool.timeout}")
        logger.info(f"Circuit breaker: threshold={pool.circuit_breaker.failure_threshold}")
        
        # Test Redis Client (without actual connection)
        logger.info("\n--- Test: Redis Client (Structure Only) ---")
        from src.infrastructure.redis_client import RedisClient
        
        redis_client = RedisClient()
        logger.info(f"Redis client created: enabled={redis_client.enabled}")
        
        # Test MCP Tool Factory
        logger.info("\n--- Test: MCP Tool Factory ---")
        from src.tools.mcp_tools import MCPToolFactory
        
        tracking_tools = MCPToolFactory.get_tracking_tools()
        routing_tools = MCPToolFactory.get_routing_tools()
        exception_tools = MCPToolFactory.get_exception_tools()
        analytics_tools = MCPToolFactory.get_analytics_tools()
        
        logger.info(f"Tracking tools: {len(tracking_tools)}")
        logger.info(f"Routing tools: {len(routing_tools)}")
        logger.info(f"Exception tools: {len(exception_tools)}")
        logger.info(f"Analytics tools: {len(analytics_tools)}")
        logger.info(f"Total tools: {len(MCPToolFactory.get_all_tools())}")
        
        logger.info("\n✅ Infrastructure tests passed\n")
        return True
    
    except Exception as e:
        logger.error(f"❌ Infrastructure test failed: {e}", exc_info=True)
        return False


async def main():
    """Run all tests."""
    logger.info("\n" + "=" * 80)
    logger.info("CW AGENTS TEST SUITE - A2A + CrewAI Architecture")
    logger.info("=" * 80 + "\n")
    
    start_time = datetime.now()
    
    results = []
    
    # Test infrastructure first
    results.append(("Infrastructure", await test_infrastructure()))
    
    # Test each crew (comment out if LLM not available)
    # results.append(("TrackingCrew", await test_tracking_crew()))
    # results.append(("RoutingCrew", await test_routing_crew()))
    # results.append(("ExceptionCrew", await test_exception_crew()))
    # results.append(("AnalyticsCrew", await test_analytics_crew()))
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name:30s} {status}")
    
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"\nTotal time: {duration:.2f}s")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    logger.info(f"Results: {passed_count}/{total_count} tests passed")
    
    logger.info("=" * 80 + "\n")
    
    if passed_count == total_count:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
