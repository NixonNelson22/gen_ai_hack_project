from google.adk.agents import Agent, LlmAgent

ui_agent = LlmAgent(
    name="ui_agent",
    model="gemini-2.0-flash",
    description="Agent that takes constraints and required quality from the the user.",
    instruction="""
    You are a helpful assistant that greets the user.
    Ask the user for their constraints and required quality of the cement.
    IMPORTANT: 
    - required constraints are temperature, feeder_rate, and vibration.
    - each constraint MUST have lower and upper bounds.
    - if any constraint is missing, ask the user to provide it.
    - you must arrange the constraints in a json object as shown in the example below.
    - required quality is a numeric value out of 10. if its missing or invalid, ask the user to provide it again.
    RETURN:
    - json object with the following format:
    {
        "constraints": {
            "temperature": {"lower": float, "upper": float},
            "feeder_rate": {"lower": float, "upper": float},
            "vibration": {"lower": float, "upper": float}
        },
        "required_quality": int
    }
    - Example:
    {
        "constraints": {
            "temperature": {"lower": 100, "upper": 200},
            "feeder_rate": {"lower": 50, "upper": 150},
            "vibration": {"lower": 10, "upper": 20}
        },
        "required_quality": 9
    }
    DO NOT INCLUDE ANY OTHER INFORMATION OUTSIDE THE JSON OBJECT. 
    STRICTLY RETURN THE JSON OBJECT ONLY.
    """,
    output_key="constraints",
)