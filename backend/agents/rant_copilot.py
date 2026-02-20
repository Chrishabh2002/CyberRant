from typing import List, Dict, Any
from .prompts import RANT_COPILOT_SYSTEM_PROMPT
from .tools import CyberRantTools
from .ask_rant import BaseAgent
from .models import AgentState
import os
import re

class RantCopilotAgent(BaseAgent):
    """
    Action-Oriented Copilot.
    Implements Tool-Use / Function Calling patterns.
    """
    def __init__(self, model_name: str = None):
        super().__init__(model_name)
        self.tools = CyberRantTools.get_tool_definitions()

    def run(self, user_query: str, chat_history: List[Dict[str, str]], execution_available: bool = True) -> Dict[str, Any]:
        # 1. Prepare dynamic system prompt based on availability
        status_suffix = ""
        if not execution_available:
            status_suffix = "\n\nCRITICAL STATUS: LOCAL EXECUTION AGENT IS OFFLINE. Proceed in PLANNING_ONLY mode. Formalize the plan but do not attempt discovery."
        
        messages = [
            {"role": "system", "content": RANT_COPILOT_SYSTEM_PROMPT + status_suffix},
            *chat_history,
            {"role": "user", "content": user_query}
        ]

        # 2. Call Real OpenAI LLM
        try:
            # Check if LLM is actually configured
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY is missing from environment.")

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.2,
                timeout=45.0 # Add timeout to prevent hanging
            )
            content = response.choices[0].message.content
            
            # Severity / Operational Contract parsing
            severity = "LOW"
            if "RISK LEVEL: HIGH" in content.upper() or "SEVERITY: CRITICAL" in content.upper():
                severity = "CRITICAL"
            
            # State determination
            state = AgentState.AWAITING_APPROVAL
            if severity == "CRITICAL":
                state = AgentState.APPROVAL_REQUIRED
            
            # Intent Extraction
            intent = "System Analysis"
            patterns = [r"Intent\s*:\s*(.*)", r"Mission\s*:\s*(.*)", r"Task\s*:\s*(.*)"]
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    intent = match.group(1).strip().replace("*", "").replace("#", "")
                    break
            
            action_plan = None
            try:
                # Robust extraction for Task and Resource
                task_match = re.search(r"Execution Task\s*:\s*(.*)", content, re.IGNORECASE) or \
                             re.search(r"Task\s*:\s*(.*)", content, re.IGNORECASE) or \
                             re.search(r"Command\(s\) to be executed\s*:\s*(.*)", content, re.IGNORECASE) or \
                             re.search(r"- Command\(s\) to be executed:\s*(.*)", content, re.IGNORECASE)
                
                resource_match = re.search(r"Target Resource\s*:\s*(.*)", content, re.IGNORECASE) or \
                                 re.search(r"Resource\s*:\s*(.*)", content, re.IGNORECASE)
                
                extracted_task = task_match.group(1).strip().replace("`", "") if task_match else None
                extracted_resource = resource_match.group(1).strip().replace("`", "") if resource_match else "Local System"
                
                if not extracted_task:
                    # HEURISTIC FALLBACK: If LLM failed to format but gave a command elsewhere
                    if "ipconfig" in content.lower() or "ifconfig" in content.lower():
                        extracted_task = "ipconfig"
                    elif "network_recon" in content.lower() or "scan" in content.lower():
                        extracted_task = "network_recon"
                    elif "system_audit" in content.lower() or "audit" in content.lower():
                        extracted_task = "system_audit"
                    elif "list_sandbox_files" in content.lower() or "list" in content.lower():
                        extracted_task = "list_sandbox_files"
                
                if extracted_task:
                    action_plan = {
                        "operation": extracted_task,
                        "entity": extracted_resource,
                        "risk": severity,
                        "justification": f"Strategic plan formulated for high-integrity {extracted_task} on {extracted_resource}."
                    }
            except:
                pass

            return {
                "message": content,
                "severity": severity,
                "state": state,
                "confidence": "HIGH",
                "action_plan": action_plan,
                "mode": "PLANNING_ONLY" if not execution_available else "OPERATIONAL",
                "execution_available": execution_available,
                "intent": intent,
                "phases": [
                    { "name": "Technical Risk Assessment", "permission_required": False },
                    { "name": "Supervised Execution", "permission_required": True }
                ]
            }
        except Exception as e:
            import traceback
            print(f"[!] AGENT CRITICAL FAILURE: {e}")
            traceback.print_exc()
            
            # HEURISTIC MISSION RECOVERY (Works even if AI is down)
            fallback_task = None
            if "ip" in user_query.lower() or "address" in user_query.lower():
                fallback_task = "ipconfig"
            elif "scan" in user_query.lower() or "recon" in user_query.lower():
                fallback_task = "network_recon"
            elif "audit" in user_query.lower():
                fallback_task = "system_audit"
            elif "list" in user_query.lower() or "sandbox" in user_query.lower():
                fallback_task = "list_sandbox_files"

            fallback_plan = None
            if fallback_task:
                fallback_plan = {
                    "operation": fallback_task,
                    "entity": "Local Host",
                    "risk": "LOW",
                    "justification": "Heuristic fallback mission created due to AI engine latency. Proceed with direct operational command."
                }

            return {
                "message": f"MISSION UPDATE: The primary AI neural link is experiencing high latency or reachability issues. \n\n[PROBABLE MISSION]: {fallback_task or 'Unknown'}\n\nCyberRant Zero-Trust protocol has activated a heuristic fallback plan. You may proceed with the discovered operational task.",
                "severity": "MEDIUM",
                "state": AgentState.AWAITING_APPROVAL if fallback_task else AgentState.FAILED,
                "intent": user_query[:50],
                "risk": "LOW",
                "action_plan": fallback_plan,
                "phases": [],
                "execution_available": execution_available
            }

    def _handle_tool_execution(self, tool_calls: List[Any]) -> Dict[str, Any]:
        # Logic to verify permissions, request HITL approval, and execute
        pass
