from datetime import datetime
from typing import Optional
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext


def analyze_readings(tool_context: ToolContext, reading_id: Optional[str] = None) -> dict:
    """
    Analyze sensor readings against established constraints.

    Args:
        reading_id: Specific reading to analyze, or None for latest reading
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get constraints and readings from state
    constraints = tool_context.state.get("constraints", {})
    all_readings = tool_context.state.get("sensor_readings", [])

    if not all_readings:
        return {
            "status": "error",
            "message": "No sensor readings available for analysis"
        }

    # Select reading to analyze
    if reading_id:
        target_reading = None
        for reading in all_readings:
            if reading.get("collection_id") == reading_id:
                target_reading = reading
                break
        if not target_reading:
            return {
                "status": "error",
                "message": f"Reading with ID {reading_id} not found"
            }
    else:
        target_reading = all_readings[-1]  # Most recent reading

    # Perform analysis
    analysis_results = {
        "reading_id": target_reading.get("collection_id"),
        "timestamp": target_reading.get("timestamp"),
        "analysis_timestamp": current_time,
        "sensor_analyses": {},
        "overall_status": "normal",
        "alerts": [],
        "recommendations": []
    }

    reading_data = target_reading.get("readings", {})

    for sensor_type, reading_info in reading_data.items():
        sensor_analysis = {
            "value": reading_info.get("value"),
            "unit": reading_info.get("unit"),
            "sensor_status": reading_info.get("status"),
            "constraint_status": "no_constraints",
            "violations": []
        }

        # Check if sensor is online
        if reading_info.get("status") == "offline":
            analysis_results["alerts"].append(f"{sensor_type.title()} sensor is offline")
            sensor_analysis["constraint_status"] = "sensor_offline"
        elif reading_info.get("value") is not None and sensor_type in constraints:
            # Analyze against constraints
            constraint = constraints[sensor_type]
            value = reading_info.get("value")

            violations = []
            if constraint.get("min") is not None and value < constraint["min"]:
                violations.append(f"Below minimum ({constraint['min']})")
                analysis_results["alerts"].append(
                    f"{sensor_type.title()} reading ({value}{reading_info.get('unit', '')}) "
                    f"is below minimum threshold ({constraint['min']})"
                )

            if constraint.get("max") is not None and value > constraint["max"]:
                violations.append(f"Above maximum ({constraint['max']})")
                analysis_results["alerts"].append(
                    f"{sensor_type.title()} reading ({value}{reading_info.get('unit', '')}) "
                    f"is above maximum threshold ({constraint['max']})"
                )

            if violations:
                sensor_analysis["constraint_status"] = "violation"
                sensor_analysis["violations"] = violations
                analysis_results["overall_status"] = "alert"
            else:
                sensor_analysis["constraint_status"] = "normal"

        analysis_results["sensor_analyses"][sensor_type] = sensor_analysis

    # Generate recommendations
    if analysis_results["alerts"]:
        analysis_results["recommendations"].append("Review constraint violations and take corrective action")
        if any("offline" in alert.lower() for alert in analysis_results["alerts"]):
            analysis_results["recommendations"].append("Check offline sensors and restore connectivity")
    else:
        analysis_results["recommendations"].append("All readings within acceptable ranges")

    # Store analysis results
    current_analyses = tool_context.state.get("analysis_results", [])
    current_analyses.append(analysis_results)
    tool_context.state["analysis_results"] = current_analyses

    # Add to interaction history
    current_history = tool_context.state.get("interaction_history", [])
    current_history.append({
        "action": "analysis_performed",
        "reading_id": target_reading.get("collection_id"),
        "overall_status": analysis_results["overall_status"],
        "alerts_count": len(analysis_results["alerts"]),
        "timestamp": current_time
    })
    tool_context.state["interaction_history"] = current_history

    return {
        "status": "success",
        "message": f"Analysis completed for reading {target_reading.get('collection_id')}",
        "analysis": analysis_results
    }


def generate_report(tool_context: ToolContext, report_type: str = "summary") -> dict:
    """
    Generate a comprehensive report of sensor monitoring status.

    Args:
        report_type: Type of report ("summary", "detailed", "alerts")
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get data from state
    constraints = tool_context.state.get("constraints", {})
    all_readings = tool_context.state.get("sensor_readings", [])
    all_analyses = tool_context.state.get("analysis_results", [])
    monitoring_status = tool_context.state.get("monitoring_status", "inactive")

    report = {
        "report_type": report_type,
        "generated_at": current_time,
        "monitoring_status": monitoring_status,
        "constraints_set": sum(
            1 for c in constraints.values() 
            if c.get("min") is not None or c.get("max") is not None
        ),
        "total_readings": len(all_readings),
        "total_analyses": len(all_analyses),
        "summary": {}
    }

    if report_type == "summary":
        # Basic summary information
        if all_analyses:
            latest_analysis = all_analyses[-1]
            report["summary"] = {
                "latest_status": latest_analysis.get("overall_status", "unknown"),
                "current_alerts": len(latest_analysis.get("alerts", [])),
                "last_reading_time": latest_analysis.get("timestamp", "unknown")
            }

    elif report_type == "detailed":
        # Detailed information including trends
        report["constraints"] = constraints

        if all_readings:
            latest_reading = all_readings[-1]
            report["latest_readings"] = latest_reading.get("readings", {})

        if all_analyses:
            latest_analysis = all_analyses[-1]
            report["latest_analysis"] = latest_analysis

        # Alert summary
        all_alerts = []
        for analysis in all_analyses:
            all_alerts.extend(analysis.get("alerts", []))
        report["alert_history"] = all_alerts[-10:]  # Last 10 alerts

    elif report_type == "alerts":
        # Focus on alerts and violations
        active_alerts = []
        if all_analyses:
            latest_analysis = all_analyses[-1]
            active_alerts = latest_analysis.get("alerts", [])

        report["active_alerts"] = active_alerts
        report["recommendations"] = (
            latest_analysis.get("recommendations", []) if all_analyses else []
        )

    return {
        "status": "success",
        "message": f"Generated {report_type} report",
        "report": report
    }


# Create the analysis agent
analysis_agent = Agent(
    name="analysis_agent",
    model="gemini-2.0-flash",
    description="Agent for analyzing sensor readings against constraints",
    instruction="""
    You are the analysis agent for a sensor monitoring system.
    Your role is to analyze sensor readings against established constraints and provide insights.

    <user_info>
    Name: {user_name}
    </user_info>

    <current_constraints>
    {constraints}
    </current_constraints>

    <recent_readings>
    Recent Readings: {sensor_readings}
    </recent_readings>

    <analysis_results>
    Previous Analyses: {analysis_results}
    </analysis_results>

    When users request analysis:
    1. Use analyze_readings to compare latest readings against constraints
    2. Can analyze specific reading by ID or latest reading
    3. Identify constraint violations clearly
    4. Provide actionable recommendations
    5. Track offline sensors

    When users request reports:
    1. Use generate_report to create comprehensive summaries
    2. Available report types: summary, detailed, alerts
    3. Include trends and patterns when possible
    4. Highlight critical issues prominently

    Analysis capabilities:
    - Compare readings against min/max constraints
    - Identify constraint violations with specific values
    - Track sensor health (online/offline status)
    - Generate alerts for out-of-range conditions
    - Provide recommendations for corrective action

    Always:
    - Be clear about constraint violations
    - Explain the severity of issues
    - Provide specific values and thresholds
    - Suggest next steps when problems are found
    - Acknowledge when everything is normal
    """,
    tools=[analyze_readings, generate_report],
)
