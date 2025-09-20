# Streamlit operator dashboard: list agents + send tasks

import streamlit as st       # UI library
import requests              # For HTTP calls to MCP server
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
MCP_BASE = os.getenv("MCP_BASE", "http://127.0.0.1:8000")  # MCP server base URL

# -------------------------
# Dashboard title
# -------------------------
st.title("Operator Dashboard - MCP Local")

# -------------------------
# Refresh agents button
# -------------------------
if st.button("Refresh agents"):
    # Currently does nothing; page reload refreshes automatically
    pass

# -------------------------
# Fetch agents from MCP server
# -------------------------
agents = requests.get(f"{MCP_BASE}/agents").json().get("agents", [])

# Display registered agents
st.subheader("Registered Agents")
for a in agents:
    st.write(f"- {a['id']}  ({a['name']})")  # show agent id and name

# -------------------------
# Task sending section
# -------------------------
st.subheader("Send Task")

# Select target agent from dropdown (or "none" if no agents)
target = st.selectbox("Target agent id", [a['id'] for a in agents] or ["none"])

# Select task type
task_type = st.selectbox("Task type", ["grind_optimize", "sample"])

# Optional payload for task (entered as JSON string)
payload_txt = st.text_area("Payload (json)", '{"example": 1}')

# Button to send the task
if st.button("Send"):
    try:
        # Convert payload text to Python dict using eval (risky in prod!)
        payload = {"target_agent_id": target, "task_type": task_type, "payload": eval(payload_txt)}
        
        # POST task to MCP server
        r = requests.post(f"{MCP_BASE}/send_task", json=payload)
        
        # Display server response
        st.write("Sent:", r.json())
    except Exception as e:
        # Handle invalid JSON / network errors
        st.error(f"Bad payload or error: {e}")
