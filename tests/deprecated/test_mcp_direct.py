#!/usr/bin/env python3
"""
Quick test of MCP SSE connection
"""
import asyncio
import aiohttp
import json

async def test_mcp():
    """Test MCP server via SSE"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("📡 Connecting to SSE...")
        
        # Get endpoint from SSE
        async with session.get(f"{base_url}/sse", headers={"Accept": "text/event-stream"}) as response:
            print(f"Status: {response.status}")
            
            endpoint = None
            async for line in response.content:
                line_text = line.decode('utf-8').strip()
                print(f"SSE: {line_text}")
                
                if line_text.startswith('data:'):
                    data = line_text[5:].strip()
                    if '/messages/' in data:
                        endpoint = data
                        print(f"✅ Got endpoint: {endpoint}")
                        break
        
        if not endpoint:
            print("❌ Failed to get endpoint")
            return
        
        # Call track_shipment tool
        print("\n📦 Calling track_shipment...")
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "track_shipment",
                "arguments": {"identifier": "job-2025-001"}
            }
        }
        
        async with session.post(
            f"{base_url}{endpoint}",
            json=message,
            headers={"Content-Type": "application/json"}
        ) as response:
            print(f"Status: {response.status}")
            text = await response.text()
            print(f"Response: {text}")
            
            if response.status in [200, 202]:
                try:
                    result = json.loads(text)
                    print(f"✅ Result: {json.dumps(result, indent=2)}")
                except:
                    print("⚠️  Non-JSON response")

if __name__ == "__main__":
    asyncio.run(test_mcp())
