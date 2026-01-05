"""
Tracking Crew - Handles shipment tracking, monitoring, and batch operations.
Replaces TrackingAgent from old architecture.

Features preserved:
- Track individual shipments
- Continuous monitoring loop (300s interval)
- Batch tracking (up to 50 shipments)
- State persistence via Redis
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from crewai import Agent, Task, Crew, Process
from crewai.tasks.task_output import TaskOutput

from ..core.llm_factory import get_llm, get_llm_with_retry
from ..tools.mcp_tools import MCPToolFactory
from ..infrastructure.redis_client import get_redis_client
from ..core.config import settings

logger = logging.getLogger(__name__)


class TrackingCrew:
    """
    Tracking Crew for shipment tracking and monitoring operations.
    
    Agents:
    - Tracking Specialist: Handles individual tracking requests
    - Data Analyst: Processes batch operations and monitoring
    
    Features:
    - Real-time shipment tracking
    - Continuous monitoring (300s interval)
    - Batch tracking (up to 50 shipments)
    - State persistence
    """
    
    def __init__(self):
        self.name = "tracking_crew"
        self.tools = MCPToolFactory.get_tracking_tools()
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Create agents
        self.tracking_specialist = self._create_tracking_specialist()
        self.data_analyst = self._create_data_analyst()
        
        logger.info(f"TrackingCrew initialized with {len(self.tools)} tools")
    
    def _create_tracking_specialist(self) -> Agent:
        """Create tracking specialist agent."""
        return Agent(
            role="Shipment Tracking Specialist",
            goal="Track shipments accurately and provide real-time status updates",
            backstory="""You are an expert in logistics tracking with years of experience
            monitoring shipments across multiple carriers and transportation modes. You excel
            at providing accurate, timely updates and identifying potential delivery issues
            before they become problems.""",
            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm=get_llm()
        )
    
    def _create_data_analyst(self) -> Agent:
        """Create data analyst agent."""
        return Agent(
            role="Logistics Data Analyst",
            goal="Process large-scale tracking data and identify patterns efficiently",
            backstory="""You are a data analyst specializing in logistics operations. You excel
            at processing batch tracking requests, analyzing shipment patterns, and providing
            insights on delivery performance. You understand how to optimize batch operations
            and monitor multiple shipments simultaneously.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=get_llm()
        )
    
    async def initialize(self):
        """Initialize crew resources."""
        logger.info(f"{self.name} initialized")
    
    async def cleanup(self):
        """Cleanup crew resources."""
        if self.monitoring_active:
            await self.stop_monitoring()
        logger.info(f"{self.name} cleaned up")
    
    async def track_shipment(self, shipment_id: str) -> Dict[str, Any]:
        """
        Track a single shipment.
        
        Args:
            shipment_id: Shipment ID to track
        
        Returns:
            Tracking result
        """
        try:
            # Try primary LLM, fallback to secondary if needed
            llm = await get_llm_with_retry()
            self.tracking_specialist.llm = llm
            
            task = Task(
                description=f"""Track shipment {shipment_id} and provide detailed status information.
                Include current location, status, estimated delivery time, and any issues or delays.
                Be specific and accurate in your response.""",
                expected_output="Detailed tracking information with status, location, and ETA",
                agent=self.tracking_specialist
            )
            
            crew = Crew(
                agents=[self.tracking_specialist],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            return {
                "success": True,
                "shipment_id": shipment_id,
                "result": str(result),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error tracking shipment {shipment_id}: {e}")
            return {
                "success": False,
                "shipment_id": shipment_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def batch_track(self, shipment_ids: List[str]) -> Dict[str, Any]:
        """
        Track multiple shipments in batch (max 50).
        
        Args:
            shipment_ids: List of shipment IDs to track
        
        Returns:
            Batch tracking results
        """
        try:
            # Enforce batch limit
            if len(shipment_ids) > settings.BATCH_SIZE:
                logger.warning(f"Batch size {len(shipment_ids)} exceeds limit {settings.BATCH_SIZE}, truncating")
                shipment_ids = shipment_ids[:settings.BATCH_SIZE]
            
            # Try primary LLM, fallback to secondary if needed
            llm = await get_llm_with_retry()
            self.data_analyst.llm = llm
            
            shipment_list = ", ".join(shipment_ids)
            
            task = Task(
                description=f"""Track the following {len(shipment_ids)} shipments in batch: {shipment_list}.
                For each shipment, provide status, location, and ETA.
                Identify any shipments with delays or issues that need attention.
                Provide a summary of overall batch status.""",
                expected_output="Batch tracking results with individual status and overall summary",
                agent=self.data_analyst
            )
            
            crew = Crew(
                agents=[self.data_analyst],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            return {
                "success": True,
                "batch_size": len(shipment_ids),
                "shipment_ids": shipment_ids,
                "result": str(result),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error in batch tracking: {e}")
            return {
                "success": False,
                "batch_size": len(shipment_ids),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def search_shipments(self, query: Dict[str, Any], limit: int = 50) -> Dict[str, Any]:
        """
        Search shipments by criteria.
        
        Args:
            query: Search criteria
            limit: Maximum results
        
        Returns:
            Search results
        """
        try:
            llm = await get_llm_with_retry()
            self.tracking_specialist.llm = llm
            
            query_str = ", ".join([f"{k}={v}" for k, v in query.items()])
            
            task = Task(
                description=f"""Search for shipments matching the following criteria: {query_str}.
                Return up to {limit} matching shipments with their current status and key details.
                Organize results in a clear, actionable format.""",
                expected_output="List of matching shipments with status and details",
                agent=self.tracking_specialist
            )
            
            crew = Crew(
                agents=[self.tracking_specialist],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            return {
                "success": True,
                "query": query,
                "limit": limit,
                "result": str(result),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error searching shipments: {e}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def start_monitoring(self):
        """Start continuous monitoring loop."""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"Started monitoring loop (interval: {settings.TRACKING_POLL_INTERVAL}s)")
    
    async def stop_monitoring(self):
        """Stop continuous monitoring loop."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped monitoring loop")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop (300s interval)."""
        while self.monitoring_active:
            try:
                # Get shipments to monitor from Redis
                redis_client = await get_redis_client()
                monitoring_tasks = await redis_client.get_monitoring_tasks(self.name)
                
                if monitoring_tasks:
                    logger.info(f"Monitoring {len(monitoring_tasks)} shipments")
                    
                    # Extract shipment IDs
                    shipment_ids = [task["shipment_id"] for task in monitoring_tasks[:settings.BATCH_SIZE]]
                    
                    # Batch track
                    result = await self.batch_track(shipment_ids)
                    
                    # Store result in cache
                    cache_key = f"monitoring_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    await redis_client.set_cache(cache_key, result, ttl=3600)
                
                # Wait for next interval
                await asyncio.sleep(settings.TRACKING_POLL_INTERVAL)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(settings.TRACKING_POLL_INTERVAL)
    
    async def add_to_monitoring(self, shipment_id: str, data: Optional[Dict[str, Any]] = None):
        """Add shipment to monitoring list."""
        redis_client = await get_redis_client()
        await redis_client.add_to_monitoring(
            self.name,
            shipment_id,
            data or {"added_at": datetime.now().isoformat()}
        )
        logger.info(f"Added shipment {shipment_id} to monitoring")
    
    async def remove_from_monitoring(self, shipment_id: str):
        """Remove shipment from monitoring list."""
        redis_client = await get_redis_client()
        await redis_client.remove_from_monitoring(self.name, shipment_id)
        logger.info(f"Removed shipment {shipment_id} from monitoring")
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring status."""
        redis_client = await get_redis_client()
        monitoring_tasks = await redis_client.get_monitoring_tasks(self.name)
        
        return {
            "active": self.monitoring_active,
            "interval_seconds": settings.TRACKING_POLL_INTERVAL,
            "monitored_shipments": len(monitoring_tasks),
            "shipment_ids": [task["shipment_id"] for task in monitoring_tasks]
        }
