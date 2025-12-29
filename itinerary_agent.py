"""
Itinerary Agent - Specialist for creating day-by-day travel plans.
"""

from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from constants import get_llm, ATTRACTIONS_DATA


@tool
def get_attractions_tool(destination: str, num_days: str):
    """
    Get attractions and activities for a destination.
    
    Args:
        destination: City to get attractions for
        num_days: Number of days for the trip
        
    Returns:
        List of attractions with details
    """
    num_days = int(num_days)
    
    attractions = [
        a for a in ATTRACTIONS_DATA
        if a['city'].lower() == destination.lower()
    ]
    
    if not attractions:
        return {
            "attractions": [],
            "error": f"No attractions found for {destination}",
            "available_cities": list(set(a['city'] for a in ATTRACTIONS_DATA))
        }
    
    return {"attractions": attractions, "num_days": num_days}


def create_itinerary_agent():
    """
    Create the itinerary specialist agent.
    
    Responsibilities:
    - Get available attractions for destination
    - Create balanced day-by-day schedule
    - Distribute activities appropriately across days
    """
    llm = get_llm()
    
    itinerary_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an Itinerary Planning Specialist.

Your job: Create a day-by-day itinerary.

You have access to the get_attractions_tool. Use it to get attractions.

After getting attractions:
1. Distribute them across the days
2. Create a balanced schedule (2-3 activities per day)
3. Return a day-by-day plan with activity names, costs, and durations

Be specific and organized."""),
        ("placeholder", "{messages}")
    ])
    
    agent = itinerary_prompt | llm.bind_tools([get_attractions_tool])
    return agent

