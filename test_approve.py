import requests
import json
import time

trace_id = "cr-tr-1770574151-ent-user"
url_approve = "http://localhost:8000/agent/approval"
url_status = f"http://localhost:8000/agent/status/{trace_id}"

# 1. Approve
print(f"[*] Approving trace: {trace_id}")
resp = requests.post(url_approve, json={"trace_id": trace_id, "decision": "approve"})
print(f"[+] Approval response: {resp.json()}")

# 2. Poll for results
for _ in range(10):
    time.sleep(2)
    resp = requests.get(url_status)
    status = resp.json()
    print(f"[*] Current State: {status.get('state')}")
    if status.get('state') in ['completed', 'failed']:
        print(f"[!] FINAL MESSAGE: {status.get('message')}")
        break
