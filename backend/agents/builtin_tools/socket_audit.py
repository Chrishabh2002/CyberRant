import psutil
import json
import socket

def audit_sockets():
    connections = []
    for conn in psutil.net_connections(kind='inet'):
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}"
        raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "NONE"
        
        try:
            process = psutil.Process(conn.pid)
            proc_name = process.name()
        except:
            proc_name = "unknown"
            
        connections.append({
            "fd": conn.fd,
            "family": "IPv4" if conn.family == socket.AF_INET else "IPv6",
            "type": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
            "local_address": laddr,
            "remote_address": raddr,
            "status": conn.status,
            "pid": conn.pid,
            "process": proc_name
        })
    return connections

if __name__ == "__main__":
    try:
        data = audit_sockets()
        print(json.dumps({
            "status": "SUCCESS",
            "connections": data,
            "count": len(data),
            "artifact": "socket_report.json"
        }, indent=2))
        
        with open("socket_report.json", "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(json.dumps({"status": "FAILED", "error": str(e)}))
