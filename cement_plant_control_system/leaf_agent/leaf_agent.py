# leaf_agent/leaf_agent.py

import sys
import os
# Add project root to sys.path so we can import modules from parent directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import asyncio
import httpx  # for async HTTP requests to MCP server
import os
import uuid
from dotenv import load_dotenv
from cement_plant_control_system.data_stream.simulator import generate_plant_data  # simulated plant metrics

# Load environment variables from .env file
load_dotenv()

# Base URL for MCP server
MCP_BASE = os.getenv("MCP_BASE", "http://127.0.0.1:8000")
# Leaf agent ID (unique, from env or random if not set)
AGENT_ID = os.getenv("LEAF_AGENT_ID", f"leaf-{uuid.uuid4().hex[:6]}")
# Leaf agent name (for registration)
AGENT_NAME = "leaf_agent"
# Polling interval in seconds for checking new tasks
POLL_INTERVAL = 1.0

# -------------------------
# Agent registration
# -------------------------
async def register():
    """
    Register this leaf agent with the MCP server.
    Sends agent ID, name, and endpoint (not used currently).
    """
    url = f"{MCP_BASE}/register"
    payload = {"id": AGENT_ID, "name": AGENT_NAME, "endpoint": ""}

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        if r.status_code != 200:
            print(f"[leaf] registration failed: {r.status_code} {r.text}")
        else:
            print(f"[leaf] registered id={AGENT_ID}")

# -------------------------
# Optimization logic
# -------------------------
def optimize_grinding(plant_data):
    """
    Simple rule-based optimization for grinding process.
    Evaluates plant metrics and returns recommendations.
    """
    actions = []

    # Apply rules based on plant metrics
    if plant_data["grinding_power"] > 28:
        actions.append("Reduce mill speed by 5%")
    if plant_data["kiln_temp"] > 1480:
        actions.append("Reduce fuel input by 3%")
    if plant_data["fuel_mix"]["AF"] < 30:
        actions.append("Increase alternative fuel to 30% TSR")
    if plant_data["raw_mix_lime"] > 65:
        actions.append("Reduce lime feed slightly")
    if plant_data["emissions"]["CO2"] > 850:
        actions.append("Reduce fossil fuel proportion")

    # Default action if no rules triggered
    if not actions:
        actions.append("No changes needed — operating within optimal range")

    return actions

# -------------------------
# Report results back to MCP
# -------------------------
async def report_result(client, task_id, result):
    """
    Send optimization results or task output back to MCP server.
    """
    url = f"{MCP_BASE}/report_result"
    payload = {
        "agent_id": AGENT_ID,
        "task_id": task_id,
        "result": result,
    }
    await client.post(url, json=payload)

# -------------------------
# Polling loop for tasks
# -------------------------
async def poll_loop():
    """
    Continuous loop that fetches tasks from MCP server, processes them,
    and reports results. Handles 'grind_optimize' and 'sample' task types.
    """
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Fetch task for this agent
                r = await client.get(f"{MCP_BASE}/fetch_task/{AGENT_ID}")
                if r.status_code != 200:
                    # Non-200 responses could mean queue not ready
                    print(f"[leaf] fetch_task failed: {r.status_code} {r.text}")
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                data = r.json()
            except Exception as e:
                print(f"[leaf] error fetching/parsing task: {e}")
                await asyncio.sleep(POLL_INTERVAL)
                continue

            # Extract task from response
            task = data.get("task")
            if task:
                task_id = task["task_id"]
                print(f"[leaf] got task {task['task_type']} id={task_id}")

                if task["task_type"] == "grind_optimize":
                    # Generate simulated plant metrics
                    plant_data = generate_plant_data()
                    print("[leaf] running grind optimization on:", plant_data)

                    # Compute optimization recommendations
                    recommendations = optimize_grinding(plant_data)
                    print("[leaf] optimization recommendations:", recommendations)

                    # Report results back to MCP
                    await report_result(client, task_id, str(recommendations))

                elif task["task_type"] == "sample":
                    # Simply echo payload
                    print("[leaf] sample task payload:", task["payload"])
                    await report_result(client, task_id, f"Echo: {task['payload']}")

            # Wait before polling again
            await asyncio.sleep(POLL_INTERVAL)

# -------------------------
# Main entry point
# -------------------------
async def main():
    # Register agent first
    await register()
    # Start polling for tasks
    await poll_loop()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
