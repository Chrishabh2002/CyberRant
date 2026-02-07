import abc
import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from .prompts import ASK_RANT_SYSTEM_PROMPT

load_dotenv()

class BaseAgent(abc.ABC):
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("DEFAULT_MODEL", "arcee-ai/trinity-large-preview:free")
        self.client = OpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

    @abc.abstractmethod
    def run(self, user_query: str, chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        pass

class AskRantAgent(BaseAgent):
    """
    Learning & Guidance Agent.
    Implements RAG patterns to provide security advice.
    """
    def run(self, user_query: str, chat_history: List[Dict[str, str]]) -> str:
        # 1. Perform Retrieval (Simulated Knowledge Base Context)
        context = self._retrieve_knowledge_base_context(user_query)
        
        # 2. Build Message Chain
        messages = [
            {"role": "system", "content": ASK_RANT_SYSTEM_PROMPT},
            *chat_history,
            {"role": "user", "content": f"Use the following internal context to help the user:\nContext: {context}\n\nUser Question: {user_query}"}
        ]
        
        # 3. Call Real OpenAI LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )
            content = response.choices[0].message.content
            # Simulated Extraction: In production, use JSON mode or Regex
            # For now, default Learning/LOW severity for Mode A
            return {
                "message": content,
                "severity": "LOW",
                "confidence": "HIGH"
            }
        except Exception as e:
            return {"message": f"Error connecting to AI Engine: {str(e)}", "severity": "LOW"}

    def _retrieve_knowledge_base_context(self, query: str) -> str:
        # In production, this would call a Vector DB (Pinecone/Milvus)
        return "Internal Knowledge: Log4j CVE-2021-44228 affects JNDI lookups via log messages. OWASP Top 10 2021 includes Broken Access Control, Cryptographic Failures, and Injection as top risks."
