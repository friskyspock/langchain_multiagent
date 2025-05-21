from typing import Optional
import requests
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field

class FlightSearchToolInputs(BaseModel):
    origin: str = Field(description="Origin city")
    destination: str = Field(description="Destination city")
    date: str = Field(description="Date of travel")

class FlightStatusToolInputs(BaseModel):
    flight_number: str = Field(description="Flight number")
    date: str = Field(description="Date of travel")


class FlightSearchTool(BaseTool):
    name: str = "Flight Search Tool"
    description: str = "Search for flights from an origin to a destination on a given date"
    args_schema: Optional[ArgsSchema] = FlightSearchToolInputs
    return_direct: bool = True

    def _run(self, origin: str, destination: str, date: str) -> str:
        url = f"http://127.0.0.1:8000/flights?origin={origin}&destination={destination}&date={date}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                return f"API Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Request failed: {e}"


class FlightStatusTool(BaseTool):
    name: str = "Flight Status Tool"
    description: str = "Get the status of a flight on a given date"
    args_schema: Optional[ArgsSchema] = FlightStatusToolInputs
    return_direct: bool = True

    def _run(self, flight_number: str) -> str:
        url = f"http://127.0.0.1:8000/flight-status/{flight_number}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                return f"API Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Request failed: {e}"