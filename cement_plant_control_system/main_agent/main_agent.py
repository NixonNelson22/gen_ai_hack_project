# main_agent: registers to MCP, sends tasks to leaf_agent
import asyncio
import httpx
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

MCP_BASE = os.getenv("MCP_BASE", "http://127.0.0.1:8000")
AGENT_ID = os.getenv("MAIN_AGENT_ID", f"main-{uuid.uuid4().hex[:6]}")
AGENT_NAME = "main_agent"
POLL_INTERVAL = 2.0

async def register():
    url = f"{MCP_BASE}/register"
    payload = {"id": AGENT_ID, "name": AGENT_NAME, "endpoint": ""}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)
    print(f"[main] registered id={AGENT_ID}")

async def orchestrate_loop():
    leaf_id = os.getenv("LEAF_AGENT_ID")  # expects leaf id set in env or .env
    if not leaf_id:
        print("[main] WARNING: LEAF_AGENT_ID not set; using guess 'leaf-1'")
        leaf_id = "leaf-1"
    async with httpx.AsyncClient() as client:
        while True:
            # Periodic example: send a grind optimization task
            task = {
                "target_agent_id": leaf_id,
                "task_type": "grind_optimize",
                "payload": {"mill_speed": 80, "variance_est": 0.05}
            }
            await client.post(f"{MCP_BASE}/send_task", json=task)
            print("[main] queued grind_optimize to leaf")
            await asyncio.sleep(POLL_INTERVAL)

async def main():
    await register()
    await orchestrate_loop()

if __name__ == "__main__":
    asyncio.run(main())
