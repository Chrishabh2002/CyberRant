/**
 * CyberRant Agent API Client
 * Used for developer/QA testing only.
 */

const API_BASE_URL = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? "http://localhost:8000"
    : "";

export const agentApi = {
    /**
     * Dispatches a query to the specified agent.
     */
    async execute(agentType, query, chatHistory = []) {
        const response = await fetch(`${API_BASE_URL}/agent/execute`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                agent_type: agentType,
                query: query,
                chat_history: chatHistory,
            }),
        });

        if (!response.ok) {
            if (response.status === 503) {
                return { state: "SYSTEM_OFFLINE", message: "System is disarmed via Kill-Switch." };
            }
            throw new Error(`API Error: ${response.statusText}`);
        }

        return await response.json();
    },

    /**
     * Approves or Rejects a pending action for HITL.
     */
    async respondToApproval(traceId, action, modifiedParams = null) {
        const response = await fetch(`${API_BASE_URL}/agent/approval`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                trace_id: traceId,
                decision: action, // "approve" | "reject"
                modified_params: modifiedParams,
            }),
        });

        return await response.json();
    },

    /**
     * Polls for async media status.
     */
    async getStatus(traceId) {
        const response = await fetch(`${API_BASE_URL}/agent/status/${traceId}`);
        if (!response.ok) return null;
        return await response.json();
    },

    API_BASE_URL
};
