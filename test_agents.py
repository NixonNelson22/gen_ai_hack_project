# test_agents.py
import requests
import time

MCP_BASE = "http://127.0.0.1:8000"

# Define agents you want to test
AGENTS = {
    "leaf-1": "leaf_agent",
    "main-1": "main_agent"
}

# Define task type
TASK_TYPE = "grind_optimize"

def send_task(agent_id):
    """Send a grind optimization task with empty payload."""
    task_resp = requests.post(f"{MCP_BASE}/send_task", json={
        "target_agent_id": agent_id,
        "task_type": TASK_TYPE,
        "payload": {}  # empty so agent uses simulated plant data
    })
    task_data = task_resp.json()
    print(f"Task sent to {agent_id}: {task_data}")
    return task_data.get("task_id")

def fetch_results(agent_id, task_id, retries=15, wait=1):
    """Fetch results for a specific task, retrying if necessary."""
    for _ in range(retries):
        results_resp = requests.get(f"{MCP_BASE}/fetch_results/{agent_id}")
        results_data = results_resp.json()
        results_raw = results_data.get("results", {})

        # Convert Redis hash to list of dicts
        task_results = [{"task_id": tid, "result": res} for tid, res in results_raw.items() if tid == task_id]

        if task_results:
            return task_results
        print(f"Waiting for {agent_id} to process task {task_id}...")
        time.sleep(wait)
    return []

def main():
    for agent_id, agent_name in AGENTS.items():
        task_id = send_task(agent_id)
        if not task_id:
            print(f"Task not queued for {agent_id}. Is the agent running?")
            continue
        task_results = fetch_results(agent_id, task_id)
        if task_results:
            print(f"Results for {agent_name} ({agent_id}): {task_results}")
        else:
            print(f"No results found for {agent_name} ({agent_id}).")

if __name__ == "__main__":
    main()
