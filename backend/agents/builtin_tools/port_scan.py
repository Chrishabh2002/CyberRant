import socket
import sys
import json

def scan_ports(target, ports):
    results = []
    print(f"[*] Starting scan on {target}...")
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((target, port))
        if result == 0:
            status = "OPEN"
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"
            results.append({"port": port, "status": status, "service": service})
        sock.close()
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python port_scan.py <target> [ports_comma_or_space_sep]"}))
        sys.exit(1)
    
    target = sys.argv[1]
    raw_ports = sys.argv[2:] if len(sys.argv) > 2 else ["80"]
    
    ports = []
    for p_group in raw_ports:
        # Handle "80,443" or just "80"
        for p in p_group.replace(",", " ").split():
            try:
                ports.append(int(p))
            except ValueError:
                continue
    
    if not ports:
        ports = [80, 443, 22] # Default common ports
    
    try:
        results = scan_ports(target, ports)
        data = {"target": target, "results": results}
        # Save artifact for ecosystem visibility
        with open("recon_report.json", "w") as f:
            json.dump(data, f, indent=2)
            
        print(json.dumps({"status": "SUCCESS", "results": results, "artifact": "recon_report.json"}, indent=2))
    except Exception as e:
        print(json.dumps({"status": "FAILED", "error": str(e)}))
