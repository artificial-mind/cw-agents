"""
MCP Connection Pool with SSE support, retry logic, and circuit breaker.
Adapted from original cw-agents infrastructure to work with new architecture.
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from ..core.config import settings

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    def call_succeeded(self):
        """Record successful call."""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info("Circuit breaker closed after successful recovery")
    
    def call_failed(self):
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def can_attempt(self) -> bool:
        """Check if request can be attempted."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout:
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker entering half-open state")
                    return True
            return False
        
        # HALF_OPEN state
        return True
    
    def get_state(self) -> str:
        """Get current circuit breaker state."""
        return self.state.value


class MCPConnection:
    """Single MCP connection with SSE support."""
    
    def __init__(self, url: str, timeout: int = 30):
        self.url = url
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None
        self.last_used = datetime.now()
        self.is_active = False
    
    async def connect(self):
        """Establish connection."""
        if not self.client:
            self.client = httpx.AsyncClient(
                base_url=self.url,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            self.is_active = True
            logger.debug(f"MCP connection established to {self.url}")
    
    async def close(self):
        """Close connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
            self.is_active = False
            logger.debug(f"MCP connection closed to {self.url}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError))
    )
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call MCP tool with retry logic.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
        
        Returns:
            Tool execution result
        """
        if not self.client:
            await self.connect()
        
        self.last_used = datetime.now()
        
        payload = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = await self.client.post("/", json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"MCP tool error: {result['error']}")
            
            return result.get("result", {})
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling {tool_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling {tool_name}: {e}")
            raise
    
    async def stream_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """
        Call MCP tool with SSE streaming.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
        
        Yields:
            Stream events
        """
        if not self.client:
            await self.connect()
        
        self.last_used = datetime.now()
        
        payload = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            async with self.client.stream("POST", "/stream", json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip():
                            yield data
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP error streaming {tool_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error streaming {tool_name}: {e}")
            raise


class MCPConnectionPool:
    """
    Connection pool for MCP server with:
    - Connection pooling and reuse
    - Circuit breaker pattern
    - Retry logic
    - SSE streaming support
    """
    
    def __init__(
        self,
        url: str = None,
        max_connections: int = None,
        timeout: int = None,
        circuit_breaker_threshold: int = None,
        circuit_breaker_timeout: int = None
    ):
        self.url = url or settings.MCP_SERVER_URL
        self.max_connections = max_connections or settings.MCP_MAX_CONNECTIONS
        self.timeout = timeout or settings.MCP_TIMEOUT
        
        # Connection pool
        self.connections: List[MCPConnection] = []
        self.available_connections: asyncio.Queue = asyncio.Queue()
        self._lock = asyncio.Lock()
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold or settings.MCP_CIRCUIT_BREAKER_THRESHOLD,
            timeout=circuit_breaker_timeout or settings.MCP_CIRCUIT_BREAKER_TIMEOUT
        )
        
        # Metrics
        self.metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "circuit_breaker_rejections": 0
        }
        
        logger.info(f"MCP Connection Pool initialized: {self.url} (max: {self.max_connections})")
    
    async def initialize(self):
        """Initialize connection pool."""
        async with self._lock:
            for _ in range(self.max_connections):
                conn = MCPConnection(self.url, self.timeout)
                self.connections.append(conn)
                await self.available_connections.put(conn)
        
        logger.info(f"MCP Connection Pool ready with {len(self.connections)} connections")
    
    async def get_connection(self) -> MCPConnection:
        """Get connection from pool."""
        conn = await self.available_connections.get()
        if not conn.is_active:
            await conn.connect()
        return conn
    
    async def return_connection(self, conn: MCPConnection):
        """Return connection to pool."""
        await self.available_connections.put(conn)
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        use_circuit_breaker: bool = True
    ) -> Dict[str, Any]:
        """
        Call MCP tool through connection pool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            use_circuit_breaker: Whether to use circuit breaker
        
        Returns:
            Tool execution result
        """
        # Check circuit breaker
        if use_circuit_breaker and not self.circuit_breaker.can_attempt():
            self.metrics["circuit_breaker_rejections"] += 1
            raise Exception(f"Circuit breaker is {self.circuit_breaker.get_state()}")
        
        self.metrics["total_calls"] += 1
        
        conn = await self.get_connection()
        try:
            result = await conn.call_tool(tool_name, arguments)
            
            # Success
            self.metrics["successful_calls"] += 1
            if use_circuit_breaker:
                self.circuit_breaker.call_succeeded()
            
            return result
        
        except Exception as e:
            # Failure
            self.metrics["failed_calls"] += 1
            if use_circuit_breaker:
                self.circuit_breaker.call_failed()
            
            logger.error(f"Failed to call tool {tool_name}: {e}")
            raise
        
        finally:
            await self.return_connection(conn)
    
    async def stream_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ):
        """
        Call MCP tool with SSE streaming through connection pool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
        
        Yields:
            Stream events
        """
        conn = await self.get_connection()
        try:
            async for event in conn.stream_tool(tool_name, arguments):
                yield event
        finally:
            await self.return_connection(conn)
    
    async def close(self):
        """Close all connections in pool."""
        async with self._lock:
            for conn in self.connections:
                await conn.close()
            self.connections.clear()
        
        logger.info("MCP Connection Pool closed")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pool metrics."""
        return {
            **self.metrics,
            "circuit_breaker_state": self.circuit_breaker.get_state(),
            "active_connections": len(self.connections),
            "available_connections": self.available_connections.qsize()
        }


# Global pool instance
_mcp_pool: Optional[MCPConnectionPool] = None


async def get_mcp_pool() -> MCPConnectionPool:
    """Get global MCP connection pool."""
    global _mcp_pool
    
    if _mcp_pool is None:
        _mcp_pool = MCPConnectionPool()
        await _mcp_pool.initialize()
    
    return _mcp_pool


async def close_mcp_pool():
    """Close global MCP connection pool."""
    global _mcp_pool
    
    if _mcp_pool:
        await _mcp_pool.close()
        _mcp_pool = None
