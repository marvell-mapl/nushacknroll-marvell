"""
Accommodation Agent - Specialist for finding and recommending hotels.
"""

from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from datetime import datetime
from constants import get_llm, ACCOMMODATIONS_DATA


@tool
def search_hotels_tool(destination: str, check_in: str, check_out: str, guests: str = "1"):
    """
    Search accommodations database for available hotels.
    
    Args:
        destination: City to search in
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        guests: Number of guests
        
    Returns:
        List of available accommodations with details
    """
    guests = int(guests)
    
    # Calculate nights
    try:
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        if nights <= 0:
            nights = 3
    except:
        nights = 3
    
    matching_hotels = [
        h for h in ACCOMMODATIONS_DATA
        if h['city'].lower() == destination.lower()
    ]
    
    if not matching_hotels:
        return {
            "hotels": [],
            "error": f"No hotels found in {destination}",
            "available_cities": list(set(h['city'] for h in ACCOMMODATIONS_DATA))
        }
    
    # Sort by rating
    matching_hotels = sorted(matching_hotels, key=lambda x: x['rating'], reverse=True)
    
    results = []
    for hotel in matching_hotels[:5]:
        results.append({
            "id": hotel['id'],
            "name": hotel['name'],
            "type": hotel['type'],
            "price_per_night": hotel['price_per_night'],
            "total_price": hotel['price_per_night'] * nights,
            "rating": hotel['rating'],
            "location": hotel['location'],
            "amenities": hotel['amenities'],
            "description": hotel['description']
        })
    
    return {"hotels": results, "nights": nights, "guests": guests}


def create_accommodation_agent():
    """
    Create the accommodation specialist agent.
    
    Responsibilities:
    - Search for available hotels
    - Evaluate options based on rating, location, price, amenities
    - Recommend the best hotel
    """
    llm = get_llm()
    
    accommodation_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an Accommodation Booking Specialist.

Your job: Find the BEST hotel for the user.

You have access to the search_hotels_tool. Use it to search hotels.

After searching:
1. Pick the BEST hotel based on: rating, location, price, and amenities
2. Return a summary with: name, price, rating, and why you chose it

Be concise and specific."""),
        ("placeholder", "{messages}")
    ])
    
    agent = accommodation_prompt | llm.bind_tools([search_hotels_tool])
    return agent

