import os
import json
import platform

def audit_env():
    # Capture relevant env vars without leaking sensitive values entirely
    # We redact values but show presence and metadata
    env_data = {}
    for key, value in os.environ.items():
        # Redact potentially sensitive values
        is_sensitive = any(word in key.lower() for word in ["key", "secret", "password", "token", "auth", "db", "credential"])
        
        env_data[key] = {
            "is_sensitive": is_sensitive,
            "length": len(value),
            "value_preview": f"{value[:4]}...{value[-2:]}" if is_sensitive and len(value) > 6 else (value if not is_sensitive else "REDACTED")
        }
    
    return {
        "os_env_count": len(os.environ),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "vars": env_data
    }

if __name__ == "__main__":
    try:
        data = audit_env()
        print(json.dumps({
            "status": "SUCCESS",
            "audit": data,
            "artifact": "env_audit.json"
        }, indent=2))
        
        with open("env_audit.json", "w") as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(json.dumps({"status": "FAILED", "error": str(e)}))
