"""
Flight Agent - LLM-Powered Specialist with Multiple Tools

This agent has its own LLM and can use multiple internal tools to:
- Search flights by different criteria
- Filter by preferences
- Compare options
- Make intelligent recommendations
"""

from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage
from constants import get_llm, FLIGHTS_DATA


# ============================================
# INTERNAL TOOLS (Available to flight agent)
# ============================================

@tool
def search_flights_by_price(origin: str, destination: str, passengers: str = "1"):
    """Search flights sorted by price (cheapest first).
    
    Use this when user wants the most affordable options.
    
    Args:
        origin: Departure city
        destination: Arrival city
        passengers: Number of passengers
        
    Returns:
        dict: Flights sorted by price
    """
    passengers = int(passengers)
    
    matching_flights = [
        f for f in FLIGHTS_DATA
        if f['origin'].lower() == origin.lower() and 
           f['destination'].lower() == destination.lower()
    ]
    
    if not matching_flights:
        return {"flights": [], "error": f"No flights found"}
    
    # Sort by price
    sorted_flights = sorted(matching_flights, key=lambda x: x['price'])
    
    results = []
    for flight in sorted_flights[:5]:
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
    
    return {"flights": results, "sort_by": "price"}


@tool
def search_flights_by_duration(origin: str, destination: str, passengers: str = "1"):
    """Search flights sorted by duration (fastest first).
    
    Use this when user wants the quickest journey.
    
    Args:
        origin: Departure city
        destination: Arrival city
        passengers: Number of passengers
        
    Returns:
        dict: Flights sorted by duration
    """
    passengers = int(passengers)
    
    matching_flights = [
        f for f in FLIGHTS_DATA
        if f['origin'].lower() == origin.lower() and 
           f['destination'].lower() == destination.lower()
    ]
    
    if not matching_flights:
        return {"flights": [], "error": f"No flights found"}
    
    # Sort by duration
    sorted_flights = sorted(matching_flights, key=lambda x: x['duration_hours'])
    
    results = []
    for flight in sorted_flights[:5]:
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
    
    return {"flights": results, "sort_by": "duration"}


@tool
def filter_direct_flights(origin: str, destination: str, passengers: str = "1"):
    """Search for direct flights only (no stops).
    
    Use this when user wants non-stop flights.
    
    Args:
        origin: Departure city
        destination: Arrival city
        passengers: Number of passengers
        
    Returns:
        dict: Direct flights only
    """
    passengers = int(passengers)
    
    matching_flights = [
        f for f in FLIGHTS_DATA
        if f['origin'].lower() == origin.lower() and 
           f['destination'].lower() == destination.lower() and
           f['stops'] == 0
    ]
    
    if not matching_flights:
        return {"flights": [], "error": f"No direct flights available"}
    
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
    
    return {"flights": results, "filter": "direct_only"}


@tool
def filter_by_class(origin: str, destination: str, travel_class: str, passengers: str = "1"):
    """Filter flights by class (Economy, Business, First).
    
    Use this when user has a class preference.
    
    Args:
        origin: Departure city
        destination: Arrival city
        travel_class: Desired class (Economy, Business, First)
        passengers: Number of passengers
        
    Returns:
        dict: Flights matching the specified class
    """
    passengers = int(passengers)
    
    matching_flights = [
        f for f in FLIGHTS_DATA
        if f['origin'].lower() == origin.lower() and 
           f['destination'].lower() == destination.lower() and
           f['class'].lower() == travel_class.lower()
    ]
    
    if not matching_flights:
        return {"flights": [], "error": f"No {travel_class} flights available"}
    
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
    
    return {"flights": results, "filter": f"{travel_class}_class"}


# ============================================
# FLIGHT AGENT (Exposed to supervisor as tool)
# ============================================

@tool
def flight_agent(origin: str, destination: str, date: str, passengers: str = "1", preferences: str = "balanced"):
    """AI-powered flight booking specialist with intelligent search.
    
    Uses multiple search strategies and AI reasoning to find the best flight.
    
    Use this agent when you need to find flights for the user.
    
    Args:
        origin: Departure city (e.g., 'Singapore', 'New York')
        destination: Arrival city (e.g., 'Paris', 'Tokyo')
        date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers (default: '1')
        preferences: User preference - 'cheapest', 'fastest', 'direct', 'balanced', 'business'
        
    Returns:
        str: AI-generated flight recommendation with reasoning
    """
    # Create sub-agent with its own LLM
    llm = get_llm()
    
    # Define internal tools this agent can use
    flight_tools = [
        search_flights_by_price,
        search_flights_by_duration,
        filter_direct_flights,
        filter_by_class
    ]
    
    # Agent's system prompt
    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert Flight Booking Specialist with intelligent search capabilities.

Your internal tools:
- search_flights_by_price: Find cheapest flights
- search_flights_by_duration: Find fastest flights
- filter_direct_flights: Find non-stop flights only
- filter_by_class: Filter by Economy/Business/First class

User preference: {preferences}

Your strategy based on preference:
- 'cheapest': Use search_flights_by_price
- 'fastest': Use search_flights_by_duration
- 'direct': Use filter_direct_flights
- 'business' or 'first': Use filter_by_class with appropriate class
- 'balanced': Use search_flights_by_price, then pick best overall value

Process:
1. Choose the RIGHT tool(s) based on user preference
2. Analyze the results
3. Pick the BEST option with clear reasoning
4. Format as a professional recommendation

Be smart about tool selection - don't call unnecessary tools!"""),
        ("placeholder", "{messages}")
    ])
    
    # Bind tools to agent's LLM
    agent = agent_prompt | llm.bind_tools(flight_tools)
    
    # Create the agent's task
    task = HumanMessage(
        content=f"""Find the best flight from {origin} to {destination} on {date} for {passengers} passenger(s).

User preference: {preferences}

Use your tools wisely to find the optimal flight."""
    )
    
    # Execute agent's ReAct loop
    messages = [task]
    max_iterations = 5
    
    for iteration in range(max_iterations):
        # Agent reasons and decides which tool(s) to call
        result = agent.invoke({"messages": messages})
        messages.append(result)
        
        # Check if agent is done (no more tool calls)
        if not hasattr(result, 'tool_calls') or not result.tool_calls:
            break
        
        # Execute all tool calls
        for tool_call in result.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            # Map tool names to functions
            tool_map = {
                "search_flights_by_price": search_flights_by_price,
                "search_flights_by_duration": search_flights_by_duration,
                "filter_direct_flights": filter_direct_flights,
                "filter_by_class": filter_by_class
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
    final_response = messages[-1].content if messages else "No flights found"
    
    return final_response

