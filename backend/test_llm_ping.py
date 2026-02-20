from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENROUTER_API_KEY")
)

try:
    print(f"[*] Testing LLM Connection with model: {os.getenv('DEFAULT_MODEL')}")
    response = client.chat.completions.create(
        model=os.getenv("DEFAULT_MODEL"),
        messages=[{"role": "user", "content": "Hello, respond with 'PONG'"}],
        temperature=0.1
    )
    print(f"[+] Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"[!] LLM Test Failed: {e}")
