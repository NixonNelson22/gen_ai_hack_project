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

"""

from pydantic import BaseModel, Field

class ConstraintBounds(BaseModel):
  lower: float = Field(..., description="Lower bound of the constraint.")
  upper: float = Field(..., description="Upper bound of the constraint.")

class SensorData(BaseModel):
  temperature: float = Field(..., description="Current temperature reading from the sensor.")
  feeder_rate: float = Field(..., description="Current feeder rate reading from the sensor.")
  vibration: float = Field(..., description="Current vibration reading from the sensor.")

class Constraints(BaseModel):
  temperature: ConstraintBounds = Field(..., description="Lower and upper bounds for temperature.")
  feeder_rate: ConstraintBounds = Field(..., description="Lower and upper bounds for feeder rate.")
  vibration: ConstraintBounds = Field(..., description="Lower and upper bounds for vibration.")

class UserInput(BaseModel):
  constraints: Constraints = Field(..., description="Constraints provided by the user.")
  required_quality: int = Field(..., description="Required quality of the cement (out of 10).")

class AgentOutput(BaseModel):
  timestamp: str = Field(..., description="Timestamp of the data.")
  agent_id: str = Field(..., description="ID of the agent.")
  constraints: Constraints = Field(..., description="Constraints provided by the user.")
  required_quality: int = Field(..., description="Required quality of the cement (out of 10).")
  sensor_data: SensorData = Field(..., description="Sensor data collected by the agent.")
  embedding: list[float] = Field(..., description="Embedding of the sensor data.")
  results: bool = Field(..., description="Results of the sensor data analysis.")
  local_decision: str = Field(..., description="Local decision made by the agent.")