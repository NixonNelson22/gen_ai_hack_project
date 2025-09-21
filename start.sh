#!/bin/bash

# Start the MCP server in the background
echo "Starting MCP server..."
uvicorn cement_plant_control_system.mcp_server.main:app --reload --port 8080 > logs/mcp_server.log 2>&1 &
MCP_SERVER_PID=$!

# Wait for the MCP server to be ready
echo "Waiting for MCP server to be ready..."
while ! curl -s http://127.0.0.1:8080/agents > /dev/null; do
    sleep 1
done

echo "MCP server is ready."

# Set the leaf agent ID
export LEAF_AGENT_ID="leaf-1"

# Start the other components
echo "Starting leaf agent..."
python cement_plant_control_system/leaf_agent/leaf_agent.py > logs/leaf_agent.log 2>&1 &
LEAF_AGENT_PID=$!

echo "Starting main agent..."
python cement_plant_control_system/main_agent/main_agent.py > logs/main_agent.log 2>&1 &
MAIN_AGENT_PID=$!

echo "Waiting for agents to register..."
sleep 5

echo "Operator dashboard is available at http://127.0.0.1:8080/dashboard"

# Wait for all background processes to finish
wait $MCP_SERVER_PID $LEAF_AGENT_PID $MAIN_AGENT_PID
