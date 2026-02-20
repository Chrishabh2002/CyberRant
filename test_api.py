import requests
import json

url = "http://localhost:8000/agent/execute"
data = {
    "agent_type": "RANT_COPILOT",
    "query": "I need my IP address"
}

resp = requests.post(url, json=data)
print(json.dumps(resp.json()))
