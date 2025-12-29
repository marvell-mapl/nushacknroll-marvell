"""
Travel Agent - Complete Implementation
Multi-agent ReAct framework with LangGraph for travel planning.
Simplified hackathon architecture with 4 specialized tools.
"""

from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage
from typing import List, Literal, TypedDict, Annotated
import operator
from datetime import datetime
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Load data files once at startup
DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "flights.json", 'r', encoding='utf-8') as f:
    FLIGHTS_DATA = json.load(f)

with open(DATA_DIR / "accommodations.json", 'r', encoding='utf-8') as f:
    ACCOMMODATIONS_DATA = json.load(f)

with open(DATA_DIR / "attractions.json", 'r', encoding='utf-8') as f:
    ATTRACTIONS_DATA = json.load(f)


# ============================================
# STEP 1: DEFINE TOOLS
# ============================================

@tool
def flightsAgent(origin: str, destination: str, date: str, passengers: str = "1"):
    """
    Search for available flights. Call this when user asks about flights or air travel.
    
    Args:
        origin: Departure city (e.g., "New York", "London", "Singapore")
        destination: Arrival city (e.g., "Paris", "Tokyo", "Bali")
        date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers (default 1)
        
    Returns:
        List of available flights with prices and times
    """
    # Convert passengers to int
    passengers = int(passengers)
    
    # Search flights data
    matching_flights = [
        f for f in FLIGHTS_DATA
        if f['origin'].lower() == origin.lower() and 
           f['destination'].lower() == destination.lower()
    ]
    
    if not matching_flights:
        result = f"### ✈️ No flights found: {origin} → {destination}\n\n"
        result += "Sorry, we don't have flights for this route in our database.\n"
        result += f"Available destinations from {origin}: "
        
        # Show available destinations from this origin
        available = set(f['destination'] for f in FLIGHTS_DATA if f['origin'].lower() == origin.lower())
        result += ", ".join(sorted(available)) if available else "None"
        
        return {"messages": result}
    
    # Format flight options
    flight_options = []
    for i, flight in enumerate(matching_flights[:5], 1):  # Show up to 5 flights
        total_price = flight['price'] * passengers
        stops_text = "Direct" if flight['stops'] == 0 else f"{flight['stops']} stop(s)"
        
        flight_options.append(
            f"**Flight {i}:** {flight['airline']} ({flight['id']})\n"
            f"  💵 Price: ${total_price} ({passengers} passenger(s) × ${flight['price']})\n"
            f"  🛫 Departs: {flight['departure_time']} | 🛬 Arrives: {flight['arrival_time']}\n"
            f"  ⏱️ Duration: {flight['duration_hours']} hours | {stops_text}\n"
            f"  🎫 Class: {flight['class']}\n"
        )
    
    result = f"### ✈️ Available Flights: {origin} → {destination}\n\n"
    result += "\n".join(flight_options)
    result += f"\n\n*Showing {len(matching_flights[:5])} of {len(matching_flights)} available flights*"
    
    return {"messages": result}


