# leaf_agent: registers to MCP, polls for tasks, executes stub actions
import asyncio
import httpx
import os
import uuid
from dotenv import load_dotenv

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
                # simple task handling
                if task["task_type"] == "grind_optimize":
                    # placeholder for real ML/GenAI call
                    await asyncio.sleep(0.5)
                    print("[leaf] performed grind optimization; energy reduced by ~1-2% (stub)")
                elif task["task_type"] == "sample":
                    print("[leaf] sample task payload:", task["payload"])
            await asyncio.sleep(POLL_INTERVAL)

async def main():
    await register()
    await poll_loop()

if __name__ == "__main__":
    asyncio.run(main())
