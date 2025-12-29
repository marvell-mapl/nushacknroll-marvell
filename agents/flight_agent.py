"""
Flight Agent
Responsible for analyzing and recommending flights based on user requirements.
"""

from typing import Dict, Any, List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.llm import get_llm
from utils.data_loader import get_data_loader


def load_prompt() -> str:
    """Load the flight agent prompt template."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "flight_agent.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def recommend_flight(
    origin: str,
    destination: str,
    budget: float,
    preferences: str = ""
) -> Dict[str, Any]:
    """
    Main entry point for flight recommendations.
    
    Args:
        origin: Departure city
        destination: Arrival city
        budget: Maximum budget for flights
        preferences: Optional user preferences (e.g., "prefer morning flights")
    
    Returns:
        Dictionary containing:
        - recommended_flight: The chosen flight details
        - reasoning: Explanation of the choice
        - alternatives: Other options considered
        - cost: Flight price
    """
    # Load data
    data_loader = get_data_loader()
    available_flights = data_loader.filter_flights(
        origin=origin,
        destination=destination,
        max_price=budget
    )
    
    # Handle no flights found
    if not available_flights:
        return {
            "recommended_flight": None,
            "reasoning": f"No flights found from {origin} to {destination} within budget of ${budget}",
            "alternatives": [],
            "cost": 0
        }
    
    # TODO: Students can enhance the filtering logic here
    # Ideas: Add date filtering, multi-city support, preferred airlines
    
    # Prepare context for LLM
    flights_summary = "\n".join([
        f"- {f['airline']} Flight {f['id']}: ${f['price']}, "
        f"{f['departure_time']}-{f['arrival_time']}, "
        f"{f['duration_hours']}hrs, {f['stops']} stops, {f['class']}"
        for f in available_flights
    ])
    
    user_prompt = f"""
Analyze these available flights from {origin} to {destination}:

{flights_summary}

User's budget: ${budget}
User preferences: {preferences if preferences else "None specified"}

Use the ReAct framework to recommend the BEST flight option:
1. Thought: Analyze the options considering budget, timing, and convenience
2. Action: Recommend a specific Flight ID with price
3. Observation: Explain trade-offs and why this is the best choice

Be specific and include the Flight ID in your Action.
    """
    
    # Get LLM recommendation using ReAct
    llm = get_llm()
    system_prompt = load_prompt()
    react_response = llm.generate_react(user_prompt, system_prompt)
    
    # Parse Flight ID from Action
    # TODO: Students can improve parsing with structured outputs
    recommended_id = None
    reasoning = react_response["full_reasoning"]
    
    try:
        action_text = react_response["action"]
        # Look for flight ID pattern (e.g., FL001, FL002)
        import re
        flight_id_match = re.search(r'FL\d{3}', action_text, re.IGNORECASE)
        if flight_id_match:
            recommended_id = flight_id_match.group(0).upper()
    except:
        pass
    
    # Find the recommended flight
    recommended_flight = None
    if recommended_id:
        recommended_flight = next(
            (f for f in available_flights if f['id'] == recommended_id),
            available_flights[0]  # Fallback to first option
        )
    else:
        # If parsing fails, pick the best value flight
        recommended_flight = min(available_flights, key=lambda f: f['price'])
    
    return {
        "recommended_flight": recommended_flight,
        "reasoning": reasoning,
        "react_breakdown": react_response,  # Include ReAct components
        "alternatives": [f for f in available_flights if f != recommended_flight][:2],
        "cost": recommended_flight['price']
    }


if __name__ == "__main__":
    # Test the agent independently
    result = recommend_flight(
        origin="Singapore",
        destination="Tokyo",
        budget=500,
        preferences="Prefer morning flights"
    )
    print(f"Recommended Flight: {result['recommended_flight']['id']}")
    print(f"Cost: ${result['cost']}")
    print(f"\nReasoning:\n{result['reasoning']}")

