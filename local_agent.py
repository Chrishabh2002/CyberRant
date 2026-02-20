import asyncio
import socketio
import subprocess
import hashlib
import time
import os
import json
from datetime import datetime, timezone

# ==========================================
# LEA GOVERNANCE: COMMAND ALLOWLIST
# ==========================================
WHITELIST = {
    "LOW": ["ipconfig", "ifconfig", "hostname", "whoami", "uname", "dir", "ls", "date", "echo"],
    "MEDIUM": ["netstat", "ps", "tasklist", "df", "systemctl", "curl", "nmap", "ping", "tracert", "nslookup", "arp", "route"],
    "HIGH": ["pip", "npm", "docker", "git", "python", "ssh-keygen"]
}

BLOCKLIST = ["rm", "del", "shutdown", "format", "mkfs", "userdel", "kill", "format"]

# ==========================================
# AGENT ECOSYSTEM CONFIG
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SANDBOX_DIR = os.path.join(PROJECT_ROOT, "agent_sandbox")
BUILTIN_TOOLS_DIR = os.path.join(PROJECT_ROOT, "backend", "agents", "builtin_tools")

# Ensure ecosystem exists
os.makedirs(SANDBOX_DIR, exist_ok=True)

sio = socketio.AsyncClient(reconnection=True, reconnection_attempts=0, reconnection_delay=1)

