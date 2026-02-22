import os
import json
import fnmatch

def search_files(root_dir, patterns):
    matches = []
    # Search within the sandbox by default for safety
    for root, dirnames, filenames in os.walk(root_dir):
        for pattern in patterns:
            for filename in fnmatch.filter(filenames, pattern):
                full_path = os.path.join(root, filename)
                try:
                    stats = os.stat(full_path)
                    matches.append({
                        "name": filename,
                        "path": os.path.relpath(full_path, root_dir),
                        "size": stats.st_size,
                        "modified": stats.st_mtime
                    })
                except:
                    continue
    return matches

if __name__ == "__main__":
    # Target common sensitive patterns
    SENSITIVE_PATTERNS = [
        "*.env", "*.log", "*.config", "*secret*", "*key*", "*.pem", 
        "*.json", "*.yaml", "*.yml", "docker-compose*"
    ]
    
    # We restrict search to /app (Docker) or current dir (Local) for safety
    SEARCH_ROOT = os.environ.get("AGENT_SANDBOX", os.getcwd())
    
    try:
        results = search_files(SEARCH_ROOT, SENSITIVE_PATTERNS)
        print(json.dumps({
            "status": "SUCCESS",
            "root": SEARCH_ROOT,
            "match_count": len(results),
            "matches": results[:50], # Limit to first 50
            "artifact": "recon_files.json"
        }, indent=2))
        
        with open("recon_files.json", "w") as f:
            json.dump(results, f, indent=2)
            
    except Exception as e:
        print(json.dumps({"status": "FAILED", "error": str(e)}))
