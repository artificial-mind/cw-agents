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
        
        # Day 6 - Real-time tracking skills (Tools 12-14)
        {
            "name": "track-vessel-realtime",
            "description": "Track vessel in real-time using AIS data with comprehensive navigation details. Provides live GPS position, speed in knots, heading in degrees, vessel status, next port, and ETA.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "vessel_name": {
                        "type": "string",
                        "description": "Name of the vessel (e.g., 'MAERSK SEALAND', 'MSC GULSUN')"
                    },
                    "imo_number": {
                        "type": "string",
                        "description": "IMO number (7 digits) - alternative to vessel_name"
                    },
                    "mmsi": {
                        "type": "string",
                        "description": "MMSI number (9 digits) - alternative to vessel_name"
                    }
                }
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "vessel_name": {"type": "string"},
                    "imo": {"type": "string"},
                    "mmsi": {"type": "string"},
                    "position": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "number"},
                            "lon": {"type": "number"}
                        }
                    },
                    "speed": {"type": "number", "description": "Speed in knots"},
                    "heading": {"type": "number", "description": "Heading in degrees"},
                    "status": {"type": "string", "description": "Navigation status"},
                    "next_port": {"type": "string"},
                    "eta": {"type": "string", "format": "date-time"}
                }
            },
            "examples": [
                {
                    "input": {"vessel_name": "MAERSK"},
                    "output": {
                        "vessel_name": "MAERSK SEALAND",
                        "position": {"lat": 37.776995, "lon": -122.420063},
                        "speed": 12.64,
                        "heading": 273.0,
                        "status": "Underway using engine",
                        "next_port": "Oakland",
                        "eta": "2025-01-25T14:00:00Z"
                    }
                }
            ]
        },
        {
            "name": "track-multimodal",
            "description": "Track shipment across multiple transport modes (ocean, rail, truck). Shows complete journey with all legs, progress percentage, current location, and handoff points between carriers.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shipment_id": {
                        "type": "string",
                        "description": "Shipment or job number (e.g., 'job-2025-001')"
                    }
                },
                "required": ["shipment_id"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "shipment_id": {"type": "string"},
                    "status": {"type": "string"},
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "current_mode": {"type": "string"},
                    "current_location": {"type": "string"},
                    "progress_percentage": {"type": "number"},
                    "journey": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "leg_number": {"type": "integer"},
                                "mode": {"type": "string"},
                                "carrier": {"type": "string"},
                                "from": {"type": "string"},
                                "to": {"type": "string"},
                                "status": {"type": "string"},
                                "eta": {"type": "string"}
                            }
                        }
                    },
                    "total_legs": {"type": "integer"},
                    "completed_legs": {"type": "integer"}
                }
            },
            "examples": [
                {
                    "input": {"shipment_id": "job-2025-001"},
                    "output": {
                        "shipment_id": "job-2025-001",
                        "status": "in_transit",
                        "progress_percentage": 16.7,
                        "current_mode": "ocean",
                        "journey": [
                            {
                                "leg_number": 1,
                                "mode": "ocean",
                                "from": "Shanghai Port",
                                "to": "Los Angeles Port",
                                "status": "in_transit"
                            }
                        ]
                    }
                }
            ]
        },
        {
            "name": "track-container-live",
            "description": "Track container with live IoT sensor data. Provides real-time GPS location, temperature monitoring, humidity, shock detection, door events, battery level, and active alerts.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "container_number": {
                        "type": "string",
                        "description": "Container number (e.g., 'MAEU1234567')"
                    }
                },
                "required": ["container_number"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "container_number": {"type": "string"},
                    "container_type": {"type": "string"},
                    "shipment_id": {"type": "string"},
                    "tracking_status": {"type": "string"},
                    "battery_level": {"type": "integer"},
                    "gps": {
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                            "accuracy_meters": {"type": "integer"}
                        }
                    },
                    "temperature": {
                        "type": "object",
                        "properties": {
                            "temperature_celsius": {"type": "number"},
                            "setpoint_celsius": {"type": "number"},
                            "deviation": {"type": "number"}
                        }
                    },
                    "humidity": {
                        "type": "object",
                        "properties": {
                            "relative_humidity_percent": {"type": "number"}
                        }
                    },
                    "shock_events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {"type": "string"},
                                "severity": {"type": "string"},
                                "g_force": {"type": "number"}
                            }
                        }
                    },
                    "door_events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {"type": "string"},
                                "action": {"type": "string"},
                                "location": {"type": "string"}
                            }
                        }
                    },
                    "alerts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "severity": {"type": "string"},
                                "message": {"type": "string"}
                            }
                        }
                    },
                    "alert_count": {"type": "integer"}
                }
            },
            "examples": [
                {
                    "input": {"container_number": "MAEU1234567"},
                    "output": {
                        "container_number": "MAEU1234567",
                        "container_type": "40HC Reefer",
                        "gps": {"latitude": 37.776995, "longitude": -122.420063},
                        "temperature": {
                            "temperature_celsius": -15.8,
                            "setpoint_celsius": -18.0,
                            "deviation": 2.2
                        },
                        "alerts": [
                            {
                                "type": "temperature_deviation",
                                "severity": "medium",
                                "message": "Temperature deviation: 2.2°C from setpoint"
                            }
                        ],
                        "alert_count": 1
                    }
                }
            ]
        },
        
        # Customer communication skills (Day 7 - Tool 28)
        {
            "name": "send-status-update",
            "description": "Send shipment status notification to customer via email or SMS. Supports multiple notification types (departed, in_transit, arrived, customs_cleared, delivered, delay_warning, exception_alert) and languages.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shipment_id": {
                        "type": "string",
                        "description": "Shipment ID"
                    },
                    "notification_type": {
                        "type": "string",
                        "description": "Type of notification",
                        "enum": ["departed", "in_transit", "arrived", "customs_cleared", "delivered", "delay_warning", "exception_alert"]
                    },
                    "recipient_email": {
                        "type": "string",
                        "description": "Customer email address"
                    },
                    "recipient_phone": {
                        "type": "string",
                        "description": "Customer phone number (format: +1234567890)"
                    },
                    "channel": {
                        "type": "string",
                        "description": "Delivery channel",
                        "enum": ["email", "sms", "both"],
                        "default": "email"
                    },
                    "language": {
                        "type": "string",
                        "description": "Notification language",
                        "enum": ["en", "ar", "zh"],
                        "default": "en"
                    }
                },
                "required": ["shipment_id", "notification_type"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "shipment_id": {"type": "string"},
                    "notification_type": {"type": "string"},
                    "channel": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "deliveries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "channel": {"type": "string"},
                                "recipient": {"type": "string"},
                                "delivered": {"type": "boolean"},
                                "message_id": {"type": "string"}
                            }
                        }
                    },
                    "content_preview": {"type": "string"}
                }
            },
            "examples": [
                {
                    "input": {
                        "shipment_id": "SHIP12345",
                        "notification_type": "departed",
                        "recipient_email": "customer@example.com",
                        "channel": "email",
                        "language": "en"
                    },
                    "output": {
                        "success": True,
                        "shipment_id": "SHIP12345",
                        "notification_type": "departed",
                        "channel": "email",
                        "deliveries": [
                            {
                                "channel": "email",
                                "recipient": "customer@example.com",
                                "delivered": True,
                                "message_id": "email-SHIP12345-1704635000"
                            }
                        ],
                        "content_preview": "Shipment SHIP12345 Has Departed"
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
        },
        {
            "name": "proactive-delay-warning",
            "description": "Proactively warn customers about potential delays using ML predictions. Automatically triggers if ML confidence exceeds 70%. Includes risk factors and recommended actions.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shipment_id": {
                        "type": "string",
                        "description": "Shipment ID to monitor for delays"
                    },
                    "recipient_email": {
                        "type": "string",
                        "description": "Customer email address (optional)"
                    }
                },
                "required": ["shipment_id"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "warning_sent": {
                        "type": "boolean",
                        "description": "Whether proactive warning was sent"
                    },
                    "ml_confidence": {
                        "type": "number",
                        "description": "ML prediction confidence (0.0-1.0)"
                    },
                    "risk_factors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Identified risk factors"
                    },
                    "predicted_delay_hours": {
                        "type": "integer",
                        "description": "Predicted delay duration in hours"
                    }
                }
            },
            "examples": [
                {
                    "input": {
                        "shipment_id": "job-2025-001",
                        "recipient_email": "customer@example.com"
                    },
                    "output": {
                        "warning_sent": True,
                        "ml_confidence": 0.85,
                        "risk_factors": ["Weather conditions", "Port congestion"],
                        "predicted_delay_hours": 24
                    }
                }
            ]
        }
    ],
    capabilities=[
        "exception-handling",
        "issue-resolution",
        "escalation-management",
        "auto-detection",
        "severity-assessment",
        "proactive-monitoring"
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
        },
        {
            "name": "generate-tracking-link",
            "description": "Generate a public tracking link for customer portal access without authentication. Links are valid for 30 days and allow customers to track their shipment without logging in.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shipment_id": {
                        "type": "string",
                        "description": "Shipment ID to generate tracking link for"
                    }
                },
                "required": ["shipment_id"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "tracking_url": {
                        "type": "string",
                        "description": "Public tracking URL (e.g., https://track.cwlogistics.com/abc-123-xyz)"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Link expiry date/time"
                    },
                    "token": {
                        "type": "string",
                        "description": "Unique tracking token (UUID)"
                    }
                }
            },
            "examples": [
                {
                    "input": {"shipment_id": "job-2025-001"},
                    "output": {
                        "tracking_url": "https://track.cwlogistics.com/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "expires_at": "2026-02-06T00:00:00Z",
                        "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
                    }
                }
            ]
        }
    ],
    capabilities=[
        "analytics-reporting",
        "kpi-calculation",
        "trend-analysis",
        "performance-forecasting",
        "data-caching",
        "public-tracking-links"
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
        "track-vessel-realtime": "tracking",
        "track-multimodal": "tracking",
        "track-container-live": "tracking",
        # Customer communication skills
        "send-status-update": "tracking",
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
