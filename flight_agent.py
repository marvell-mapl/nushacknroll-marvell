"""
Flight Agent - Specialist for finding and recommending flights.
"""

from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from constants import get_llm, FLIGHTS_DATA


@tool
def search_flights_tool(origin: str, destination: str, date: str, passengers: str = "1"):
    """
    Search flights database for available flights.
    
    Args:
        origin: Departure city
        destination: Arrival city
        date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers
        
    Returns:
        List of available flights with details
    """
    passengers = int(passengers)
    
    matching_flights = [
        f for f in FLIGHTS_DATA
        if f['origin'].lower() == origin.lower() and 
           f['destination'].lower() == destination.lower()
    ]
    
    if not matching_flights:
        return {
            "flights": [],
            "error": f"No flights found from {origin} to {destination}",
            "available_destinations": list(set(f['destination'] for f in FLIGHTS_DATA if f['origin'].lower() == origin.lower()))
        }
    
    # Return structured data
    results = []
    for flight in matching_flights[:5]:
        results.append({
            "id": flight['id'],
            "airline": flight['airline'],
            "price": flight['price'],
            "total_price": flight['price'] * passengers,
            "departure_time": flight['departure_time'],
            "arrival_time": flight['arrival_time'],
            "duration_hours": flight['duration_hours'],
            "class": flight['class'],
            "stops": flight['stops']
        })
    
    return {"flights": results, "passengers": passengers}


def create_flight_agent():
    """
    Create the flight specialist agent.
    
    Responsibilities:
    - Search for available flights
    - Evaluate options based on price, duration, convenience
    - Recommend the best flight
    """
    llm = get_llm()
    
    flight_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Flight Booking Specialist.
        
Your job: Find the BEST flight option for the user.

You have access to the search_flights_tool. Use it to search flights.

After searching:
1. Pick the BEST flight based on: price, duration, and convenience
2. Return a summary with: airline, price, times, and why you chose it

Be concise and specific."""),
        ("placeholder", "{messages}")
    ])
    
    agent = flight_prompt | llm.bind_tools([search_flights_tool])
    return agent

