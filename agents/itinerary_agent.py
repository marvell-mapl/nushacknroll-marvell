"""
Itinerary Agent
Responsible for creating day-by-day activity plans with attractions.
"""

from typing import Dict, Any, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.llm import get_llm
from utils.data_loader import get_data_loader


def load_prompt() -> str:
    """Load the itinerary agent prompt template."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "itinerary_agent.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_itinerary(
    destination: str,
    days: int,
    remaining_budget: float,
    preferences: str = ""
) -> Dict[str, Any]:
    """
    Main entry point for itinerary creation.
    
    Args:
        destination: City to explore
        days: Number of days for activities
        remaining_budget: Budget available for activities
        preferences: Optional preferences (e.g., "love culture and food")
    
    Returns:
        Dictionary containing:
        - daily_plan: List of activities organized by day
        - total_cost: Total cost of all activities
        - summary: Overview of the itinerary
    """
    # Load available attractions
    data_loader = get_data_loader()
    available_attractions = data_loader.filter_attractions(city=destination)
    
    if not available_attractions:
        return {
            "daily_plan": [],
            "total_cost": 0,
            "summary": f"No attractions found for {destination}"
        }
    
    # TODO: Students can add smart selection based on interests, proximity, time optimization
    
    # Prepare attractions summary
    attractions_summary = "\n".join([
        f"- {a['name']} ({a['category']}): ${a['cost']}, "
        f"{a['duration_hours']}hrs - {a['description']}"
        for a in available_attractions
    ])
    
    user_prompt = f"""
Create a {days}-day itinerary for {destination} from these attractions:

{attractions_summary}

Constraints:
- Total budget for activities: ${remaining_budget}
- {days} full days to plan
- Balance activity types (culture, nature, landmarks, food)
- Don't over-pack days (max 3-4 activities per day)

User preferences: {preferences if preferences else "None specified"}

Use the ReAct framework to create a balanced itinerary:
1. Thought: Consider budget, variety, pacing, and must-see attractions
2. Action: Create a day-by-day plan listing specific attractions
3. Observation: Explain the balance and reasoning behind the itinerary

Include specific attraction names in your Action section organized by day.
    """
    
    # Get LLM recommendation using ReAct
    llm = get_llm()
    system_prompt = load_prompt()
    react_response = llm.generate_react(user_prompt, system_prompt)
    response = react_response["raw_response"]
    
    # Parse the response
    # TODO: Students can implement structured parsing
    daily_plan = []
    total_cost = 0
    
    # Simple parsing: extract activities mentioned
    current_day = 0
    for line in response.split('\n'):
        if line.strip().startswith('DAY'):
            current_day += 1
            daily_plan.append({
                "day": current_day,
                "activities": []
            })
        elif line.strip().startswith('-') and daily_plan:
            # Extract activity name
            activity_text = line.strip()[1:].strip()
            # Try to match with an attraction
            for attr in available_attractions:
                if attr['name'].lower() in activity_text.lower():
                    daily_plan[-1]['activities'].append(attr)
                    total_cost += attr['cost']
                    break
    
    # Fallback: create a simple itinerary if parsing fails
    if not daily_plan:
        activities_per_day = len(available_attractions) // days if days > 0 else 0
        activities_per_day = max(2, min(4, activities_per_day))
        
        for day in range(1, days + 1):
            start_idx = (day - 1) * activities_per_day
            end_idx = start_idx + activities_per_day
            day_activities = available_attractions[start_idx:end_idx]
            
            daily_plan.append({
                "day": day,
                "activities": day_activities
            })
            total_cost += sum(a['cost'] for a in day_activities)
    
    return {
        "daily_plan": daily_plan,
        "total_cost": total_cost,
        "summary": react_response["full_reasoning"],
        "react_breakdown": react_response  # Include ReAct components
    }


if __name__ == "__main__":
    # Test the agent independently
    result = create_itinerary(
        destination="Tokyo",
        days=3,
        remaining_budget=200,
        preferences="Love culture and food"
    )
    print(f"Total Activities Cost: ${result['total_cost']}")
    print(f"\nItinerary:\n{result['summary']}")

