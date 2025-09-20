from google.adk.agents import Agent, LoopAgent, SequentialAgent

from .subagents.leaf_agent import leaf_agent
from .subagents.main_agent import main_agent
from .subagents.ui_agent import ui_agent

# root agent

refinement_loop = LoopAgent(
    name="quality_refinement_loop",
    max_iterations=1,
    sub_agents=[
        main_agent, 
        leaf_agent
    ],
    description="A loop that refines the output quality by using a main agent and a leaf until required quality is met.",
)

root_agent = SequentialAgent(
    name="ai_agent",
    description="Takes input from user and refines the quality of cememnt by changing parameters.",
    sub_agents=[
        ui_agent,
        refinement_loop
    ],
)

