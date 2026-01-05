"""
A2A Protocol AgentCards - Define capabilities and skills for each crew.
Based on A2A Protocol v1.0 specification.
"""
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# AgentCard Base Structure
# ============================================================================

def create_base_card(
    agent_id: str,
    name: str,
    description: str,
    skills: List[Dict[str, Any]],
    capabilities: List[str],
) -> Dict[str, Any]:
    """Create base AgentCard structure per A2A v1.0 spec."""
    return {
        "agent_id": agent_id,
        "name": name,
        "description": description,
        "version": "1.0.0",
        "protocol_version": "1.0",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "skills": skills,
        "capabilities": capabilities,
        "endpoints": {
            "message_send": "/message:send",
            "message_stream": "/message:stream",
            "task_create": "/tasks",
            "task_status": "/tasks/{task_id}",
            "task_cancel": "/tasks/{task_id}/cancel"
        },
        "supported_modes": ["synchronous", "asynchronous", "streaming"],
        "authentication": {
            "type": "bearer",
            "required": False
        }
    }


# ============================================================================
# Tracking Crew AgentCard
# ============================================================================

TRACKING_CARD = create_base_card(
    agent_id="cw-tracking-crew",
    name="CW Tracking Crew",
    description="Multi-agent crew for shipment tracking, monitoring, and ETA management. Specializes in real-time tracking updates, batch processing, and automated monitoring.",
    skills=[
        {
            "name": "track-shipment",
            "description": "Track individual shipment by ID and get current status, location, and ETA",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shipment_id": {
                        "type": "string",
                        "description": "Unique shipment identifier"
                    }
                },
                "required": ["shipment_id"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "shipment_id": {"type": "string"},
                    "status": {"type": "string"},
                    "location": {"type": "string"},
                    "eta": {"type": "string"},
                    "last_update": {"type": "string"}
                }
            },
            "examples": [
                {
                    "input": {"shipment_id": "SH-12345"},
                    "output": {
                        "shipment_id": "SH-12345",
                        "status": "in_transit",
                        "location": "Los Angeles, CA",
                        "eta": "2026-01-05T14:00:00Z",
                        "last_update": "2026-01-02T18:30:00Z"
                    }
                }
            ]
        },
        {
            "name": "search-shipments",
            "description": "Search shipments by various criteria (status, customer, date range, etc.)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "object",
                        "description": "Search criteria",
                        "properties": {
                            "status": {"type": "string"},
                            "customer_id": {"type": "string"},
                            "date_from": {"type": "string"},
                            "date_to": {"type": "string"}
                        }
                    },
                    "limit": {
                        "type": "integer",
                        "default": 50,
                        "maximum": 100
                    }
                },
                "required": ["query"]
            },
            "output_schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "shipment_id": {"type": "string"},
                        "status": {"type": "string"},
                        "customer_id": {"type": "string"}
                    }
                }
            }
        },
        {
            "name": "batch-track",
            "description": "Track multiple shipments in batch (up to 50 shipments)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shipment_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 50
                    }
                },
                "required": ["shipment_ids"]
            }
        },
        {
            "name": "monitor-shipments",
            "description": "Start automated monitoring loop for active shipments (5-minute intervals)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Filters for shipments to monitor"
                    }
                }
            }
        },
        {
            "name": "update-eta",
            "description": "Update estimated time of arrival for a shipment",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shipment_id": {"type": "string"},
                    "new_eta": {"type": "string", "format": "date-time"},
                    "reason": {"type": "string"}
                },
                "required": ["shipment_id", "new_eta", "reason"]
            }
        },
        {
            "name": "track-vessel",
            "description": "Track a vessel in real-time using AIS data. Get live position, speed, heading, status, destination, and ETA.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "vessel_name": {
                        "type": "string",
                        "description": "Name of the vessel to track (e.g., 'MAERSK ESSEX', 'MSC GULSUN')"
                    }
                },
                "required": ["vessel_name"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "vessel_name": {"type": "string"},
                    "imo": {"type": "string"},
                    "position": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "number"},
                            "lon": {"type": "number"}
                        }
                    },
                    "navigation": {
                        "type": "object",
                        "properties": {
                            "speed": {"type": "number"},
                            "heading": {"type": "number"}
                        }
                    },
                    "destination": {"type": "string"},
                    "eta": {"type": "string"}
                }
            }
        },
        {
            "name": "predict-delay",
            "description": "Predict if a shipment will be delayed using ML model. Provides probability, confidence score, risk factors, and recommendations.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shipment_id": {
                        "type": "string",
                        "description": "Shipment ID, container number, or bill of lading"
                    }
                },
                "required": ["shipment_id"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "shipment_id": {"type": "string"},
                    "will_delay": {"type": "boolean"},
                    "confidence": {"type": "number", "description": "Confidence score 0-1"},
                    "delay_probability": {"type": "number", "description": "Probability of delay 0-1"},
                    "risk_factors": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "recommendation": {"type": "string"},
                    "model_accuracy": {"type": "number"}
                }
            },
            "examples": [
                {
                    "input": {"shipment_id": "job-2025-001"},
                    "output": {
                        "shipment_id": "job-2025-001",
                        "will_delay": False,
                        "confidence": 0.731,
                        "delay_probability": 0.269,
                        "risk_factors": ["Historical route performance analysis"],
                        "recommendation": "Moderate confidence in on-time delivery - continue monitoring.",
                        "model_accuracy": 0.815
                    }
                }
            ]
        },
        
        # Document generation skills
        {
            "name": "generate-bol",
            "description": "Generate Bill of Lading (BOL) PDF document for a shipment. BOL is the critical shipping document that serves as receipt, contract of carriage, and document of title.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "shipment_id": {
                        "type": "string",
                        "description": "Unique shipment identifier"
                    }
                },
                "required": ["shipment_id"]
            },
            "outputSchema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "document_type": {"type": "string"},
                    "document_number": {"type": "string"},
                    "file_path": {"type": "string"},
                    "document_url": {"type": "string"},
                    "file_size_kb": {"type": "number"}
                }
            },
            "examples": [
                {
                    "input": {"shipment_id": "job-2025-001"},
                    "output": {
                        "success": True,
                        "document_type": "BILL_OF_LADING",
                        "document_number": "BOL-job-2025-001",
                        "file_path": "/generated_documents/BOL_job-2025-001.pdf",
                        "document_url": "/documents/BOL_job-2025-001.pdf",
                        "file_size_kb": 2.65
                    }
                }
            ]
        },
        {
            "name": "generate-invoice",
            "description": "Generate Commercial Invoice PDF for customs clearance. Includes exporter/importer details, line items with HS codes, pricing, and declared customs value.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "shipment_id": {
                        "type": "string",
                        "description": "Unique shipment identifier"
                    },
                    "invoice_number": {
                        "type": "string",
                        "description": "Optional invoice number (auto-generated if not provided)"
                    }
                },
                "required": ["shipment_id"]
            },
            "outputSchema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "document_type": {"type": "string"},
                    "invoice_number": {"type": "string"},
                    "file_path": {"type": "string"},
                    "document_url": {"type": "string"},
                    "file_size_kb": {"type": "number"},
                    "total_amount": {"type": "number"},
                    "currency": {"type": "string"}
                }
            },
            "examples": [
                {
                    "input": {"shipment_id": "job-2025-001", "invoice_number": "INV-2025-001"},
                    "output": {
                        "success": True,
                        "document_type": "COMMERCIAL_INVOICE",
                        "invoice_number": "INV-2025-001",
                        "file_path": "/generated_documents/INV_INV-2025-001.pdf",
                        "document_url": "/documents/INV_INV-2025-001.pdf",
                        "file_size_kb": 2.53,
                        "total_amount": 241500.00,
                        "currency": "USD"
                    }
                }
            ]
        },
        {
            "name": "generate-packing-list",
            "description": "Generate Packing List PDF with detailed cargo breakdown. Includes package-by-package details, items, dimensions, weights, and special handling instructions.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "shipment_id": {
                        "type": "string",
                        "description": "Unique shipment identifier"
                    },
                    "packing_list_number": {
                        "type": "string",
                        "description": "Optional packing list number (auto-generated if not provided)"
                    }
                },
                "required": ["shipment_id"]
            },
            "outputSchema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "document_type": {"type": "string"},
                    "packing_list_number": {"type": "string"},
                    "file_path": {"type": "string"},
                    "document_url": {"type": "string"},
                    "file_size_kb": {"type": "number"},
                    "total_packages": {"type": "integer"},
                    "total_weight_kg": {"type": "number"}
                }
            },
            "examples": [
                {
                    "input": {"shipment_id": "job-2025-001"},
                    "output": {
                        "success": True,
                        "document_type": "PACKING_LIST",
                        "packing_list_number": "PKG-job-2025-001",
                        "file_path": "/generated_documents/PKG_PKG-job-2025-001.pdf",
                        "document_url": "/documents/PKG_PKG-job-2025-001.pdf",
                        "file_size_kb": 2.24,
                        "total_packages": 2,
                        "total_weight_kg": 401.3
                    }
                }
            ]
        }
    ],
    capabilities=[
        "shipment-tracking",
        "vessel-tracking",
        "real-time-monitoring",
        "batch-processing",
        "eta-management",
        "predictive-analytics",
        "ml-predictions",
        "document-generation",
        "pdf-export",
        "customs-documents",
        "state-persistence"
    ]
)


