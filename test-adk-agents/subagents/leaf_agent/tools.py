from typing import Dict
from google.adk.tools.tool_context import ToolContext

def exit_loop(tool_context: ToolContext) -> Dict[str, any]:
    """
    Tool to exit the loop only when required quality is met, the max iterations are reached or the constraints are failed.
    Agrs: 
        tool_context: context for tool execution
    Returns:
        empty dict to signal exit
    """
    tool_context.logger.info("Exiting loop as required quality is met.")
    tool_context.actions.escalate = True
    return {}