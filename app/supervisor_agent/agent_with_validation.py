from langgraph.prebuilt import create_react_agent
from supervisor_agent.handoffs import assign_to_input_validation_tool, assign_to_flight_search_tool, assign_to_flight_status_tool
from llm import llm
from worker_agents.validation_agent import input_validation_agent
from worker_agents.search_agent import flight_search_agent
from worker_agents.status_agent import flight_status_agent
from langgraph.graph import StateGraph, MessagesState, START, END

supervisor_agent_with_validation = create_react_agent(
    model=llm,
    tools=[assign_to_input_validation_tool, assign_to_flight_search_tool, assign_to_flight_status_tool],
    prompt=(
        "You are a supervisor managing three agents:\n"
        "- an input validation agent: Use this FIRST for any flight search requests to validate user input\n"
        "- a flight search agent: Use this ONLY after validation confirms all required info is present\n"
        "- a flight status agent: Use this for flight status inquiries\n"
        "\nWORKFLOW FOR FLIGHT SEARCHES:\n"
        "1. ALWAYS send flight search requests to input validation agent FIRST\n"
        "2. Only proceed to flight search agent if validation passes\n"
        "3. If validation fails, ask user for missing information\n"
        "\nCRITICAL RULES:\n"
        "1. NEVER assume or infer missing information\n"
        "2. For flight searches: ALWAYS validate input first\n"
        "3. Only assign tasks when validation confirms all required information is present\n"
        "4. Assign work to one agent at a time, do not call agents in parallel\n"
        "\nDo not do any work yourself. "
        "If you are not sure what to do, ask the user for more information."
    ),
    name="supervisor",
)

workflow_with_validation = StateGraph(MessagesState)
workflow_with_validation.add_node("supervisor", supervisor_agent_with_validation, destinations=("input_validation_agent", "flight_search_agent", "flight_status_agent", END))
workflow_with_validation.add_node("input_validation_agent", input_validation_agent)
workflow_with_validation.add_node("flight_search_agent", flight_search_agent)
workflow_with_validation.add_node("flight_status_agent", flight_status_agent)
workflow_with_validation.add_edge(START, "supervisor")
workflow_with_validation.add_edge("input_validation_agent", "supervisor")
workflow_with_validation.add_edge("flight_search_agent", "supervisor")
workflow_with_validation.add_edge("flight_status_agent", "supervisor")

supervisor_with_validation = workflow_with_validation.compile()
