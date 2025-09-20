# test_leaf_agent.py
import requests
import time

MCP_BASE = "http://127.0.0.1:8000"
AGENT_ID = "leaf-1"  # must match the leaf agent ID exactly

# 1️⃣ Send a grind optimization task with empty payload
task_resp = requests.post(f"{MCP_BASE}/send_task", json={
    "target_agent_id": AGENT_ID,
    "task_type": "grind_optimize",
    "payload": {}  # empty so leaf agent uses simulated plant data
})
task_data = task_resp.json()
print("Task sent:", task_data)

task_id = task_data.get("task_id")
if not task_id:
    raise ValueError("Task not queued. Check if leaf agent is running.")

# 2️⃣ Wait for leaf agent to process task
task_results = []
for _ in range(15):  # retry up to 15 times
    results_resp = requests.get(f"{MCP_BASE}/fetch_results/{AGENT_ID}")
    results_data = results_resp.json()
    results_raw = results_data.get("results", {})

    # convert Redis hash to list of dicts
    task_results = [{"task_id": tid, "result": res} for tid, res in results_raw.items() if tid == task_id]

    if task_results:
        break
    print("Waiting for leaf agent to process task...")
    time.sleep(1)

# 3️⃣ Print results
if task_results:
    print("Results for task:", task_results)
else:
    print("No results found. Check if leaf agent is running and polling correctly.")
