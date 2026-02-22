import psutil
import json
import os
import time

def monitor_processes():
    proc_list = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_info']):
        try:
            pinfo = proc.info
            # Calculate memory in MB
            pinfo['memory_mb'] = pinfo['memory_info'].rss / (1024 * 1024)
            del pinfo['memory_info'] # Remove raw object
            proc_list.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort by memory usage
    proc_list = sorted(proc_list, key=lambda x: x['memory_mb'], reverse=True)
    return proc_list[:25] # Return top 25

if __name__ == "__main__":
    try:
        data = monitor_processes()
        print(json.dumps({
            "status": "SUCCESS",
            "top_processes": data,
            "system_load": os.getloadavg() if hasattr(os, 'getloadavg') else "N/A",
            "artifact": "process_report.json"
        }, indent=2))
        
        with open("process_report.json", "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(json.dumps({"status": "FAILED", "error": str(e)}))
