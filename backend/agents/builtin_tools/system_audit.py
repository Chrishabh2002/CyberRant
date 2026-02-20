import platform
import os
import json
import psutil # Assuming psutil is available or we fallback

def audit_system():
    audit_data = {
        "os": platform.system(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "user": os.getlogin() if hasattr(os, 'getlogin') else "unknown",
        "working_dir": os.getcwd()
    }
    
    # Try to get process count if psutil is available
    try:
        import psutil
        audit_data["process_count"] = len(psutil.pids())
        audit_data["cpu_usage"] = f"{psutil.cpu_percent()}%"
        audit_data["memory_usage"] = f"{psutil.virtual_memory().percent}%"
    except ImportError:
        audit_data["process_count"] = "psutil not installed"

    return audit_data

if __name__ == "__main__":
    try:
        data = audit_system()
        # Save artifact for the ecosystem browser
        with open("audit_report.json", "w") as f:
            json.dump(data, f, indent=2)
            
        print(json.dumps({"status": "SUCCESS", "audit": data, "artifact": "audit_report.json"}, indent=2))
    except Exception as e:
        print(json.dumps({"status": "FAILED", "error": str(e)}))
