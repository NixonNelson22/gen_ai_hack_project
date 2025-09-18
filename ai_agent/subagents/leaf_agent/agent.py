"""
Example:
{
  "timestamp": "2025-09-13T09:00:00Z",
  "agent_id": "leaf-01",
  "sensor_data": {
    "temperature": 1050,
    "feeder_rate": 50,
    "vibration": 3.2
  },
  "embedding": [0.12, 0.98, -0.44, 0.03, 0.55],
  "results": {
    "temperature": "pass",
    "feeder_rate": "fail",  
    "vibration": "pass"
  },
  "local_decision": "increase_feeder_rate"
}

"""

from google.adk.agents import Agent

from .tools import exit_loop

leaf_agent = Agent(
    name="leaf_agent",
    model="gemini-2.0-flash",
    description="Takes real time values from sensors and passes them to main agent.",
    instruction="""
    You are a assistant to main agent that collects real time values from sensors and passes them to main agent.
    read the constraints and required quality that we received from the user.
    print them in the json format as shown below:
    {
        "sensor_data": {
            "temperature": 1050,
            "feeder_rate": 50,
            "vibration": 3.2
        }
    }
    """,
    tools=[exit_loop],
    output_key="sensor_data",
)