# ============================================================================
# Routing Crew AgentCard
# ============================================================================

ROUTING_CARD = create_base_card(
    agent_id="cw-routing-crew",
    name="CW Routing Crew",
    description="Multi-agent crew for route calculation, optimization, and alternative route planning. Specializes in multi-modal transport, waypoint optimization, and constraint handling.",
    skills=[
        {
            "name": "calculate-route",
            "description": "Calculate optimal route between origin and destination with mode and constraints",
            "input_schema": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Origin location (address or coordinates)"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination location (address or coordinates)"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["driving", "truck", "rail", "ship"],
                        "default": "driving"
                    },
                    "constraints": {
                        "type": "object",
                        "properties": {
                            "avoid_tolls": {"type": "boolean"},
                            "avoid_highways": {"type": "boolean"},
                            "max_weight": {"type": "number"},
                            "hazmat": {"type": "boolean"}
                        }
                    }
                },
                "required": ["origin", "destination"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "route_id": {"type": "string"},
                    "distance": {"type": "number"},
                    "duration": {"type": "number"},
                    "waypoints": {"type": "array"},
                    "estimated_cost": {"type": "number"}
                }
            }
        },
        {
            "name": "optimize-route",
            "description": "Optimize route for multiple waypoints to minimize distance/time/cost",
            "input_schema": {
                "type": "object",
                "properties": {
                    "waypoints": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of locations to visit"
                    },
                    "start_location": {"type": "string"},
                    "end_location": {"type": "string"},
                    "optimization_goal": {
                        "type": "string",
                        "enum": ["shortest", "fastest", "cheapest"],
                        "default": "shortest"
                    }
                },
                "required": ["waypoints", "start_location"]
            }
        },
        {
            "name": "find-alternatives",
            "description": "Find alternative routes when primary route has issues",
            "input_schema": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "current_issue": {
                        "type": "string",
                        "description": "Issue with current route (traffic, closure, weather, etc.)"
                    },
                    "max_alternatives": {
                        "type": "integer",
                        "default": 3,
                        "maximum": 5
                    }
                },
                "required": ["origin", "destination", "current_issue"]
            }
        }
    ],
    capabilities=[
        "route-optimization",
        "multi-modal-transport",
        "waypoint-optimization",
        "constraint-handling",
        "alternative-routing"
    ]
)


