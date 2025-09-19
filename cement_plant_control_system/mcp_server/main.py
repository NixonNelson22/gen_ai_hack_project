# MCP server: simple orchestrator with in-memory pub/sub
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
import asyncio
import uuid

app = FastAPI(title="MCP Server - Local")

class AgentInfo(BaseModel):
    id: str
    name: str
    endpoint: str  # http endpoint to send tasks to

agents: Dict[str, AgentInfo] = {}
# simple in-memory queue per agent
queues: Dict[str, asyncio.Queue] = {}

@app.post("/register")
async def register(agent: AgentInfo):
    if agent.id in agents:
        raise HTTPException(status_code=400, detail="Agent already registered")
    agents[agent.id] = agent
    queues[agent.id] = asyncio.Queue()
    return {"status": "registered", "agent_id": agent.id}

@app.get("/agents")
async def list_agents():
    return {"agents": [a.dict() for a in agents.values()]}

class Task(BaseModel):
    target_agent_id: str
    task_type: str
    payload: Dict[str, Any] = {}

@app.post("/send_task")
async def send_task(task: Task):
    if task.target_agent_id not in queues:
        raise HTTPException(status_code=404, detail="Agent not found")
    await queues[task.target_agent_id].put({
        "task_type": task.task_type,
        "payload": task.payload,
        "task_id": str(uuid.uuid4())
    })
    return {"status": "queued"}

@app.get("/fetch_task/{agent_id}")
async def fetch_task(agent_id: str):
    if agent_id not in queues:
        raise HTTPException(status_code=404, detail="Agent not found")
    q = queues[agent_id]
    try:
        task = q.get_nowait()
        return {"task": task}
    except asyncio.QueueEmpty:
        return {"task": None}
