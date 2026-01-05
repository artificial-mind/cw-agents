"""
MCP Tool Factory - Wraps MCP tools as CrewAI tools.
Provides all 11 MCP tools from cw-ai-server to CrewAI agents.
"""
import logging
import asyncio
from typing import Any, Dict, List, Optional
from crewai.tools import tool

from ..infrastructure.mcp_pool import get_mcp_pool

logger = logging.getLogger(__name__)


# ============================================================================
# Tracking Tools
# ============================================================================

@tool("Track Shipment")
def track_shipment(shipment_id: str) -> str:
    """Track a shipment and get current status, location, and estimated delivery.
    
    Args:
        shipment_id: Unique identifier for the shipment
    
    Returns:
        Tracking information as string
    """
    async def _async_track():
        try:
            pool = await get_mcp_pool()
            result = await pool.call_tool("track_shipment", {"shipment_id": shipment_id})
            return str(result)
        except Exception as e:
            logger.error(f"Error tracking shipment {shipment_id}: {e}")
            return f"Error: {str(e)}"
    
    return asyncio.run(_async_track())


@tool("Search Shipments")
def search_shipments(query: str, limit: int = 50) -> str:
    """Search shipments by various criteria (status, customer, date range, etc.).
    
    Args:
        query: Search criteria as JSON string (e.g., '{"status": "in_transit"}')
        limit: Maximum number of results to return
    
    Returns:
        Search results as string
    """
    async def _async_search():
        try:
            import json
            query_dict = json.loads(query) if isinstance(query, str) else query
            pool = await get_mcp_pool()
            result = await pool.call_tool("search_shipments", {"query": query_dict, "limit": limit})
            return str(result)
        except Exception as e:
            logger.error(f"Error searching shipments: {e}")
            return f"Error: {str(e)}"
    
    return asyncio.run(_async_search())


@tool("Update ETA")
def update_eta(shipment_id: str, new_eta: str, reason: str) -> str:
    """Update the estimated time of arrival for a shipment.
    
    Args:
        shipment_id: Shipment ID to update
        new_eta: New estimated time of arrival (ISO format)
        reason: Reason for ETA update
    
    Returns:
        Update confirmation as string
    """
    async def _async_update():
        try:
            pool = await get_mcp_pool()
            result = await pool.call_tool("update_eta", {
                "shipment_id": shipment_id,
                "new_eta": new_eta,
                "reason": reason
            })
            return str(result)
        except Exception as e:
            logger.error(f"Error updating ETA for {shipment_id}: {e}")
            return f"Error: {str(e)}"
    
    return asyncio.run(_async_update())


@tool("Calculate Route")
def calculate_route(origin: str, destination: str, mode: str = "driving", constraints: str = "{}") -> str:
    """Calculate optimal route between two locations with mode and constraints.
    
    Args:
        origin: Origin location (address or coordinates)
        destination: Destination location (address or coordinates)
        mode: Transportation mode (driving, truck, rail, ship)
        constraints: Route constraints as JSON string (e.g., '{"avoid_tolls": true}')
    
    Returns:
        Route information as string
    """
    async def _async_calculate():
        try:
            import json
            constraints_dict = json.loads(constraints) if isinstance(constraints, str) else constraints
            pool = await get_mcp_pool()
            result = await pool.call_tool("calculate_route", {
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "constraints": constraints_dict
            })
            return str(result)
        except Exception as e:
            logger.error(f"Error calculating route: {e}")
            return f"Error: {str(e)}"
    
    return asyncio.run(_async_calculate())


@tool("Optimize Route")
def optimize_route(waypoints: str, start_location: str, end_location: str = "", optimization_goal: str = "shortest") -> str:
    """Optimize route for multiple waypoints to minimize distance/time/cost.
    
    Args:
        waypoints: List of locations to visit as JSON array string
        start_location: Starting location
        end_location: Ending location (if different from start)
        optimization_goal: Optimization goal (shortest, fastest, cheapest)
    
    Returns:
        Optimized route as string
    """
    async def _async_optimize():
        try:
            import json
            waypoints_list = json.loads(waypoints) if isinstance(waypoints, str) else waypoints
            pool = await get_mcp_pool()
            result = await pool.call_tool("optimize_route", {
                "waypoints": waypoints_list,
                "start_location": start_location,
                "end_location": end_location or None,
                "optimization_goal": optimization_goal
            })
            return str(result)
        except Exception as e:
            logger.error(f"Error optimizing route: {e}")
            return f"Error: {str(e)}"
    
    return asyncio.run(_async_optimize())


@tool("Find Alternatives")
def find_alternatives(origin: str, destination: str, current_issue: str) -> str:
    """Find alternative routes when primary route has issues.
    
    Args:
        origin: Origin location
        destination: Destination location
        current_issue: Issue with current route
    
    Returns:
        Alternative routes as string
    """
    async def _async_find():
        try:
            pool = await get_mcp_pool()
            result = await pool.call_tool("find_alternatives", {
                "origin": origin,
                "destination": destination,
                "current_issue": current_issue
            })
            return str(result)
        except Exception as e:
            logger.error(f"Error finding alternatives: {e}")
            return f"Error: {str(e)}"
    
    return asyncio.run(_async_find())


