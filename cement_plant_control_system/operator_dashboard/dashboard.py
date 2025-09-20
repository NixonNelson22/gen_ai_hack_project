# Streamlit operator dashboard: list agents, send tasks, and display results
import streamlit as st
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()
MCP_BASE = os.getenv("MCP_BASE", "http://127.0.0.1:8000")

# -------------------------
# Page title and layout
# -------------------------
st.set_page_config(page_title="Operator Dashboard", layout="wide")
st.title("🚀 Cement Plant Operator Dashboard")

# -------------------------
# Sidebar: refresh & auto-update
# -------------------------
st.sidebar.header("Settings")
auto_refresh = st.sidebar.checkbox("Auto-refresh every 5s", value=False)

# -------------------------
# Function: fetch registered agents
# -------------------------
def get_agents():
    try:
        resp = requests.get(f"{MCP_BASE}/agents").json()
        return resp.get("agents", [])
    except Exception as e:
        st.error(f"Failed to fetch agents: {e}")
        return []

# -------------------------
# Function: fetch results for an agent
# -------------------------
def get_results(agent_id):
    try:
        resp = requests.get(f"{MCP_BASE}/fetch_results/{agent_id}").json()
        results = resp.get("results", {})
        # Convert to list of dicts for easier display
        return [{"task_id": k, "result": v} for k, v in results.items()]
    except Exception as e:
        st.error(f"Failed to fetch results for {agent_id}: {e}")
        return []

# -------------------------
# Function: send a task to an agent
# -------------------------
def send_task(agent_id, task_type, payload):
    try:
        payload_dict = {"target_agent_id": agent_id, "task_type": task_type, "payload": payload}
        resp = requests.post(f"{MCP_BASE}/send_task", json=payload_dict)
        return resp.json()
    except Exception as e:
        st.error(f"Failed to send task: {e}")
        return {}

# -------------------------
# Main dashboard layout
# -------------------------
agents = get_agents()

# Registered agents table
st.subheader("Registered Agents")
if agents:
    for a in agents:
        st.write(f"- **{a['id']}**  ({a['name']})")
else:
    st.write("No agents registered yet.")

# -------------------------
# Task sending section
# -------------------------
st.subheader("Send Task")
col1, col2, col3 = st.columns(3)

with col1:
    target_agent = st.selectbox("Target agent id", [a['id'] for a in agents] or ["none"])
with col2:
    task_type = st.selectbox("Task type", ["grind_optimize", "sample"])
with col3:
    payload_txt = st.text_area("Payload (json)", '{"example": 1}', height=50)

if st.button("Send Task"):
    try:
        payload = eval(payload_txt)  # convert string to dict
        response = send_task(target_agent, task_type, payload)
        st.success(f"Task sent: {response}")
    except Exception as e:
        st.error(f"Invalid payload: {e}")

# -------------------------
# Results display section
# -------------------------
st.subheader("Agent Task Results")

for a in agents:
    results = get_results(a['id'])
    if results:
        with st.expander(f"Results for {a['name']} ({a['id']})"):
            for r in results:
                st.markdown(f"- **Task ID:** {r['task_id']}")
                st.markdown(f"  - **Result:** {r['result']}")
    else:
        st.write(f"No results yet for {a['name']} ({a['id']})")

# -------------------------
# Auto-refresh if enabled
# -------------------------
if auto_refresh:
    st.experimental_rerun()
