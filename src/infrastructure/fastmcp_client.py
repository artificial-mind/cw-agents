"""
FastMCP SSE Client - Call MCP server tools via SSE.
Proper implementation using aiohttp for SSE connection with response streaming.
"""
import logging
import json
import asyncio
from typing import Dict, Any, Optional
import aiohttp

logger = logging.getLogger(__name__)


class FastMCPClient:
    """Client for calling FastMCP server via SSE."""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.sse_session: Optional[aiohttp.ClientSession] = None
        self.post_session: Optional[aiohttp.ClientSession] = None
        self.endpoint: Optional[str] = None
        self.session_id: Optional[str] = None
        self.message_id = 0
        self.sse_response: Optional[aiohttp.ClientResponse] = None
        self.pending_responses: Dict[int, asyncio.Future] = {}
    
    async def connect(self):
        """Connect to MCP server via SSE and establish session."""
        if self.sse_session and self.endpoint and not self.sse_session.closed:
            logger.debug("Already connected to MCP server")
            return  # Already connected
        
        # Close any existing sessions first
        if self.sse_session and not self.sse_session.closed:
            await self.sse_session.close()
        if self.post_session and not self.post_session.closed:
            await self.post_session.close()
        
        self.sse_session = aiohttp.ClientSession()
        self.post_session = aiohttp.ClientSession()
        
        try:
            # Connect to /sse endpoint and keep it open
            logger.info(f"Connecting to {self.server_url}/sse")
            self.sse_response = await self.sse_session.get(
                f"{self.server_url}/sse",
                headers={"Accept": "text/event-stream"},
                timeout=aiohttp.ClientTimeout(total=None)  # No timeout for SSE
            )
            
            if self.sse_response.status != 200:
                text = await self.sse_response.text()
                raise Exception(f"Failed to connect to SSE: {self.sse_response.status} - {text}")
            
            # Read the endpoint from first SSE event
            logger.debug(f"SSE connection established, reading endpoint...")
            async for line in self.sse_response.content:
                line_text = line.decode('utf-8').strip()
                
                if line_text.startswith('data:'):
                    data = line_text[5:].strip()
                    
                    if '/messages/' in data:
                        self.endpoint = data
                        if 'session_id=' in data:
                            raw_session_id = data.split('session_id=')[1].split('&')[0]
                            # FastMCP library strips dashes from UUIDs in URLs, add them back
                            if len(raw_session_id) == 32 and '-' not in raw_session_id:
                                self.session_id = f"{raw_session_id[:8]}-{raw_session_id[8:12]}-{raw_session_id[12:16]}-{raw_session_id[16:20]}-{raw_session_id[20:]}"
                            else:
                                self.session_id = raw_session_id
                        
                        logger.info(f"✅ Connected - Endpoint: {self.endpoint}, Session: {self.session_id}")
                        break
            
            if not self.endpoint:
                raise Exception("Failed to get endpoint from SSE")
            
            # Start background task to listen for SSE events
            asyncio.create_task(self._listen_sse_events())
            
            # Give the listener a moment to start
            await asyncio.sleep(0.1)
            
            # Send initialize message (MCP protocol requirement)
            logger.info("Sending initialize message...")
            init_response = await self._send_message({
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "a2a-client",
                        "version": "1.0.0"
                    }
                }
            })
            logger.info(f"✅ Initialize response: {init_response}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}", exc_info=True)
            await self.close()
            raise
    
    async def _listen_sse_events(self):
        """Background task to listen for SSE response events."""
        try:
            logger.debug("Starting SSE event listener...")
            async for line in self.sse_response.content:
                line_text = line.decode('utf-8').strip()
                
                if not line_text:
                    continue
                
                if line_text.startswith('data:'):
                    data = line_text[5:].strip()
                    
                    try:
                        event_data = json.loads(data)
                        
                        # Check if this is a JSON-RPC response
                        if "id" in event_data and "result" in event_data:
                            msg_id = event_data["id"]
                            if msg_id in self.pending_responses:
                                self.pending_responses[msg_id].set_result(event_data)
                                logger.debug(f"✅ Got response for message {msg_id}")
                    except json.JSONDecodeError:
                        logger.debug(f"Non-JSON SSE data: {data}")
        except Exception as e:
            logger.error(f"SSE listener error: {e}", exc_info=True)
    
    async def _send_message(self, message: Dict[str, Any], wait_response: bool = True) -> Dict[str, Any]:
        """Send JSON-RPC message to MCP server and optionally wait for response."""
        if not self.post_session or not self.endpoint:
            raise Exception("Not connected to MCP server")
        
        full_url = f"{self.server_url}{self.endpoint}"
        msg_id = message.get("id")
        
        # Create future for response if waiting
        if wait_response and msg_id:
            self.pending_responses[msg_id] = asyncio.Future()
        
        logger.debug(f"Sending message {msg_id} to {full_url}")
        
        try:
            async with self.post_session.post(
                full_url,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                logger.debug(f"POST response: {response.status}")
                
                if response.status not in [200, 202]:
                    text = await response.text()
                    raise Exception(f"MCP request failed: {response.status} - {text}")
            
            # Wait for SSE response
            if wait_response and msg_id:
                try:
                    result = await asyncio.wait_for(self.pending_responses[msg_id], timeout=30.0)
                    return result
                except asyncio.TimeoutError:
                    raise Exception(f"Timeout waiting for response to message {msg_id}")
                finally:
                    self.pending_responses.pop(msg_id, None)
            
            return {"status": "accepted"}
            
        except Exception as e:
            logger.error(f"Error sending MCP message: {e}", exc_info=True)
            if msg_id:
                self.pending_responses.pop(msg_id, None)
            raise
    
    def _next_id(self) -> int:
        """Get next message ID."""
        self.message_id += 1
        return self.message_id
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call MCP tool via SSE.
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
        
        Returns:
            Tool result
        """
        await self.connect()
        
        # Send tools/call message
        message = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        logger.debug(f"Calling MCP tool: {tool_name} with args: {arguments}")
        response = await self._send_message(message, wait_response=True)
        
        if "error" in response:
            raise Exception(f"MCP tool error: {response['error']}")
        
        # Extract result from response
        result = response.get("result", {})
        
        # Handle different result formats
        if isinstance(result, dict):
            if "content" in result:
                # FastMCP returns content array
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]
                    if isinstance(first_item, dict):
                        text = first_item.get("text", "{}")
                        try:
                            return json.loads(text)
                        except json.JSONDecodeError:
                            return {"text": text}
                    return first_item
                return content
            return result
        
        return result
    
    async def close(self):
        """Close the MCP client sessions."""
        if self.sse_session:
            await self.sse_session.close()
            self.sse_session = None
        
        if self.post_session:
            await self.post_session.close()
            self.post_session = None
        
        if self.sse_response:
            self.sse_response.close()
            self.sse_response = None
        
        self.endpoint = None
        self.session_id = None
        logger.info("MCP client sessions closed")


# Global client instance with lock for thread safety
_client: Optional[FastMCPClient] = None
_client_lock = asyncio.Lock()


async def get_fastmcp_client() -> FastMCPClient:
    """Get or create FastMCP client (singleton with connection pooling)."""
    global _client
    
    async with _client_lock:
        if _client is None:
            logger.info("Creating new FastMCP client...")
            _client = FastMCPClient()
            await _client.connect()
        elif not _client.sse_session or not _client.endpoint:
            logger.info("Reconnecting FastMCP client...")
            await _client.connect()
    
    return _client
