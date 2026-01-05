"""
CrewExecutor - Routes A2A Messages to appropriate crews and handles execution.
Implements A2A Protocol v1.0 message handling and crew orchestration.
"""
import logging
import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from ..a2a_server.agent_cards import (
    get_crew_by_skill,
    get_card_by_crew,
    list_all_skills
)
from ..crews.tracking_crew import TrackingCrew
from ..crews.routing_crew import RoutingCrew
from ..crews.exception_crew import ExceptionCrew
from ..crews.analytics_crew import AnalyticsCrew

logger = logging.getLogger(__name__)


# ============================================================================
# A2A Protocol Models
# ============================================================================

class MessageStatus(str, Enum):
    """Message processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class A2AMessage:
    """A2A Protocol Message structure."""
    
    def __init__(
        self,
        message_id: Optional[str] = None,
        skill: Optional[str] = None,
        content: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.message_id = message_id or str(uuid.uuid4())
        self.skill = skill
        self.content = content or ""
        self.parameters = parameters or {}
        self.context = context or {}
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.status = MessageStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "skill": self.skill,
            "content": self.content,
            "parameters": self.parameters,
            "context": self.context,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "status": self.status.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        """Create from dictionary."""
        return cls(
            message_id=data.get("message_id"),
            skill=data.get("skill"),
            content=data.get("content"),
            parameters=data.get("parameters"),
            context=data.get("context"),
            metadata=data.get("metadata")
        )


class A2AArtifact:
    """A2A Protocol Artifact (response) structure."""
    
    def __init__(
        self,
        artifact_id: Optional[str] = None,
        message_id: Optional[str] = None,
        content: Optional[Any] = None,
        artifact_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.artifact_id = artifact_id or str(uuid.uuid4())
        self.message_id = message_id
        self.content = content
        self.artifact_type = artifact_type
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "artifact_id": self.artifact_id,
            "message_id": self.message_id,
            "content": self.content,
            "artifact_type": self.artifact_type,
            "metadata": self.metadata,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AArtifact":
        """Create from dictionary."""
        return cls(
            artifact_id=data.get("artifact_id"),
            message_id=data.get("message_id"),
            content=data.get("content"),
            artifact_type=data.get("artifact_type", "text"),
            metadata=data.get("metadata")
        )


class A2ATask:
    """A2A Protocol Task structure for async execution."""
    
    def __init__(
        self,
        task_id: Optional[str] = None,
        message: Optional[A2AMessage] = None,
        status: MessageStatus = MessageStatus.PENDING
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.message = message
        self.status = status
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.updated_at = self.created_at
        self.result: Optional[A2AArtifact] = None
        self.error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "message": self.message.to_dict() if self.message else None,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "result": self.result.to_dict() if self.result else None,
            "error": self.error
        }


# ============================================================================
# Crew Executor
# ============================================================================

class CrewExecutor:
    """
    Routes A2A Messages to appropriate crews and manages execution.
    Handles skill-based routing, crew initialization, and result transformation.
    """
    
    def __init__(self):
        """Initialize CrewExecutor with crew instances."""
        self.tracking_crew: Optional[TrackingCrew] = None
        self.routing_crew: Optional[RoutingCrew] = None
        self.exception_crew: Optional[ExceptionCrew] = None
        self.analytics_crew: Optional[AnalyticsCrew] = None
        
        # Task registry for async execution
        self.tasks: Dict[str, A2ATask] = {}
        
        logger.info("CrewExecutor initialized")
    
    async def initialize(self):
        """Initialize all crew instances."""
        try:
            logger.info("Initializing crews...")
            
            # Initialize crews
            self.tracking_crew = TrackingCrew()
            await self.tracking_crew.initialize()
            
            self.routing_crew = RoutingCrew()
            await self.routing_crew.initialize()
            
            self.exception_crew = ExceptionCrew()
            await self.exception_crew.initialize()
            
            self.analytics_crew = AnalyticsCrew()
            await self.analytics_crew.initialize()
            
            logger.info("All crews initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing crews: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup crew resources."""
        logger.info("Cleaning up crews...")
        
        crews = [
            self.tracking_crew,
            self.routing_crew,
            self.exception_crew,
            self.analytics_crew
        ]
        
        for crew in crews:
            if crew:
                try:
                    await crew.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up crew: {e}")
    
    def route_message(self, message: A2AMessage) -> str:
        """
        Route message to appropriate crew based on skill.
        
        Args:
            message: A2A message with skill and parameters
        
        Returns:
            Crew name (tracking, routing, exception, analytics)
        
        Raises:
            ValueError: If skill is unknown or not provided
        """
        if not message.skill:
            raise ValueError("Message must specify a skill")
        
        crew_name = get_crew_by_skill(message.skill)
        
        if not crew_name:
            available_skills = list_all_skills()
            raise ValueError(
                f"Unknown skill: {message.skill}. "
                f"Available skills: {', '.join(available_skills)}"
            )
        
        logger.info(f"Routing message {message.message_id} to {crew_name} crew (skill: {message.skill})")
        return crew_name
    
    async def execute_message(
        self,
        message: A2AMessage,
        stream: bool = False
    ) -> A2AArtifact:
        """
        Execute message by routing to appropriate crew.
        
        Args:
            message: A2A message to execute
            stream: Whether to stream results (for future streaming support)
        
        Returns:
            A2A artifact with result
        
        Raises:
            ValueError: If skill is unknown or crew not initialized
            Exception: If crew execution fails
        """
        try:
            # Update message status
            message.status = MessageStatus.PROCESSING
            
            # Route to appropriate crew
            crew_name = self.route_message(message)
            
            # Get crew instance
            crew = self._get_crew(crew_name)
            
            if not crew:
                raise ValueError(f"Crew not initialized: {crew_name}")
            
            # Execute based on skill
            result = await self._execute_skill(crew, crew_name, message)
            
            # Update message status
            message.status = MessageStatus.COMPLETED
            
            # Create artifact
            artifact = A2AArtifact(
                message_id=message.message_id,
                content=result,
                artifact_type="json" if isinstance(result, dict) else "text",
                metadata={
                    "crew": crew_name,
                    "skill": message.skill,
                    "execution_time": datetime.utcnow().isoformat() + "Z"
                }
            )
            
            logger.info(f"Message {message.message_id} completed successfully")
            return artifact
            
        except Exception as e:
            message.status = MessageStatus.FAILED
            logger.error(f"Error executing message {message.message_id}: {e}")
            
            # Create error artifact
            artifact = A2AArtifact(
                message_id=message.message_id,
                content={"error": str(e)},
                artifact_type="error",
                metadata={
                    "skill": message.skill,
                    "error_time": datetime.utcnow().isoformat() + "Z"
                }
            )
            return artifact
    
    async def create_task(self, message: A2AMessage) -> A2ATask:
        """
        Create async task for message execution.
        
        Args:
            message: A2A message to execute asynchronously
        
        Returns:
            A2A task with task_id for status tracking
        """
        task = A2ATask(message=message)
        self.tasks[task.task_id] = task
        
        logger.info(f"Created task {task.task_id} for message {message.message_id}")
        
        # Start background execution
        asyncio.create_task(self._execute_task(task))
        
        return task
    
    async def get_task_status(self, task_id: str) -> Optional[A2ATask]:
        """Get status of async task."""
        return self.tasks.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel async task."""
        task = self.tasks.get(task_id)
        if task and task.status in [MessageStatus.PENDING, MessageStatus.PROCESSING]:
            task.status = MessageStatus.CANCELLED
            task.updated_at = datetime.utcnow().isoformat() + "Z"
            logger.info(f"Task {task_id} cancelled")
            return True
        return False
    
    # Private methods
    
    def _get_crew(self, crew_name: str):
        """Get crew instance by name."""
        crews = {
            "tracking": self.tracking_crew,
            "routing": self.routing_crew,
            "exception": self.exception_crew,
            "analytics": self.analytics_crew
        }
        return crews.get(crew_name)
    
    async def _execute_skill(
        self,
        crew: Any,
        crew_name: str,
        message: A2AMessage
    ) -> Any:
        """Execute specific skill on crew."""
        skill = message.skill
        params = message.parameters
        
        # Map skills to crew methods
        if crew_name == "tracking":
            if skill == "track-shipment":
                return await crew.track_shipment(params.get("shipment_id"))
            elif skill == "search-shipments":
                return await crew.search_shipments(params.get("query"), params.get("limit", 50))
            elif skill == "batch-track":
                return await crew.batch_track(params.get("shipment_ids"))
            elif skill == "monitor-shipments":
                return await crew.start_monitoring(params.get("filters"))
            elif skill == "update-eta":
                return await crew.update_eta(
                    params.get("shipment_id"),
                    params.get("new_eta"),
                    params.get("reason")
                )
        
        elif crew_name == "routing":
            if skill == "calculate-route":
                return await crew.calculate_route(
                    params.get("origin"),
                    params.get("destination"),
                    params.get("mode", "driving"),
                    params.get("constraints", {})
                )
            elif skill == "optimize-route":
                return await crew.optimize_route(
                    params.get("waypoints"),
                    params.get("start_location"),
                    params.get("end_location"),
                    params.get("optimization_goal", "shortest")
                )
            elif skill == "find-alternatives":
                return await crew.find_alternatives(
                    params.get("origin"),
                    params.get("destination"),
                    params.get("current_issue")
                )
        
        elif crew_name == "exception":
            if skill == "handle-exception":
                return await crew.handle_exception(
                    params.get("shipment_id"),
                    params.get("exception_type"),
                    params.get("description"),
                    params.get("severity", "medium")
                )
            elif skill == "resolve-issue":
                return await crew.resolve_issue(
                    params.get("exception_id"),
                    params.get("resolution"),
                    params.get("notes")
                )
            elif skill == "escalate-problem":
                return await crew.escalate_problem(
                    params.get("exception_id"),
                    params.get("escalation_level"),
                    params.get("reason")
                )
            elif skill == "auto-detect-exceptions":
                return await crew.auto_detect_exceptions(params.get("threshold_hours", 24))
        
        elif crew_name == "analytics":
            if skill == "generate-report":
                return await crew.generate_report(
                    params.get("report_type"),
                    params.get("start_date"),
                    params.get("end_date"),
                    params.get("filters", {})
                )
            elif skill == "calculate-kpis":
                return await crew.calculate_kpis(
                    params.get("kpi_types"),
                    params.get("timeframe")
                )
            elif skill == "analyze-trends":
                return await crew.analyze_trends(
                    params.get("metric"),
                    params.get("period")
                )
            elif skill == "forecast-performance":
                return await crew.forecast_performance(
                    params.get("metric"),
                    params.get("forecast_days", 30),
                    params.get("confidence_level", 0.95)
                )
            elif skill == "query-database":
                return await crew.query_database(
                    params.get("query_type"),
                    params.get("parameters")
                )
        
        raise ValueError(f"Unknown skill: {skill} for crew: {crew_name}")
    
    async def _execute_task(self, task: A2ATask):
        """Execute task in background."""
        try:
            task.status = MessageStatus.PROCESSING
            task.updated_at = datetime.utcnow().isoformat() + "Z"
            
            # Execute message
            artifact = await self.execute_message(task.message)
            
            # Update task
            task.result = artifact
            task.status = MessageStatus.COMPLETED
            task.updated_at = datetime.utcnow().isoformat() + "Z"
            
        except Exception as e:
            task.status = MessageStatus.FAILED
            task.error = str(e)
            task.updated_at = datetime.utcnow().isoformat() + "Z"
            logger.error(f"Task {task.task_id} failed: {e}")
