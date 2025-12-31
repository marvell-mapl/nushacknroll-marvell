"""
Accommodation Agent - LLM-Powered Specialist with Multiple Tools

This agent has its own LLM and can use multiple internal tools to:
- Search by rating
- Search by price
- Filter by hotel type
- Filter by amenities
- Make intelligent recommendations
"""

from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage
from datetime import datetime
from constants import get_llm, ACCOMMODATIONS_DATA


# ============================================
# HELPER FUNCTION
# ============================================

def _calculate_nights(check_in: str, check_out: str) -> int:
    """Calculate number of nights between dates."""
    try:
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        return nights if nights > 0 else 3
    except:
        return 3


# ============================================
# INTERNAL TOOLS (Available to accommodation agent)
# ============================================

@tool
def search_hotels_by_rating(destination: str, check_in: str, check_out: str, guests: str = "1"):
    """Search hotels sorted by rating (highest rated first).
    
    Use this when user wants the best quality accommodations.
    
    Args:
        destination: City to search in
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        guests: Number of guests
        
    Returns:
        dict: Hotels sorted by rating
    """
    nights = _calculate_nights(check_in, check_out)
    
    matching_hotels = [
        h for h in ACCOMMODATIONS_DATA
        if h['city'].lower() == destination.lower()
    ]
    
    if not matching_hotels:
        return {"hotels": [], "error": "No hotels found"}
    
    # Sort by rating (highest first)
    sorted_hotels = sorted(matching_hotels, key=lambda x: x['rating'], reverse=True)
    
    results = []
    for hotel in sorted_hotels[:5]:
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
    
    return {"hotels": results, "nights": nights, "sort_by": "rating"}


@tool
def search_hotels_by_price(destination: str, check_in: str, check_out: str, guests: str = "1"):
    """Search hotels sorted by price (cheapest first).
    
    Use this when user wants budget-friendly options.
    
    Args:
        destination: City to search in
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        guests: Number of guests
        
    Returns:
        dict: Hotels sorted by price
    """
    nights = _calculate_nights(check_in, check_out)
    
    matching_hotels = [
        h for h in ACCOMMODATIONS_DATA
        if h['city'].lower() == destination.lower()
    ]
    
    if not matching_hotels:
        return {"hotels": [], "error": "No hotels found"}
    
    # Sort by price (cheapest first)
    sorted_hotels = sorted(matching_hotels, key=lambda x: x['price_per_night'])
    
    results = []
    for hotel in sorted_hotels[:5]:
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
    
    return {"hotels": results, "nights": nights, "sort_by": "price"}


@tool
def filter_by_hotel_type(destination: str, hotel_type: str, check_in: str, check_out: str, guests: str = "1"):
    """Filter hotels by type (Hotel, Resort, Boutique, Hostel, Apartment).
    
    Use this when user specifies a preferred accommodation type.
    
    Args:
        destination: City to search in
        hotel_type: Type of accommodation (Hotel, Resort, Boutique, Hostel, Apartment)
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        guests: Number of guests
        
    Returns:
        dict: Hotels matching the specified type
    """
    nights = _calculate_nights(check_in, check_out)
    
    matching_hotels = [
        h for h in ACCOMMODATIONS_DATA
        if h['city'].lower() == destination.lower() and
           h['type'].lower() == hotel_type.lower()
    ]
    
    if not matching_hotels:
        return {"hotels": [], "error": f"No {hotel_type} accommodations found"}
    
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
    
    return {"hotels": results, "nights": nights, "filter": f"{hotel_type}_type"}


