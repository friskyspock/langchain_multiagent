from typing import Optional
import requests
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool, StructuredTool
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field

class FlightSearchToolInputs(BaseModel):
    origin: str = Field(description="Origin city")
    destination: str = Field(description="Destination city")
    date: str = Field(description="Date of travel")

class FlightStatusToolInputs(BaseModel):
    flight_number: str = Field(description="Flight number")
    date: str = Field(description="Date of travel")

def search_flights(origin: str, destination: str, date: str) -> str:
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

def get_flight_status(flight_number: str, date: str) -> str:
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