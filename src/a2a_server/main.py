"""
A2A Server - FastAPI server implementing A2A Protocol v1.0.
Exposes AgentCards and handles message/task endpoints.
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from ..a2a_server.agent_cards import (
    COMBINED_CARD,
    TRACKING_CARD,
    ROUTING_CARD,
    EXCEPTION_CARD,
    ANALYTICS_CARD,
    get_card_by_crew
)
from ..executors.simple_executor import get_simple_executor
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ============================================================================
# Global Executor Instance
# ============================================================================

executor = None


# ============================================================================
# Pydantic Models for API
# ============================================================================

class MessageRequest(BaseModel):
    """Request model for message:send endpoint."""
    message_id: Optional[str] = None
    skill: str = Field(..., description="Skill to execute")
    content: Optional[str] = Field(None, description="Message content")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Skill parameters")
    context: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MessageResponse(BaseModel):
    """Response model for message:send endpoint."""
    message_id: str
    artifact: Dict[str, Any]
    status: str


class TaskRequest(BaseModel):
    """Request model for task creation."""
    message: MessageRequest


class TaskResponse(BaseModel):
    """Response model for task endpoints."""
    task_id: str
    status: str
    created_at: str
    updated_at: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    crews: Dict[str, str]


# ============================================================================
# Lifespan Context Manager
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global executor
    
    # Startup
    logger.info("Starting A2A Server...")
    executor = await get_simple_executor()
    logger.info("A2A Server ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down A2A Server...")
    if executor:
        await executor.cleanup()
    logger.info("A2A Server stopped")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="CW Multi-Agent System",
    description="A2A Protocol v1.0 compliant multi-crew agent system for logistics",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# AgentCard Endpoints
# ============================================================================

@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """
    Get combined AgentCard for all crews.
    A2A Protocol discovery endpoint.
    """
    return JSONResponse(content=COMBINED_CARD)


@app.get("/crews/{crew_name}/agent-card")
async def get_crew_card(crew_name: str):
    """Get AgentCard for specific crew."""
    card = get_card_by_crew(crew_name)
    if not card:
        raise HTTPException(status_code=404, detail=f"Crew not found: {crew_name}")
    return JSONResponse(content=card)


@app.get("/crews")
async def list_crews():
    """List all available crews."""
    return JSONResponse(content={
        "crews": [
            {"name": "tracking", "card": TRACKING_CARD},
            {"name": "routing", "card": ROUTING_CARD},
            {"name": "exception", "card": EXCEPTION_CARD},
            {"name": "analytics", "card": ANALYTICS_CARD}
        ]
    })


# ============================================================================
# Message Endpoints
# ============================================================================

@app.post("/message:send", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """
    Synchronous message execution.
    A2A Protocol message:send endpoint.
    """
    try:
        # Execute skill directly
        result = await executor.execute_skill(
            skill=request.skill,
            parameters=request.parameters or {}
        )
        
        # Build artifact from result
        import uuid
        message_id = request.message_id or str(uuid.uuid4())
        artifact_id = str(uuid.uuid4())
        
        artifact = {
            "artifact_id": artifact_id,
            "message_id": message_id,
            "content": result,
            "artifact_type": "json",
            "metadata": {
                "skill": request.skill,
                "execution_time": result.get("timestamp")
            },
            "created_at": result.get("timestamp")
        }
        
        return MessageResponse(
            message_id=message_id,
            artifact=artifact,
            status="completed" if result.get("success") else "failed"
        )
        # Execute message
        artifact = await executor.execute_message(message)
        
        return MessageResponse(
            message_id=message.message_id,
            artifact=artifact.to_dict(),
            status=message.status.value
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/message:stream")
async def stream_message(request: MessageRequest):
    """
    Streaming message execution.
    A2A Protocol message:stream endpoint.
    """
    raise HTTPException(status_code=501, detail="Streaming not implemented yet - use /message:send instead")


# ============================================================================
# Task Endpoints (Asynchronous Execution)
# ============================================================================

@app.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """
    Create asynchronous task.
    A2A Protocol task creation endpoint.
    """
    raise HTTPException(status_code=501, detail="Async tasks not implemented yet - use /message:send instead")


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """
    Get task status.
    A2A Protocol task status endpoint.
    """
    raise HTTPException(status_code=501, detail="Async tasks not implemented yet - use /message:send instead")


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """
    Cancel task.
    A2A Protocol task cancellation endpoint.
    """
    raise HTTPException(status_code=501, detail="Async tasks not implemented yet - use /message:send instead")


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        crews={
            "tracking": "ready" if executor.tracking_crew else "not_initialized",
            "routing": "ready" if executor.routing_crew else "not_initialized",
            "exception": "ready" if executor.exception_crew else "not_initialized",
            "analytics": "ready" if executor.analytics_crew else "not_initialized"
        }
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "CW Multi-Agent System",
        "version": "1.0.0",
        "protocol": "A2A v1.0",
        "endpoints": {
            "agent_card": "/.well-known/agent-card.json",
            "message_send": "/message:send",
            "message_stream": "/message:stream",
            "tasks": "/tasks",
            "health": "/health"
        },
        "documentation": "/docs"
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content={"error": "Validation Error", "detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    """Handle general errors."""
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run the A2A server."""
    uvicorn.run(
        "src.a2a_server.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )


if __name__ == "__main__":
    main()
