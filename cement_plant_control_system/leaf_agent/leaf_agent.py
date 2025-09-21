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
from cement_plant_control_system.log_config import setup_logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = setup_logging(__name__)

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
        try:
            r = await client.post(url, json=payload)
            r.raise_for_status()  # Raise an exception for bad status codes
            logger.info(f"Agent registered with ID: {AGENT_ID}")
        except httpx.RequestError as e:
            logger.error(f"Failed to register agent: {e}")

# -------------------------
# Optimization logic
# -------------------------
def optimize_tsr(plant_data):
    """
    Simple rule-based optimization for TSR.
    Evaluates plant metrics and returns recommendations.
    """
    actions = []
    try:
        af_calorific = plant_data.get("Fuel_Calorific_Value", 4500)
        ff_calorific = 4500  # Assuming a default for fossil fuel
        af_flow = plant_data.get("AF_Fuel_Flow_Setpoint", 0)
        ff_flow = plant_data.get("Fossil_Fuel_Flow_SP", 0)

        total_energy = (af_flow * af_calorific) + (ff_flow * ff_calorific)
        if total_energy > 0:
            tsr_current = ((af_flow * af_calorific) / total_energy) * 100
        else:
            tsr_current = 0

        tsr_target = plant_data.get("TSR_Target_Percentage", 30)

        if tsr_current < tsr_target:
            actions.append(f"Increase AF Fuel Flow to meet TSR target of {tsr_target}%. Current TSR is {tsr_current:.2f}%")

    except Exception as e:
        logger.error(f"Error in TSR calculation: {e}")
        actions.append(f"Error in TSR calculation: {e}")

    if plant_data.get("Burning_Zone_Temp_SP", 1450) < 1400:
        actions.append("Increase fuel flow to raise burning zone temperature.")

    if plant_data.get("Oxygen_Concentration_SP", 2) < 1.5:
        actions.append("Increase air flow to ensure complete combustion.")

    if plant_data.get("CO_Emission_Limit_SP", 850) > 850:
        actions.append("Reduce fuel flow or increase air to lower CO emissions.")

    if plant_data.get("NOx_Emission_Limit_SP", 450) > 450:
        actions.append("Optimize combustion temperature to reduce NOx emissions.")

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
    try:
        await client.post(url, json=payload)
        logger.info(f"Successfully reported result for task {task_id}")
    except httpx.RequestError as e:
        logger.error(f"Failed to report result for task {task_id}: {e}")

# -------------------------
# Polling loop for tasks
# -------------------------
async def poll_loop():
    """
    Continuous loop that fetches tasks from MCP server, processes them,
    and reports results. Handles 'tsr_optimize' and 'sample' task types.
    """
    async with httpx.AsyncClient() as client:
        while True:
            try:
                r = await client.get(f"{MCP_BASE}/fetch_task/{AGENT_ID}")
                r.raise_for_status()
                data = r.json()
            except httpx.RequestError as e:
                logger.error(f"Error fetching task: {e}")
                await asyncio.sleep(POLL_INTERVAL)
                continue
            except Exception as e:
                logger.error(f"Error parsing task response: {e}")
                await asyncio.sleep(POLL_INTERVAL)
                continue

            task = data.get("task")
            if task:
                task_id = task["task_id"]
                logger.info(f"Received task {task['task_type']} with ID {task_id}")

                if task["task_type"] == "tsr_optimize":
                    plant_data = generate_plant_data()
                    logger.debug(f"Running TSR optimization on: {plant_data}")
                    recommendations = optimize_tsr(plant_data)
                    logger.info(f"Optimization recommendations: {recommendations}")
                    await report_result(client, task_id, str(recommendations))

                elif task["task_type"] == "sample":
                    logger.info(f"Sample task payload: {task['payload']}")
                    await report_result(client, task_id, f"Echo: {task['payload']}")

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
