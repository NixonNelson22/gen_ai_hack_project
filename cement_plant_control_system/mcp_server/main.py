# MCP server: orchestrator using Redis
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any
import uuid
import redis
import json
import logging
from .log_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Server - Redis")

# -------------------------
# Redis connection
# -------------------------
# Connect to local Redis on port 6380
# db=0 is default database, decode_responses=True returns strings instead of bytes
try:
    r = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)
    r.ping()
    logger.info("Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    # Depending on the use case, you might want to exit the application
    # For this example, we'll log the error and continue
    r = None

# -------------------------
# Agent registration
# -------------------------
class AgentInfo(BaseModel):
    id: str
    name: str
    endpoint: str  # HTTP endpoint (not used for now)

@app.post("/register")
async def register(agent: AgentInfo):
    logger.debug(f"Received request to register agent: {agent}")
    if not r:
        raise HTTPException(status_code=500, detail="Redis connection not available")
    key = f"agent:{agent.id}:queue"
    r.hset("agents", agent.id, json.dumps(agent.dict()))
    r.delete(key)
    r.delete(f"agent:{agent.id}:results")
    logger.info(f"Agent {agent.id} registered successfully.")
    return {"status": "registered", "agent_id": agent.id}

@app.get("/agents")
async def list_agents():
    logger.debug("Received request to list agents.")
    if not r:
        raise HTTPException(status_code=500, detail="Redis connection not available")
    agents_raw = r.hgetall("agents")
    agents = [json.loads(v) for v in agents_raw.values()]
    logger.debug(f"Found {len(agents)} agents.")
    return {"agents": agents}

# -------------------------
# Task management
# -------------------------
class Task(BaseModel):
    target_agent_id: str
    task_type: str
    payload: Dict[str, Any] = {}

@app.post("/send_task")
async def send_task(task: Task):
    logger.debug(f"Received request to send task: {task}")
    if not r:
        raise HTTPException(status_code=500, detail="Redis connection not available")
    key = f"agent:{task.target_agent_id}:queue"
    if not r.hexists("agents", task.target_agent_id):
        logger.warning(f"Attempted to send task to non-existent agent: {task.target_agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    task_id = str(uuid.uuid4())
    task_obj = {"task_id": task_id, "task_type": task.task_type, "payload": task.payload}
    r.rpush(key, json.dumps(task_obj))
    logger.info(f"Task {task_id} queued for agent {task.target_agent_id}.")
    return {"status": "queued", "task_id": task_id}

@app.get("/fetch_task/{agent_id}")
async def fetch_task(agent_id: str):
    logger.debug(f"Received request to fetch task for agent: {agent_id}")
    if not r:
        raise HTTPException(status_code=500, detail="Redis connection not available")
    key = f"agent:{agent_id}:queue"
    if not r.hexists("agents", agent_id):
        logger.warning(f"Attempted to fetch task for non-existent agent: {agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    task_raw = r.lpop(key)
    if not task_raw:
        logger.debug(f"No tasks found for agent: {agent_id}")
        return {"task": None}
    task = json.loads(task_raw)
    logger.debug(f"Fetched task {task['task_id']} for agent: {agent_id}")
    return {"task": task}

# -------------------------
# Results reporting
# -------------------------
class ResultReport(BaseModel):
    agent_id: str
    task_id: str
    result: str

@app.post("/report_result")
async def report_result(report: ResultReport):
    logger.debug(f"Received result report from agent: {report.agent_id}")
    if not r:
        raise HTTPException(status_code=500, detail="Redis connection not available")
    key = f"agent:{report.agent_id}:results"
    if not r.hexists("agents", report.agent_id):
        logger.warning(f"Received result from non-existent agent: {report.agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    r.hset(key, report.task_id, report.result)
    logger.info(f"Result for task {report.task_id} from agent {report.agent_id} stored.")
    return {"status": "ok"}

@app.get("/fetch_results/{agent_id}")
async def fetch_results(agent_id: str):
    logger.debug(f"Received request to fetch results for agent: {agent_id}")
    if not r:
        raise HTTPException(status_code=500, detail="Redis connection not available")
    key = f"agent:{agent_id}:results"
    if not r.exists(key):
        logger.debug(f"No results found for agent: {agent_id}")
        return {"results": {}}
    results_raw = r.hgetall(key)
    logger.debug(f"Fetched {len(results_raw)} results for agent: {agent_id}")
    return {"results": results_raw}

# -------------------------
# Dashboard
# -------------------------
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    return FileResponse("cement_plant_control_system/operator_dashboard/index.html")

@app.get("/dashboard/agents", response_class=HTMLResponse)
async def get_dashboard_agents():
    if not r:
        return "<p>Redis connection not available</p>"
    agents_raw = r.hgetall("agents")
    agents = [json.loads(v) for v in agents_raw.values()]
    html = "<h2>Registered Agents</h2><table><tr><th>ID</th><th>Name</th></tr>"
    for agent in agents:
        html += f"<tr><td>{agent['id']}</td><td>{agent['name']}</td></tr>"
    html += "</table>"

    # also update the agent dropdown
    options = ""
    for agent in agents:
        options += f"<option value='{agent['id']}'>{agent['id']}</option>"
    
    return f"{html}<script>document.getElementById('agent_id').innerHTML = '{options}';</script>"


@app.get("/dashboard/results", response_class=HTMLResponse)
async def get_dashboard_results():
    if not r:
        return "<p>Redis connection not available</p>"
    agents_raw = r.hgetall("agents")
    agents = [json.loads(v) for v in agents_raw.values()]
    html = "<h2>Agent Task Results</h2>"
    for agent in agents:
        key = f"agent:{agent['id']}:results"
        if not r.exists(key):
            html += f"<h3>{agent['name']} ({agent['id']})</h3><p>No results yet.</p>"
            continue
        results_raw = r.hgetall(key)
        html += f"<h3>{agent['name']} ({agent['id']})</h3>"
        html += "<table><tr><th>Task ID</th><th>Result</th></tr>"
        for task_id, result in results_raw.items():
            html += f"<tr><td>{task_id}</td><td>{result}</td></tr>"
        html += "</table>"
    return html

@app.post("/dashboard/send_task", response_class=HTMLResponse)
async def dashboard_send_task(agent_id: str = Form(...), task_type: str = Form(...), payload: str = Form(...)):
    logger.debug(f"Received request to send task from dashboard: {agent_id}")
    if not r:
        raise HTTPException(status_code=500, detail="Redis connection not available")
    key = f"agent:{agent_id}:queue"
    if not r.hexists("agents", agent_id):
        logger.warning(f"Attempted to send task to non-existent agent: {agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    task_id = str(uuid.uuid4())
    try:
        payload_dict = json.loads(payload)
    except json.JSONDecodeError:
        return "<p>Invalid JSON payload</p>"
    task_obj = {"task_id": task_id, "task_type": task_type, "payload": payload_dict}
    r.rpush(key, json.dumps(task_obj))
    logger.info(f"Task {task_id} queued for agent {agent_id}.")
    return f"<p>Task {task_id} sent to {agent_id}</p>"

