"""
Simple Tool Executor - MCP tool execution via SSE.
Uses FastMCP client for consistent architecture across all services.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..infrastructure.fastmcp_client import get_fastmcp_client

logger = logging.getLogger(__name__)


class SimpleExecutor:
    """Simple executor that calls MCP tools directly without LLM/agent overhead."""
    
    def __init__(self):
        self.name = "simple_executor"
        self.skill_map = self._build_skill_map()
    
    def _build_skill_map(self) -> Dict[str, Dict[str, Any]]:
        """Map skill names to MCP tool names and parameter mappings."""
        return {
            # Tracking skills
            "track-shipment": {
                "tool": "track_shipment",
                "params": lambda p: {"identifier": p.get("shipment_id") or p.get("identifier")}
            },
            "search-shipments": {
                "tool": "search_shipments",
                "params": lambda p: {
                    "query": p.get("query", {}),
                    "limit": p.get("limit", 50)
                }
            },
            "batch-track": {
                "tool": "batch_track_shipments",
                "params": lambda p: {"shipment_ids": p["shipment_ids"]}
            },
            "update-eta": {
                "tool": "update_eta",
                "params": lambda p: {
                    "shipment_id": p["shipment_id"],
                    "new_eta": p["new_eta"],
                    "reason": p.get("reason", "")
                }
            },
            
            # Routing skills
            "calculate-route": {
                "tool": "calculate_route",
                "params": lambda p: {
                    "origin": p["origin"],
                    "destination": p["destination"],
                    "mode": p.get("mode", "road")
                }
            },
            "optimize-route": {
                "tool": "optimize_multi_stop_route",
                "params": lambda p: {
                    "stops": p["stops"],
                    "start_location": p.get("start_location"),
                    "end_location": p.get("end_location")
                }
            },
            "find-alternatives": {
                "tool": "find_alternative_routes",
                "params": lambda p: {
                    "origin": p["origin"],
                    "destination": p["destination"],
                    "num_alternatives": p.get("num_alternatives", 3)
                }
            },
            
            # Exception skills
            "handle-exception": {
                "tool": "log_exception",
                "params": lambda p: {
                    "shipment_id": p["shipment_id"],
                    "exception_type": p["exception_type"],
                    "description": p["description"],
                    "severity": p.get("severity", "medium")
                }
            },
            "resolve-issue": {
                "tool": "resolve_exception",
                "params": lambda p: {
                    "exception_id": p["exception_id"],
                    "resolution": p["resolution"]
                }
            },
            "escalate-problem": {
                "tool": "escalate_exception",
                "params": lambda p: {
                    "exception_id": p["exception_id"],
                    "escalation_level": p.get("escalation_level", "manager")
                }
            },
            
            # Analytics skills
            "generate-report": {
                "tool": "generate_report",
                "params": lambda p: {
                    "report_type": p["report_type"],
                    "filters": p.get("filters", {}),
                    "timeframe": p.get("timeframe", "weekly")
                }
            },
            "calculate-kpis": {
                "tool": "calculate_kpis",
                "params": lambda p: {
                    "kpi_types": p.get("kpi_types", ["on_time_delivery"]),
                    "timeframe": p.get("timeframe", "monthly")
                }
            },
            "analyze-trends": {
                "tool": "analyze_trends",
                "params": lambda p: {
                    "metric": p["metric"],
                    "timeframe": p.get("timeframe", "monthly"),
                    "period_count": p.get("period_count", 12)
                }
            },
            "forecast-performance": {
                "tool": "forecast_performance",
                "params": lambda p: {
                    "metric": p["metric"],
                    "forecast_periods": p.get("forecast_periods", 6)
                }
            },
            "query-database": {
                "tool": "query_database",
                "params": lambda p: {
                    "query_type": p["query_type"],
                    "parameters": p.get("parameters", {})
                }
            },
            
            # Vessel tracking skills
            "track-vessel": {
                "tool": "real_time_vessel_tracking",
                "params": lambda p: {"vessel_name": p.get("vessel_name") or p.get("name")}
            },
            
            # Predictive AI skills
            "predict-delay": {
                "tool": "predictive_delay_detection",
                "params": lambda p: {"identifier": p.get("shipment_id") or p.get("identifier")}
            }
        }
    
    async def initialize(self):
        """Initialize executor resources."""
        logger.info(f"{self.name} initialized with {len(self.skill_map)} skills")
    
    async def cleanup(self):
        """Cleanup executor resources."""
        logger.info(f"{self.name} cleaned up")
    
    async def execute_skill(self, skill: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a skill by calling MCP tools via SSE.
        
        Args:
            skill: Skill name (e.g., "track-shipment")
            parameters: Skill parameters
        
        Returns:
            Execution result with success status and data
        """
        try:
            # Validate skill exists
            if skill not in self.skill_map:
                return {
                    "success": False,
                    "error": f"Unknown skill: {skill}",
                    "available_skills": list(self.skill_map.keys()),
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get skill configuration
            skill_config = self.skill_map[skill]
            tool_name = skill_config["tool"]
            
            # Transform parameters
            try:
                tool_params = skill_config["params"](parameters)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Invalid parameters for skill '{skill}': {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Call MCP tool via SSE
            client = await get_fastmcp_client()
            result = await client.call_tool(tool_name, tool_params)
            
            return {
                "success": True,
                "skill": skill,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error executing skill {skill}: {e}", exc_info=True)
            return {
                "success": False,
                "skill": skill,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Global executor instance
_executor_instance: Optional[SimpleExecutor] = None


async def get_simple_executor() -> SimpleExecutor:
    """Get or create the simple executor instance."""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = SimpleExecutor()
        await _executor_instance.initialize()
    return _executor_instance
