from datetime import datetime
from google.genai import types

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

async def update_interaction_history(session_service, app_name, user_id, session_id, entry):
    try:
        session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
        history = session.state.get("interaction_history", [])
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history.append(entry)
        updated_state = session.state.copy()
        updated_state["interaction_history"] = history
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=updated_state,
        )
    except Exception as e:
        print(f"Error updating interaction history: {e}")

async def add_user_query_to_history(session_service, app_name, user_id, session_id, query):
    await update_interaction_history(
        session_service, app_name, user_id, session_id,
        {"action": "user_query", "query": query}
    )

async def add_agent_response_to_history(session_service, app_name, user_id, session_id, agent_name, response):
    await update_interaction_history(
        session_service, app_name, user_id, session_id,
        {"action": "agent_response", "agent": agent_name, "response": response}
    )

async def display_state(session_service, app_name, user_id, session_id, label="Current State"):
    sensor_order = ["temperature", "feeder_rate", "vibration"]

    try:
        session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
        print(f"\n{'-' * 10} {label} {'-' * 10}")
        print(f"👤 User: {session.state.get('user_name', 'Unknown')}")
        monitoring_status = session.state.get("monitoring_status", "inactive")
        status_emoji = "🟢" if monitoring_status == "active" else "🔴"
        print(f"{status_emoji} Monitoring: {monitoring_status}")
        constraints = session.state.get("constraints", {})
        print("⚙️  Constraints:")
        for sensor_type in sensor_order:
            constraint = constraints.get(sensor_type, {})
            min_val = constraint.get("min", "None")
            max_val = constraint.get("max", "None")
            unit = constraint.get("unit", "")
            label_txt = sensor_type.replace("_", " ").title()
            print(f"  - {label_txt}: {min_val} - {max_val} {unit}")
        sensor_readings = session.state.get("sensor_readings", [])
        if sensor_readings:
            latest_reading = sensor_readings[-1]
            print(f"📊 Latest Reading ({latest_reading.get('timestamp', 'Unknown time')}):")
            for sensor_type in sensor_order:
                reading_info = latest_reading.get("readings", {}).get(sensor_type, {})
                value = reading_info.get("value", "N/A")
                unit = reading_info.get("unit", "")
                status = reading_info.get("status", "unknown")
                status_emoji = "🟢" if status == "online" else "🔴"
                label_txt = sensor_type.replace("_", " ").title()
                print(f"  - {label_txt}: {value} {unit} {status_emoji}")
        else:
            print("📊 Sensor Readings: None")
        analysis_results = session.state.get("analysis_results", [])
        if analysis_results:
            latest_analysis = analysis_results[-1]
            overall_status = latest_analysis.get("overall_status", "unknown")
            alerts = latest_analysis.get("alerts", [])
            status_emoji = "🔴" if overall_status == "alert" else "🟢"
            print(f"🔍 Latest Analysis: {overall_status} {status_emoji}")
            if alerts:
                print("  ⚠️  Active Alerts:")
                for alert in alerts[:3]:
                    print(f"    - {alert}")
        else:
            print("🔍 Analysis Results: None")
        interaction_history = session.state.get("interaction_history", [])
        if interaction_history:
            print(f"📝 Total Interactions: {len(interaction_history)}")
            recent = [h.get("action", "unknown") for h in interaction_history[-3:]]
            print(f"  Recent: {' → '.join(recent)}")
        else:
            print("📝 Interaction History: None")
        print("-" * (22 + len(label)))
    except Exception as e:
        print(f"Error displaying state: {e}")

async def process_agent_response(event):
    print(f"Event ID: {event.id}, Author: {event.author}")
    final_response = None
    if event.is_final_response():
        if (
            event.content and event.content.parts and
            hasattr(event.content.parts[0], "text") and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            print(f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╔══ AGENT RESPONSE ═══════════════════════════════════════════{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.BOLD}{final_response}{Colors.RESET}")
            print(f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╚═══════════════════════════════════════════════════════════════{Colors.RESET}\n")
    return final_response

async def call_agent_async(runner, user_id, session_id, query):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}--- Processing Query: {query} ---{Colors.RESET}")
    final_response_text = None
    agent_name = None

    await display_state(runner.session_service, runner.app_name, user_id, session_id, "State BEFORE processing")

    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.author:
                agent_name = event.author
            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"{Colors.BG_RED}{Colors.WHITE}ERROR during agent run: {e}{Colors.RESET}")

    if final_response_text and agent_name:
        await add_agent_response_to_history(
            runner.session_service, runner.app_name, user_id, session_id, agent_name, final_response_text
        )

    await display_state(runner.session_service, runner.app_name, user_id, session_id, "State AFTER processing")
    print(f"{Colors.YELLOW}{'-' * 30}{Colors.RESET}")
    return final_response_text
