from langgraph.prebuilt import create_react_agent
from supervisor_agent.handoffs import assign_to_flight_search_tool, assign_to_flight_status_tool
from llm import llm

supervisor_agent = create_react_agent(
    model=llm,
    tools=[assign_to_flight_search_tool, assign_to_flight_status_tool],
    prompt=(
        "You are a supervisor managing two agents:\n"
        "- a flight search agent. Assign flight search tasks to this agent\n"
        "- a flight status agent. Assign flight status tasks to this agent\n"
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any work yourself."
    ),
    name="supervisor",
)