# CW Multi-Agent System# 🤖 CW-Agents: Multi-Agent Logistics Intelligence System



**A2A Protocol Server for Logistics Operations**> **A2A (Agent-to-Agent) Protocol Implementation for Scalable Logistics Operations**



---[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)

## Quick Start[![Redis](https://img.shields.io/badge/Redis-7.0+-red.svg)](https://redis.io)



```bash## 🎯 Overview

# Install

pip install -r requirements.txtCW-Agents is a specialized multi-agent system designed for logistics and shipment operations. It implements the A2A (Agent-to-Agent) protocol to enable autonomous, scalable, and intelligent handling of logistics workflows.



# Configure### Architecture

cp .env.example .env

# Edit .env with your API keys```

┌─────────────────────────────────┐

# Start server│   CW-UI (11Labs Voice Agent)    │  ← User Interface

python start_server.py└─────────────┬───────────────────┘

              │

# Test┌─────────────▼───────────────────┐

curl http://localhost:8001/health│   CW-BRAIN (Orchestrator)       │  ← Intelligence Layer

```│   - LLM Decision Making          │

│   - Agent Coordination           │

Server runs on **http://localhost:8001**└─────────────┬───────────────────┘

              │ A2A Protocol (Redis Pub/Sub)

---┌─────────────▼───────────────────┐

│   CW-AGENTS (This Repository)   │  ← Specialized Agents

## What It Does│   - TrackingAgent                │

│   - RoutingAgent                 │

Multi-crew agent system providing **27 skills** across **4 specialized crews**:│   - ExceptionAgent               │

│   - DocumentationAgent           │

| Crew | Skills | Purpose |│   - AnalyticsAgent               │

|------|--------|---------|└─────────────┬───────────────────┘

| **Tracking** | 5 | Track shipments, batch operations, monitoring |              │ MCP Protocol (SSE)

| **Routing** | 3 | Route calculation, optimization, alternatives |┌─────────────▼───────────────────┐

| **Exception** | 4 | Handle delays, resolve issues, escalations |│  CW-AI-SERVER (MCP Server)      │  ← Data & Tools Layer

| **Analytics** | 5 | Reports, KPIs, trends, forecasting |│  - Database Operations           │

│  - External API Integrations     │

---└─────────────────────────────────┘

```

## API Examples

## ✨ Features

### Track Shipment

```bash### Core Infrastructure

curl -X POST http://localhost:8001/message:send \- 🏗️ **Base Agent Framework** - Abstract base class for all agents

  -H "Content-Type: application/json" \- 🔄 **MCP Connection Pool** - Shared, load-balanced connections to MCP server

  -d '{"skill": "track-shipment", "parameters": {"shipment_id": "SH-12345"}}'- 📨 **Redis Pub/Sub Messaging** - Inter-agent communication

```- 🎯 **Agent Registry** - Dynamic agent discovery and management

- 🔧 **Tool Execution Engine** - Standardized tool calling interface

### Calculate Route- 📊 **State Management** - Redis-backed agent state tracking

```bash- 🛡️ **Circuit Breakers** - Fault tolerance for external services

curl -X POST http://localhost:8001/message:send \- 📈 **Health Monitoring** - Agent status and performance metrics

  -H "Content-Type: application/json" \

  -d '{### Specialized Agents

    "skill": "calculate-route",

    "parameters": {#### 1. TrackingAgent 🚢

      "origin": "Los Angeles, CA",**Primary Responsibility:** Real-time shipment tracking and location updates

      "destination": "New York, NY"

    }**Capabilities:**

  }'- Continuous monitoring of shipment locations

```- ETA prediction and updates

- Anomaly detection (delays, stalls, route deviations)

### Get Analytics- Batch tracking operations

```bash- Automatic notifications on status changes

curl -X POST http://localhost:8001/message:send \

  -H "Content-Type: application/json" \**Tools Used:** `track_shipment`, `search_shipments`, `update_eta`

  -d '{

    "skill": "calculate-kpis",**Message Handlers:**

    "parameters": {- `TRACK_SHIPMENT` - Track a single shipment

      "kpi_types": ["on_time_delivery", "exception_rate"],- `SEARCH_SHIPMENTS` - Search with filters

      "timeframe": "monthly"- `UPDATE_ETA` - Update estimated arrival time

    }- `MONITOR_SHIPMENT` - Start continuous monitoring

  }'- `BATCH_TRACK` - Track multiple shipments

```

