from langgraph.prebuilt import create_react_agent
from llm import llm
from tools import FlightStatusTool

flight_status_agent = create_react_agent(
    name="flight_status_agent",
    model=llm,
    tools=[FlightStatusTool],
    prompt=(
        "You are a flight status agent.\n"
        "You will be given a flight number. You will return the status of the flight.\n"
        "INSTRUCTIONS:\n"
        "- If the flight number is missing, ask the user for it\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    )
)