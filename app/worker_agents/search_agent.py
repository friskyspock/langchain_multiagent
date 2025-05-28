from langgraph.prebuilt import create_react_agent
from llm import llm
from tools import FlightSearchTool

flight_search_agent = create_react_agent(
    name="flight_search_agent",
    model=llm,
    tools=[FlightSearchTool],
    prompt=(
        "You are a flight search agent.\n"
        "You will be given parameters of a flight. You will return a list of flights.\n"
        "\nINSTRUCTIONS:\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
        "- You will be provided with a session ID. Send session ID to tools."
    )
)