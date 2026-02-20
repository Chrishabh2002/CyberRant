from typing import List, Dict, Any
from .prompts import RANT_COPILOT_SYSTEM_PROMPT
from .tools import CyberRantTools
from .ask_rant import BaseAgent
from .models import AgentState

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
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.2
            )
            content = response.choices[0].message.content
            
            # Severity / Operational Contract parsing
            severity = "LOW"
            if "RISK LEVEL: HIGH" in content.upper() or "SEVERITY: CRITICAL" in content.upper():
                severity = "CRITICAL"
            elif "RISK LEVEL: MEDIUM" in content.upper():
                severity = "HIGH"
            
            # Determine State: If offline, we can still be in AWAITING_APPROVAL to show the plan
            state = AgentState.COMPLETED
            if "WAITING FOR OPERATOR AUTHORIZATION" in content.upper():
                state = AgentState.AWAITING_APPROVAL
            elif not execution_available:
                state = AgentState.COMPLETED
            else:
                state = AgentState.AWAITING_APPROVAL
            
            # Implementation of the user's "Contract" fields
            import re
            
            # Extract Intent/Goal from content
            intent = user_query[:50]
            goal_patterns = [r"Mission Goal\s*:\s*(.*)", r"Goal\s*:\s*(.*)"]
            for pattern in goal_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    intent = match.group(1).strip().replace("*", "").replace("#", "")
                    break
            
            action_plan = None
            try:
                # Robust extraction for Task and Resource
                task_match = re.search(r"Execution Task\s*:\s*(.*)", content, re.IGNORECASE) or \
                             re.search(r"Task\s*:\s*(.*)", content, re.IGNORECASE) or \
                             re.search(r"Command\(s\) to be executed\s*:\s*(.*)", content, re.IGNORECASE)
                
                resource_match = re.search(r"Target Resource\s*:\s*(.*)", content, re.IGNORECASE) or \
                                 re.search(r"Resource\s*:\s*(.*)", content, re.IGNORECASE)
                
                extracted_task = task_match.group(1).strip().replace("`", "") if task_match else "Operational Analysis"
                extracted_resource = resource_match.group(1).strip().replace("`", "") if resource_match else "Local System"
                
                action_plan = {
                    "operation": extracted_task,
                    "entity": extracted_resource,
                    "risk": severity,
                    "justification": f"Plan formulated for high-integrity {extracted_task} on {extracted_resource}."
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
            print(f"[!] Agent Loop Failure: {e}")
            return {
                "message": "Planning boundary reached. Automated plan generation is on standby.",
                "severity": "MEDIUM",
                "state": AgentState.FAILED,
                "intent": user_query[:50],
                "risk": "LOW",
                "phases": [],
                "execution_available": execution_available
            }

    def _handle_tool_execution(self, tool_calls: List[Any]) -> Dict[str, Any]:
        # Logic to verify permissions, request HITL approval, and execute
        pass
