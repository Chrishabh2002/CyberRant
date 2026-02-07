import time
import logging
from typing import List, Dict, Any
from .models import AgentState, GuardrailPolicy, SystemConfig, FeatureFlag

class AgentOrchestrator:
    """
    The central coordinator for all AI interactions.
    Handles Logging, Guardrails, and State Transitions.
    """
    def __init__(self, user_id: str, team_id: str, enabled_features: List[FeatureFlag] = None):
        self.user_id = user_id
        self.team_id = team_id
        self.enabled_features = enabled_features or []
        self.logger = logging.getLogger(f"AgentTrace-{user_id}")

    def process_request(self, agent_type: str, user_query: str):
        # 1. Global Kill-Switch Check (Zero-Trust)
        if not SystemConfig.IS_SYSTEM_ARMED:
            return {
                "state": AgentState.SYSTEM_OFFLINE, 
                "message": "CRITICAL: The CyberRant Agent system is DISARMED. All operations are halted."
            }

        # 2. Universal Identity & Trace Generation
        start_time = time.time()
        trace_id = f"cr-tr-{int(start_time)}-{self.user_id[:8]}"
        
        # 3. Enterprise Security Guardrail & Intent Classification (Pre-LLM)
        evaluation = GuardrailPolicy.classify_and_evaluate(agent_type, user_query)
        determined_mode = evaluation.get("mode")
        
        if evaluation["state"] in [AgentState.BLOCKED, AgentState.REFUSED]:
            self._log_event(trace_id, evaluation["state"].value, evaluation["reason"])
            return {
                "trace_id": trace_id,
                "state": evaluation["state"], 
                "message": evaluation["reason"],
                "severity": evaluation.get("severity", "HIGH")
            }

        # 4. Mode Enforcement / Agent Selection
        try:
            # We Dispatch based on user selection but enforce Mode context
            from .ask_rant import AskRantAgent
            from .rant_copilot import RantCopilotAgent
            
            # If user selected ASK_RANT but trigger says OPERATIONAL, we still use ASK_RANT 
            # but it will handle it via its refined educator prompt (Mode A).
            # If user selected RANT_COPILOT, it must strictly follow Mode B.
            
            agent = AskRantAgent() if agent_type == "ASK_RANT" else RantCopilotAgent()
                
            if not agent:
                raise ValueError(f"Invalid agent type: {agent_type}")
            
            # Run the agent
            agent_res = agent.run(user_query, [])
            
            return {
                "trace_id": trace_id,
                "state": AgentState.COMPLETED,
                "message": agent_res.get("message", ""),
                "severity": agent_res.get("severity", "LOW"),
                "confidence": agent_res.get("confidence", "MEDIUM"),
                "mode": determined_mode.value if determined_mode else None
            }
        except Exception as e:
            self._log_event(trace_id, "ERROR", str(e))
            return {"trace_id": trace_id, "state": AgentState.FAILED, "error": f"Internal Orchestration Error: {str(e)}"}

    def _log_event(self, trace_id: str, event_type: str, details: str):
        # Strict observability requirement for audit trails
        log_entry = {
            "timestamp": time.time(),
            "trace_id": trace_id,
            "user_id": self.user_id,
            "team_id": self.team_id,
            "status": event_type,
            "details": details
        }
        self.logger.info(f"| AUDIT | {trace_id} | {event_type} | {details}")
        # Production: forward log_entry to secure telemetry (Fluentd/Splunk)
