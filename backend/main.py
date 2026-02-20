from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import time
import asyncio
import subprocess
import sys
from dotenv import load_dotenv
import socketio
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Import our agent logic
from agents.orchestrator import AgentOrchestrator
from agents.models import AgentState, FeatureFlag
from services.media_orchestrator import MediaOrchestrator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    asyncio.create_task(simulate_ambient_intel())
    
    # Automatically spawn the Local Execution Agent (Security Bridge)
    # Robust Path Discovery: Check both parent and current directory (for flattened cloud deploys)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(os.path.dirname(current_dir), "local_agent.py"),
        os.path.join(current_dir, "local_agent.py")
    ]
    
    lea_path = None
    for p in possible_paths:
        if os.path.exists(p):
            lea_path = p
            project_root = os.path.dirname(p)
            break

    if lea_path:
        print(f"[*] Dispatching Security Bridge: {lea_path}")
        # Wipe log for fresh run
        with open("lea_bridge.log", "w") as f:
            f.write(f"--- BRIDGE INITIALIZED {time.ctime()} ---\n")
            
        port = os.getenv("PORT", "8000")
        target_url = f"http://localhost:{port}"
        
        subprocess.Popen([sys.executable, "-u", lea_path, target_url], 
                         stdout=open("lea_bridge.log", "a"), 
                         stderr=subprocess.STDOUT,
                         cwd=project_root)
        print(f"[+] Security Bridge initialization sequence started (Target: {target_url})")
        
    yield
    # Shutdown logic (optional)
    print("[*] Application context terminating.")

fastapi_app = FastAPI(title="CyberRant Agent API", lifespan=lifespan)

# Initialize Socket.io for LEA connection
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio, fastapi_app)

