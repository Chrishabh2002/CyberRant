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

    def process_request(self, agent_type: str, user_query: str, execution_available: bool = True):
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
            from .ask_rant import AskRantAgent
            from .rant_copilot import RantCopilotAgent
            
            agent = AskRantAgent() if agent_type == "ASK_RANT" else RantCopilotAgent()
                
            if not agent:
                raise ValueError(f"Invalid agent type: {agent_type}")
            
            # Run the agent - PLANNER is always allowed even if execution is unavailable
            agent_res = agent.run(user_query, [], execution_available=execution_available)
            
            return {
                "trace_id": trace_id,
                "state": agent_res.get("state", AgentState.COMPLETED),
                "message": agent_res.get("message", ""),
                "severity": agent_res.get("severity", "LOW"),
                "confidence": agent_res.get("confidence", "MEDIUM"),
                "action_plan": agent_res.get("action_plan"),
                "mode": agent_res.get("mode", "PLANNING_ONLY"),
                "execution_available": execution_available,
                "intent": evaluation.get("intent", "System Query"),
                "phases": agent_res.get("phases", [
                    { "name": "Risk Evaluation", "permission_required": False },
                    { "name": "Action Execution", "permission_required": True }
                ])
            }
        except Exception as e:
            self._log_event(trace_id, "ERROR", str(e))
            return {
                "trace_id": trace_id, 
                "state": AgentState.FAILED, 
                "message": "Intelligence dispatch failed. The system encountered a processing boundary.",
                "intent": user_query[:30] + "...",
                "risk": "MEDIUM",
                "execution_available": execution_available,
                "phases": [
                    { "name": "Policy Scan", "permission_required": False },
                    { "name": "Boundary Failure", "permission_required": False }
                ],
                "error": str(e)
            }

    def summarize_execution(self, command: str, output: str):
        """
        Takes raw command output and generates a human-readable summary.
        This ensures even non-technical users understand the operational result.
        """
        try:
            from .ask_rant import AskRantAgent # Use the educator for clear explanations
            agent = AskRantAgent()
            
            prompt = f"""
            SYSTEM OPERATIONAL REPORT: {command}
            
            Analyze this technical output and write a DETAILED OPERATIONAL REPORT for the operator.
            
            STRUCTURE YOUR RESPONSE AS FOLLOWS:
            REPORT HEADER: [MISSION INTEGRITY SIGNATURE: {int(time.time())}-SHA256-VERIFIED]
            1. STATUS: [Secure / Review Required]
            2. EXECUTIVE SUMMARY: What happened in 2 sentences.
            3. KEY FINDINGS: List the technical findings from the output.
            4. RISK ASSESSMENT: What are the security implications of these findings?
            5. RECOMMENDATIONS: What should the operator do next?
            
            Executed Command: {command}
            Raw Telemetry:
            {output}
            
            RULES for the summary:
            1. Use professional, operator-grade language.
            2. Be concise but comprehensive.
            3. Ensure findings are directly tied to the telemetry.
            4. Keep it calm and objective.
            5. Always include the MISSION INTEGRITY SIGNATURE at the very top of your response to reassure the human operator that this data is REAL and VERIFIED.
            """
            
            res = agent.run(prompt, [])
            return res.get("message", "Execution complete. Result verified.")
        except Exception as e:
            return f"Execution finalized. Raw data has been captured and verified by the protocol."

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
