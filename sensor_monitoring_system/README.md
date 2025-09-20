# Sensor Monitoring System

A stateful multi-agent sensor monitoring system built with Google's Agent Development Kit (ADK).

## Project Structure

sensor_monitoring_system/
├── main.py
├── utils.py
├── .env
├── requirements.txt
└── sensor_monitoring_agent/
    ├── init.py
    ├── agent.py
    └── sub_agents/
        ├── constraint_agent/
        │   ├── init.py
        │   └── agent.py
        ├── sensor_agent/
        │   ├── init.py
        │   └── agent.py
        └── analysis_agent/
            ├── init.py
            └── agent.py


## Setup Instructions

1. Create the directory structure as shown above.
2. Install dependencies:  
   `pip install google-adk python-dotenv`
3. Place the code files in appropriate locations.
4. Set your Google API key in `.env`.

## Usage

Run the following:

```bash
python main.py
```

### Example Commands

- Set constraints: "Set temperature between 20 and 30 degrees"
- Get readings: "Get current sensor readings"
- Analyze data: "Analyze the latest readings"
- Generate report: "Generate a detailed report"
- Start monitoring: "Start continuous monitoring"

## System Features

**Agents:**

- Constraint Agent: Set and manage sensor thresholds
- Sensor Agent: Collect synthetic or real sensor data
- Analysis Agent: Analyze readings, detect violations, and generate reports

**State Features:**

- Shared state across all interactions
- Comprehensive history tracking
- Modular architecture for future scaling

## Notes

- To implement real sensors and advanced database storage, extend the sensor agent and swap InMemorySessionService for database-backed alternatives.
