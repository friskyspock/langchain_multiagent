from typing import Optional
import requests
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool, StructuredTool
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class FlightSearchToolInputs(BaseModel):
    session_id: str
    origin: Optional[str] = Field(description="Origin city. Pass NULL if not provided.")
    destination: Optional[str] = Field(description="Destination city. Pass NULL if not provided.")
    date: Optional[str] = Field(description="Date of travel. Pass NULL if not provided.")

class FlightStatusToolInputs(BaseModel):
    session_id: str
    flight_number: str = Field(description="Flight number")
    date: str = Field(description="Date of travel")

def search_flights(session_id: str, origin: Optional[str], destination: Optional[str], date: Optional[str]) -> str:
    missing_fields = []
    if not origin:
        if redis_client.hexists(session_id, "origin"):
            origin = redis_client.hget(session_id, "origin").decode('utf-8')
        else:
            missing_fields.append("origin")
    else:
        redis_client.hset(session_id, "origin", origin)
    if not destination:
        if redis_client.hexists(session_id, "destination"):
            destination = redis_client.hget(session_id, "destination").decode('utf-8')
        else:
            missing_fields.append("destination")
    else:
        redis_client.hset(session_id, "destination", destination)
    if not date:
        if redis_client.hexists(session_id, "date"):
            date = redis_client.hget(session_id, "date").decode('utf-8')
        else:
            missing_fields.append("date")
    else:
        redis_client.hset(session_id, "date", date)

    if len(missing_fields) > 0:
        return f"Missing required fields: {', '.join(missing_fields)}. Please provide origin, destination, and date."
    
    url = f"http://127.0.0.1:8000/flights?origin={origin}&destination={destination}&date={date}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e}"


FlightSearchTool = StructuredTool.from_function(
    func=search_flights,
    name="flight_search_tool",
    description="Search for flights from an origin to a destination on a given date",
    args_schema=FlightSearchToolInputs,
    return_direct=True
)

def get_flight_status(session_id: str, flight_number: str, date: str) -> str:
    url = f"http://127.0.0.1:8000/flight-status/{flight_number}?date={date}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e}"

FlightStatusTool = StructuredTool.from_function(
    func=get_flight_status,
    name="flight_status_tool",
    description="Get the status of a flight on a given date",
    args_schema=FlightStatusToolInputs,
    return_direct=True
)

# class FlightSearchTool(BaseTool):
#     name: str = "Flight Search Tool"
#     description: str = "Search for flights from an origin to a destination on a given date"
#     args_schema: Optional[ArgsSchema] = FlightSearchToolInputs
#     return_direct: bool = True

#     def _run(self, origin: str, destination: str, date: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
#         url = f"http://127.0.0.1:8000/flights?origin={origin}&destination={destination}&date={date}"
#         try:
#             response = requests.get(url)
#             if response.status_code == 200:
#                 return response.text
#             else:
#                 return f"API Error: {response.status_code} - {response.text}"
#         except Exception as e:
#             return f"Request failed: {e}"


# class FlightStatusTool(BaseTool):
#     name: str = "Flight Status Tool"
#     description: str = "Get the status of a flight on a given date"
#     args_schema: Optional[ArgsSchema] = FlightStatusToolInputs
#     return_direct: bool = True

#     def _run(self, flight_number: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
#         url = f"http://127.0.0.1:8000/flight-status/{flight_number}"
#         try:
#             response = requests.get(url)
#             if response.status_code == 200:
#                 return response.text
#             else:
#                 return f"API Error: {response.status_code} - {response.text}"
#         except Exception as e:
#             return f"Request failed: {e}"