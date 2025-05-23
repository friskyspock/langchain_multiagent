from langgraph.prebuilt import create_react_agent
from supervisor_agent.handoffs import assign_to_flight_search_tool, assign_to_flight_status_tool
from llm import llm
from worker_agents.search_agent import flight_search_agent
from worker_agents.status_agent import flight_status_agent
from langgraph.graph import StateGraph, MessagesState, START, END

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

workflow = StateGraph(MessagesState)
workflow.add_node("supervisor", supervisor_agent, destinations=("flight_search_agent", "flight_status_agent", END))
workflow.add_node("flight_search_agent", flight_search_agent)
workflow.add_node("flight_status_agent", flight_status_agent)
workflow.add_edge(START, "supervisor")
workflow.add_edge("flight_search_agent", "supervisor")
workflow.add_edge("flight_status_agent", "supervisor")

supervisor = workflow.compile()