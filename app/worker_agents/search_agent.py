from langgraph.prebuilt import create_react_agent
from llm import llm
from tools import FlightSearchTool

flight_search_agent = create_react_agent(
    model=llm,
    tools=[FlightSearchTool],
    prompt=""
)