"""
Multi-Agent Travel Planner - Main orchestration.
Brings together all specialist agents into a coordinated system.
"""

from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from typing import List, TypedDict, Annotated
import operator

from flight_agent import create_flight_agent, search_flights_tool
from accommodation_agent import create_accommodation_agent, search_hotels_tool
from itinerary_agent import create_itinerary_agent, get_attractions_tool
from budget_agent import create_budget_agent, calculate_budget_tool
from supervisor import create_supervisor


# ============================================
# STATE DEFINITION
# ============================================

class TravelState(TypedDict):
    """State passed between agents in the workflow."""
    messages: Annotated[List, operator.add]
    next_agent: str  # Which agent to call next
    flight_info: dict  # Store flight selection
    hotel_info: dict  # Store hotel selection
    itinerary_info: dict  # Store itinerary
    budget_info: dict  # Store budget


# ============================================
# GRAPH NODES
# ============================================

def supervisor_node(state: TravelState):
    """Supervisor decides which agent to call next."""
    supervisor = create_supervisor()
    result = supervisor.invoke({"messages": state['messages']})
    
    # Extract which agent to call from response
    content = result.content.lower()
    
    if "flight_agent" in content:
        next_agent = "flight_agent"
    elif "accommodation_agent" in content:
        next_agent = "accommodation_agent"
    elif "itinerary_agent" in content:
        next_agent = "itinerary_agent"
    elif "budget_agent" in content:
        next_agent = "budget_agent"
    elif "finish" in content:
        next_agent = "FINISH"
    else:
        # Default flow
        if not state.get('flight_info'):
            next_agent = "flight_agent"
        elif not state.get('hotel_info'):
            next_agent = "accommodation_agent"
        elif not state.get('itinerary_info'):
            next_agent = "itinerary_agent"
        elif not state.get('budget_info'):
            next_agent = "budget_agent"
        else:
            next_agent = "FINISH"
    
    return {**state, "next_agent": next_agent, "messages": [result]}


def flight_agent_node(state: TravelState):
    """Flight agent searches and recommends flights."""
    agent = create_flight_agent()
    
    # Create task for flight agent
    task_msg = HumanMessage(content="Search for flights and recommend the best option.")
    
    # Agent reasons and calls tool
    result = agent.invoke({"messages": state['messages'] + [task_msg]})
    
    # If tool call, execute it
    if hasattr(result, 'tool_calls') and result.tool_calls:
        tool_call = result.tool_calls[0]
        tool_result = search_flights_tool.invoke(tool_call['args'])
        
        # Store in state
        return {
            **state,
            "flight_info": tool_result,
            "messages": [
                AIMessage(content=f"Flight agent found {len(tool_result.get('flights', []))} options", tool_calls=result.tool_calls),
                ToolMessage(content=str(tool_result), tool_call_id=tool_call['id'], name="search_flights_tool")
            ]
        }
    
    return {**state, "messages": [result]}


def accommodation_agent_node(state: TravelState):
    """Accommodation agent searches and recommends hotels."""
    agent = create_accommodation_agent()
    
    task_msg = HumanMessage(content="Search for accommodations and recommend the best option.")
    
    result = agent.invoke({"messages": state['messages'] + [task_msg]})
    
    if hasattr(result, 'tool_calls') and result.tool_calls:
        tool_call = result.tool_calls[0]
        tool_result = search_hotels_tool.invoke(tool_call['args'])
        
        return {
            **state,
            "hotel_info": tool_result,
            "messages": [
                AIMessage(content=f"Accommodation agent found {len(tool_result.get('hotels', []))} options", tool_calls=result.tool_calls),
                ToolMessage(content=str(tool_result), tool_call_id=tool_call['id'], name="search_hotels_tool")
            ]
        }
    
    return {**state, "messages": [result]}


def itinerary_agent_node(state: TravelState):
    """Itinerary agent creates day-by-day plan."""
    agent = create_itinerary_agent()
    
    task_msg = HumanMessage(content="Create a day-by-day itinerary with activities.")
    
    result = agent.invoke({"messages": state['messages'] + [task_msg]})
    
    if hasattr(result, 'tool_calls') and result.tool_calls:
        tool_call = result.tool_calls[0]
        tool_result = get_attractions_tool.invoke(tool_call['args'])
        
        return {
            **state,
            "itinerary_info": tool_result,
            "messages": [
                AIMessage(content=f"Itinerary agent found {len(tool_result.get('attractions', []))} attractions", tool_calls=result.tool_calls),
                ToolMessage(content=str(tool_result), tool_call_id=tool_call['id'], name="get_attractions_tool")
            ]
        }
    
    return {**state, "messages": [result]}


def budget_agent_node(state: TravelState):
    """Budget agent calculates total costs."""
    agent = create_budget_agent()
    
    # Extract costs from previous agents
    flight_cost = 0
    hotel_cost = 0
    activities_cost = 0
    num_days = 3
    
    if state.get('flight_info') and state['flight_info'].get('flights'):
        flight_cost = state['flight_info']['flights'][0]['total_price']
    
    if state.get('hotel_info') and state['hotel_info'].get('hotels'):
        hotel_cost = state['hotel_info']['hotels'][0]['total_price']
        num_days = state['hotel_info']['nights']
    
    if state.get('itinerary_info') and state['itinerary_info'].get('attractions'):
        activities_cost = sum(a['cost'] for a in state['itinerary_info']['attractions'])
    
    task_msg = HumanMessage(
        content=f"Calculate budget with: flights=${flight_cost}, hotel=${hotel_cost}, days={num_days}, activities=${activities_cost}"
    )
    
    result = agent.invoke({"messages": state['messages'] + [task_msg]})
    
    if hasattr(result, 'tool_calls') and result.tool_calls:
        tool_call = result.tool_calls[0]
        tool_result = calculate_budget_tool.invoke(tool_call['args'])
        
        return {
            **state,
            "budget_info": tool_result,
            "messages": [
                AIMessage(content="Budget calculated", tool_calls=result.tool_calls),
                ToolMessage(content=str(tool_result), tool_call_id=tool_call['id'], name="calculate_budget_tool")
            ]
        }
    
    return {**state, "messages": [result]}


