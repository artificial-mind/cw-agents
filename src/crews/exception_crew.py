"""
Exception Crew - Handles exception detection, resolution, and escalation.
Replaces ExceptionAgent from old architecture.

Features preserved:
- Handle shipping exceptions (delays, damage, lost items)
- Auto-detect exceptions (24h threshold)
- Resolve issues with documentation
- Escalate critical problems
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from crewai import Agent, Task, Crew, Process

from ..core.llm_factory import get_llm, get_llm_with_retry
from ..tools.mcp_tools import MCPToolFactory
from ..infrastructure.redis_client import get_redis_client
from ..core.config import settings

logger = logging.getLogger(__name__)


class ExceptionCrew:
    """
    Exception Crew for handling shipping exceptions and issues.
    
    Agents:
    - Exception Handler: Identifies and handles exceptions
    - Resolution Specialist: Resolves issues and manages escalations
    
    Features:
    - Exception logging and handling
    - Auto-detection of delays (24h threshold)
    - Issue resolution tracking
    - Escalation management
    """
    
    def __init__(self):
        self.name = "exception_crew"
        self.tools = MCPToolFactory.get_exception_tools()
        
        # Create agents
        self.exception_handler = self._create_exception_handler()
        self.resolution_specialist = self._create_resolution_specialist()
        
        logger.info(f"ExceptionCrew initialized with {len(self.tools)} tools")
    
    def _create_exception_handler(self) -> Agent:
        """Create exception handler agent."""
        return Agent(
            role="Shipping Exception Handler",
            goal="Identify, log, and categorize shipping exceptions quickly and accurately",
            backstory="""You are an expert in logistics exception management with years of
            experience handling delays, damages, and lost shipments. You excel at quickly
            identifying the root cause of problems and categorizing them by severity to
            ensure appropriate response.""",
            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm=get_llm()
        )
    
    def _create_resolution_specialist(self) -> Agent:
        """Create resolution specialist agent."""
        return Agent(
            role="Issue Resolution Specialist",
            goal="Resolve shipping issues effectively and escalate critical problems appropriately",
            backstory="""You are a problem-solving expert specializing in logistics operations.
            You understand how to resolve common shipping issues quickly and know when to
            escalate problems to higher management. You maintain detailed documentation of
            all resolutions for future reference.""",
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
        logger.info(f"{self.name} cleaned up")
    
    async def handle_exception(
        self,
        shipment_id: str,
        exception_type: str,
        description: str,
        severity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Handle shipping exception.
        
        Args:
            shipment_id: Shipment with exception
            exception_type: Type of exception
            description: Exception description
            severity: Severity level
        
        Returns:
            Exception handling result
        """
        try:
            llm = await get_llm_with_retry()
            self.exception_handler.llm = llm
            
            task = Task(
                description=f"""Handle shipping exception for shipment {shipment_id}.
                Exception type: {exception_type}
                Description: {description}
                Severity: {severity}
                
                Log the exception, assess the impact, and provide recommended actions.
                If severity is high or critical, flag for immediate escalation.""",
                expected_output="Exception logged with impact assessment and recommended actions",
                agent=self.exception_handler
            )
            
            crew = Crew(
                agents=[self.exception_handler],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            # Store in Redis for tracking
            redis_client = await get_redis_client()
            exception_data = {
                "shipment_id": shipment_id,
                "exception_type": exception_type,
                "description": description,
                "severity": severity,
                "handled_at": datetime.now().isoformat(),
                "result": str(result)
            }
            await redis_client.set_state(
                f"exception:{shipment_id}",
                exception_data,
                ttl=86400 * 7  # 7 days
            )
            
            return {
                "success": True,
                "shipment_id": shipment_id,
                "exception_type": exception_type,
                "severity": severity,
                "result": str(result)
            }
        
        except Exception as e:
            logger.error(f"Error handling exception: {e}")
            return {
                "success": False,
                "shipment_id": shipment_id,
                "error": str(e)
            }
    
    async def resolve_issue(
        self,
        exception_id: str,
        resolution: str,
        notes: str
    ) -> Dict[str, Any]:
        """
        Resolve an exception/issue.
        
        Args:
            exception_id: Exception to resolve
            resolution: Resolution action
            notes: Resolution notes
        
        Returns:
            Resolution result
        """
        try:
            llm = await get_llm_with_retry()
            self.resolution_specialist.llm = llm
            
            task = Task(
                description=f"""Resolve exception {exception_id}.
                Resolution action: {resolution}
                Notes: {notes}
                
                Document the resolution thoroughly, update all affected parties,
                and close the exception. Verify that the resolution is complete.""",
                expected_output="Confirmed resolution with documentation",
                agent=self.resolution_specialist
            )
            
            crew = Crew(
                agents=[self.resolution_specialist],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            # Update Redis state
            redis_client = await get_redis_client()
            resolution_data = {
                "exception_id": exception_id,
                "resolution": resolution,
                "notes": notes,
                "resolved_at": datetime.now().isoformat(),
                "result": str(result)
            }
            await redis_client.set_state(
                f"resolution:{exception_id}",
                resolution_data,
                ttl=86400 * 30  # 30 days
            )
            
            return {
                "success": True,
                "exception_id": exception_id,
                "resolution": resolution,
                "result": str(result)
            }
        
        except Exception as e:
            logger.error(f"Error resolving issue: {e}")
            return {
                "success": False,
                "exception_id": exception_id,
                "error": str(e)
            }
    
    async def escalate_problem(
        self,
        exception_id: str,
        escalation_level: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Escalate problem to higher level.
        
        Args:
            exception_id: Exception to escalate
            escalation_level: Escalation level
            reason: Escalation reason
        
        Returns:
            Escalation result
        """
        try:
            llm = await get_llm_with_retry()
            self.resolution_specialist.llm = llm
            
            task = Task(
                description=f"""Escalate exception {exception_id} to {escalation_level} level.
                Reason: {reason}
                
                Prepare comprehensive escalation documentation including timeline,
                impact assessment, attempted resolutions, and recommendations for
                higher-level intervention.""",
                expected_output="Complete escalation package ready for management review",
                agent=self.resolution_specialist
            )
            
            crew = Crew(
                agents=[self.resolution_specialist],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            # Store escalation in Redis
            redis_client = await get_redis_client()
            escalation_data = {
                "exception_id": exception_id,
                "escalation_level": escalation_level,
                "reason": reason,
                "escalated_at": datetime.now().isoformat(),
                "result": str(result)
            }
            await redis_client.set_state(
                f"escalation:{exception_id}",
                escalation_data,
                ttl=86400 * 30  # 30 days
            )
            
            # Increment escalation metric
            await redis_client.increment_metric(f"escalations_{escalation_level}")
            
            return {
                "success": True,
                "exception_id": exception_id,
                "escalation_level": escalation_level,
                "result": str(result)
            }
        
        except Exception as e:
            logger.error(f"Error escalating problem: {e}")
            return {
                "success": False,
                "exception_id": exception_id,
                "error": str(e)
            }
    
    async def auto_detect_exceptions(self) -> Dict[str, Any]:
        """
        Auto-detect exceptions based on 24h threshold.
        
        Returns:
            Detected exceptions
        """
        try:
            llm = await get_llm_with_retry()
            self.exception_handler.llm = llm
            
            # Calculate threshold
            threshold_hours = settings.EXCEPTION_AUTO_DETECT_HOURS
            threshold_time = datetime.now() - timedelta(hours=threshold_hours)
            
            task = Task(
                description=f"""Analyze recent shipments to detect exceptions.
                Look for shipments that are delayed by more than {threshold_hours} hours
                (since {threshold_time.isoformat()}).
                
                Search for shipments with:
                - Significant delays beyond promised delivery
                - Status changes indicating problems
                - Abnormal location patterns
                
                Report all detected exceptions with recommended actions.""",
                expected_output="List of detected exceptions with severity and recommendations",
                agent=self.exception_handler
            )
            
            crew = Crew(
                agents=[self.exception_handler],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            return {
                "success": True,
                "threshold_hours": threshold_hours,
                "detection_time": datetime.now().isoformat(),
                "result": str(result)
            }
        
        except Exception as e:
            logger.error(f"Error in auto-detection: {e}")
            return {
                "success": False,
                "error": str(e)
            }
