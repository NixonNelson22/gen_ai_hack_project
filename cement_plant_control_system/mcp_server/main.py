# MCP server: orchestrator using Redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uuid
import redis
import json

app = FastAPI(title="MCP Server - Redis")

# -------------------------
# Redis connection
# -------------------------
# Connect to local Redis on port 6380
# db=0 is default database, decode_responses=True returns strings instead of bytes
r = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)

# -------------------------
# Agent registration
# -------------------------
class AgentInfo(BaseModel):
    id: str
    name: str
    endpoint: str  # HTTP endpoint (not used for now)

@app.post("/register")
async def register(agent: AgentInfo):
    """
    Registers a new agent in Redis. Resets its queue and results if already exists.
    """
    key = f"agent:{agent.id}:queue"  # key for agent's task queue

    # Store agent info in "agents" hash; overwrites if exists
    r.hset("agents", agent.id, json.dumps(agent.dict()))

    # Ensure agent's queue and results hash are empty
    r.delete(key)  # task queue
    r.delete(f"agent:{agent.id}:results")  # results hash

    return {"status": "registered", "agent_id": agent.id}

@app.get("/agents")
async def list_agents():
    """
    List all registered agents with their info.
    """
    agents_raw = r.hgetall("agents")  # fetch all agents
    # parse JSON info for each agent
    return {"agents": [json.loads(v) for v in agents_raw.values()]}

# -------------------------
# Task management
# -------------------------
class Task(BaseModel):
    target_agent_id: str
    task_type: str
    payload: Dict[str, Any] = {}  # optional data for the task

@app.post("/send_task")
async def send_task(task: Task):
    """
    Queue a new task for a specific agent.
    """
    key = f"agent:{task.target_agent_id}:queue"

    # Check if target agent exists
    if not r.hexists("agents", task.target_agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Task object to store in Redis
    task_obj = {"task_id": task_id, "task_type": task.task_type, "payload": task.payload}

    # Push the task onto the agent's queue
    r.rpush(key, json.dumps(task_obj))

    return {"status": "queued", "task_id": task_id}

@app.get("/fetch_task/{agent_id}")
async def fetch_task(agent_id: str):
    """
    Fetch the next task for the given agent from Redis queue.
    Returns {"task": None} if no tasks are pending.
    """
    key = f"agent:{agent_id}:queue"

    # Verify agent exists
    if not r.hexists("agents", agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    # Pop the next task (FIFO)
    task_raw = r.lpop(key)
    if not task_raw:
        return {"task": None}

    return {"task": json.loads(task_raw)}  # parse JSON task

# -------------------------
# Results reporting
# -------------------------
class ResultReport(BaseModel):
    agent_id: str
    task_id: str
    result: str

@app.post("/report_result")
async def report_result(report: ResultReport):
    """
    Report task result from an agent and store in Redis hash.
    Each agent has a separate results hash: agent:<id>:results
    """
    key = f"agent:{report.agent_id}:results"

    # Check if agent exists
    if not r.hexists("agents", report.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    # Store the result: task_id -> result string
    r.hset(key, report.task_id, report.result)
    return {"status": "ok"}

@app.get("/fetch_results/{agent_id}")
async def fetch_results(agent_id: str):
    """
    Fetch all results for a given agent.
    Returns an empty dict if no results are stored.
    """
    key = f"agent:{agent_id}:results"

    if not r.exists(key):
        return {"results": {}}

    results_raw = r.hgetall(key)
    return {"results": results_raw}