def final_summary_node(state: TravelState):
    """Create final comprehensive summary."""
    summary_parts = []
    
    # Get user's original request
    user_request = ""
    for msg in state['messages']:
        if isinstance(msg, HumanMessage):
            user_request = msg.content
            break
    
    summary_parts.append(f"Based on your request: '{user_request}'\n")
    summary_parts.append("Here's your complete travel plan!\n\n")
    
    # Flight
    if state.get('flight_info') and state['flight_info'].get('flights'):
        flight = state['flight_info']['flights'][0]
        summary_parts.append(f"✈️ **FLIGHT**: {flight['airline']}")
        summary_parts.append(f"   Price: ${flight['total_price']} ({state['flight_info']['passengers']} passenger(s))")
        summary_parts.append(f"   {flight['departure_time']} → {flight['arrival_time']} ({flight['duration_hours']}hrs)")
        summary_parts.append(f"   Class: {flight['class']}\n\n")
    
    # Hotel
    if state.get('hotel_info') and state['hotel_info'].get('hotels'):
        hotel = state['hotel_info']['hotels'][0]
        summary_parts.append(f"🏨 **HOTEL**: {hotel['name']}")
        summary_parts.append(f"   Price: ${hotel['total_price']} ({state['hotel_info']['nights']} nights)")
        summary_parts.append(f"   Rating: {hotel['rating']}/5.0 | Location: {hotel['location']}")
        summary_parts.append(f"   {hotel['description']}\n\n")
    
    # Itinerary
    if state.get('itinerary_info') and state['itinerary_info'].get('attractions'):
        summary_parts.append("📅 **ITINERARY**:\n")
        attractions = state['itinerary_info']['attractions']
        num_days = state['itinerary_info']['num_days']
        attractions_per_day = max(1, len(attractions) // num_days)
        
        for day in range(1, num_days + 1):
            summary_parts.append(f"\nDay {day}:")
            start_idx = (day - 1) * attractions_per_day
            end_idx = start_idx + min(3, len(attractions) - start_idx)
            for attr in attractions[start_idx:end_idx]:
                cost_str = "Free" if attr['cost'] == 0 else f"${attr['cost']}"
                summary_parts.append(f"  • {attr['name']} ({attr['category']}) - {cost_str}, {attr['duration_hours']}hrs")
        summary_parts.append("\n\n")
    
    # Budget
    if state.get('budget_info'):
        budget = state['budget_info']
        summary_parts.append("💰 **BUDGET BREAKDOWN**:\n")
        summary_parts.append(f"   Flights: ${budget['flights']}")
        summary_parts.append(f"   Accommodation: ${budget['accommodation']}")
        summary_parts.append(f"   Activities: ${budget['activities']}")
        summary_parts.append(f"   Food & Dining: ${budget['food']}")
        summary_parts.append(f"   Local Transport: ${budget['transport']}")
        summary_parts.append(f"   Miscellaneous: ${budget['miscellaneous']}")
        summary_parts.append(f"   **TOTAL: ${budget['total']}**\n\n")
    
    summary_parts.append("Let me know if you'd like to adjust anything! ✨")
    
    final_message = AIMessage(content="\n".join(summary_parts))
    return {**state, "messages": [final_message]}


# ============================================
# ROUTING
# ============================================

def route_next(state: TravelState) -> str:
    """Route to next agent or finish."""
    next_agent = state.get("next_agent", "")
    
    if next_agent == "FINISH":
        return "final_summary"
    elif next_agent == "flight_agent":
        return "flight_agent"
    elif next_agent == "accommodation_agent":
        return "accommodation_agent"
    elif next_agent == "itinerary_agent":
        return "itinerary_agent"
    elif next_agent == "budget_agent":
        return "budget_agent"
    else:
        return "supervisor"


# ============================================
# BUILD GRAPH
# ============================================

def build_travel_agent():
    """Build the multi-agent travel planning system."""
    workflow = StateGraph(TravelState)
    
    # Add all agent nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("flight_agent", flight_agent_node)
    workflow.add_node("accommodation_agent", accommodation_agent_node)
    workflow.add_node("itinerary_agent", itinerary_agent_node)
    workflow.add_node("budget_agent", budget_agent_node)
    workflow.add_node("final_summary", final_summary_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add routing
    workflow.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "flight_agent": "flight_agent",
            "accommodation_agent": "accommodation_agent",
            "itinerary_agent": "itinerary_agent",
            "budget_agent": "budget_agent",
            "final_summary": "final_summary"
        }
    )
    
    # Each agent goes back to supervisor
    workflow.add_edge("flight_agent", "supervisor")
    workflow.add_edge("accommodation_agent", "supervisor")
    workflow.add_edge("itinerary_agent", "supervisor")
    workflow.add_edge("budget_agent", "supervisor")
    
    # Final summary ends
    workflow.add_edge("final_summary", END)
    
    return workflow.compile()


if __name__ == "__main__":
    print("🚀 Building multi-agent travel planner...")
    agent = build_travel_agent()
    print("✅ Multi-agent system ready!")
