"""
Budget Agent - Specialist for calculating trip costs.
"""

from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from constants import get_llm


@tool
def calculate_budget_tool(flights_cost: str, hotel_cost: str, num_days: str, activities_cost: str = "0"):
    """
    Calculate total trip budget breakdown.
    
    Args:
        flights_cost: Total flight cost
        hotel_cost: Total hotel cost
        num_days: Number of days
        activities_cost: Total activities cost
        
    Returns:
        Complete budget breakdown
    """
    flights_cost = int(flights_cost)
    hotel_cost = int(hotel_cost)
    num_days = int(num_days)
    activities_cost = int(activities_cost)
    
    food_cost = num_days * 60
    transport_cost = num_days * 30
    misc_cost = int((flights_cost + hotel_cost) * 0.1)
    
    total_cost = flights_cost + hotel_cost + activities_cost + food_cost + transport_cost + misc_cost
    
    return {
        "flights": flights_cost,
        "accommodation": hotel_cost,
        "activities": activities_cost,
        "food": food_cost,
        "transport": transport_cost,
        "miscellaneous": misc_cost,
        "total": total_cost,
        "num_days": num_days
    }


def create_budget_agent():
    """
    Create the budget specialist agent.
    
    Responsibilities:
    - Calculate total trip costs
    - Provide detailed breakdown
    - Check against user's budget if provided
    """
    llm = get_llm()
    
    budget_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Budget Planning Specialist.

Your job: Calculate total trip costs.

You have access to the calculate_budget_tool. Use it with the costs provided.

After calculating:
1. Show the complete breakdown
2. Highlight the total cost
3. If a budget was mentioned, check if we're within it

Be clear about the numbers."""),
        ("placeholder", "{messages}")
    ])
    
    agent = budget_prompt | llm.bind_tools([calculate_budget_tool])
    return agent

