import random
from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

def collect_sensor_reading(tool_context: ToolContext) -> dict:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    readings = {
        "temperature": {
            "value": round(random.uniform(900.0, 1300.0), 2),
            "unit": "C",
            "timestamp": current_time,
            "status": "online",
        },
        "feeder_rate": {
            "value": round(random.uniform(30.0, 180.0), 2),
            "unit": "kg/h",
            "timestamp": current_time,
            "status": "online",
        },
        "vibration": {
            "value": round(random.uniform(5.0, 25.0), 2),
            "unit": "mm/s",
            "timestamp": current_time,
            "status": "online",
        },
    }

    current_readings = tool_context.state.get("sensor_readings", [])
    reading_entry = {
        "readings": readings,
        "timestamp": current_time,
        "collection_id": f"reading_{len(current_readings) + 1}"
    }
    current_readings.append(reading_entry)
    tool_context.state["sensor_readings"] = current_readings
    
    # Optionally, log
    print(f"Synthetic sensor data collected at {current_time}")
    
    return {
        "status": "success",
        "message": "Synthetic sensor readings collected.",
        "readings": readings,
        "timestamp": current_time,
        "collection_id": reading_entry["collection_id"],
    }

# Create the sensor agent
sensor_agent = Agent(
    name="sensor_agent",
    model="gemini-2.0-flash",
    description="""
    You are the sensor data collection agent for an industrial monitoring system. 
    Your responsibility is to autonomously collect and manage sensor readings for multiple sensor types.

    <user_info>
    Name: {user_name}
    </user_info>

    <monitoring_status>
    Status: {monitoring_status}
    </monitoring_status>

    <recent_readings>
    Recent Sensor Readings: {sensor_readings}
    </recent_readings>

    Supported Sensors:
    - Temperature (°C)
    - Feeder Rate (kg/h)
    - Vibration (mm/s)

    When requested, generate synthetic readings for one or all sensors.
    Store all readings with timestamps in the shared system state.

    Always:
    - Provide values clearly with units.
    - Indicate sensor online/offline status.
    - Alert if any sensor is offline.
    - Clearly communicate monitoring status changes.

    Note: Currently generating synthetic sensor data for testing. Production will integrate with real sensor APIs.
    """,
    tools=[collect_sensor_reading],
)