#### 2. ExceptionAgent ⚠️

---**Primary Responsibility:** Proactive issue detection and resolution



## All Skills**Capabilities:**

- Delay detection (>24h threshold by default)

### 🚚 Tracking- Severity assessment with scoring (0-10+ scale)

- `track-shipment` - Track single shipment- Automatic escalation for critical issues (score >= 8)

- `search-shipments` - Search by criteria- Risk flag management

- `batch-track` - Track up to 50 at once- Integration with TrackingAgent anomalies

- `monitor-shipments` - Auto-monitoring (5min loop)- Coordinates with RoutingAgent for alternatives

- `update-eta` - Update delivery estimate

**Tools Used:** `get_delayed_shipments`, `set_risk_flag`, `add_note`, `search_shipments`

### 🗺️ Routing

- `calculate-route` - Optimal route between two points**Message Handlers:**

- `optimize-route` - Multi-stop optimization- `CHECK_EXCEPTIONS` - Monitor delayed shipments

- `find-alternatives` - Backup routes- `ASSESS_SEVERITY` - Calculate severity score

- `ESCALATE` - Escalate critical issues

### ⚠️ Exception- `RESOLVE_EXCEPTION` - Mark as resolved

- `handle-exception` - Log and handle issues- `ANOMALY_DETECTED` - Handle TrackingAgent alerts

- `resolve-issue` - Mark as resolved

- `escalate-problem` - Escalate to management#### 3. RoutingAgent 🗺️

- `auto-detect-exceptions` - Auto-detect 24h+ delays**Primary Responsibility:** Route optimization and path planning



### 📊 Analytics**Capabilities:**

- `generate-report` - Create detailed reports- Optimal route calculation with caching

- `calculate-kpis` - Calculate KPIs- Alternative route suggestions (cost, reliability, air freight)

- `analyze-trends` - Trend analysis- Cost optimization strategies

- `forecast-performance` - Performance forecasting- Transit time estimation

- `query-database` - Database queries with caching- Historical data enhancement

- Synthetic route calculation fallback

---

**Tools Used:** `get_route_info`, `search_shipments`

## Architecture

**Message Handlers:**

```- `CALCULATE_ROUTE` - Calculate optimal route

Brain (:5000)- `GET_ALTERNATIVE_OPTIONS` - Find alternative paths

    ↓ HTTP- `OPTIMIZE_COST` - Cost-based optimization

A2A Server (:8001)- `ESTIMATE_TRANSIT` - Estimate transit time

    ↓ CrewExecutor (skill routing)

    ├─→ TrackingCrew#### 4. AnalyticsAgent 📊

    ├─→ RoutingCrew**Primary Responsibility:** KPIs, reporting, and forecasting

    ├─→ ExceptionCrew

    └─→ AnalyticsCrew**Capabilities:**

        ↓ MCP Tools- Generate operational reports (daily/weekly/monthly)

        ↓ MCP Pool- Calculate key performance indicators

        ↓- Trend analysis (delays, volume, routes)

CW-MCP Server (:8000)- Predictive forecasting

```- Historical performance tracking



**Design**: Single A2A endpoint with internal crew routing (simpler than multiple agents on different ports)**Tools Used:** `get_analytics`, `query_database`, `search_shipments`



---**Message Handlers:**

- `GENERATE_REPORT` - Create comprehensive reports

## Configuration- `GET_KPIS` - Calculate KPIs

- `ANALYZE_TRENDS` - Historical trend analysis

Key settings in `.env`:- `FORECAST` - Predictive forecasting

- `GET_HISTORICAL_PERFORMANCE` - Performance metrics

```env

# Server#### 5. DocumentationAgent 📄

SERVER_PORT=8001**Primary Responsibility:** Shipping document management



# LLM (dual model with automatic fallback)**Capabilities:**

LLM_STRATEGY=openai-first- Bill of Lading generation

OPENAI_API_KEY=your_key- Customs documentation

OLLAMA_BASE_URL=http://localhost:11434- Compliance verification

- Document retrieval

# MCP Server

MCP_SERVER_URL=http://localhost:8000**Tools Used:** `query_database`, external document APIs



# Redis (optional, for caching)**Status:** 🚧 Coming Soon

REDIS_HOST=localhost**Primary Responsibility:** KPIs, reporting, and forecasting

REDIS_ENABLED=True

```**Capabilities:**

