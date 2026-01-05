#!/usr/bin/env python3
"""
Start the CW A2A Agent Server.
Run this to start the multi-crew agent system on port 8001.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    from src.a2a_server.main import main
    
    print("="*80)
    print("CW Multi-Agent System - A2A Server")
    print("="*80)
    print(f"Starting server on port 8001...")
    print(f"AgentCard: http://localhost:8001/.well-known/agent-card.json")
    print(f"API Docs: http://localhost:8001/docs")
    print(f"Health: http://localhost:8001/health")
    print("="*80)
    
    main()
