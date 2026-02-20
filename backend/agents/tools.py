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
                "name": "network_recon",
                "description": "Performs reconnaissance on a target using the agent's internal port scanning engine.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "Target IP or hostname"},
                        "ports": {"type": "string", "description": "Comma-separated list of ports (e.g. 80,443,8080)"}
                    },
                    "required": ["target", "ports"]
                }
            },
            {
                "name": "system_audit",
                "description": "Executes a deep-tissue system audit to capture OS state, processes, and memory telemetry.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "list_sandbox_files",
                "description": "Retrieves a listing of all operational artifacts, logs, and files within the agent's personal sandbox.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
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
            }
        ]
