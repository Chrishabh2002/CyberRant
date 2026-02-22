import socket
import psutil
import json
import platform

def get_ip_info():
    interfaces = {}
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        addresses = []
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                addresses.append({
                    "ip": address.address,
                    "netmask": address.netmask,
                    "broadcast": address.broadcast
                })
        if addresses:
            interfaces[interface_name] = addresses
            
    # Get hostname IP as well
    hostname = socket.gethostname()
    try:
        primary_ip = socket.gethostbyname(hostname)
    except:
        primary_ip = "127.0.0.1"
        
    return {
        "hostname": hostname,
        "primary_ip": primary_ip,
        "interfaces": interfaces,
        "platform": platform.system()
    }

if __name__ == "__main__":
    try:
        data = get_ip_info()
        print(json.dumps({
            "status": "SUCCESS",
            "network_info": data,
            "artifact": "network_config.json"
        }, indent=2))
        
        # Save artifact
        with open("network_config.json", "w") as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(json.dumps({"status": "FAILED", "error": str(e)}))
