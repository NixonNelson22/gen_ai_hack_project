# main_agent: registers to MCP, sends tasks to leaf_agent

import asyncio
import httpx  # async HTTP requests to MCP server
import os
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base URL for MCP server
MCP_BASE = os.getenv("MCP_BASE", "http://127.0.0.1:8000")
# Unique main agent ID (from env or random if not set)
AGENT_ID = os.getenv("MAIN_AGENT_ID", f"main-{uuid.uuid4().hex[:6]}")
# Name for main agent
AGENT_NAME = "main_agent"
# Polling interval (seconds) for sending tasks
POLL_INTERVAL = 2.0

# -------------------------
# Agent registration
# -------------------------
async def register():
    """
    Register this main agent with the MCP server.
    Sends agent ID, name, and endpoint (currently not used).
    """
    url = f"{MCP_BASE}/register"
    payload = {"id": AGENT_ID, "name": AGENT_NAME, "endpoint": ""}

    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

    print(f"[main] registered id={AGENT_ID}")

# -------------------------
# Task orchestration loop
# -------------------------
async def orchestrate_loop():
    """
    Periodically sends tasks to a leaf agent.
    Fetches leaf agent ID from environment or defaults to 'leaf-1'.
    """
    leaf_id = os.getenv("LEAF_AGENT_ID")  # expects leaf id set in env or .env
    if not leaf_id:
        print("[main] WARNING: LEAF_AGENT_ID not set; using guess 'leaf-1'")
        leaf_id = "leaf-1"

    async with httpx.AsyncClient() as client:
        while True:
            # Example: send a grind optimization task to leaf agent
            task = {
                "target_agent_id": leaf_id,
                "task_type": "grind_optimize",
                "payload": {"mill_speed": 80, "variance_est": 0.05}  # optional parameters
            }

            # POST task to MCP server
            await client.post(f"{MCP_BASE}/send_task", json=task)
            print("[main] queued grind_optimize to leaf")

            # Wait before sending next task
            await asyncio.sleep(POLL_INTERVAL)

# -------------------------
# Main entry point
# -------------------------
async def main():
    # Register this agent first
    await register()
    # Start sending tasks to leaf in a loop
    await orchestrate_loop()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
