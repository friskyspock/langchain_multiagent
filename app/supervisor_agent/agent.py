from langgraph.prebuilt import create_react_agent
from supervisor_agent.handoffs import assign_to_flight_search_tool, assign_to_flight_status_tool
from llm import llm
from worker_agents.search_agent import flight_search_agent
from worker_agents.status_agent import flight_status_agent
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver 
memory = MemorySaver() 

supervisor_agent = create_react_agent(
    model=llm,
    tools=[assign_to_flight_search_tool, assign_to_flight_status_tool],
    prompt=(
        "You are a supervisor managing two agents:\n"
        "- a flight search agent. Assign flight search tasks to this agent\n"
        "- a flight status agent. Assign flight status tasks to this agent\n"
        "\nCRITICAL RULES:\n"
        "1. NEVER assume or infer missing information (especially dates)\n"
        "2. For flight searches: origin, destination, AND date are required\n"
        "3. For flight status: flight number is required\n"
        "4. You will be provided with a session ID. Send session ID to all agents\n"
        "\nAssign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any work yourself. "
        "Only send parameters explicitly provided by the user to the agents. "
        "If you are not sure what to do, ask the user for more information."
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