@tool
def accommodationsAgent(destination: str, check_in: str, check_out: str, guests: str = "1"):
    """
    Search for hotels and accommodations. Call this when user asks about places to stay, hotels, or lodging.
    
    Args:
        destination: City or location (e.g., "Paris", "Barcelona", "Tokyo")
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        guests: Number of guests (default 1)
        
    Returns:
        List of available hotels with prices and ratings
    """
    # Convert guests to int
    guests = int(guests)
    
    # Calculate number of nights
    try:
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        if nights <= 0:
            nights = 3  # Default
    except:
        nights = 3  # Default
    
    # Search accommodations data
    matching_hotels = [
        h for h in ACCOMMODATIONS_DATA
        if h['city'].lower() == destination.lower()
    ]
    
    if not matching_hotels:
        result = f"### 🏨 No accommodations found in {destination}\n\n"
        result += "Sorry, we don't have accommodations for this city in our database.\n"
        result += "Available cities: "
        
        # Show available cities
        available = set(h['city'] for h in ACCOMMODATIONS_DATA)
        result += ", ".join(sorted(available))
        
        return {"messages": result}
    
    # Sort by rating (descending)
    matching_hotels = sorted(matching_hotels, key=lambda x: x['rating'], reverse=True)
    
    # Format hotel options
    hotel_options = []
    for i, hotel in enumerate(matching_hotels[:5], 1):  # Show up to 5 hotels
        total_price = hotel['price_per_night'] * nights
        amenities_str = ", ".join(hotel['amenities'][:4])
        if len(hotel['amenities']) > 4:
            amenities_str += f", +{len(hotel['amenities']) - 4} more"
        
        hotel_options.append(
            f"**Option {i}:** {hotel['name']} ({hotel['id']})\n"
            f"  🏢 Type: {hotel['type']} | 📍 {hotel['location']}\n"
            f"  ⭐ Rating: {hotel['rating']}/5.0\n"
            f"  💵 ${hotel['price_per_night']}/night × {nights} nights = **${total_price}**\n"
            f"  🎯 Amenities: {amenities_str}\n"
            f"  ℹ️ {hotel['description']}\n"
        )
    
    result = f"### 🏨 Accommodations in {destination}\n"
    result += f"**📅 {check_in} to {check_out}** ({nights} nights, {guests} guest(s))\n\n"
    result += "\n".join(hotel_options)
    result += f"\n\n*Showing {len(matching_hotels[:5])} of {len(matching_hotels)} available accommodations*"
    
    return {"messages": result}


@tool
def budgetAgent(flights_cost: str, hotel_cost: str, num_days: str, activities_cost: str = "0"):
    """
    Calculate total trip budget with detailed breakdown. Call this when user wants to know total cost or budget.
    
    Args:
        flights_cost: Total flight cost in dollars
        hotel_cost: Total hotel cost in dollars
        num_days: Number of days for the trip
        activities_cost: Total cost of planned activities in dollars (default 0)
        
    Returns:
        Detailed budget breakdown with total cost and analysis
    """
    # Convert to integers
    flights_cost = int(flights_cost)
    hotel_cost = int(hotel_cost)
    num_days = int(num_days)
    activities_cost = int(activities_cost)
    
    # Calculate additional costs with realistic estimates
    food_cost = num_days * 60  # Estimate $60 per day for food
    transport_cost = num_days * 30  # Estimate $30 per day for local transport
    misc_cost = int((flights_cost + hotel_cost) * 0.1)  # 10% buffer
    
    total_cost = flights_cost + hotel_cost + activities_cost + food_cost + transport_cost + misc_cost
    
    result = f"""### 💰 Complete Trip Budget Breakdown

| Category | Cost |
|----------|------|
| ✈️ **Flights** | ${flights_cost:,} |
| 🏨 **Accommodation** | ${hotel_cost:,} |
| 🎭 **Activities** | ${activities_cost:,} |
| 🍽️ **Food & Dining** | ${food_cost:,} (${food_cost // num_days}/day) |
| 🚗 **Local Transport** | ${transport_cost:,} (${transport_cost // num_days}/day) |
| 💼 **Miscellaneous** | ${misc_cost:,} (10% buffer) |
| **━━━━━━━━━━** | **━━━━━━━** |
| **💵 TOTAL** | **${total_cost:,}** |

📊 **Budget Analysis:**
- Flight costs represent {(flights_cost/total_cost*100):.1f}% of total budget
- Accommodation costs represent {(hotel_cost/total_cost*100):.1f}% of total budget
- Daily spending (food + transport + activities): ${(food_cost + transport_cost + activities_cost) // num_days}/day

*Budget calculated for {num_days} days*
"""
    
    return {"messages": result}