- Real-time operational metrics

---- Predictive analytics

- Custom report generation

## API Endpoints- Trend analysis



| Method | Endpoint | Purpose |**Tools Used:** `get_analytics`, `query_database`, `advanced_search`

|--------|----------|---------|

| GET | `/.well-known/agent-card.json` | AgentCard discovery |## 🚀 Quick Start

| GET | `/health` | Health check |

| POST | `/message:send` | Execute skill (sync) |### Prerequisites

| POST | `/message:stream` | Execute skill (streaming) |

| POST | `/tasks` | Create async task |- Python 3.11+

| GET | `/tasks/{id}` | Get task status |- Redis 7.0+ (running locally or remote)

| GET | `/docs` | API documentation |- Access to CW-AI-SERVER (MCP server)

- CW-BRAIN (for orchestration)

---

### Installation

## Brain Integration

```bash

Create client in `cw-brain`:# Clone repository

cd cw-agents

```python

import httpx# Create virtual environment

python -m venv venv

class A2AAgentClient:source venv/bin/activate  # On Windows: venv\Scripts\activate

    def __init__(self, base_url="http://localhost:8001"):

        self.base_url = base_url# Install dependencies

        self.client = httpx.AsyncClient(base_url=base_url)pip install -r requirements.txt

    

    async def send_message(self, skill: str, parameters: dict):# Configure environment

        response = await self.client.post(cp .env.example .env

            "/message:send",# Edit .env with your settings

            json={"skill": skill, "parameters": parameters}```

        )

        return response.json()### Configuration

```

Create `.env` file:

Use in routes:

```env

```python# Redis Configuration

client = A2AAgentClient()REDIS_HOST=localhost

REDIS_PORT=6379

@app.post("/track")REDIS_DB=1

async def track(shipment_id: str):REDIS_PASSWORD=

    return await client.send_message(

        "track-shipment",# MCP Server

        {"shipment_id": shipment_id}MCP_SERVER_URL=https://cw-mcp.onrender.com

    )MCP_CONNECTION_POOL_SIZE=5

```MCP_TIMEOUT=30



---# Agent Configuration

AGENT_WORKER_COUNT=10

## TestingAGENT_QUEUE_SIZE=100

AGENT_TASK_TIMEOUT=60

```bash

# Run test suite (6 tests)# Logging

python test_a2a_server.pyLOG_LEVEL=INFO

LOG_FORMAT=json

# Test infrastructure

python test_crews.py# Health Checks

```HEALTH_CHECK_INTERVAL=30

AGENT_HEARTBEAT_INTERVAL=10

**All tests passing** ✅```



---### Running Agents



## Deployment```bash

# Start all agents

### Prerequisitespython -m src.main

1. CW-MCP Server running on :8000

2. Redis running on :6379 (optional)# Start specific agent

3. Ollama on :11434 or OpenAI API keypython -m src.agents.tracking_agent



### Start Services# Start with monitoring

```bashpython -m src.main --with-monitoring

# 1. MCP Server```

cd cw-ai-server && python src/server_fastmcp.py

### Testing

# 2. A2A Agent Server

cd cw-agents && python start_server.py```bash

# Run all tests

# 3. Brainpytest

cd cw-brain && python src/server.py

```# Run specific agent tests

pytest tests/test_tracking_agent.py

---

# Run with coverage

## Troubleshootingpytest --cov=src --cov-report=html

```

**Server won't start?**

- Check port 8001 is free: `lsof -i :8001`## 📁 Project Structure

- Verify MCP server running: `curl http://localhost:8000/health`

```

**LLM errors?**cw-agents/

- Check OpenAI API key├── src/

- Verify Ollama running: `curl http://localhost:11434/api/tags`│   ├── core/

- Try `LLM_STRATEGY=ollama-only`│   │   ├── __init__.py

│   │   ├── base_agent.py          # Abstract agent class

**Redis errors?**│   │   ├── agent_registry.py      # Agent discovery & management

- Set `REDIS_ENABLED=False` to disable│   │   ├── orchestrator.py        # Task distribution

- Or start Redis: `redis-server`│   │   ├── protocols.py           # A2A message formats

│   │   ├── exceptions.py          # Custom exceptions

---│   │   └── config.py              # Configuration management

│   │

## Project Structure│   ├── infrastructure/

│   │   ├── __init__.py

```│   │   ├── mcp_pool.py            # MCP connection pool

cw-agents/│   │   ├── redis_client.py        # Redis pub/sub client

├── src/│   │   ├── state_manager.py       # Agent state tracking

│   ├── a2a_server/        # AgentCards + FastAPI server│   │   ├── circuit_breaker.py     # Fault tolerance

│   ├── executors/         # Message routing│   │   └── health_monitor.py      # Health checks

│   ├── crews/             # 4 specialized crews│   │

│   ├── tools/             # MCP tool wrappers│   ├── agents/

│   ├── infrastructure/    # MCP pool + Redis│   │   ├── __init__.py

│   └── core/              # Config + LLM factory│   │   ├── tracking_agent.py      # Shipment tracking specialist

├── test_a2a_server.py     # Test suite│   │   ├── routing_agent.py       # Route optimization

├── start_server.py        # Server launcher│   │   ├── exception_agent.py     # Issue detection/handling

├── requirements.txt       # Dependencies│   │   ├── documentation_agent.py # Document management

└── README.md              # This file│   │   └── analytics_agent.py     # KPIs and reporting

```│   │

│   ├── integrations/

---│   │   ├── __init__.py

│   │   ├── brain_connector.py     # CW-Brain integration

## Why These Design Choices?│   │   └── mcp_connector.py       # MCP tool execution

│   │

**Single agent vs multiple?**│   ├── utils/

- One endpoint is simpler for internal monolithic system│   │   ├── __init__.py

- Easier Brain integration│   │   ├── logger.py              # Structured logging

- Faster (in-process routing)│   │   ├── metrics.py             # Performance metrics

- Can scale all together│   │   └── helpers.py             # Utility functions

│   │

**Custom A2A vs official SDK?**│   └── main.py                    # Application entry point

- SDK is for cross-org communication│

- We only need internal skill routing├── config/

- Simpler message format: `{"skill": "...", "parameters": {...}}`│   ├── agents.yaml                # Agent definitions

- Already tested and working│   ├── workflows.yaml             # Orchestration rules

│   └── tools.yaml                 # Tool configurations

---│

├── tests/

## Status│   ├── unit/                      # Unit tests

│   ├── integration/               # Integration tests

✅ **Complete & Tested**│   └── e2e/                       # End-to-end tests

- All 27 skills implemented│

- All 4 crews working├── docs/

- 6/6 tests passing│   ├── ARCHITECTURE.md            # System architecture

- FastAPI server ready│   ├── AGENTS.md                  # Agent specifications

- Dual LLM support (OpenAI + Ollama)│   ├── A2A_PROTOCOL.md            # Protocol documentation

│   └── DEPLOYMENT.md              # Deployment guide

🔜 **Next Steps**│

- Test live server├── .env.example                   # Environment template

- Integrate with Brain├── requirements.txt               # Python dependencies

- End-to-end testing├── pyproject.toml                 # Poetry configuration

├── docker-compose.yml             # Local development

---└── README.md                      # This file

```

**Version**: 1.0.0  

**Last Updated**: January 2, 2026  ## 🔧 Agent Development

**License**: MIT

### Creating a New Agent

```python
from src.core.base_agent import BaseAgent, AgentCapability
from src.core.protocols import AgentTask, AgentResponse

class CustomAgent(BaseAgent):
    """Custom agent implementation"""
    
    name = "custom_agent"
    capabilities = [
        AgentCapability.QUERY,
        AgentCapability.UPDATE,
    ]
    
    required_tools = [
        "search_shipments",
        "track_shipment"
    ]
    
    async def initialize(self):
        """Agent initialization logic"""
        await super().initialize()
        # Custom initialization
    
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """Process incoming task"""
        # Task processing logic
        result = await self.execute_tool(
            "track_shipment",
            identifier=task.payload.get("shipment_id")
        )
        
        return AgentResponse(
            success=True,
            data=result,
            metadata={"agent": self.name}
        )
    
    async def cleanup(self):
        """Agent cleanup logic"""
        await super().cleanup()
        # Custom cleanup
```

### Registering Agent

```yaml
# config/agents.yaml
agents:
  custom_agent:
    enabled: true
    instances: 2
    priority: 5
    capabilities:
      - query
      - update
    tools:
      - search_shipments
      - track_shipment
    config:
      polling_interval: 60
      batch_size: 10
```

## 📡 A2A Protocol

### Message Format

```python
{
    "message_id": "uuid",
    "from_agent": "tracking_agent_01",
    "to_agent": "exception_agent",  # or "orchestrator"
    "action": "DELAY_DETECTED",
    "payload": {
        "shipment_id": "JOB-2025-002",
        "severity": "high",
        "details": {
            "delay_hours": 48,
            "reason": "Port congestion"
        }
    },
    "timestamp": "2025-12-28T10:00:00Z",
    "requires_response": true,
    "correlation_id": "parent-task-uuid"
}
```

### Communication Patterns

#### 1. Request-Response
```python
# Agent A sends request
response = await agent.send_and_wait(
    to_agent="routing_agent",
    action="CALCULATE_ROUTE",
    payload={"origin": "HKG", "destination": "RTM"}
)
```

#### 2. Fire-and-Forget
```python
# Agent A sends notification
await agent.publish(
    to_agent="analytics_agent",
    action="SHIPMENT_DELIVERED",
    payload={"shipment_id": "JOB-001"}
)
```

#### 3. Broadcast
```python
# Orchestrator broadcasts to all agents
await orchestrator.broadcast(
    action="SYSTEM_SHUTDOWN",
    payload={"reason": "Maintenance"}
)
```

## 🔍 Monitoring & Observability

### Health Checks

```bash
# Check all agents status
curl http://localhost:9000/health

# Check specific agent
curl http://localhost:9000/health/tracking_agent
```

### Metrics

```bash
# Prometheus metrics endpoint
curl http://localhost:9000/metrics
```

**Available Metrics:**
- `agent_tasks_total` - Total tasks processed
- `agent_tasks_duration_seconds` - Task processing time
- `agent_errors_total` - Error count
- `mcp_tool_calls_total` - MCP tool usage
- `redis_messages_total` - Message count

## 🛣️ Roadmap

### Phase 1: Foundation ✅
- [x] Base agent framework
- [x] MCP connection pool
- [x] Redis pub/sub messaging
- [x] Agent registry
- [x] TrackingAgent implementation

### Phase 2: Core Agents (In Progress)
- [ ] RoutingAgent
- [ ] ExceptionAgent
- [ ] DocumentationAgent
- [ ] AnalyticsAgent

### Phase 3: Intelligence
- [ ] Machine learning integration
- [ ] Predictive analytics
- [ ] Auto-scaling based on load
- [ ] Agent collaboration patterns

### Phase 4: Production
- [ ] Kubernetes deployment
- [ ] Multi-region support
- [ ] Advanced monitoring
- [ ] Performance optimization

## 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Agent Specifications](docs/AGENTS.md)
- [A2A Protocol](docs/A2A_PROTOCOL.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Integration with Other Services

### CW-Brain Integration

CW-Brain acts as the orchestrator, delegating tasks to specialized agents:

```python
# In CW-Brain
from src.agents.agent_coordinator import AgentCoordinator

coordinator = AgentCoordinator()

# Delegate to tracking agent
result = await coordinator.request_agent_action(
    agent_type="tracking_agent",
    task={
        "action": "TRACK_SHIPMENT",
        "shipment_id": "JOB-2025-001"
    }
)
```

### CW-AI-Server Integration

Agents connect to CW-AI-SERVER via MCP protocol for tool execution:

```python
# Agents use shared MCP pool
result = await self.mcp_pool.execute_tool(
    tool_name="track_shipment",
    parameters={"identifier": "JOB-2025-001"}
)
```

## 🐛 Troubleshooting

### Common Issues

**Issue: Agent not receiving messages**
```bash
# Check Redis connection
redis-cli ping

# Check agent subscription
redis-cli PUBSUB CHANNELS agents:*
```

**Issue: MCP connection timeout**
```bash
# Check MCP server health
curl https://cw-mcp.onrender.com/health

# Increase timeout in .env
MCP_TIMEOUT=60
```

## 📄 License

Proprietary - Artificial Mind © 2025

## 👥 Contributing

Internal project. For questions, contact the CW team.

---

**Built with ❤️ for the future of logistics automation**
