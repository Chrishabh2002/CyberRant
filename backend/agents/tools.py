"""
CyberRant Tool Definitions
Used by Rant AI Agent to interact with the platform and infrastructure.
"""

from typing import List, Dict, Any

class CyberRantTools:
    @staticmethod
    def get_tool_definitions() -> List[Dict[str, Any]]:
        return [
            {
                "name": "quarantine_instance",
                "description": "Isolates a cloud instance by moving it to a restricted security group.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string", "description": "The unique ID of the instance (e.g., i-12345678)"},
                        "cloud_provider": {"enum": ["aws", "azure", "gcp"], "description": "The cloud platform"},
                        "reason": {"type": "string", "description": "Justification for the quarantine"}
                    },
                    "required": ["instance_id", "cloud_provider"]
                }
            },
            {
                "name": "list_exposed_assets",
                "description": "Retrieves a list of internal assets with public-facing vulnerabilities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "severity_threshold": {"enum": ["low", "medium", "high", "critical"]},
                        "limit": {"type": "integer", "default": 10}
                    }
                }
            },
            {
                "name": "trigger_scan",
                "description": "Initiates a new security scan on a target domain or IP range.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "Domain or CIDR range"},
                        "scan_type": {"enum": ["vulnerability", "port", "compliance"]}
                    },
                    "required": ["target", "scan_type"]
                }
            }
        ]