# Ensure media directory exists and serve it
try:
    os.makedirs("media/audio", exist_ok=True)
    os.makedirs("media/video", exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create media directories: {e}")

fastapi_app.mount("/media", StaticFiles(directory="media"), name="media")

# Enable CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@fastapi_app.get("/ping")
async def ping():
    return {
        "status": "ok", 
        "message": "CyberRant Intelligence Gateway is Online.",
        "lea_connected": connected_lea_sid is not None
    }

# Verification: Check for Critical API Keys
if not os.getenv("OPENROUTER_API_KEY"):
    print("CRITICAL WARNING: OPENROUTER_API_KEY is not set. AI Agents will be inoperative.")

media_orchestrator = MediaOrchestrator()

class ExecuteRequest(BaseModel):
    agent_type: str
    query: str
    chat_history: Optional[List[Dict[str, str]]] = []

class ApprovalRequest(BaseModel):
    trace_id: str
    decision: str
    modified_params: Optional[Dict[str, Any]] = None

# In-memory storage for active traces, connected LEA, and ecosystem status
trace_store = {}
connected_lea_sid = None
ecosystem_state = {
    "nodes": {},
    "global_threat_level": "LOW",
    "active_missions": 0
}

@sio.on("ecosystem_pulse")
async def ecosystem_pulse(sid, data):
    agent_id = data.get("agent_id", "unknown")
    ecosystem_state["nodes"][agent_id] = {
        "stats": data,
        "last_seen": data.get("timestamp"),
        "status": "ONLINE"
    }
    ecosystem_state["active_missions"] = sum(1 for t in trace_store.values() if t.get("state") == "EXECUTING")
    # Broadcast to all frontend clients
    await sio.emit("ecosystem_update", ecosystem_state)

@fastapi_app.get("/agent/ecosystem")
async def get_ecosystem():
    return ecosystem_state

@sio.event
async def connect(sid, environ):
    print(f"[*] New socket connection: {sid}")

@sio.on("register_lea")
async def register_lea(sid, data):
    global connected_lea_sid
    connected_lea_sid = sid
    print(f"[+] Local Execution Agent Registered: {data.get('agent_id')} (SID: {sid})")

@sio.on("execution_log")
async def execution_log(sid, data):
    trace_id = data.get("trace_id")
    log = data.get("log")
    if trace_id and log:
        if trace_id not in trace_store:
            trace_store[trace_id] = {"logs": [], "state": "EXECUTING"}
        
        if "logs" not in trace_store[trace_id]:
            trace_store[trace_id]["logs"] = []
            
        trace_store[trace_id]["logs"].append(log)
        # Periodic broadcast to frontend if needed, otherwise polling will catch it
        # await sio.emit("frontend_log", data)

@sio.on("execution_report")
async def execution_report(sid, data):
    trace_id = data.get("trace_id")
    if trace_id:
        print(f"[+] Execution Report received for {trace_id}: {data.get('status')}")
        # Keep existing logs
        existing_logs = trace_store.get(trace_id, {}).get("logs", [])
        raw_output = data.get('verified_output', "")
        
        # Initial status update
        prev_data = trace_store.get(trace_id, {})
        trace_store[trace_id] = {
            "state": "PROCESSING",
            "message": "Analyzing execution telemetry and generating operational summary...",
            "trace_id": trace_id,
            "severity": prev_data.get("severity", "LOW"),
            "intent": prev_data.get("intent"),
            "phases": prev_data.get("phases"),
            "mode": prev_data.get("mode"),
            "execution_available": prev_data.get("execution_available", True),
            "logs": existing_logs,
            "metadata": {
                "hash": data.get("execution_hash"),
                "timestamp": data.get("timestamp")
            }
        }

        # Run AI summarization in the background for both SUCCESS and FAILED
        async def run_summary():
            try:
                orchestrator = AgentOrchestrator(user_id="ent-user-882", team_id="soc-blue-team")
                summary = orchestrator.summarize_execution(data.get('executed_command'), raw_output)
                trace_store[trace_id]["message"] = summary
                trace_store[trace_id]["state"] = AgentState.COMPLETED if data.get("status") == "SUCCESS" else AgentState.FAILED
                print(f"[+] Final briefing generated for {trace_id}")
            except Exception as e:
                print(f"[!] Briefing generation failed: {e}")
                trace_store[trace_id]["message"] = f"Execution {data.get('status')}. Telemetry captured."
                trace_store[trace_id]["state"] = AgentState.COMPLETED if data.get("status") == "SUCCESS" else AgentState.FAILED

        import asyncio
        asyncio.create_task(run_summary())

@sio.on("sandbox_files_report")
async def sandbox_files_report(sid, data):
    trace_id = data.get("trace_id")
    if trace_id and trace_id in trace_store:
        trace_store[trace_id]["sandbox_files"] = data.get("files", [])
        print(f"[+] Sandbox inventory updated for {trace_id}")

@fastapi_app.get("/agent/sandbox/{trace_id}")
async def fetch_sandbox(trace_id: str):
    if not connected_lea_sid:
        return {"error": "LEA Offline"}
    await sio.emit("list_sandbox_files", {"trace_id": trace_id}, to=connected_lea_sid)
    return {"status": "request_sent"}

@sio.event
async def disconnect(sid):
    global connected_lea_sid
    if connected_lea_sid == sid:
        connected_lea_sid = None
        print(f"[!] Local Execution Agent Disconnected: {sid}")

@fastapi_app.post("/agent/execute")
async def execute_agent(req: ExecuteRequest, background_tasks: BackgroundTasks):
    if os.getenv("SYSTEM_STATUS") == "DISARMED":
        return {"state": "BLOCKED", "message": "System is currently DISARMED."}

    enabled_flags = [FeatureFlag.CAN_READ_SCAN_DATA]
    orchestrator = AgentOrchestrator(user_id="ent-user-882", team_id="soc-blue-team", enabled_features=enabled_flags)
    
    # FIX #2: Check LEA availability and allow planner to continue regardless
    is_lea_connected = connected_lea_sid is not None
    print(f"[*] LEA Status for Trace: {'ONLINE' if is_lea_connected else 'OFFLINE'}")
    
    result = orchestrator.process_request(req.agent_type, req.query, execution_available=is_lea_connected)
    trace_id = result.get("trace_id")
    
    # Trigger Media Generation for ASK_RANT (Learning Module)
    if req.agent_type == "ASK_RANT" and result.get("state") == AgentState.COMPLETED:
        text_for_media = result.get("message", "")
        if text_for_media:
            # Determine if video is needed (e.g. for explain commands)
            include_video = any(word in req.query.lower() for word in ["explain", "how to", "tutorial", "what is"])
            background_tasks.add_task(
                media_orchestrator.generate_media_pack,
                trace_id,
                text_for_media,
                include_video=include_video,
                severity=result.get("severity", "LOW")
            )

    trace_store[trace_id] = result
    return result

@fastapi_app.post("/agent/approval")
async def handle_approval(req: ApprovalRequest):
    if req.trace_id not in trace_store:
        raise HTTPException(status_code=404, detail="Trace not found")

    if req.decision == "approve":
        # GRACEFUL SYNC: Wait up to 3 seconds if LEA just connected or is reconnecting
        max_retries = 6
        retry_count = 0
        while not connected_lea_sid and retry_count < max_retries:
            await asyncio.sleep(0.5)
            retry_count += 1

        if not connected_lea_sid:
            return {
                "state": AgentState.FAILED,
                "message": "PLAN STAGED. The Security Bridge (LEA) is currently unreachable. Ensure the local execution agent is running and has established a heartbeat pulse.",
                "trace_id": req.trace_id
            }

        stored_res = trace_store[req.trace_id]
        message = stored_res.get("message", "")
        action_plan = stored_res.get("action_plan")
        
        import re
        command = "whoami" # Safe fallback
        args = []
        
        # PRIORITY 1: Direct extraction from Action Plan Object (Most Reliable)
        if action_plan and action_plan.get("operation"):
            full_op = action_plan["operation"].strip().replace("`", "")
            parts = full_op.split()
            if parts:
                command = parts[0]
                args = parts[1:]
        else:
            # PRIORITY 2: Regex parsing from Message String
            patterns = [
                r"Execution Task\s*:\s*(.*)",
                r"- Command\(s\) to be executed:\s*(.*)",
                r"\[PROBABLE MISSION\]:\s*(.*)",
                r"Task\s*:\s*(.*)"
            ]
            
            for pattern in patterns:
                cmd_match = re.search(pattern, message, re.IGNORECASE)
                if cmd_match:
                    full_line = cmd_match.group(1).strip().replace("`", "")
                    parts = full_line.split()
                    if parts:
                        command = parts[0]
                        args = parts[1:]
                        break
        
        await sio.emit("execute_command", {
            "trace_id": req.trace_id,
            "command": command,
            "args": args
        }, to=connected_lea_sid)

        # Update trace store state so polling reflects EXECUTING
        trace_store[req.trace_id]["state"] = "EXECUTING"

        return {
            "state": "EXECUTING",
            "message": "Dispatching signed execution request to Local Execution Agent. Awaiting verified output...",
            "trace_id": req.trace_id
        }
    else:
        return {
            "state": AgentState.FAILED,
            "message": "Action was rejected by the operator.",
            "trace_id": req.trace_id
        }

@fastapi_app.get("/agent/status/{trace_id}")
async def get_agent_status(trace_id: str):
    if trace_id in trace_store:
        res = trace_store[trace_id].copy()
        
        # Merge Media Status
        media_info = media_orchestrator.get_job_status(trace_id)
        res["media_status"] = media_info
        
        # Upgrade State based on Media Availability
        if res.get("state") == AgentState.COMPLETED.value or res.get("state") == "completed":
            if media_info.get("overall_state") in ["PROCESSING", "TEXT READY"]:
                res["state"] = "TEXT READY"
            elif media_info.get("overall_state") == "COMPLETED" and (media_info.get("audio_url") or media_info.get("video_url")):
                res["state"] = "MEDIA READY"
        
        # In case the result is an AgentState object, convert to value
        if hasattr(res.get("state"), "value"):
            res["state"] = res["state"].value
        return res
    return {"state": "NOT_FOUND"}

# Serve static files from the distributed frontend (Production)
if os.path.exists("static"):
    fastapi_app.mount("/", StaticFiles(directory="static", html=True), name="static")

async def simulate_ambient_intel():
    """Simulates the agent's autonomous thinking and world-monitoring."""
    import random
    events = [
        "Analyzing sandbox integrity patterns...",
        "Optimizing neural bridge latency...",
        "Scanning for persistent environmental drifts...",
        "Updating local safety heuristic weights...",
        "Syncing mission history with v-labs core...",
        "Monitoring background entropy levels...",
        "Validating zero-trust authentication tokens...",
        "Compiling autonomous behavioral metadata..."
    ]
    while True:
        try:
            event = random.choice(events)
            await sio.emit("cognitive_event", {
                "message": event,
                "timestamp": time.time(),
                "node": "CyberRant-Edge-01"
            })
            await asyncio.sleep(random.randint(8, 15))
        except Exception:
            await asyncio.sleep(30)

# Lifespan handles startup now

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
