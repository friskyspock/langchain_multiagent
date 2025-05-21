from langgraph.prebuilt import create_react_agent
from llm import llm
from tools import FlightStatusTool

flight_status_agent = create_react_agent(
    model=llm,
    tools=[FlightStatusTool],
    prompt=""
)