@tool("Handle Exception")
def handle_exception(shipment_id: str, exception_type: str, description: str, severity: str = "medium") -> str:
    """Handle and log shipping exceptions (delays, damage, lost items, etc.).
    
    Args:
        shipment_id: Shipment ID with exception
        exception_type: Type of exception (delay, damage, lost, etc.)
        description: Description of the exception
        severity: Severity level (low, medium, high, critical)
    
    Returns:
        Exception handling result as string
    """
    async def _async_handle():
        try:
            pool = await get_mcp_pool()
            result = await pool.call_tool("handle_exception", {
                "shipment_id": shipment_id,
                "exception_type": exception_type,
                "description": description,
                "severity": severity
            })
            return str(result)
        except Exception as e:
            logger.error(f"Error handling exception for {shipment_id}: {e}")
            return f"Error: {str(e)}"
    
    return asyncio.run(_async_handle())


@tool("Resolve Issue")
def resolve_issue(exception_id: str, resolution: str, notes: str) -> str:
    """Mark an exception/issue as resolved with resolution details.
    
    Args:
        exception_id: Exception/issue ID to resolve
        resolution: Resolution action taken
        notes: Additional notes about the resolution
    
    Returns:
        Resolution confirmation as string
    """
    async def _async_resolve():
        try:
            pool = await get_mcp_pool()
            result = await pool.call_tool("resolve_issue", {
                "exception_id": exception_id,
                "resolution": resolution,
                "notes": notes
            })
            return str(result)
        except Exception as e:
            logger.error(f"Error resolving issue {exception_id}: {e}")
            return f"Error: {str(e)}"
    
    return asyncio.run(_async_resolve())


@tool("Escalate Problem")
def escalate_problem(exception_id: str, escalation_level: str, reason: str) -> str:
    """Escalate unresolved exception to higher management level.
    
    Args:
        exception_id: Exception/issue ID to escalate
        escalation_level: Escalation level (manager, director, executive)
        reason: Reason for escalation
    
    Returns:
        Escalation confirmation as string
    """
    async def _async_escalate():
        try:
            pool = await get_mcp_pool()
            result = await pool.call_tool("escalate_problem", {
                "exception_id": exception_id,
                "escalation_level": escalation_level,
                "reason": reason
            })
            return str(result)
        except Exception as e:
            logger.error(f"Error escalating problem {exception_id}: {e}")
            return f"Error: {str(e)}"
    
    return asyncio.run(_async_escalate())


@tool("Get Analytics")
def get_analytics(report_type: str, start_date: str, end_date: str, filters: str = "{}") -> str:
    """Get analytics and reports for specified date range and criteria.
    
    Args:
        report_type: Type of report (shipments, exceptions, performance, etc.)
        start_date: Start date for analysis (ISO format)
        end_date: End date for analysis (ISO format)
        filters: Additional filters as JSON string
    
    Returns:
        Analytics data as string
    """
    async def _async_analytics():
        try:
            import json
            filters_dict = json.loads(filters) if isinstance(filters, str) else filters
            pool = await get_mcp_pool()
            result = await pool.call_tool("get_analytics", {
                "report_type": report_type,
                "start_date": start_date,
                "end_date": end_date,
                "filters": filters_dict
            })
            return str(result)
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return f"Error: {str(e)}"
    
    return asyncio.run(_async_analytics())


@tool("Query Database")
def query_database(query_type: str, parameters: str) -> str:
    """Query database for specific information (shipments, customers, carriers, etc.).
    
    Args:
        query_type: Type of query (shipments, customers, carriers, etc.)
        parameters: Query parameters as JSON string
    
    Returns:
        Query results as string
    """
    async def _async_query():
        try:
            import json
            parameters_dict = json.loads(parameters) if isinstance(parameters, str) else parameters
            pool = await get_mcp_pool()
            result = await pool.call_tool("query_database", {
                "query_type": query_type,
                "parameters": parameters_dict
            })
            return str(result)
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            return f"Error: {str(e)}"
    
    return asyncio.run(_async_query())


class MCPToolFactory:
    """Factory for creating MCP tool instances."""
    
    TRACKING_TOOLS = [track_shipment, search_shipments, update_eta]
    ROUTING_TOOLS = [calculate_route, optimize_route, find_alternatives]
    EXCEPTION_TOOLS = [handle_exception, resolve_issue, escalate_problem]
    ANALYTICS_TOOLS = [get_analytics, query_database]
    ALL_TOOLS = [*TRACKING_TOOLS, *ROUTING_TOOLS, *EXCEPTION_TOOLS, *ANALYTICS_TOOLS]
    
    @classmethod
    def get_tracking_tools(cls) -> List:
        """Get all tracking tools."""
        return cls.TRACKING_TOOLS.copy()
    
    @classmethod
    def get_routing_tools(cls) -> List:
        """Get all routing tools."""
        return cls.ROUTING_TOOLS.copy()
    
    @classmethod
    def get_exception_tools(cls) -> List:
        """Get all exception handling tools."""
        return cls.EXCEPTION_TOOLS.copy()
    
    @classmethod
    def get_analytics_tools(cls) -> List:
        """Get all analytics tools."""
        return cls.ANALYTICS_TOOLS.copy()
    
    @classmethod
    def get_all_tools(cls) -> List:
        """Get all available tools."""
        return cls.ALL_TOOLS.copy()
    
    @classmethod
    def get_tools_by_category(cls, categories: List[str]) -> List:
        """
        Get tools by categories.
        
        Args:
            categories: List of category names ("tracking", "routing", "exception", "analytics")
        
        Returns:
            List of tool instances
        """
        tools = []
        for category in categories:
            if category == "tracking":
                tools.extend(cls.get_tracking_tools())
            elif category == "routing":
                tools.extend(cls.get_routing_tools())
            elif category == "exception":
                tools.extend(cls.get_exception_tools())
            elif category == "analytics":
                tools.extend(cls.get_analytics_tools())
            else:
                logger.warning(f"Unknown tool category: {category}")
        
        return tools
