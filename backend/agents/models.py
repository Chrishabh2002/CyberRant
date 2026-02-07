from enum import Enum
from typing import Optional, List, Dict, Any

class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    TOOL_EXECUTING = "tool_executing"
    AWAITING_APPROVAL = "awaiting_approval"
    PARTIAL_SUCCESS = "partial_success"
    COMPLETED = "completed"
    REFUSED = "refused"      # Soft policy (e.g., tone, style, off-topic)
    BLOCKED = "blocked"      # Hard Red-Line (Security violation)
    FAILED = "failed"
    SYSTEM_OFFLINE = "system_offline"

class FeatureFlag(Enum):
    CAN_WRITE_SCRIPTS = "can_write_scripts"
    CAN_MODIFY_INFRA = "can_modify_infra"
    CAN_READ_SCAN_DATA = "can_read_scan_data"
    AUDIO_OUTPUT = "audio_output"

class SystemConfig:
    # In production, these should be managed via secure vault/env
    IS_SYSTEM_ARMED = True
    ACTIVE_PROMPT_VERSION = "v1.0.2-stable"

class GovernanceMode(Enum):
    LEARNING = "MODE_A_LEARNING"
    OPERATIONAL = "MODE_B_OPERATIONAL"

class GuardrailPolicy:
    RED_LINE_PATTERNS = [
        "shutdown all production servers", "shut down all production servers",
        "delete all databases", "rotate iam keys globally",
        "disable security monitoring", "mass infrastructure shutdown",
        "power off cluster", "power-off cluster",
        "wipe infrastructure", "disable all servers"
    ]

    MALICIOUS_PATTERNS = [
        "write sql injection exploit", "generate reverse shell",
        "phishing email template", "malware creation",
        "credential harvesting", "bypass security controls", "exploit script"
    ]

    MODE_A_TRIGGERS = ["explain", "what is", "how does", "beginner", "overview", "audio", "video", "education", "awareness"]
    MODE_B_TRIGGERS = ["incident", "alert", "anomaly", "breach", "detected", "logs", "attempts", "traffic", "admin", "report"]

    @staticmethod
    def classify_and_evaluate(agent_type: str, prompt: str) -> Dict[str, Any]:
        normalized = prompt.lower().strip()
        
        # 1. Determine MODE automatically
        mode = GovernanceMode.LEARNING
        if any(t in normalized for t in GuardrailPolicy.MODE_B_TRIGGERS):
            mode = GovernanceMode.OPERATIONAL
        elif any(t in normalized for t in GuardrailPolicy.MODE_A_TRIGGERS):
            mode = GovernanceMode.LEARNING
        else:
            # Fallback to agent default
            mode = GovernanceMode.LEARNING if agent_type == "ASK_RANT" else GovernanceMode.OPERATIONAL

        # 2. Priority 1: CRITICAL RED-LINE
        if any(p in normalized for p in GuardrailPolicy.RED_LINE_PATTERNS):
            return {
                "state": AgentState.BLOCKED,
                "reason": "Security Buffer Active: request involves restricted operations.",
                "severity": "CRITICAL",
                "mode": mode
            }

        # 3. Priority 2: MALICIOUS / EXPLOIT INTENT
        if any(p in normalized for p in GuardrailPolicy.MALICIOUS_PATTERNS):
            return {
                "state": AgentState.REFUSED,
                "reason": "Policy Alignment: The request involves prohibited content. Redirecting to conceptual education.",
                "severity": "HIGH",
                "mode": GovernanceMode.LEARNING # Forces conceptual mode
            }

        # 4. Priority 3: MODE Enforcement / Cross-over
        # If user is in ASK_RANT but trigger is Operational, we stick to Role expectations but apply Mode logic
        if agent_type == "ASK_RANT" and mode == GovernanceMode.OPERATIONAL:
             return {
                "state": AgentState.COMPLETED,
                "reason": "Intel dispatching via Educational lens.",
                "severity": "LOW",
                "mode": GovernanceMode.LEARNING 
            }

        return {
            "state": AgentState.COMPLETED,
            "reason": "Intelligence verified. Dispatching via calm enterprise protocols.",
            "severity": "LOW",
            "mode": mode
        }