# ============================================================================
# Exception Crew AgentCard
# ============================================================================

EXCEPTION_CARD = create_base_card(
    agent_id="cw-exception-crew",
    name="CW Exception Crew",
    description="Multi-agent crew for exception handling, issue resolution, and escalation management. Specializes in delay handling, damage assessment, auto-detection, and resolution tracking.",
    skills=[
        {
            "name": "handle-exception",
            "description": "Handle and log shipping exceptions (delays, damage, lost items, etc.)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shipment_id": {"type": "string"},
                    "exception_type": {
                        "type": "string",
                        "enum": ["delay", "damage", "lost", "customs", "address_issue", "weather", "carrier_issue"]
                    },
                    "description": {"type": "string"},
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "default": "medium"
                    }
                },
                "required": ["shipment_id", "exception_type", "description"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "exception_id": {"type": "string"},
                    "status": {"type": "string"},
                    "recommended_actions": {"type": "array"}
                }
            }
        },
        {
            "name": "resolve-issue",
            "description": "Mark an exception/issue as resolved with resolution details",
            "input_schema": {
                "type": "object",
                "properties": {
                    "exception_id": {"type": "string"},
                    "resolution": {
                        "type": "string",
                        "description": "Resolution action taken"
                    },
                    "notes": {"type": "string"}
                },
                "required": ["exception_id", "resolution", "notes"]
            }
        },
        {
            "name": "escalate-problem",
            "description": "Escalate unresolved exception to higher management level",
            "input_schema": {
                "type": "object",
                "properties": {
                    "exception_id": {"type": "string"},
                    "escalation_level": {
                        "type": "string",
                        "enum": ["manager", "director", "executive"]
                    },
                    "reason": {"type": "string"}
                },
                "required": ["exception_id", "escalation_level", "reason"]
            }
        },
        {
            "name": "auto-detect-exceptions",
            "description": "Automatically detect shipments with potential exceptions (24+ hour delays)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "threshold_hours": {
                        "type": "integer",
                        "default": 24
                    }
                }
            }
        }
    ],
    capabilities=[
        "exception-handling",
        "issue-resolution",
        "escalation-management",
        "auto-detection",
        "severity-assessment"
    ]
)


