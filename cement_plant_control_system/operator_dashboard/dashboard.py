# Streamlit operator dashboard: list agents + send tasks
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
MCP_BASE = os.getenv("MCP_BASE", "http://127.0.0.1:8000")

st.title("Operator Dashboard - MCP Local")

if st.button("Refresh agents"):
    pass

agents = requests.get(f"{MCP_BASE}/agents").json().get("agents", [])
st.subheader("Registered Agents")
for a in agents:
    st.write(f"- {a['id']}  ({a['name']})")

st.subheader("Send Task")
target = st.selectbox("Target agent id", [a['id'] for a in agents] or ["none"])
task_type = st.selectbox("Task type", ["grind_optimize", "sample"])
payload_txt = st.text_area("Payload (json)", '{"example": 1}')

if st.button("Send"):
    try:
        payload = {"target_agent_id": target, "task_type": task_type, "payload": eval(payload_txt)}
        r = requests.post(f"{MCP_BASE}/send_task", json=payload)
        st.write("Sent:", r.json())
    except Exception as e:
        st.error(f"Bad payload or error: {e}")
