"""
Example:
{
  "timestamp": "2025-09-13T09:00:00Z",
  "agent_id": "leaf-01",
  constraints": {
    "temperature": {"lower": 100, "upper": 200},
    "feeder_rate": {"lower": 50, "upper": 150},
    "vibration": {"lower": 10, "upper": 20}
  },
  "required_quality": 8,
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

{
    "constraints": {
        "temperature": {"lower": 1000, "upper": 1200},
        "feeder_rate": {"lower": 50, "upper": 150},
        "vibration": {"lower": 10, "upper": 20}
    },
    "required_quality": 9
}

"""

from google.adk.agents import LlmAgent, Agent

from .tools import get_current_time
from ...schema import UserInput

ui_agent = Agent(
    name="ui_agent",
    model="gemini-2.0-flash",
    description="Agent that takes constraints and required quality from the the user.",
    instruction="""
    You are a helpful assistant that greets the user and collects their input.
    Ask the user for their constraints and required quality of the cement.
    IMPORTANT: 
    - Required constraints are temperature, feeder_rate, and vibration.
    - Each constraint MUST have lower and upper bounds.
    - If any constraint is missing, ask the user to provide it.
    - You must arrange the constraints in a json object as shown in the example below.
    - Required quality is a numeric value out of 10. if its missing or invalid, ask the user to provide it again.
    RETURN:
    - json object with the following format with the values provided by the user:
    {
      "constraints": {
        "temperature": {"lower": float, "upper": float},
        "feeder_rate": {"lower": float, "upper": float},
        "vibration": {"lower": float, "upper": float}
      },
      "required_quality": int
    }
    
    DO NOT INCLUDE ANY OTHER INFORMATION OUTSIDE THE JSON OBJECT. 
    STRICTLY RETURN THE JSON OBJECT ONLY.
    ONLY USE DATA PROVIDED BY THE USER. DO NOT MAKE UP ANY DATA.
    """,
    # output_schema=UserInput,
    # input_schema=None,
    output_key="user_input",
)