# ============================================================================
# Analytics Crew AgentCard
# ============================================================================

ANALYTICS_CARD = create_base_card(
    agent_id="cw-analytics-crew",
    name="CW Analytics Crew",
    description="Multi-agent crew for KPIs, reports, trends analysis, and performance forecasting. Specializes in data aggregation, visualization, predictive analytics, and caching.",
    skills=[
        {
            "name": "generate-report",
            "description": "Generate comprehensive analytics report for specified date range",
            "input_schema": {
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["shipments", "exceptions", "performance", "carrier", "customer"]
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Additional filters"
                    }
                },
                "required": ["report_type", "start_date", "end_date"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "report_id": {"type": "string"},
                    "summary": {"type": "object"},
                    "data": {"type": "array"},
                    "visualizations": {"type": "array"}
                }
            }
        },
        {
            "name": "calculate-kpis",
            "description": "Calculate key performance indicators for shipment operations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "kpi_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["on_time_delivery", "exception_rate", "avg_delivery_time", "customer_satisfaction", "cost_per_shipment"]
                        }
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly", "quarterly"]
                    }
                },
                "required": ["kpi_types", "timeframe"]
            }
        },
        {
            "name": "analyze-trends",
            "description": "Analyze trends in shipment data and identify patterns",
            "input_schema": {
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "Metric to analyze (volume, delays, costs, etc.)"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period for analysis"
                    }
                },
                "required": ["metric", "period"]
            }
        },
        {
            "name": "forecast-performance",
            "description": "Forecast future performance based on historical data",
            "input_schema": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string"},
                    "forecast_days": {
                        "type": "integer",
                        "default": 30
                    },
                    "confidence_level": {
                        "type": "number",
                        "default": 0.95
                    }
                },
                "required": ["metric"]
            }
        },
        {
            "name": "query-database",
            "description": "Query database for specific information with caching",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string",
                        "enum": ["shipments", "customers", "carriers", "routes", "exceptions"]
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Query parameters"
                    }
                },
                "required": ["query_type", "parameters"]
            }
        }
    ],
    capabilities=[
        "analytics-reporting",
        "kpi-calculation",
        "trend-analysis",
        "performance-forecasting",
        "data-caching"
    ]
)