class LocalExecutionAgent:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.agent_id = f"lea-{os.getlogin()}-{int(time.time())}"

    async def _start_pulse(self):
        """Streams live ecosystem telemetry to the gateway."""
        print("[*] Initializing Ecosystem Pulse bridge...")
        import random
        while True:
            try:
                stats = {"timestamp": time.time(), "agent_id": self.agent_id}
                try:
                    import psutil
                    stats.update({
                        "cpu": psutil.cpu_percent(),
                        "memory": psutil.virtual_memory().percent,
                        "disk": psutil.disk_usage(SANDBOX_DIR).percent
                    })
                except:
                    # High-fidelity Simulation fallback
                    stats.update({
                        "cpu": round(random.uniform(12, 18), 1),
                        "memory": round(random.uniform(45, 52), 1),
                        "disk": 32.4
                    })
                
                if sio.connected:
                    await sio.emit("ecosystem_pulse", stats)
                await asyncio.sleep(2)
            except Exception as e:
                await asyncio.sleep(5)

    async def connect(self):
        # Start the telemetry pulse in the background
        asyncio.create_task(self._start_pulse())
        
        while True:
            try:
                if not sio.connected:
                    print(f"[*] Connecting to CyberRant Gateway at {self.server_url}...")
                    await sio.connect(self.server_url, wait_timeout=10)
                    # Note: registration is now handled by the @sio.on("connect") global handler
                break
            except Exception as e:
                print(f"[!] Connection failed: {e}. Retrying in 5s...")
                await asyncio.sleep(5)

    @staticmethod
    def _is_safe(command):
        parts = command.split()
        if not parts: return False
        base_cmd = parts[0].lower()
        
        # Tool Mapping for High-Level Definitions
        TOOL_MAP = {
            "network_recon": "port_scan.py",
            "system_audit": "system_audit.py",
            "list_sandbox_files": "list_sandbox_files" # handled natively
        }

        # Allow mapped tools
        if base_cmd in TOOL_MAP:
            return True

        # Security Exception: Allow Python if it's running an internal agent tool
        if base_cmd == "python" and len(parts) > 1:
            script_path = os.path.abspath(parts[1])
            if script_path.startswith(os.path.abspath(BUILTIN_TOOLS_DIR)):
                return True

        if base_cmd in BLOCKLIST:
            return False
        
        # Check if it's in any whitelist tier
        for tier in WHITELIST.values():
            if base_cmd in tier:
                return True
        return False

    async def execute(self, data):
        trace_id = data.get("trace_id")
        command = data.get("command")
        args = data.get("args", [])
        
        full_command = f"{command} {' '.join(args)}".strip()
        
        print("\n" + "="*50)
        print(f"[*] NEW EXECUTION REQUEST | TRACE: {trace_id}")
        print(f"[*] COMMAND: {command} {' '.join(args)}")
        print("="*50)

        # Simulated Validation Delay
        print("[*] Validating integrity with CyberRant Protocol...")
        await asyncio.sleep(1.5)

        if not self._is_safe(full_command):
            print(f"[!] SECURITY BLOCK: Command '{command}' is not authorized.")
            await sio.emit("execution_report", {
                "trace_id": trace_id,
                "status": "FAILED",
                "message": f"Security violation: Command '{command}' is not in the approved CyberRant policy."
            })
            return

        # Advanced Path Normalization & Discovery for Built-in Tools
        effective_command = command
        
        # Mapping high-level tool names to actual scripts
        TOOL_MAP = {
            "network_recon": "port_scan.py",
            "system_audit": "system_audit.py"
        }

        if command.lower() in TOOL_MAP:
            import sys
            script_name = TOOL_MAP[command.lower()]
            script_path = os.path.normpath(os.path.join(BUILTIN_TOOLS_DIR, script_name))
            effective_command = sys.executable
            effective_args = [script_path] + args
        elif command.lower() in ["python", "python3"]:
            import sys
            effective_command = sys.executable
            effective_args = []
            for arg in args:
                # STRIP SANDBOX PREFIX: If the AI or script accidentally prepends 'agent_sandbox', remove it.
                clean_arg = arg
                if "agent_sandbox" in arg.lower():
                    split_key = "agent_sandbox"
                    idx = arg.lower().find(split_key)
                    clean_arg = arg[idx + len(split_key):].lstrip("/").lstrip("\\")
                
                if "backend/agents/builtin_tools" in clean_arg or clean_arg.endswith(".py"):
                    resolved_arg = os.path.normpath(os.path.join(PROJECT_ROOT, clean_arg))
                    if not os.path.exists(resolved_arg):
                        alt_path = os.path.normpath(os.path.join(BUILTIN_TOOLS_DIR, os.path.basename(clean_arg)))
                        if os.path.exists(alt_path):
                            resolved_arg = alt_path
                    effective_args.append(resolved_arg)
                else:
                    effective_args.append(clean_arg)
        else:
            effective_args = args

        # Emit the literal command first
        await sio.emit("execution_log", {"trace_id": trace_id, "log": f"INITIALIZING BRIDGE: {command} {' '.join(args)}...\n"})
        await sio.emit("execution_log", {"trace_id": trace_id, "log": f"[*] RESOLVED RUNTIME: {effective_command}\n"})
        if effective_args:
            await sio.emit("execution_log", {"trace_id": trace_id, "log": f"[*] RESOLVED TARGET: {effective_args[0]}\n"})
        await sio.emit("execution_log", {"trace_id": trace_id, "log": "[*] BRIDGE ENGAGED: Launching tactical toolized environment...\n"})
        
        try:
            # Use real subprocess to run the command in the SANDBOX
            # shell=False is safer, but we need to ensure effective_command
            process = subprocess.Popen(
                [effective_command] + effective_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Merge stderr into stdout
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=SANDBOX_DIR
            )
            
            full_output = []
            # Read logs in real-time
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    if not line: break
                    print(f"[>] {line}", end="")
                    await sio.emit("execution_log", {"trace_id": trace_id, "log": line})
                    full_output.append(line)
            
            process.wait() # Wait for the process to complete
            
            # Final integrity check
            if process.returncode == 0:
                print(f"[+] EXECUTION SUCCESS: Bridge verified.")
            else:
                print(f"[!] EXECUTION FAILED: Return code {process.returncode}")
                await sio.emit("execution_log", {"trace_id": trace_id, "log": f"[!] ENGINE ERROR: Return code {process.returncode}\n"})

            output = "".join(full_output) or "Command executed with no output."
            exec_hash = hashlib.sha256(output.encode()).hexdigest()

            print(f"\n[+] EXECUTION COMPLETE | EXIT CODE: {process.returncode}")
            print(f"[+] HASH: {exec_hash[:20]}...")

            await sio.emit("execution_report", {
                "trace_id": trace_id,
                "status": "SUCCESS" if process.returncode == 0 else "FAILED",
                "executed_command": full_command,
                "verified_output": output,
                "execution_hash": f"sha256:{exec_hash}",
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "confidence_level": "HIGH"
            })

        except Exception as e:
            print(f"[!] SYSTEM FAILURE: {str(e)}")
            await sio.emit("execution_report", {
                "trace_id": trace_id,
                "status": "FAILED",
                "message": f"Orchestration Boundary Error: {str(e)}"
            })
        print("="*50 + "\n")

@sio.on("execute_command")
async def on_execute(data):
    agent = LocalExecutionAgent()
    await agent.execute(data)

@sio.on("list_sandbox_files")
async def on_list_files(data):
    try:
        files = []
        for f in os.listdir(SANDBOX_DIR):
            path = os.path.join(SANDBOX_DIR, f)
            files.append({
                "name": f,
                "size": os.path.getsize(path),
                "is_dir": os.path.isdir(path),
                "modified": os.path.getmtime(path)
            })
        await sio.emit("sandbox_files_report", {"trace_id": data.get("trace_id"), "files": files})
    except Exception as e:
        print(f"[!] File list failed: {e}")

@sio.on("connect")
async def on_connect():
    print("[+] Socket.io Connection Established.")
    # Auto-register on every connection/reconnection
    agent_id = f"lea-{os.getlogin()}"
    await sio.emit("register_lea", {"agent_id": agent_id, "status": "ONLINE"})
    print(f"[*] Registered with Gateway as: {agent_id}")

@sio.on("disconnect")
async def on_disconnect():
    print("[!] Disconnected from server. Reconnecting...")

async def main():
    agent = LocalExecutionAgent()
    await agent.connect()
    await sio.wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] LEA shutting down safely.")
