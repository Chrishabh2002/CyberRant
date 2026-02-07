# CyberRant AI Agent: Production Execution Specification

## 1. Full User Experience (UX) Flow

### Entry Points
- **Omni-Search Bar**: Persistent top-level search for Ask Rant AI.
- **Contextual Actions**: "Explain this vulnerability" or "Remediate this asset" buttons within specialized data tables (Scans, Inventory).
- **Command Palette**: `Ctrl + K` interface for Rant AI Agent to execute operations quickly.

### User States & Feedback
- **Idle**: Standard input field with placeholder "Ask anything or type a command...".
- **Processing**: 
    - *UI*: Progress bar with status labels (e.g., "Scanning internal assets...", "Consulting compliance docs...").
    - *Backend*: Streaming chunks for text; polling/webhook for multimodal.
- **Approval Required (Copilot)**: 
    - *UI*: Multi-step plan cards with "Confirm" / "Edit" / "Cancel" buttons.
    - *Safety*: Highlights "Destructive" steps in red.
- **Partial Results**: 
    - *UI*: Shows text answer immediately while a "Generating Video Explainer..." spinner appears in the footer.
- **Refusals/Errors**:
    - *UI*: Red-bordered cards with specific codes (e.g., `CR-403: Policy Violation`). NO generic "Something went wrong."

---

## 2. Multimodal Architecture (Ask Rant AI)

To support Text, Audio, and Video (NotebookLM style), we implement an **Asynchronous Pipeline**.

### Lifecycle
1. **Primary Generation**: LLM generates the text response (Latency: <3s).
2. **Audio/Video Triggering**: If requested (or user preference), the backend pushes the text payload to a Task Queue (Celery/RabbitMQ).
3. **Synthesis**:
    - **Audio (TTS)**: OpenAI TTS or ElevenLabs generating MP3.
    - **Video (Visualizer)**: Automated creation of a slide-like video using the generated summary points + stock security icons + TTS overlay.
4. **Delivery**: UI receives a WebSocket `MEDIA_READY` event with the S3 URL.

### Caching & Cost Control
- **Content-Hash Caching**: If 5 users ask the same question about "CVE-2024-1234", the Video Explainer is generated once and cached via its prompt hash for 24h.
- **Tiered Quotas**: 
    - *Basic*: Text only.
    - *Pro*: Text + Audio.
    - *Enterprise*: Unlimited Video Explainers.
- **TTL (Time to Live)**: Audio/Video assets are deleted from S3 after 48h unless "Saved" by the user.

---

## 3. Observability & Governance

### Logging Strategy (The "Agent Trace")
Every interaction creates a `TraceID` containing:
- **Input Context**: Full prompt + injected RAG snippets.
- **Intermediate Steps**: CoT (Chain of Thought) logs, internal tool calls, and latency per step.
- **Metadata**: UserID, TeamID, ProjectID, Model Version.

### Cost & Hallucination Monitoring
- **Cost Tracking**: Backend calculates token usage per request and updates a `daily_spend` column in the User Profile.
- **Confidence Scoring**: Ask Rant must include a self-reported confidence score. If < 0.7, trigger a "I'm less certain about this, please verify with docs" warning.
- **Abuse Monitor**: Rate limits tailored to agent type (Action-oriented agents have tighter throttles than Chat-based ones).

---

## 4. Hard Guardrails & Red-Line Policies

### Ask Rant AI Refusals
- **Active Exploitation**: "Draft a phishing email" or "Write a Metasploit module for X".
- **Internal Secrets**: "Show me the admin credentials for the production DB".
- **PII Leakage**: "Tell me the email addresses of all users affected by this breach".

### Rant AI Agent "Never" List (Hardcoded Blocks)
- **Primary Data Deletion**: Cannot drop tables or delete S3 buckets.
- **IAM Escalation**: Cannot modify its own permissions or user group memberships.
- **Mass Shutdown**: Cannot stop >10% of the production cluster in a single operation.
- **Shadow Provisioning**: Cannot create new billable resources (EC2, RDS) without a second human admin approval.

---

## 5. Engineering Execution Notes

### Phase 1: Foundation (MVP)
- **Backend**: Implement the `BaseAgent` class with RBAC-aware tool injection.
- **Frontend**: Create the "Chat Drawer" component with streaming text support.
- **Guardrails**: Implement the "Red-Line" regex and policy-check middleware.

### Phase 2: Action & Observation
- **Action**: Build the "Approval Card" UI and the HITL (Human-in-the-Loop) state machine.
- **Observability**: Deploy the Logging & Trace DB (OpenTelemetry/Elasticsearch).

### Phase 3: Multimodal & Scale
- **Multimodal**: Integrate TTS and the Video Synthesis worker.
- **Optimization**: Implement Content-Hash caching and Redis-based rate limiting.

### Handoff Points
- **Frontend**: Focus on the `StatefulChat` component and `Ctrl+K` hook.
- **Backend**: Focus on the `AgentOrchestrator` and `ToolSanitizer`.
- **SecOps**: Define the `ToolManifest` (the list of what the agent is allowed to do).