@tool
def filter_by_amenities(destination: str, required_amenities: str, check_in: str, check_out: str, guests: str = "1"):
    """Filter hotels by required amenities.
    
    Use this when user needs specific amenities (e.g., "WiFi, Pool").
    
    Args:
        destination: City to search in
        required_amenities: Comma-separated amenities (e.g., "WiFi, Pool, Gym")
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        guests: Number of guests
        
    Returns:
        dict: Hotels with all required amenities
    """
    nights = _calculate_nights(check_in, check_out)
    required = [a.strip().lower() for a in required_amenities.split(',')]
    
    matching_hotels = [
        h for h in ACCOMMODATIONS_DATA
        if h['city'].lower() == destination.lower() and
           all(any(req in amenity.lower() for amenity in h['amenities']) for req in required)
    ]
    
    if not matching_hotels:
        return {"hotels": [], "error": f"No hotels with {required_amenities}"}
    
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
    
    return {"hotels": results, "nights": nights, "filter": f"amenities_{required_amenities}"}


# ============================================
# ACCOMMODATION AGENT (Exposed to supervisor as tool)
# ============================================

@tool
def accommodation_agent(destination: str, check_in: str, check_out: str, guests: str = "1", preferences: str = "balanced"):
    """AI-powered hotel booking specialist with intelligent search.
    
    Uses multiple search strategies and AI reasoning to find the best accommodation.
    
    Use this agent when you need to find hotels/accommodations for the user.
    
    Args:
        destination: City to search in (e.g., 'Paris', 'Tokyo', 'New York')
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        guests: Number of guests (default: '1')
        preferences: User preference - 'cheapest', 'luxury', 'resort', 'boutique', 'balanced', or amenities like 'pool,gym'
        
    Returns:
        str: AI-generated hotel recommendation with reasoning
    """
    # Create sub-agent with its own LLM
    llm = get_llm()
    
    # Define internal tools this agent can use
    hotel_tools = [
        search_hotels_by_rating,
        search_hotels_by_price,
        filter_by_hotel_type,
        filter_by_amenities
    ]
    
    # Agent's system prompt
    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert Hotel Booking Specialist with intelligent search capabilities.

Your internal tools:
- search_hotels_by_rating: Find highest rated hotels
- search_hotels_by_price: Find cheapest hotels
- filter_by_hotel_type: Filter by type (Hotel, Resort, Boutique, Hostel, Apartment)
- filter_by_amenities: Filter by amenities (WiFi, Pool, Gym, etc.)

User preference: {preferences}

Your strategy based on preference:
- 'cheapest': Use search_hotels_by_price
- 'luxury': Use search_hotels_by_rating
- 'resort', 'boutique', 'hotel': Use filter_by_hotel_type
- If mentions amenities (pool, gym, etc.): Use filter_by_amenities
- 'balanced': Use search_hotels_by_rating, then pick best value

Process:
1. Choose the RIGHT tool(s) based on user preference
2. Analyze the results
3. Pick the BEST option with clear reasoning
4. Format as a professional recommendation

Be smart about tool selection!"""),
        ("placeholder", "{messages}")
    ])
    
    # Bind tools to agent's LLM
    agent = agent_prompt | llm.bind_tools(hotel_tools)
    
    # Create the agent's task
    task = HumanMessage(
        content=f"""Find the best hotel in {destination} from {check_in} to {check_out} for {guests} guest(s).

User preference: {preferences}

Use your tools wisely to find the optimal accommodation."""
    )
    
    # Execute agent's ReAct loop
    messages = [task]
    max_iterations = 5
    
    for iteration in range(max_iterations):
        # Agent reasons and decides which tool(s) to call
        result = agent.invoke({"messages": messages})
        messages.append(result)
        
        # Check if agent is done
        if not hasattr(result, 'tool_calls') or not result.tool_calls:
            break
        
        # Execute all tool calls
        for tool_call in result.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            # Map tool names to functions
            tool_map = {
                "search_hotels_by_rating": search_hotels_by_rating,
                "search_hotels_by_price": search_hotels_by_price,
                "filter_by_hotel_type": filter_by_hotel_type,
                "filter_by_amenities": filter_by_amenities
            }
            
            if tool_name in tool_map:
                tool_result = tool_map[tool_name].invoke(tool_args)
                
                # Add tool result to conversation
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call['id'],
                        name=tool_name
                    )
                )
    
    # Get the agent's final recommendation
    final_response = messages[-1].content if messages else "No hotels found"
    
    return final_response

