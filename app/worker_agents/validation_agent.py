from langgraph.prebuilt import create_react_agent
from llm import llm
from langchain_core.tools import tool
from typing import Dict, List
import re
from datetime import datetime

@tool
def validate_flight_search_input(user_input: str) -> str:
    """
    Validates if user input contains all required information for flight search.
    Returns validation result and missing fields if any.
    """
    # Extract information from user input
    missing_fields = []
    extracted_info = {}
    
    # Simple patterns to detect origin/destination/date
    # This is a basic implementation - you might want to use NLP for better extraction
    
    # Check for date patterns (YYYY-MM-DD, MM/DD/YYYY, etc.)
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
        r'\d{1,2}-\d{1,2}-\d{4}',  # MM-DD-YYYY
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}',  # Month DD, YYYY
        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{4}',  # Mon DD, YYYY
    ]
    
    date_found = False
    for pattern in date_patterns:
        if re.search(pattern, user_input.lower()):
            date_found = True
            break
    
    if not date_found:
        missing_fields.append("date")
    
    # Simple check for origin/destination keywords
    # This is basic - in practice you'd want better NLP
    location_keywords = ['from', 'to', 'origin', 'destination', 'airport']
    has_location_context = any(keyword in user_input.lower() for keyword in location_keywords)
    
    # Count potential airport codes (3-letter codes)
    airport_codes = re.findall(r'\b[A-Z]{3}\b', user_input.upper())
    
    if len(airport_codes) < 2 and not has_location_context:
        missing_fields.append("origin")
        missing_fields.append("destination")
    elif len(airport_codes) < 1:
        missing_fields.append("origin or destination")
    
    if missing_fields:
        return f"VALIDATION_FAILED: Missing required information: {', '.join(missing_fields)}. Please provide origin, destination, and travel date."
    else:
        return "VALIDATION_PASSED: All required information appears to be present."

input_validation_agent = create_react_agent(
    name="input_validation_agent",
    model=llm,
    tools=[validate_flight_search_input],
    prompt=(
        "You are an input validation agent for flight searches.\n"
        "Your job is to validate if user input contains ALL required information before allowing flight searches.\n"
        "\nREQUIRED INFORMATION FOR FLIGHT SEARCH:\n"
        "1. Origin (departure location/airport)\n"
        "2. Destination (arrival location/airport)\n"
        "3. Travel date\n"
        "\nINSTRUCTIONS:\n"
        "- Use the validation tool to check if user input has all required fields\n"
        "- If validation fails, ask the user to provide the missing information\n"
        "- If validation passes, confirm that the input is complete\n"
        "- Be helpful and specific about what information is missing\n"
        "- Do NOT make assumptions about missing information\n"
        "- After validation, respond to the supervisor directly"
    )
)