@tool
def itineraryAgent(destination: str, num_days: str, interests: str = "sightseeing, food, culture"):
    """
    Generate a detailed day-by-day travel itinerary. Call this when user wants a complete trip plan or daily schedule.
    
    Args:
        destination: Travel destination city
        num_days: Number of days for the trip
        interests: User's interests (e.g., "adventure, food, history", "beaches, relaxation", "museums, culture")
        
    Returns:
        Formatted day-by-day itinerary with activities
    """
    # Convert num_days to int
    num_days = int(num_days)
    
    # Get attractions for destination
    attractions = [
        a for a in ATTRACTIONS_DATA
        if a['city'].lower() == destination.lower()
    ]
    
    if not attractions:
        result = f"### 📋 No attractions found for {destination}\n\n"
        result += "Sorry, we don't have attraction data for this city.\n"
        result += "Available cities with attractions: "
        
        available = set(a['city'] for a in ATTRACTIONS_DATA)
        result += ", ".join(sorted(available))
        
        return {"messages": result}
    
    result = f"### 📋 Your {num_days}-Day {destination} Itinerary\n"
    result += f"**Interests:** {interests}\n\n"
    
    # Distribute attractions across days
    attractions_per_day = max(1, len(attractions) // num_days)
    attraction_index = 0
    total_cost = 0
    
    for day in range(1, num_days + 1):
        result += f"#### 🗓️ Day {day}\n\n"
        
        # Select attractions for this day
        day_attractions = attractions[attraction_index:attraction_index + min(3, len(attractions) - attraction_index)]
        
        if not day_attractions:
            # Cycle back if we run out
            day_attractions = attractions[:min(3, len(attractions))]
        
        for attraction in day_attractions:
            emoji_map = {
                "Culture": "🏛️",
                "Landmark": "🗼",
                "Food": "🍜",
                "Nature": "🌳",
                "Shopping": "🛍️"
            }
            emoji = emoji_map.get(attraction['category'], "📍")
            
            cost_text = "Free" if attraction['cost'] == 0 else f"${attraction['cost']}"
            
            result += f"- **{emoji} {attraction['name']}** ({attraction['category']})\n"
            result += f"  ⏱️ Duration: {attraction['duration_hours']} hours | 💵 Cost: {cost_text}\n"
            result += f"  ℹ️ {attraction['description']}\n\n"
            
            total_cost += attraction['cost']
            attraction_index += 1
        
        result += "\n"
    
    result += f"**💰 Total Activities Cost: ${total_cost}**\n\n"
    result += "*💡 This itinerary can be customized based on your preferences and pace.*"
    
    return {"messages": result}


# ============================================
# STEP 2: SETUP LLM
# ============================================

def set_up_llm(temperature=0, max_tokens=5000):
    """Initialize Groq LLM with configuration."""
    llm = ChatGroq(
        model="llama-3.1-70b-versatile",  # Best for complex reasoning
        temperature=temperature,
        max_tokens=max_tokens,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    return llm


def set_up_agent(tools: List, prompt_template):
    """Bind tools to LLM and create chain with prompt."""
    llm = set_up_llm(temperature=0)
    llm_w_tools = llm.bind_tools(tools)
    chain = prompt_template | llm_w_tools
    return chain


# ============================================
# STEP 3: CREATE SUPERVISOR PROMPT
# ============================================

travel_supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""
You are TravelBot, an expert AI Travel Assistant helping users plan their perfect trip.
Today's date is {datetime.now().strftime("%Y-%m-%d")}.

You have access to these specialized tools:
1. **flightsAgent** - Search for flights (requires: origin, destination, date, passengers)
2. **accommodationsAgent** - Search for hotels (requires: destination, check_in, check_out, guests)
3. **budgetAgent** - Calculate trip budget (requires: flights_cost, hotel_cost, num_days)
4. **itineraryAgent** - Generate day-by-day plan (requires: destination, num_days, interests)

**Tool-routing rules (ReAct Framework):**
- If user mentions flights/airlines/flying → call flightsAgent
- If user mentions hotels/accommodation/where to stay → call accommodationsAgent
- If user asks about cost/budget/price/total → call budgetAgent (must have flight & hotel costs first)
- If user wants a complete plan/itinerary/schedule/daily activities → call itineraryAgent

**Important guidelines:**
- Ask for missing information (dates, destination, number of travelers) conversationally
- Present options clearly and help users make decisions
- Be friendly, enthusiastic, and conversational (use emojis occasionally)
- After calling tools, summarize the results and offer next steps
- For complete trip planning, call tools in sequence: flights → accommodation → itinerary → budget
- Use actual data from tools - never make up prices or availability

**Example conversational flow:**
User: "I want to visit Tokyo"
You: "Tokyo is an amazing destination! 🗼 When are you planning to travel? And for how many days?"

User: "Maybe in March, for about 4 days"
You: [Call flightsAgent, then accommodationsAgent, then itineraryAgent, then budgetAgent]
Then provide a complete summary and ask if they'd like to adjust anything.

**Communication style:**
- Warm and helpful, like talking to a knowledgeable friend
- Use natural language, not robotic
- Show enthusiasm about their destination
- Provide context and tips along with data
    """),
    ("placeholder", "{messages}")
])

# Create the agent by binding tools
travel_supervisor_agent = set_up_agent(
    tools=[flightsAgent, accommodationsAgent, budgetAgent, itineraryAgent],
    prompt_template=travel_supervisor_prompt
)


# ============================================
# STEP 4: BUILD LANGGRAPH STATE MACHINE
# ============================================

class TravelState(TypedDict):
    """State object passed between nodes in the graph."""
    messages: Annotated[List[BaseMessage], operator.add]  # Conversation history
    tools_called: List  # Track which tools were invoked


def invoke_travel_supervisor(state: TravelState):
    """
    Node: Invoke the supervisor agent to decide next action.
    This is the "Reasoning" step in the ReAct framework.
    """
    # Pass messages as a dict for ChatPromptTemplate
    result = travel_supervisor_agent.invoke({"messages": state['messages']})
    state['messages'].append(AIMessage(content=result.content, tool_calls=result.tool_calls))
    state['tools_called'].append("invoke_travel_supervisor")
    return state


def travel_tool_node(state: TravelState):
    """
    Node: Execute travel-related tools.
    This is the "Acting" step in the ReAct framework.
    """
    tools_by_name = {
        "flightsAgent": flightsAgent,
        "accommodationsAgent": accommodationsAgent,
        "budgetAgent": budgetAgent,
        "itineraryAgent": itineraryAgent
    }
    
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        print(f"🔧 Running tool: {tool_call['name']}")
        
        # Execute tool
        observation = tool.invoke(tool_call["args"])
        
        # Add tool result to conversation
        state['messages'].append(ToolMessage(
            content=observation["messages"],
            name=tool_call["name"],
            tool_call_id=tool_call["id"]
        ))
        state['tools_called'].append(tool_call["name"])
    
    return state


def should_continue_travel(state: TravelState) -> Literal["Action", END]:
    """
    Edge: Decide whether to continue the ReAct loop or end.
    This implements the "Observation" step - evaluating if more actions are needed.
    """
    last_message = state["messages"][-1]
    
    # Continue if LLM requested more tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "Action"
    
    # End if no more actions needed
    return END


def build_travel_agent():
    """
    Build the complete LangGraph travel agent with ReAct loop.
    
    Flow:
    START → invoke_supervisor → should_continue? → [Action: tool_node → loop back] or [END]
    """
    agent_builder = StateGraph(TravelState)
    
    # Add nodes
    agent_builder.add_node('travel_tool_node', travel_tool_node)
    agent_builder.add_node('invoke_travel_supervisor', invoke_travel_supervisor)
    
    # Set entry point
    agent_builder.set_entry_point("invoke_travel_supervisor")
    
    # Conditional edge: continue to tools or end
    agent_builder.add_conditional_edges(
        "invoke_travel_supervisor",
        should_continue_travel,
        {
            "Action": "travel_tool_node",  # Execute tools
            END: END,                       # Finish conversation
        },
    )
    
    # Loop back to supervisor after tools execute
    agent_builder.add_edge("travel_tool_node", "invoke_travel_supervisor")
    
    # Compile and return
    agent = agent_builder.compile()
    return agent


# ============================================
# TESTING (if running directly)
# ============================================

if __name__ == "__main__":
    print("🚀 Building travel agent...")
    agent = build_travel_agent()
    
    print("✅ Agent built successfully!")
    print("\nTo use the agent, run: streamlit run app.py")

