from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import datetime
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the CSV datasets once at startup
df: pd.DataFrame = pd.read_csv(os.path.join(script_dir, "Flight_Schedule.csv"))
status_df: pd.DataFrame = pd.read_csv(os.path.join(script_dir, "Flight_Status.csv"))

app = FastAPI(title="Dummy Flight API")

# Pydantic models
class Flight(BaseModel):
    flight_number: str
    airline: Optional[str]
    origin: str
    destination: str
    departure_time: Optional[str]
    arrival_time: Optional[str]
    date: Optional[str] = None

class FlightStatus(BaseModel):
    flight_number: str
    status: str

# Helper functions to convert DataFrame rows to models
def row_to_flight(row: pd.Series) -> Flight:
    return Flight(
        flight_number=str(row["flightNumber"]) if not pd.isna(row["flightNumber"]) else "",
        airline=row["airline"] if not pd.isna(row["airline"]) else None,
        origin=str(row["origin"]) if not pd.isna(row["origin"]) else "",
        destination=str(row["destination"]) if not pd.isna(row["destination"]) else "",
        departure_time=row["scheduledDepartureTime"] if not pd.isna(row["scheduledDepartureTime"]) else None,
        arrival_time=row["scheduledArrivalTime"] if not pd.isna(row["scheduledArrivalTime"]) else None
    )

def row_to_flight_status(row: pd.Series) -> FlightStatus:
    return FlightStatus(
        flight_number=str(row["flightNumber"]) if not pd.isna(row["flightNumber"]) else "",
        status=str(row["status"]) if not pd.isna(row["status"]) else "Unknown"
    )

@app.get("/flights", response_model=List[Flight])
def get_all_flights(
    origin: str = Query(..., description="Origin airport code (required)"),
    destination: str = Query(..., description="Destination airport code (required)"),
    date: str = Query(..., description="Flight date in YYYY-MM-DD format (required)"),
    airline: Optional[str] = Query(None, description="Airline name (optional)")
):
    # Validate required parameters
    if not origin or not destination or not date:
        missing_fields = []
        if not origin:
            missing_fields.append("origin")
        if not destination:
            missing_fields.append("destination")
        if not date:
            missing_fields.append("date")

        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}. Please provide origin, destination, and date."
        )

    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Please use YYYY-MM-DD format."
        )

    result = df.copy()

    # Apply filters (all required fields are guaranteed to have values)
    result = result[result['origin'].str.lower() == origin.lower()]
    result = result[result['destination'].str.lower() == destination.lower()]

    day = datetime.strftime(datetime.strptime(date, '%Y-%m-%d'), '%A')
    result = result[result['dayOfWeek'].apply(lambda x: True if day in x.split(',') else False)]

    if airline:
        result = result[result['airline'].str.lower() == airline.lower()]

    print(result.head())
    return [row_to_flight(row) for _, row in result.head().iterrows()]

@app.get("/flights/{flight_number}", response_model=Flight)
def get_flight_by_number(flight_number: str):
    result = df[df["flightNumber"].str.lower() == flight_number.lower()]
    if result.empty:
        raise HTTPException(status_code=404, detail="Flight not found")
    return row_to_flight(result.iloc[0])

@app.get("/flight-status/{flight_number}", response_model=FlightStatus)
def get_flight_status(flight_number: str):
    """
    Get the current status of a flight by its flight number.
    """
    result = status_df[status_df["flightNumber"].str.lower() == flight_number.lower()]
    if result.empty:
        raise HTTPException(status_code=404, detail="Flight status not found")
    return row_to_flight_status(result.iloc[0])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
