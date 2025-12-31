"""
Itinerary Agent - LLM-Powered Specialist with Multiple Tools

This agent has its own LLM and can use multiple internal tools to:
- Filter by category/interest
- Search top-rated attractions
- Find free/budget activities
- Create intelligent day-by-day plans
"""

from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage
from constants import get_llm, ATTRACTIONS_DATA


# ============================================
# INTERNAL TOOLS (Available to itinerary agent)
# ============================================

@tool
def search_all_attractions(destination: str):
    """Get all attractions for a destination.
    
    Use this to see what's available before filtering.
    
    Args:
        destination: City name
        
    Returns:
        dict: All attractions in the city
    """
    attractions = [
        a for a in ATTRACTIONS_DATA
        if a['city'].lower() == destination.lower()
    ]
    
    if not attractions:
        return {"attractions": [], "error": f"No attractions found for {destination}"}
    
    return {"attractions": attractions, "count": len(attractions)}


@tool
def filter_by_category(destination: str, category: str):
    """Filter attractions by category.
    
    Use this to match user interests to specific categories.
    
    Args:
        destination: City name
        category: Category (Culture, Landmark, Food, Nature, Shopping, Entertainment, Adventure, Wellness)
        
    Returns:
        dict: Attractions in the specified category
    """
    attractions = [
        a for a in ATTRACTIONS_DATA
        if a['city'].lower() == destination.lower() and
           a['category'].lower() == category.lower()
    ]
    
    return {"attractions": attractions, "category": category, "count": len(attractions)}


@tool
def search_top_rated(destination: str, min_rating: str = "4.0"):
    """Search for top-rated attractions.
    
    Use this when user wants the best experiences.
    
    Args:
        destination: City name
        min_rating: Minimum rating (default: "4.0")
        
    Returns:
        dict: Highly-rated attractions
    """
    min_rating = float(min_rating)
    
    attractions = [
        a for a in ATTRACTIONS_DATA
        if a['city'].lower() == destination.lower()
    ]
    
    # Filter and sort by rating (if rating field exists)
    top_attractions = sorted(attractions, key=lambda x: x.get('duration_hours', 0), reverse=True)[:10]
    
    return {"attractions": top_attractions, "min_rating": min_rating}


@tool
def filter_free_attractions(destination: str):
    """Find free or budget-friendly attractions.
    
    Use this for budget-conscious travelers.
    
    Args:
        destination: City name
        
    Returns:
        dict: Free or low-cost attractions
    """
    attractions = [
        a for a in ATTRACTIONS_DATA
        if a['city'].lower() == destination.lower() and
           a['cost'] <= 20  # Free or under $20
    ]
    
    return {"attractions": attractions, "max_cost": 20}


# ============================================
# ITINERARY AGENT (Exposed to supervisor as tool)
# ============================================

@tool
def itinerary_agent(destination: str, num_days: str, interests: str = "sightseeing, food, culture"):
    """AI-powered itinerary planner with intelligent activity selection.
    
    Creates personalized day-by-day plans based on user interests.
    
    Use this agent when you need to plan a daily schedule for the trip.
    
    Args:
        destination: City to plan itinerary for (e.g., 'Paris', 'Tokyo')
        num_days: Number of days for the trip
        interests: User's interests (e.g., 'food, culture, adventure')
        
    Returns:
        str: AI-generated day-by-day itinerary
    """
    # Create sub-agent with its own LLM
    llm = get_llm()
    
    # Define internal tools
    itinerary_tools = [
        search_all_attractions,
        filter_by_category,
        search_top_rated,
        filter_free_attractions
    ]
    
    # Agent's system prompt
    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert Itinerary Planning Specialist.

Your internal tools:
- search_all_attractions: Get all available attractions
- filter_by_category: Filter by category (Culture, Landmark, Food, Nature, Shopping, Entertainment, Adventure, Wellness)
- search_top_rated: Find top-rated experiences
- filter_free_attractions: Find budget-friendly options

User interests: {interests}
Trip duration: {num_days} days

Your strategy:
1. Identify categories that match user interests
2. Use appropriate filters to get relevant attractions
3. Select 2-3 activities per day (don't overpack!)
4. Balance different types of activities
5. Consider free options if budget is mentioned
6. Create a logical day-by-day flow

Format your output as:
📅 {num_days}-DAY ITINERARY FOR [DESTINATION]

Day 1:
  [emoji] Activity Name (Category)
     Duration | Cost
     Brief description

Day 2:
  ...

Total Activities Cost: $XXX"""),
        ("placeholder", "{messages}")
    ])
    
    # Bind tools
    agent = agent_prompt | llm.bind_tools(itinerary_tools)
    
    # Create task
    task = HumanMessage(
        content=f"""Create a {num_days}-day itinerary for {destination}.

User interests: {interests}

Use your tools to find the best activities and create a balanced daily schedule."""
    )
    
    # Execute ReAct loop
    messages = [task]
    max_iterations = 8
    
    for iteration in range(max_iterations):
        result = agent.invoke({"messages": messages})
        messages.append(result)
        
        if not hasattr(result, 'tool_calls') or not result.tool_calls:
            break
        
        for tool_call in result.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            tool_map = {
                "search_all_attractions": search_all_attractions,
                "filter_by_category": filter_by_category,
                "search_top_rated": search_top_rated,
                "filter_free_attractions": filter_free_attractions
            }
            
            if tool_name in tool_map:
                tool_result = tool_map[tool_name].invoke(tool_args)
                
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call['id'],
                        name=tool_name
                    )
                )
    
    final_response = messages[-1].content if messages else "No itinerary created"
    
    return final_response
