from datetime import datetime
from typing import Optional
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

def set_constraint(tool_context: ToolContext, sensor_type: str, min_value: Optional[float] = None, max_value: Optional[float] = None) -> dict:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    valid_sensors = ["temperature", "feeder_rate", "vibration"]
    
    if sensor_type.lower() not in valid_sensors:
        return {"status": "error", "message": f"Invalid sensor type. Must be one of: {', '.join(valid_sensors)}"}
    
    sensor_type = sensor_type.lower()
    current_constraints = tool_context.state.get("constraints", {})
    
    if sensor_type not in current_constraints:
        current_constraints[sensor_type] = {"min": None, "max": None, "unit": ""}
    
    if min_value is not None:
        current_constraints[sensor_type]["min"] = min_value
    if max_value is not None:
        current_constraints[sensor_type]["max"] = max_value
    
    tool_context.state["constraints"] = current_constraints
    
    current_history = tool_context.state.get("interaction_history", [])
    current_history.append({
        "action": "constraint_set",
        "sensor_type": sensor_type,
        "min_value": min_value,
        "max_value": max_value,
        "timestamp": current_time
    })
    tool_context.state["interaction_history"] = current_history
    
    return {
        "status": "success",
        "message": f"Constraint set for {sensor_type}: min={min_value}, max={max_value}",
        "sensor_type": sensor_type,
        "min_value": min_value,
        "max_value": max_value,
        "timestamp": current_time
    }

def clear_constraints(tool_context: ToolContext, sensor_type: Optional[str] = None) -> dict:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_constraints = tool_context.state.get("constraints", {})
    
    if sensor_type:
        if sensor_type.lower() in current_constraints:
            current_constraints[sensor_type.lower()] = {"min": None, "max": None, "unit": current_constraints[sensor_type.lower()].get("unit", "")}
            message = f"Cleared constraints for {sensor_type}"
        else:
            return {"status": "error", "message": f"No constraints found for {sensor_type}"}
    else:
        for sensor in current_constraints:
            current_constraints[sensor]["min"] = None
            current_constraints[sensor]["max"] = None
        message = "Cleared all sensor constraints"
    
    tool_context.state["constraints"] = current_constraints
    
    current_history = tool_context.state.get("interaction_history", [])
    current_history.append({"action": "constraints_cleared", "sensor_type": sensor_type, "timestamp": current_time})
    tool_context.state["interaction_history"] = current_history
    
    return {"status": "success", "message": message, "timestamp": current_time}

constraint_agent = Agent(
    name="constraint_agent",
    model="gemini-2.0-flash", 
    description="Agent for setting and managing sensor monitoring constraints",
    instruction="""You are the constraint management agent for a sensor monitoring system.
    
    Available sensors: Temperature (°C), Feeder_rate (kg/h), Vibration (mm/s)
    
    Use set_constraint tool to set min/max values for sensors.
    Use clear_constraints tool to clear constraints for specific sensors or all.
    
    Always confirm constraint changes and explain monitoring implications.""",
    tools=[set_constraint, clear_constraints],
)