# MCP server: orchestrator using SQLite
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any
import uuid
import sqlite3
import json
import logging
from .log_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)
logger.info("Starting up...")

app = FastAPI(title="MCP Server - SQLite")

# ------------------------->
# SQLite connection
# ------------------------->
DB_FILE = "mcp.db"

def get_db_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if they don't exist
def setup_database():
    conn = get_db_conn()
    c = conn.cursor()
    # Agents table
    c.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            endpoint TEXT
        )
    ''')
    # Tasks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            task_type TEXT NOT NULL,
            payload TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents (id)
        )
    ''')
    # Results table
    c.execute('''
        CREATE TABLE IF NOT EXISTS results (
            task_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            result TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents (id)
        )
    ''')
    conn.commit()
    conn.close()

setup_database()
logger.info("Application startup complete.")
# ------------------------->
# Agent registration
# ------------------------->
class AgentInfo(BaseModel):
    id: str
    name: str
    endpoint: str  # HTTP endpoint (not used for now)

@app.post("/register")
async def register(agent: AgentInfo):
    logger.debug(f"Received request to register agent: {agent}")
    conn = get_db_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO agents (id, name, endpoint) VALUES (?, ?, ?)",
                  (agent.id, agent.name, agent.endpoint))
        conn.commit()
        logger.info(f"Agent {agent.id} registered successfully.")
    except sqlite3.Error as e:
        logger.error(f"Failed to register agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to register agent")
    finally:
        conn.close()
    return {"status": "registered", "agent_id": agent.id}

@app.get("/agents")
async def list_agents():
    logger.debug("Received request to list agents.")
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM agents")
    agents = [dict(row) for row in c.fetchall()]
    conn.close()
    logger.debug(f"Found {len(agents)} agents.")
    return {"agents": agents}

# ------------------------->
# Task management
# ------------------------->
class Task(BaseModel):
    target_agent_id: str
    task_type: str
    payload: Dict[str, Any] = {}

@app.post("/send_task")
async def send_task(task: Task):
    logger.debug(f"Received request to send task: {task}")
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM agents WHERE id = ?", (task.target_agent_id,))
    if not c.fetchone():
        logger.warning(f"Attempted to send task to non-existent agent: {task.target_agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")

    task_id = str(uuid.uuid4())
    try:
        c.execute("INSERT INTO tasks (task_id, agent_id, task_type, payload) VALUES (?, ?, ?, ?)",
                  (task_id, task.target_agent_id, task.task_type, json.dumps(task.payload)))
        conn.commit()
        logger.info(f"Task {task_id} queued for agent {task.target_agent_id}.")
    except sqlite3.Error as e:
        logger.error(f"Failed to send task: {e}")
        raise HTTPException(status_code=500, detail="Failed to send task")
    finally:
        conn.close()
    return {"status": "queued", "task_id": task_id}

@app.get("/fetch_task/{agent_id}")
async def fetch_task(agent_id: str):
    logger.debug(f"Received request to fetch task for agent: {agent_id}")
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE agent_id = ? ORDER BY rowid LIMIT 1", (agent_id,))
    task_row = c.fetchone()
    if not task_row:
        logger.debug(f"No tasks found for agent: {agent_id}")
        return {"task": None}

    task = dict(task_row)
    task['payload'] = json.loads(task['payload'])
    
    # Delete the task from the queue
    c.execute("DELETE FROM tasks WHERE task_id = ?", (task['task_id'],))
    conn.commit()
    conn.close()
    
    logger.debug(f"Fetched task {task['task_id']} for agent: {agent_id}")
    return {"task": task}

# ------------------------->
# Results reporting
# ------------------------->
class ResultReport(BaseModel):
    agent_id: str
    task_id: str
    result: str

@app.post("/report_result")
async def report_result(report: ResultReport):
    logger.debug(f"Received result report from agent: {report.agent_id}")
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM agents WHERE id = ?", (report.agent_id,))
    if not c.fetchone():
        logger.warning(f"Received result from non-existent agent: {report.agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")

    try:
        c.execute("INSERT OR REPLACE INTO results (task_id, agent_id, result) VALUES (?, ?, ?)",
                  (report.task_id, report.agent_id, report.result))
        conn.commit()
        logger.info(f"Result for task {report.task_id} from agent {report.agent_id} stored.")
    except sqlite3.Error as e:
        logger.error(f"Failed to report result: {e}")
        raise HTTPException(status_code=500, detail="Failed to report result")
    finally:
        conn.close()
    return {"status": "ok"}

@app.get("/fetch_results/{agent_id}")
async def fetch_results(agent_id: str):
    logger.debug(f"Received request to fetch results for agent: {agent_id}")
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM results WHERE agent_id = ?", (agent_id,))
    results = {row['task_id']: row['result'] for row in c.fetchall()}
    conn.close()
    logger.debug(f"Fetched {len(results)} results for agent: {agent_id}")
    return {"results": results}

# ------------------------->
# Dashboard
# ------------------------->
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    return FileResponse("cement_plant_control_system/operator_dashboard/index.html")

@app.get("/dashboard/agents", response_class=HTMLResponse)
async def get_dashboard_agents():
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM agents")
    agents = [dict(row) for row in c.fetchall()]
    conn.close()

    html = "<h2>Registered Agents</h2><table><tr><th>ID</th><th>Name</th></tr>"
    for agent in agents:
        html += f"<tr><td>{agent['id']}</td><td>{agent['name']}</td></tr>"
    html += "</table>"

    options = ""
    for agent in agents:
        options += f"<option value='{agent['id']}'>{agent['id']}</option>"
    
    return f"{html}<script>document.getElementById('agent_id').innerHTML = '{options}';</script>"

@app.get("/dashboard/results", response_class=HTMLResponse)
async def get_dashboard_results():
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM agents")
    agents = [dict(row) for row in c.fetchall()]
    
    html = "<h2>Agent Task Results</h2>"
    for agent in agents:
        c.execute("SELECT * FROM results WHERE agent_id = ?", (agent['id'],))
        results = c.fetchall()
        html += f"<h3>{agent['name']} ({agent['id']})</h3>"
        if not results:
            html += "<p>No results yet.</p>"
            continue
        
        html += "<table><tr><th>Task ID</th><th>Result</th></tr>"
        for row in results:
            html += f"<tr><td>{row['task_id']}</td><td>{row['result']}</td></tr>"
        html += "</table>"
        
    conn.close()
    return html

@app.post("/dashboard/send_task", response_class=HTMLResponse)
async def dashboard_send_task(agent_id: str = Form(...), task_type: str = Form(...), payload: str = Form(...)):
    logger.debug(f"Received request to send task from dashboard: {agent_id}")
    
    try:
        payload_dict = json.loads(payload)
    except json.JSONDecodeError:
        return "<p>Invalid JSON payload</p>"

    task = Task(target_agent_id=agent_id, task_type=task_type, payload=payload_dict)
    await send_task(task)
    
    return f"<p>Task sent to {agent_id}</p>"