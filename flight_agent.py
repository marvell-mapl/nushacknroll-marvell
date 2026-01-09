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
5. If the user's preference does not match or cannot be found, always notify the user.

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
    
    print(f"  💭 Flight Agent starting ReAct loop (max {max_iterations} iterations)...")
    
    for iteration in range(max_iterations):
        print(f"\n  🔄 Iteration {iteration + 1}: Reasoning...")
        
        # Agent reasons and decides which tool(s) to call
        result = agent.invoke({"messages": messages})
        messages.append(result)
        
        # Check if agent is done (no more tool calls)
        if not hasattr(result, 'tool_calls') or not result.tool_calls:
            print(f"  ✅ Flight Agent finished reasoning - no more tools needed")
            break
        
        # Execute all tool calls
        print(f"  📞 Flight Agent decided to call {len(result.tool_calls)} internal tool(s):")
        for tool_call in result.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            print(f"     🔨 Calling: {tool_name}")
            print(f"        Args: {tool_args}")
            
            # Map tool names to functions
            tool_map = {
                "search_flights_by_price": search_flights_by_price,
                "search_flights_by_duration": search_flights_by_duration,
                "filter_direct_flights": filter_direct_flights,
                "filter_by_class": filter_by_class
            }
            
            if tool_name in tool_map:
                tool_result = tool_map[tool_name].invoke(tool_args)
                print(f"     ✓ {tool_name} returned results: {tool_result}")
                
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
