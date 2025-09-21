# main_agent: registers to MCP, sends tasks to leaf_agent

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import asyncio
import httpx  # async HTTP requests to MCP server
import os
import uuid
from dotenv import load_dotenv
from cement_plant_control_system.log_config import setup_logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = setup_logging(__name__)

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
        try:
            await client.post(url, json=payload)
            logger.info(f"Agent registered with ID: {AGENT_ID}")
        except httpx.RequestError as e:
            logger.error(f"Failed to register agent: {e}")

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
        logger.warning("LEAF_AGENT_ID not set; using guess 'leaf-1'")
        leaf_id = "leaf-1"

    async with httpx.AsyncClient() as client:
        while True:
            task = {
                "target_agent_id": leaf_id,
                "task_type": "tsr_optimize",
                "payload": {}
            }

            try:
                await client.post(f"{MCP_BASE}/send_task", json=task)
                logger.info(f"Queued task 'tsr_optimize' to leaf agent: {leaf_id}")
            except httpx.RequestError as e:
                logger.error(f"Failed to queue task: {e}")

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
