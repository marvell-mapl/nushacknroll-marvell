"""
Budget Agent
Responsible for validating costs and performing budget calculations.
"""

from typing import Dict, Any
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.llm import get_llm


def load_prompt() -> str:
    """Load the budget agent prompt template."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "budget_agent.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def validate_budget(
    total_budget: float,
    flight_cost: float,
    accommodation_cost: float,
    activities_cost: float,
    estimated_extras: float = None
) -> Dict[str, Any]:
    """
    Main entry point for budget validation.
    
    Args:
        total_budget: User's total trip budget
        flight_cost: Cost of selected flights
        accommodation_cost: Total accommodation cost
        activities_cost: Total cost of activities
        estimated_extras: Optional estimate for meals, transport, etc.
    
    Returns:
        Dictionary containing:
        - is_within_budget: Boolean indicating if plan fits budget
        - breakdown: Cost breakdown by category
        - total_spent: Sum of all costs
        - remaining: Money left over (or negative if over-budget)
        - suggestions: Recommendations if over-budget
        - analysis: Detailed explanation
    """
    # Calculate estimated extras if not provided (30% of base costs)
    if estimated_extras is None:
        estimated_extras = (flight_cost + accommodation_cost + activities_cost) * 0.3
    
    # Deterministic calculations
    total_spent = flight_cost + accommodation_cost + activities_cost + estimated_extras
    remaining = total_budget - total_spent
    is_within_budget = remaining >= 0
    
    breakdown = {
        "flights": flight_cost,
        "accommodation": accommodation_cost,
        "activities": activities_cost,
        "estimated_extras": estimated_extras,
        "total": total_spent
    }
    
    # TODO: Students can add more sophisticated budget optimization algorithms
    
    # Prepare prompt for LLM analysis using ReAct
    user_prompt = f"""
Analyze this travel budget:

TOTAL BUDGET: ${total_budget}

Cost Breakdown:
- Flights: ${flight_cost} ({flight_cost/total_budget*100:.1f}%)
- Accommodation: ${accommodation_cost} ({accommodation_cost/total_budget*100:.1f}%)
- Activities: ${activities_cost} ({activities_cost/total_budget*100:.1f}%)
- Estimated Extras (meals, transport): ${estimated_extras} ({estimated_extras/total_budget*100:.1f}%)

TOTAL SPENT: ${total_spent}
{'OVER BUDGET by $' + str(abs(remaining)) if not is_within_budget else 'REMAINING: $' + str(remaining)}

Use the ReAct framework to validate the budget:
1. Thought: Assess the budget breakdown and identify any issues or opportunities
2. Action: Provide specific status and recommendations
3. Observation: Note insights about budget allocation and balance

Be specific and actionable.
    """
    
    # Get LLM analysis using ReAct
    llm = get_llm()
    system_prompt = load_prompt()
    react_response = llm.generate_react(user_prompt, system_prompt)
    analysis = react_response["full_reasoning"]
    
    # Generate suggestions if over-budget
    suggestions = []
    if not is_within_budget:
        suggestions.append(f"Budget shortfall: ${abs(remaining):.2f}")
        if flight_cost > total_budget * 0.4:
            suggestions.append("Consider a more economical flight option")
        if accommodation_cost > total_budget * 0.35:
            suggestions.append("Look for cheaper accommodation alternatives")
        if activities_cost > total_budget * 0.25:
            suggestions.append("Reduce number of paid attractions, focus on free options")
    
    return {
        "is_within_budget": is_within_budget,
        "breakdown": breakdown,
        "total_spent": total_spent,
        "remaining": remaining,
        "percentage_used": (total_spent / total_budget * 100) if total_budget > 0 else 0,
        "suggestions": suggestions,
        "analysis": analysis,
        "react_breakdown": react_response  # Include ReAct components
    }


if __name__ == "__main__":
    # Test the agent independently
    result = validate_budget(
        total_budget=1500,
        flight_cost=450,
        accommodation_cost=480,
        activities_cost=150
    )
    print(f"Within Budget: {result['is_within_budget']}")
    print(f"Total Spent: ${result['total_spent']}")
    print(f"Remaining: ${result['remaining']}")
    print(f"\nAnalysis:\n{result['analysis']}")