# ============================================================================
# Combined AgentCard (All Crews)
# ============================================================================

COMBINED_CARD = {
    "agent_id": "cw-agents-system",
    "name": "CW Multi-Agent System",
    "description": "Comprehensive multi-crew agent system for logistics and supply chain management. Includes tracking, routing, exception handling, and analytics capabilities.",
    "version": "1.0.0",
    "protocol_version": "1.0",
    "created_at": datetime.utcnow().isoformat() + "Z",
    "crews": [
        {
            "crew_id": "tracking",
            "name": "Tracking Crew",
            "skills": [skill["name"] for skill in TRACKING_CARD["skills"]],
            "agent_card": TRACKING_CARD
        },
        {
            "crew_id": "routing",
            "name": "Routing Crew",
            "skills": [skill["name"] for skill in ROUTING_CARD["skills"]],
            "agent_card": ROUTING_CARD
        },
        {
            "crew_id": "exception",
            "name": "Exception Crew",
            "skills": [skill["name"] for skill in EXCEPTION_CARD["skills"]],
            "agent_card": EXCEPTION_CARD
        },
        {
            "crew_id": "analytics",
            "name": "Analytics Crew",
            "skills": [skill["name"] for skill in ANALYTICS_CARD["skills"]],
            "agent_card": ANALYTICS_CARD
        }
    ],
    "all_skills": [
        *[skill["name"] for skill in TRACKING_CARD["skills"]],
        *[skill["name"] for skill in ROUTING_CARD["skills"]],
        *[skill["name"] for skill in EXCEPTION_CARD["skills"]],
        *[skill["name"] for skill in ANALYTICS_CARD["skills"]]
    ],
    "all_capabilities": [
        *TRACKING_CARD["capabilities"],
        *ROUTING_CARD["capabilities"],
        *EXCEPTION_CARD["capabilities"],
        *ANALYTICS_CARD["capabilities"]
    ],
    "endpoints": {
        "message_send": "/message:send",
        "message_stream": "/message:stream",
        "task_create": "/tasks",
        "task_status": "/tasks/{task_id}",
        "task_cancel": "/tasks/{task_id}/cancel",
        "agent_card": "/.well-known/agent-card.json"
    },
    "supported_modes": ["synchronous", "asynchronous", "streaming"],
    "authentication": {
        "type": "bearer",
        "required": False
    }
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_card_by_crew(crew_name: str) -> Dict[str, Any]:
    """Get AgentCard for specific crew."""
    cards = {
        "tracking": TRACKING_CARD,
        "routing": ROUTING_CARD,
        "exception": EXCEPTION_CARD,
        "analytics": ANALYTICS_CARD
    }
    return cards.get(crew_name.lower())


def get_crew_by_skill(skill_name: str) -> str:
    """Map skill name to crew name."""
    skill_map = {
        # Tracking skills
        "track-shipment": "tracking",
        "search-shipments": "tracking",
        "batch-track": "tracking",
        "monitor-shipments": "tracking",
        "update-eta": "tracking",
        "track-vessel": "tracking",
        # Routing skills
        "calculate-route": "routing",
        "optimize-route": "routing",
        "find-alternatives": "routing",
        # Exception skills
        "handle-exception": "exception",
        "resolve-issue": "exception",
        "escalate-problem": "exception",
        "auto-detect-exceptions": "exception",
        # Analytics skills
        "generate-report": "analytics",
        "calculate-kpis": "analytics",
        "analyze-trends": "analytics",
        "forecast-performance": "analytics",
        "query-database": "analytics"
    }
    return skill_map.get(skill_name.lower())


def list_all_skills() -> List[str]:
    """List all available skills across all crews."""
    return COMBINED_CARD["all_skills"]


def list_all_capabilities() -> List[str]:
    """List all capabilities across all crews."""
    return COMBINED_CARD["all_capabilities"]
