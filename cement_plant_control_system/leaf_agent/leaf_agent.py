# leaf_agent/leaf_agent.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))



import asyncio
import httpx
import os
import uuid
from dotenv import load_dotenv
from cement_plant_control_system.data_stream.simulator import generate_plant_data  # <-- NEW

load_dotenv()

MCP_BASE = os.getenv("MCP_BASE", "http://127.0.0.1:8000")
AGENT_ID = os.getenv("LEAF_AGENT_ID", f"leaf-{uuid.uuid4().hex[:6]}")
AGENT_NAME = "leaf_agent"
POLL_INTERVAL = 1.0

async def register():
    url = f"{MCP_BASE}/register"
    payload = {"id": AGENT_ID, "name": AGENT_NAME, "endpoint": ""}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)
    print(f"[leaf] registered id={AGENT_ID}")

async def poll_loop():
    async with httpx.AsyncClient() as client:
        while True:
            r = await client.get(f"{MCP_BASE}/fetch_task/{AGENT_ID}")
            data = r.json()
            task = data.get("task")
            if task:
                print(f"[leaf] got task {task['task_type']} id={task['task_id']}")
                
                if task["task_type"] == "grind_optimize":
                    # 🚀 use simulated plant data
                    plant_data = generate_plant_data()
                    print("[leaf] running grind optimization on:", plant_data)
                    # pretend to run optimization
                    await asyncio.sleep(0.5)
                    print("[leaf] optimized grinding power → -1.3% energy (simulated)")
                
                elif task["task_type"] == "sample":
                    print("[leaf] sample task payload:", task["payload"])
            
            await asyncio.sleep(POLL_INTERVAL)

async def main():
    await register()
    await poll_loop()

if __name__ == "__main__":
    asyncio.run(main())
