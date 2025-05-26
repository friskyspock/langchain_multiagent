from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import MessagesState, StateGraph, START
from langgraph.types import Command

def create_handoff_tool(*, agent_name: str, agent_description: str|None = None):
    name: str = f"transfer_to_{agent_name}"
    description: str =agent_description or f"Ask {agent_name} for help"

    @tool(name, description=description)
    def handoff_tool(state: Annotated[MessagesState, InjectedState], tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transfered to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id
        }
        return Command(
            goto=agent_name,
            update={**state, "messages": state["messages"] + [tool_message]},
            graph=Command.PARENT
        )

    return handoff_tool


assign_to_input_validation_tool = create_handoff_tool(
    agent_name="input_validation_agent",
    agent_description="Validate if user input contains all required information for flight searches"
)

assign_to_flight_search_tool = create_handoff_tool(
    agent_name="flight_search_agent",
    agent_description="Search for flights"
)

assign_to_flight_status_tool = create_handoff_tool(
    agent_name="flight_status_agent",
    agent_description="Get the status of a flight"
)