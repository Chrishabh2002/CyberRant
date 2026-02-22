"""
n8n Webhook Integration Service
Bridges FastAPI → n8n for post-execution enrichment and analytics.

In Production:
  - FastAPI triggers n8n webhooks after agent execution completes
  - n8n performs async enrichment (LLM summarization, risk scoring, alerting)
  - Results are stored in community_intel and trend_history tables

In Local Development:
  - Falls back gracefully if n8n is not reachable
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("n8n-bridge")


class N8nWebhookService:
    """
    Handles all communication from FastAPI backend to n8n workflow engine.
    """

    def __init__(self):
        # In production (Render), this will be like: https://rant-n8n.onrender.com
        self.base_url = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678")
        self.timeout = 10.0  # seconds

    async def trigger_post_execution(self, trace_id: str, command: str, output: str, severity: str) -> Optional[Dict]:
        """
        Called AFTER LEA execution completes.
        Sends execution telemetry to n8n for async enrichment.
        """
        payload = {
            "event": "execution_complete",
            "trace_id": trace_id,
            "command": command,
            "output": output[:5000],  # Truncate to prevent payload overflow
            "severity": severity,
        }
        return await self._send_webhook("/webhook/agent-enrich", payload)

    async def trigger_community_ingest(self, content: str, author: str, engagement: Dict) -> Optional[Dict]:
        """
        Called when new community posts are created.
        Pushes to n8n for real-time trending analysis.
        """
        payload = {
            "event": "new_community_post",
            "content": content,
            "author": author,
            "engagement": engagement,
        }
        return await self._send_webhook("/webhook/community-ingest", payload)

    async def trigger_alert(self, alert_type: str, message: str, severity: str) -> Optional[Dict]:
        """
        Triggers n8n alert workflow for Slack/Discord/Email notifications.
        """
        payload = {
            "event": "security_alert",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
        }
        return await self._send_webhook("/webhook/security-alert", payload)

    async def _send_webhook(self, path: str, payload: Dict[str, Any]) -> Optional[Dict]:
        """
        Internal method to send HTTP POST to n8n webhook endpoint.
        Fails gracefully — n8n being down should NOT crash the backend.
        """
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    logger.info(f"[n8n] Webhook OK: {path} → {response.status_code}")
                    return response.json()
                else:
                    logger.warning(f"[n8n] Webhook returned {response.status_code}: {path}")
                    return None
        except httpx.ConnectError:
            logger.warning(f"[n8n] Unreachable at {url} — workflow skipped (non-blocking)")
            return None
        except Exception as e:
            logger.error(f"[n8n] Webhook error: {e}")
            return None
