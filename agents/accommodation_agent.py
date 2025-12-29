"""
Accommodation Agent
Responsible for recommending lodging based on destination and remaining budget.
"""

from typing import Dict, Any
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.llm import get_llm
from utils.data_loader import get_data_loader


def load_prompt() -> str:
    """Load the accommodation agent prompt template."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "accommodation_agent.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def recommend_accommodation(
    destination: str,
    nights: int,
    remaining_budget: float,
    preferences: str = ""
) -> Dict[str, Any]:
    """
    Main entry point for accommodation recommendations.
    
    Args:
        destination: City where accommodation is needed
        nights: Number of nights to stay
        remaining_budget: Budget left after flights
        preferences: Optional user preferences (e.g., "prefer central location")
    
    Returns:
        Dictionary containing:
        - recommended_accommodation: The chosen accommodation details
        - reasoning: Explanation of the choice
        - total_cost: Total cost for all nights
        - cost_per_night: Nightly rate
    """
    # Calculate max price per night
    max_price_per_night = remaining_budget / nights if nights > 0 else 0
    
    # Load data
    data_loader = get_data_loader()
    available_accommodations = data_loader.filter_accommodations(
        city=destination,
        max_price_per_night=max_price_per_night
    )
    
    # Handle no accommodations found
    if not available_accommodations:
        return {
            "recommended_accommodation": None,
            "reasoning": f"No accommodations found in {destination} within ${max_price_per_night:.2f}/night",
            "total_cost": 0,
            "cost_per_night": 0
        }
    
    # TODO: Students can add filtering by amenities, rating threshold, type
    
    # Prepare context for LLM
    accommodations_summary = "\n".join([
        f"- {a['name']} ({a['type']}): ${a['price_per_night']}/night, "
        f"Rating: {a['rating']}, Location: {a['location']}, "
        f"Amenities: {', '.join(a['amenities'][:3])}"
        for a in available_accommodations
    ])
    
    user_prompt = f"""
Analyze these available accommodations in {destination}:

{accommodations_summary}

Trip details:
- Duration: {nights} nights
- Budget available for accommodation: ${remaining_budget}
- Maximum per night: ${max_price_per_night:.2f}

User preferences: {preferences if preferences else "None specified"}

Use the ReAct framework to recommend the BEST accommodation:
1. Thought: Analyze the options considering budget, location, amenities, and ratings
2. Action: Recommend a specific accommodation by name with total cost
3. Observation: Explain the value proposition and trade-offs

Be specific and include the accommodation name in your Action.
    """
    
    # Get LLM recommendation using ReAct
    llm = get_llm()
    system_prompt = load_prompt()
    react_response = llm.generate_react(user_prompt, system_prompt)
    
    # Parse accommodation name from Action
    # TODO: Improve parsing logic
    recommended_accommodation = None
    try:
        action_text = react_response["action"]
        # Try to find accommodation by matching name in action
        for acc in available_accommodations:
            if acc['name'].lower() in action_text.lower():
                recommended_accommodation = acc
                break
    except:
        pass
    
    # Fallback: pick best value (rating/price ratio)
    if not recommended_accommodation:
        recommended_accommodation = max(
            available_accommodations,
            key=lambda a: a['rating'] / (a['price_per_night'] + 1)
        )
    
    total_cost = recommended_accommodation['price_per_night'] * nights
    
    return {
        "recommended_accommodation": recommended_accommodation,
        "reasoning": react_response["full_reasoning"],
        "react_breakdown": react_response,  # Include ReAct components
        "total_cost": total_cost,
        "cost_per_night": recommended_accommodation['price_per_night']
    }


if __name__ == "__main__":
    # Test the agent independently
    result = recommend_accommodation(
        destination="Tokyo",
        nights=4,
        remaining_budget=500,
        preferences="Prefer central location with good transit access"
    )
    print(f"Recommended: {result['recommended_accommodation']['name']}")
    print(f"Total Cost: ${result['total_cost']}")
    print(f"\nReasoning:\n{result['reasoning']}")

