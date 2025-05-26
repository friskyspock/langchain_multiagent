from langgraph.prebuilt import create_react_agent
from llm import llm
from tools import FlightSearchTool

flight_search_agent = create_react_agent(
    name="flight_search_agent",
    model=llm,
    tools=[FlightSearchTool],
    prompt=(
        "You are a flight search agent.\n"
        "You will be given an origin, destination, and date of a flight. You will return a list of flights.\n"
        "\nCRITICAL INSTRUCTIONS:\n"
        "- ALL THREE parameters are MANDATORY: origin, destination, AND date\n"
        "- NEVER assume, guess, or infer missing information (especially dates)\n"
        "- NEVER use today's date or any default date if not provided by the user\n"
        "- If ANY required parameter is missing, immediately ask the user to provide it\n"
        "- DO NOT call the flight search tool unless you have ALL three parameters explicitly provided\n"
        "- Date must be in YYYY-MM-DD format\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    )
)