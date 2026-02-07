# CyberRant AI Agent Architecture & Design Specification

## 1. Agent Overview

CyberRant aims to bridge the gap between static vulnerability scanning and active security posture management. To achieve this, we deploy two distinct but interconnected AI agents:

- **Ask Rant AI**: A Knowledge-Centric Advisor. Optimized for high-fidelity information retrieval (RAG), compliance guidance, and pedagogical support for security teams. Its primary goal is to "Make the user smarter."
- **Rant AI Agent**: An Action-Centric Copilot. Designed for operational efficiency, incident response automation, and infrastructure manipulation. Its primary goal is to "Done the user's work."

---

## 2. Agent 1: Ask Rant AI (Guidance-Focused)

### Purpose
To act as a persistent, knowledgeable consultant for security researchers, SOC analysts, and compliance officers. It leverages the platform's accumulated data and Global Security Intelligence to answer complex "Why" and "How" questions.

### Responsibilities
- **Compliance Mapping**: Map internal security controls to frameworks (SOC2, ISO 27001, HIPAA).
- **Vulnerability Explanation**: Provide deep-dives into CVEs, including root cause analysis and impact assessment within the specific CyberRant environment.
- **Policy Drafting**: Assist in generating organizational security policies based on industry templates.
- **Threat Intelligence Synthesis**: Summarize daily threat feeds and highlight items relevant to the organization's tech stack.

### End-to-End Workflow
1. **Request**: User asks, "What is the impact of the latest Log4j-style vulnerability on our current Node.js microservices?"
2. **Context Retrieval**: The orchestrator queries the internal asset inventory (Graph DB) and recent scan results.
3. **Synthesis**: The LLM processes the search results + asset list via Retrieval Augmented Generation (RAG).
4. **Verification**: The agent cross-references service versions against the CVE database.
5. **Output**: Returns a detailed report with:
    - List of potentially affected services.
    - Risk score based on business criticality.
    - Recommended reading/tutorials for mitigation.

---

## 3. Agent 2: Rant AI Agent (Action-Oriented)

### Purpose
A semi-autonomous "Hands-on-Keyboard" (HoK) assistant that translates natural language intentions into technical execution. It functions as a bridge between the user and the platform’s API/CLI tools.

### Responsibilities
- **Incident Remediation**: Execute predefined runbooks or generate one-off scripts to patch vulnerabilities.
- **Asset Discovery**: Trigger sub-domain enumeration or network scans on demand.
- **Permission Management**: Auditing and updating IAM policies or firewall rules.
- **Custom Tooling**: Writing and executing Python/Bash scripts in a sandboxed environment to process logs or automate reporting.

### End-to-End Workflow
1. **Intent**: User types, "Quarantine the EC2 instance `i-0abc123` because it's showing abnormal egress traffic."
2. **Analysis**: Agent parses the entity (`i-0abc123`) and the action (Quarantine).
3. **Security Check**: The Permission Engine verifies if the user has `EC2:ModifyInstanceAttribute` or `EC2:UpdateSecurityGroup` rights.
4. **Plan Generation**: Agent presents a plan: "I will detach the current Security Group and attach `sg-quarantine-only`. Do you approve?"
5. **Human-in-the-Loop (HITL)**: User clicks "Confirm".
6. **Execution**: Backend calls the AWS SDK to perform the change.
7. **Audit**: The action is logged in the CyberRant immutable audit trail.

---

## 4. Architecture Notes

### Browser vs. Backend Split

| Component | Responsibility | Environment |
| :--- | :--- | :--- |
| **Chat Interface** | Markdown rendering, syntax highlighting, real-time typing effect. | Browser (React/Vue) |
| **Agent State Manager** | Tracks if the agent is "thinking," "fetching," or "waiting for approval." | Browser (Redux/Zustand) |
| **Orchestrator** | LLM chain management (LangChain/LangGraph), Tool discovery. | Backend (Node.js/Python) |
| **Tool Execution Layer** | Sandboxed environment for running scripts (Docker/Firecracker). | Backend |
| **Memory Engine** | Vector DB (Pinecone/Milvus) for long-term memory and RAG. | Backend |
| **API Gateway** | Rate limiting, Auth, and PII scrubbing. | Backend |

### Scalability Design
- **Stateless Orchestrators**: All agent state is persisted in Redis/PostgreSQL, allowing any backend instance to pick up a conversation.
- **Asynchronous Execution**: Long-running actions (e.g., full port scans) are offloaded to a Task Queue (Celery/RabbitMQ) with WebSocket updates for the UI.
- **Token Management**: Centralized caching of LLM responses for common queries to reduce costs and latency.

---

## 5. Security & Control Considerations

### Safety & Guardrails
- **Prompt Sanitization**: Use a dedicated "Guardrail LLM" or regex layer to detect and block prompt injection attacks.
- **Boundary Enforcement**: Tools are strictly typed. The agent cannot "invent" API calls; it can only use registered Tool Definitions (JSON Schema).
- **PII Scrubbing**: Automatic masking of emails, secrets, and private keys before telemetry or LLM transmission.

### Permission Boundaries
- **Identity-Aware Proxy**: The agent inherits the user's JWT. It cannot bypass RBAC. If a user can't delete a DB, the agent can't either.
- **Destructive Action Confirmation**: Any action categorized as "Destructive" (Delete, Modify, Shutdown) **must** have a dual-approval or single-user confirmation in the UI.
- **Audit Logging**: Every LLM prompt, retrieved context, and tool execution is logged for forensic review.

### Production Readiness
- **Versioned Prompts**: Treat prompts as code (Git-tracked) to ensure reproducible agent behavior.
- **Evaluation Framework**: Use "Golden Datasets" to run automated tests on agent accuracy before new releases.
- **Hallucination Detection**: Implement a "Check-Your-Work" step where the agent must cite its source (Documentation link or DB record) for every claim.
