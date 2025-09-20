from google.adk.agents import Agent

main_agent = Agent(
    name="main_agent",
    model="gemini-2.0-flash",
    description="Agent that uses the constraints and required quality to suggest parameters for cement production.",
    instruction="""
    read the constraints and required quality that we received from the user.
    print them in the json format as shown below:
    {
        "constraints": {
            "temperature": {"lower": value, "upper": value},
            "feeder_rate": {"lower": value, "upper": value},
            "vibration": {"lower": value, "upper": value}
        },
        "required_quality": value
    }
    take the parameters from the leaf agent in the json format as shown below:
    {
        "sensor_data": {
            "temperature": value,
            "feeder_rate": value,
            "vibration": value
        }
    }
    based on the constraints, required quality and sensor values, suggest the parameters for cement production.
    """,
)