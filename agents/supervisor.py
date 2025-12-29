"""
Supervisor Agent with LangGraph Orchestration
Uses LangGraph's StateGraph for explicit multi-agent workflow management.
"""

from typing import Dict, Any, TypedDict, Annotated
import sys
from pathlib import Path
import operator

sys.path.append(str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, END
from utils.llm import get_llm
from agents.flight_agent import recommend_flight
from agents.accommodation_agent import recommend_accommodation
from agents.itinerary_agent import create_itinerary
from agents.budget_agent import validate_budget


# Define the state schema for the travel planning workflow
class TravelPlanState(TypedDict):
    """
    Shared state across all agents in the travel planning workflow.
    
    This state is passed through the LangGraph and each agent can read from
    and write to it. LangGraph manages state transitions automatically.
    """
    # User inputs
    user_input: str
    origin: str
    destination: str
    budget: float
    days: int
    nights: int
    preferences: str
    
    # Agent outputs
    flight_result: Dict[str, Any]
    accommodation_result: Dict[str, Any]
    itinerary_result: Dict[str, Any]
    budget_result: Dict[str, Any]
    
    # Final output
    summary: str
    success: bool
    
    # Tracking
    current_step: str
    errors: Annotated[list, operator.add]  # Accumulate errors


def load_prompt() -> str:
    """Load the supervisor agent prompt template."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "supervisor.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


# Node 1: Parse User Request
def parse_request_node(state: TravelPlanState) -> TravelPlanState:
    """
    LangGraph Node: Parse user input and extract travel parameters.
    
    This is the entry node of the workflow. It uses the LLM to extract
    structured information from natural language.
    """
    print("🔍 Node: Parsing user request...")
    
    user_input = state["user_input"]
    llm = get_llm()
    system_prompt = load_prompt()
    
    parsing_prompt = f"""
Extract travel planning parameters from this request:

"{user_input}"

Use the ReAct framework to parse the request:
1. Thought: Identify the key travel parameters in the user's request
2. Action: Extract specific values for origin, destination, budget, days, nights, and preferences
3. Observation: Confirm all necessary parameters are identified

Format the extracted parameters as:
ORIGIN: [city]
DESTINATION: [city]
BUDGET: [number]
DAYS: [number]
NIGHTS: [number]
PREFERENCES: [text]
    """
    
    react_response = llm.generate_react(parsing_prompt, system_prompt)
    response = react_response["raw_response"]
    
    # Default values
    params = {
        "origin": "Singapore",
        "destination": "Tokyo",
        "budget": 1500.0,
        "days": 3,
        "nights": 3,
        "preferences": ""
    }
    
    # Parse response
    for line in response.split('\n'):
        line = line.strip()
        if line.startswith("ORIGIN:"):
            params["origin"] = line.split("ORIGIN:")[1].strip()
        elif line.startswith("DESTINATION:"):
            params["destination"] = line.split("DESTINATION:")[1].strip()
        elif line.startswith("BUDGET:"):
            try:
                budget_str = line.split("BUDGET:")[1].strip().replace('$', '').replace(',', '')
                params["budget"] = float(budget_str.split()[0])
            except:
                pass
        elif line.startswith("DAYS:"):
            try:
                params["days"] = int(line.split("DAYS:")[1].strip().split()[0])
            except:
                pass
        elif line.startswith("NIGHTS:"):
            try:
                params["nights"] = int(line.split("NIGHTS:")[1].strip().split()[0])
            except:
                pass
        elif line.startswith("PREFERENCES:"):
            params["preferences"] = line.split("PREFERENCES:")[1].strip()
    
    # Update state
    return {
        **state,
        "origin": params["origin"],
        "destination": params["destination"],
        "budget": params["budget"],
        "days": params["days"],
        "nights": params["nights"],
        "preferences": params["preferences"],
        "current_step": "parsed"
    }


# Node 2: Flight Agent
def flight_agent_node(state: TravelPlanState) -> TravelPlanState:
    """
    LangGraph Node: Recommend flights based on parsed parameters.
    
    Allocates ~40% of budget to flights.
    """
    print("✈️  Node: Finding flights...")
    
    flight_result = recommend_flight(
        origin=state["origin"],
        destination=state["destination"],
        budget=state["budget"] * 0.4,
        preferences=state["preferences"]
    )
    
    return {
        **state,
        "flight_result": flight_result,
        "current_step": "flight_complete"
    }


# Node 3: Accommodation Agent
def accommodation_agent_node(state: TravelPlanState) -> TravelPlanState:
    """
    LangGraph Node: Recommend accommodation based on remaining budget.
    
    Uses budget remaining after flight allocation.
    """
    print("🏨 Node: Finding accommodation...")
    
    remaining_after_flight = state["budget"] - state["flight_result"]["cost"]
    
    accommodation_result = recommend_accommodation(
        destination=state["destination"],
        nights=state["nights"],
        remaining_budget=remaining_after_flight * 0.5,
        preferences=state["preferences"]
    )
    
    return {
        **state,
        "accommodation_result": accommodation_result,
        "current_step": "accommodation_complete"
    }


# Node 4: Itinerary Agent
def itinerary_agent_node(state: TravelPlanState) -> TravelPlanState:
    """
    LangGraph Node: Create day-by-day itinerary.
    
    Uses budget remaining after flight and accommodation.
    """
    print("📅 Node: Creating itinerary...")
    
    remaining_after_flight = state["budget"] - state["flight_result"]["cost"]
    remaining_after_accommodation = remaining_after_flight - state["accommodation_result"]["total_cost"]
    
    itinerary_result = create_itinerary(
        destination=state["destination"],
        days=state["days"],
        remaining_budget=remaining_after_accommodation * 0.7,
        preferences=state["preferences"]
    )
    
    return {
        **state,
        "itinerary_result": itinerary_result,
        "current_step": "itinerary_complete"
    }


# Node 5: Budget Validation Agent
def budget_agent_node(state: TravelPlanState) -> TravelPlanState:
    """
    LangGraph Node: Validate total budget and provide analysis.
    
    This is a deterministic validation step.
    """
    print("💰 Node: Validating budget...")
    
    budget_result = validate_budget(
        total_budget=state["budget"],
        flight_cost=state["flight_result"]["cost"],
        accommodation_cost=state["accommodation_result"]["total_cost"],
        activities_cost=state["itinerary_result"]["total_cost"]
    )
    
    return {
        **state,
        "budget_result": budget_result,
        "current_step": "budget_complete"
    }


# Node 6: Summary Generation
def summary_node(state: TravelPlanState) -> TravelPlanState:
    """
    LangGraph Node: Generate final summary and determine success.
    
    This is the final node before ending the workflow.
    """
    print("📝 Node: Generating summary...")
    
    llm = get_llm()
    system_prompt = load_prompt()
    
    flight = state["flight_result"].get("recommended_flight")
    accommodation = state["accommodation_result"].get("recommended_accommodation")
    
    summary_prompt = f"""
Provide a concise executive summary of this travel plan:

Destination: {state['destination']}
Duration: {state['days']} days
Budget: ${state['budget']}

Flight: {flight['airline'] if flight else 'Not found'} - ${state['flight_result']['cost']}
Accommodation: {accommodation['name'] if accommodation else 'Not found'} - ${state['accommodation_result']['total_cost']}
Activities Cost: ${state['itinerary_result']['total_cost']}

Budget Status: {'Within budget' if state['budget_result']['is_within_budget'] else 'Over budget'} - ${state['budget_result']['remaining']:.2f} {'remaining' if state['budget_result']['remaining'] >= 0 else 'over'}

Use the ReAct framework to create the final summary:
1. Thought: Review all agent outputs and assess overall plan quality
2. Action: Create a 2-3 sentence executive summary highlighting key aspects
3. Observation: Note any concerns or special considerations

Be concise and highlight the best aspects of the plan.
    """
    
    react_response = llm.generate_react(summary_prompt, system_prompt)
    final_summary = react_response["full_reasoning"]
    
    success = (
        state["flight_result"].get("recommended_flight") is not None and
        state["accommodation_result"].get("recommended_accommodation") is not None
    )
    
    return {
        **state,
        "summary": final_summary,
        "success": success,
        "current_step": "complete"
    }


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for travel planning.
    
    This defines the DAG (Directed Acyclic Graph) of agent interactions.
    Each node is an agent, and edges define the execution order.
    
    Workflow:
    START → Parse → Flight → Accommodation → Itinerary → Budget → Summary → END
    
    TODO: Students can add conditional edges for:
    - Retry logic if budget validation fails
    - Parallel execution of independent agents
    - Dynamic routing based on user preferences
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(TravelPlanState)
    
    # Add nodes (agents)
    workflow.add_node("parse_request", parse_request_node)
    workflow.add_node("flight_agent", flight_agent_node)
    workflow.add_node("accommodation_agent", accommodation_agent_node)
    workflow.add_node("itinerary_agent", itinerary_agent_node)
    workflow.add_node("budget_agent", budget_agent_node)
    workflow.add_node("generate_summary", summary_node)
    
    # Define edges (workflow transitions)
    workflow.set_entry_point("parse_request")
    workflow.add_edge("parse_request", "flight_agent")
    workflow.add_edge("flight_agent", "accommodation_agent")
    workflow.add_edge("accommodation_agent", "itinerary_agent")
    workflow.add_edge("itinerary_agent", "budget_agent")
    workflow.add_edge("budget_agent", "generate_summary")
    workflow.add_edge("generate_summary", END)
    
    # Compile the graph
    return workflow.compile()


# Global workflow instance
_workflow = None


def get_workflow() -> StateGraph:
    """Get or create the compiled workflow."""
    global _workflow
    if _workflow is None:
        _workflow = create_workflow()
    return _workflow


def orchestrate_planning(user_input: str) -> Dict[str, Any]:
    """
    Main entry point: Execute the LangGraph workflow.
    
    Args:
        user_input: User's natural language travel request
    
    Returns:
        Complete travel plan with all agent outputs
    """
    # Get the compiled workflow
    app = get_workflow()
    
    # Initialize state
    initial_state: TravelPlanState = {
        "user_input": user_input,
        "origin": "",
        "destination": "",
        "budget": 0.0,
        "days": 0,
        "nights": 0,
        "preferences": "",
        "flight_result": {},
        "accommodation_result": {},
        "itinerary_result": {},
        "budget_result": {},
        "summary": "",
        "success": False,
        "current_step": "init",
        "errors": []
    }
    
    # Execute the workflow
    # LangGraph automatically manages state transitions between nodes
    final_state = app.invoke(initial_state)
    
    # Return in the expected format
    return {
        "parameters": {
            "origin": final_state["origin"],
            "destination": final_state["destination"],
            "budget": final_state["budget"],
            "days": final_state["days"],
            "nights": final_state["nights"],
            "preferences": final_state["preferences"]
        },
        "flight": final_state["flight_result"],
        "accommodation": final_state["accommodation_result"],
        "itinerary": final_state["itinerary_result"],
        "budget": final_state["budget_result"],
        "summary": final_state["summary"],
        "success": final_state["success"]
    }


if __name__ == "__main__":
    # Test the LangGraph workflow
    test_request = "I want to visit Tokyo for 4 days with a budget of $1500. I love culture and food."
    print("Starting LangGraph workflow...\n")
    result = orchestrate_planning(test_request)
    print(f"\n✅ Success: {result['success']}")
    print(f"\n📋 Summary:\n{result['summary']}")
