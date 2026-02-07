# CyberRant AI Agent: Production Hardening & Sign-Off

## 1. Ownership & Responsibility Matrix

| Responsibility | Owner | Rationale |
| :--- | :--- | :--- |
| **Logic Reasoning** | AI Agent | Best for parsing intent and mapping to capabilities. |
| **Data Retrieval (RAG)** | Backend | AI should not "search" directly; it asks Backend services for filtered datasets. |
| **Authorization (RBAC)** | Backend | **Hard Rule**: AI Agent cannot authorize itself. Backend must validate all tool tokens. |
| **State Persistence** | Backend | Agent is stateless. Conversations and states live in DB/Redis. |
| **Input Sanitization** | Frontend | Preventive UX; masking sensitive fields before they reach the API. |
| **Instruction Parsing** | AI Agent | Converting natural language to JSON tool payloads. |
| **High-Blast Radius Actions**| Human | Any action affecting >10% of infra or costing >$500 requires direct human click. |
| **Root Cause Analysis** | Human | AI suggests; Human confirms. AI is an advisor, not a judge. |

---

## 2. Operational Safety Controls

### Resilience Mechanisms
- **Global Kill-Switch**: A central Redis key `AGENT_SYSTEM_ARMED` (Default: `True`). If toggled to `False`, all agent endpoints return `503 Service Unavailable` immediately.
- **Capability Feature Flags**: Granular control over toolsets. Example flags: `can_write_scripts`, `can_modify_iam`, `can_trigger_scans`.
- **Prompt Versioning**: Every prompt is stored in a versioned registry (e.g., `v1.2.4-stable`). Rollbacks can be performed via environment variable updates without redeploying code.
- **Token Budgeting**: Daily hard cap on LLM costs per tenant to prevent "spiral" spending from infinite loops.

---

## 3. Compliance & Data Handling

### Privacy Commitments
- **PII Masking**: Integrated `Presidio` or similar engine in the Backend middleware to strip Emails, IPs (not targeted), and Keys from prompts *before* they leave the internal network.
- **Data Retention**: 
    - *Traces/Logs*: 30 Days (for debugging).
    - *Conversation History*: 90 Days (unless specified by customer policy).
    - *Masked Data*: Persistent.
- **Opt-Out & Deletion**: Users can request full deletion of "Agent Memory" (Vector DB embeddings) and chat logs via the Settings UI.
- **Audit Logging**: Every single tool call is logged to an immutable "System Audit" table, separate from the Agent's own logs.

---

## 4. Production Readiness Checklist

### Must Exist (Day 1)
- [ ] **Middleware Guardrails**: Regex/LLM-based red-line filtering.
- [ ] **RBAC Inheritance**: Backend verifying that User X can actually perform Action Y.
- [ ] **Kill-Switch API**: Admin-only endpoint to shut down agent processing.
- [ ] **Rate Limiting**: Per-user and per-minute throttles.
- [ ] **HITL (Human-in-the-Loop)**: Working confirmation UI for all tool calls.

### Later Phases (Day 30+)
- [ ] **Advanced Multimodal (Video)**: Can launch with Text/Audio first.
- [ ] **Automated Eval Testing**: Continuous integration of "Golden Prompts" to detect drift.
- [ ] **Deep Vector Search**: Can start with basic RAG.

### DO NOT SHIP (Red Flags)
- [ ] Any agent with `Admin` or `Root` level credentials.
- [ ] Agents that can "Update" or "Delete" their own Audit Logs.
- [ ] Direct LLM-to-Infrastructure access (Must go through typed Tool APIs).
- [ ] Prompts that include internal database schemas or raw architecture diagrams.
