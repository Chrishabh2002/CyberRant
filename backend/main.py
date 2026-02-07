from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os

# Import our agent logic
from agents.orchestrator import AgentOrchestrator
from agents.models import AgentState, FeatureFlag
from services.media_orchestrator import MediaOrchestrator

app = FastAPI(title="CyberRant Agent API")

# Ensure media directory exists and serve it
try:
    os.makedirs("media/audio", exist_ok=True)
    os.makedirs("media/video", exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create media directories: {e}")

app.mount("/media", StaticFiles(directory="media"), name="media")

# Enable CORS for the frontend testing console
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

media_orchestrator = MediaOrchestrator()

class ExecuteRequest(BaseModel):
    agent_type: str
    query: str
    chat_history: Optional[List[Dict[str, str]]] = []

class ApprovalRequest(BaseModel):
    trace_id: str
    decision: str
    modified_params: Optional[Dict[str, Any]] = None

# In-memory storage for active traces (for testing purposes)
trace_store = {}

@app.get("/agent/status/{trace_id}")
async def get_agent_status(trace_id: str):
    """Polling endpoint to check async media generation status."""
    status = MediaOrchestrator.get_job_status(trace_id)
    # Normalize state for frontend consumption
    overall = status.get("overall_state", "PROCESSING")
    return {
        "trace_id": trace_id,
        "media_status": status,
        "state": overall
    }

@app.post("/agent/execute")
async def execute_agent(req: ExecuteRequest, background_tasks: BackgroundTasks):
    # Kill-switch check (Enterprise Safety)
    if os.getenv("SYSTEM_STATUS") == "DISARMED":
        return {"state": "BLOCKED", "message": "System is currently DISARMED."}

    enabled_flags = [FeatureFlag.CAN_READ_SCAN_DATA]
    
    orchestrator = AgentOrchestrator(
        user_id="ent-user-882", 
        team_id="soc-blue-team",
        enabled_features=enabled_flags
    )
    
    result = orchestrator.process_request(req.agent_type, req.query)
    
    # Hide internal block/refusal reasons - show professional summaries
    if result["state"] == AgentState.BLOCKED:
        return {"state": "BLOCKED", "message": "Security Buffer Active: request involves restricted operations.", "trace_id": result.get("trace_id")}
    
    if result["state"] == AgentState.REFUSED:
        return {"state": "BLOCKED", "message": "Policy Alignment: The request involves prohibited content generation.", "trace_id": result.get("trace_id")}

    trace_id = result["trace_id"]
    
    # HITL Check
    if result["state"] == AgentState.AWAITING_APPROVAL:
        return result

    # Media Pipeline Trigger
    wants_media = any(word in req.query.lower() for word in ["audio", "video", "media", "explain", "brief"])
    
    if req.agent_type == "ASK_RANT" and wants_media:
        # Normalize state
        result["state"] = "TEXT READY"
        include_video = "video" in req.query.lower()
        
        MediaOrchestrator.update_job(trace_id, 
            audio_status="PROCESSING", 
            video_status="PROCESSING" if include_video else "NONE",
            overall_state="PROCESSING"
        )

        background_tasks.add_task(
            media_orchestrator.generate_media_pack,
            trace_id=trace_id,
            text=result.get("message", "Comprehensive Security Intelligence Briefing"),
            include_video=include_video,
            severity=result.get("severity", "LOW")
        )
        
        result["media_status"] = MediaOrchestrator.get_job_status(trace_id)
    else:
        # Default completed state
        result["state"] = "COMPLETED"

    return result

@app.post("/agent/approval")
async def handle_approval(req: ApprovalRequest):
    if req.trace_id not in trace_store:
        if req.decision == "approve":
            return {
                "state": AgentState.COMPLETED,
                "message": "Action successfully executed via Rant AI Agent.",
                "trace_id": req.trace_id
            }
        else:
            return {
                "state": AgentState.FAILED,
                "message": "Action was rejected by the operator.",
                "trace_id": req.trace_id
            }
            
    return {"status": "ok", "state": AgentState.COMPLETED}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
