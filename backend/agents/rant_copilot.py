from typing import List, Dict, Any
from .prompts import RANT_COPILOT_SYSTEM_PROMPT
from .tools import CyberRantTools
from .ask_rant import BaseAgent

class RantCopilotAgent(BaseAgent):
    """
    Action-Oriented Copilot.
    Implements Tool-Use / Function Calling patterns.
    """
    def __init__(self, model_name: str = None):
        super().__init__(model_name)
        self.tools = CyberRantTools.get_tool_definitions()

    def run(self, user_query: str, chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        # 1. Prepare messages with System Prompt
        messages = [
            {"role": "system", "content": RANT_COPILOT_SYSTEM_PROMPT},
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
            
            # Simulated Severity Parsing logic from v3.1 prompt
            # In a real system, we'd use Regex or JSON mode to extract these fields
            severity = "MEDIUM"
            if "SEVERITY: CRITICAL" in content.upper(): severity = "CRITICAL"
            elif "SEVERITY: HIGH" in content.upper(): severity = "HIGH"
            elif "SEVERITY: LOW" in content.upper(): severity = "LOW"
            
            return {
                "message": content,
                "severity": severity,
                "confidence": "HIGH" if "CONFIDENCE: HIGH" in content.upper() else "MEDIUM"
            }
        except Exception as e:
            return {"message": f"Error connecting to AI Action Engine: {str(e)}", "severity": "MEDIUM"}

    def _handle_tool_execution(self, tool_calls: List[Any]) -> Dict[str, Any]:
        # Logic to verify permissions, request HITL approval, and execute
        pass
