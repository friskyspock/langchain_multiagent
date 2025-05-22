from supervisor_agent.agent import supervisor_agent
from worker_agents.search_agent import flight_search_agent
from worker_agents.status_agent import flight_status_agent
from langgraph.graph import StateGraph, MessagesState, START, END
from pretty_print import pretty_print_messages

workflow = StateGraph(MessagesState)
workflow.add_node("supervisor", supervisor_agent, destinations=("flight_search_agent", "flight_status_agent", END))
workflow.add_node("flight_search_agent", flight_search_agent)
workflow.add_node("flight_status_agent", flight_status_agent)
workflow.add_edge(START, "supervisor")
workflow.add_edge("flight_search_agent", "supervisor")
workflow.add_edge("flight_status_agent", "supervisor")

supervisor = workflow.compile()


if __name__ == "__main__":
    # print(supervisor.get_graph().draw_mermaid())
    while True:
        user_input = input("You: ")
        for chunk in supervisor.stream({"messages": [{"role": "user", "content": user_input}]}):
            # pretty_print_messages(chunk)
            print(chunk['supervisor']['messages'][-1])