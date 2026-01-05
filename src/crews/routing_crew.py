"""
Routing Crew - Handles route calculation, optimization, and alternatives.
Replaces RoutingAgent from old architecture.

Features preserved:
- Calculate routes between locations
- Optimize multi-stop routes
- Find alternative routes
- Support multiple transportation modes
"""
import logging
from typing import List, Dict, Any, Optional

from crewai import Agent, Task, Crew, Process

from ..core.llm_factory import get_llm, get_llm_with_retry
from ..tools.mcp_tools import MCPToolFactory
from ..core.config import settings

logger = logging.getLogger(__name__)


class RoutingCrew:
    """
    Routing Crew for route calculation and optimization operations.
    
    Agents:
    - Route Optimizer: Handles route calculations and optimizations
    - Logistics Planner: Plans multi-stop routes and alternatives
    
    Features:
    - Point-to-point route calculation
    - Multi-stop route optimization
    - Alternative route finding
    - Support for multiple transport modes
    """
    
    def __init__(self):
        self.name = "routing_crew"
        self.tools = MCPToolFactory.get_routing_tools()
        
        # Create agents
        self.route_optimizer = self._create_route_optimizer()
        self.logistics_planner = self._create_logistics_planner()
        
        logger.info(f"RoutingCrew initialized with {len(self.tools)} tools")
    
    def _create_route_optimizer(self) -> Agent:
        """Create route optimizer agent."""
        return Agent(
            role="Route Optimization Specialist",
            goal="Calculate optimal routes for shipments considering distance, time, and cost",
            backstory="""You are an expert in logistics routing with deep knowledge of
            transportation networks, traffic patterns, and delivery optimization. You excel
            at finding the most efficient routes while considering constraints like vehicle
            capacity, delivery windows, and road conditions.""",
            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm=get_llm()
        )
    
    def _create_logistics_planner(self) -> Agent:
        """Create logistics planner agent."""
        return Agent(
            role="Logistics Planning Expert",
            goal="Plan complex multi-stop routes and find alternatives when needed",
            backstory="""You are a logistics planning expert with extensive experience in
            multi-modal transportation and route planning. You understand how to sequence
            multiple stops efficiently and quickly identify alternative routes when
            primary options are blocked or delayed.""",
            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm=get_llm()
        )
    
    async def initialize(self):
        """Initialize crew resources."""
        logger.info(f"{self.name} initialized")
    
    async def cleanup(self):
        """Cleanup crew resources."""
        logger.info(f"{self.name} cleaned up")
    
    async def calculate_route(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate route between two locations.
        
        Args:
            origin: Starting location
            destination: Ending location
            mode: Transportation mode
            constraints: Route constraints
        
        Returns:
            Route calculation result
        """
        try:
            llm = await get_llm_with_retry()
            self.route_optimizer.llm = llm
            
            constraint_str = ", ".join([f"{k}={v}" for k, v in (constraints or {}).items()])
            
            task = Task(
                description=f"""Calculate the optimal route from {origin} to {destination}
                using {mode} transportation mode. Consider the following constraints: {constraint_str or 'none'}.
                Provide distance, estimated time, and key waypoints along the route.""",
                expected_output="Detailed route with distance, time, and waypoints",
                agent=self.route_optimizer
            )
            
            crew = Crew(
                agents=[self.route_optimizer],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            return {
                "success": True,
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "result": str(result)
            }
        
        except Exception as e:
            logger.error(f"Error calculating route: {e}")
            return {
                "success": False,
                "origin": origin,
                "destination": destination,
                "error": str(e)
            }
    
    async def optimize_route(
        self,
        waypoints: List[str],
        start_location: str,
        end_location: Optional[str] = None,
        optimization_goal: str = "shortest"
    ) -> Dict[str, Any]:
        """
        Optimize multi-stop route.
        
        Args:
            waypoints: Locations to visit
            start_location: Starting point
            end_location: Ending point (optional)
            optimization_goal: Optimization criteria
        
        Returns:
            Optimized route
        """
        try:
            llm = await get_llm_with_retry()
            self.logistics_planner.llm = llm
            
            waypoint_list = ", ".join(waypoints)
            end_str = f" and return to {end_location}" if end_location else ""
            
            task = Task(
                description=f"""Optimize the route starting from {start_location}, visiting these locations:
                {waypoint_list}{end_str}. Optimize for {optimization_goal} distance/time.
                Provide the optimal sequence of stops with total distance and time estimates.""",
                expected_output="Optimized route sequence with distance and time totals",
                agent=self.logistics_planner
            )
            
            crew = Crew(
                agents=[self.logistics_planner],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            return {
                "success": True,
                "start_location": start_location,
                "waypoints": waypoints,
                "optimization_goal": optimization_goal,
                "result": str(result)
            }
        
        except Exception as e:
            logger.error(f"Error optimizing route: {e}")
            return {
                "success": False,
                "start_location": start_location,
                "waypoints": waypoints,
                "error": str(e)
            }
    
    async def find_alternatives(
        self,
        origin: str,
        destination: str,
        current_issue: str
    ) -> Dict[str, Any]:
        """
        Find alternative routes.
        
        Args:
            origin: Starting location
            destination: Ending location
            current_issue: Issue with current route
        
        Returns:
            Alternative routes
        """
        try:
            llm = await get_llm_with_retry()
            self.logistics_planner.llm = llm
            
            task = Task(
                description=f"""Find alternative routes from {origin} to {destination}.
                The current route has this issue: {current_issue}.
                Provide at least 2-3 viable alternatives with their pros and cons.
                Consider different transportation modes and routing options.""",
                expected_output="Multiple alternative routes with analysis of each option",
                agent=self.logistics_planner
            )
            
            crew = Crew(
                agents=[self.logistics_planner],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            return {
                "success": True,
                "origin": origin,
                "destination": destination,
                "current_issue": current_issue,
                "result": str(result)
            }
        
        except Exception as e:
            logger.error(f"Error finding alternatives: {e}")
            return {
                "success": False,
                "origin": origin,
                "destination": destination,
                "error": str(e)
            }
