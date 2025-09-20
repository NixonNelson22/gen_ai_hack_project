import asyncio
from datetime import datetime
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from utils import add_user_query_to_history, call_agent_async
from sensor_monitoring_agent.agent import sensor_monitoring_agent

load_dotenv()

session_service = InMemorySessionService()

initial_state = {
    "user_name": "System Operator",
    "constraints": {
        "temperature": {"min": None, "max": None, "unit": "C"},
        "feeder_rate": {"min": None, "max": None, "unit": "kg/h"},
        "vibration": {"min": None, "max": None, "unit": "mm/s"},
    },
    "sensor_readings": [],
    "analysis_results": [],
    "interaction_history": [],
    "monitoring_status": "inactive"
}

def all_constraints_set(constraints):
    """Check if all three sensors have at least one constraint (min or max) set"""
    required_sensors = ["temperature", "feeder_rate", "vibration"]
    for sensor in required_sensors:
        constraint = constraints.get(sensor, {})
        if constraint.get("min") is None and constraint.get("max") is None:
            return False
    return True

def constraints_exist(constraints):
    """Check if any constraints are set"""
    for c in constraints.values():
        if c.get("min") is None or c.get("max") is None:
            return False
    return True

async def main_async():
    APP_NAME = "Sensor Monitoring"
    USER_ID = "operator_001"
    new_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    SESSION_ID = new_session.id
    print(f"Created new sensor monitoring session: {SESSION_ID}")

    runner = Runner(
        agent=sensor_monitoring_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    print("\nWelcome to Sensor Monitoring System!")
    print("Available commands:")
    print("- Set constraints for temperature, feeder_rate, or vibration") # set temperature between 1000 and 1200, feeder rate between 50 and 150, vibration between 10 and 20
    print("- Request sensor readings")
    print("- Analyze readings against constraints")
    print("- Generate monitoring reports")
    print("- Start or stop monitoring mode")
    print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        user_input = input("Operator: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Ending monitoring session. Goodbye!")
            break

        await add_user_query_to_history(
            session_service, APP_NAME, USER_ID, SESSION_ID, user_input
        )
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

        # Get updated session state
        session = await session_service.get_session(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            session_id=SESSION_ID
        )
        constraints = session.state.get("constraints", {})
        readings = session.state.get("sensor_readings", [])

        # Auto-trigger sensor collection when all constraints are set
        if all_constraints_set(constraints) and not readings:
            print("\n🔄 All constraints set! Auto-collecting sensor readings...")
            await call_agent_async(runner, USER_ID, SESSION_ID, "Collect current sensor readings")
            
            # Get updated state after sensor collection
            session = await session_service.get_session(
                app_name=APP_NAME, 
                user_id=USER_ID, 
                session_id=SESSION_ID
            )
            readings = session.state.get("sensor_readings", [])

        # Auto-trigger analysis when both constraints and readings exist
        if constraints_exist(constraints) and readings:
            print("\n🔍 Auto-triggering sensor data analysis...")
            await call_agent_async(runner, USER_ID, SESSION_ID, "Analyze the latest readings")

    final_session = await session_service.get_session(
        app_name=APP_NAME, 
        user_id=USER_ID, 
        session_id=SESSION_ID
    )
    print("\nFinal Session State:")
    for key, value in final_session.state.items():
        print(f"{key}: {value}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
