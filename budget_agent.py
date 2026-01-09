"""
Budget Agent - LLM-Powered Specialist with Multiple Tools

This agent has its own LLM and can use multiple internal tools to:
- Calculate detailed budgets
- Estimate daily costs
- Provide budget optimization tips
- Compare spending scenarios
"""

from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage
from constants import get_llm


# ============================================
# INTERNAL TOOLS (Available to budget agent)
# ============================================

@tool
def calculate_core_budget(flights_cost: str, hotel_cost: str, activities_cost: str):
    """Calculate budget from major expenses only.
    
    Use this for basic budget calculation.
    
    Args:
        flights_cost: Flight cost
        hotel_cost: Hotel cost
        activities_cost: Activities cost
        
    Returns:
        dict: Core expenses breakdown
    """
    flights = int(flights_cost.strip().replace('$', ''))
    hotel = int(hotel_cost.strip().replace('$', ''))
    activities = int(activities_cost.strip().replace('$', ''))
    core_total = flights + hotel + activities
    
    return {
        "flights": flights,
        "hotel": hotel,
        "activities": activities,
        "core_total": core_total
    }


@tool
def estimate_daily_costs(num_days: str, budget_level: str = "moderate"):
    """Estimate food and transport costs per day.
    
    Use this to add daily expense estimates.
    
    Args:
        num_days: Number of days
        budget_level: Budget level (budget, moderate, luxury)
        
    Returns:
        dict: Daily cost estimates
    """
    num_days = int(num_days)
    
    # Cost per day by budget level
    daily_rates = {
        "budget": {"food": 40, "transport": 20},
        "moderate": {"food": 60, "transport": 30},
        "luxury": {"food": 100, "transport": 50}
    }
    
    rates = daily_rates.get(budget_level.lower(), daily_rates["moderate"])
    
    food_total = rates["food"] * num_days
    transport_total = rates["transport"] * num_days
    daily_total = food_total + transport_total
    
    return {
        "food_per_day": rates["food"],
        "transport_per_day": rates["transport"],
        "food_total": food_total,
        "transport_total": transport_total,
        "daily_expenses_total": daily_total,
        "num_days": num_days,
        "budget_level": budget_level
    }


@tool
def calculate_miscellaneous(major_expenses_total: str):
    """Calculate miscellaneous costs (10% buffer).
    
    Use this to add a safety buffer.
    
    Args:
        major_expenses_total: Total of major expenses
        
    Returns:
        dict: Miscellaneous cost calculation
    """
    total = int(major_expenses_total.replace('$', ''))
    misc = int(total * 0.1)
    
    return {
        "miscellaneous": misc,
        "percentage": 10,
        "reason": "10% buffer for unexpected costs"
    }


@tool
def optimize_budget(total_cost: str, user_budget: str):
    """Compare total cost vs user budget and provide tips.
    
    Use this when user has a budget limit.
    
    Args:
        total_cost: Calculated total cost
        user_budget: User's budget limit
        
    Returns:
        dict: Budget comparison and tips
    """
    total = int(total_cost.replace('$', ''))
    budget = int(user_budget.replace('$', ''))
    difference = budget - total
    percentage = (total / budget * 100) if budget > 0 else 0
    
    status = "under" if difference >= 0 else "over"
    
    tips = []
    if status == "over":
        overage = abs(difference)
        tips = [
            f"Consider budget airlines to save on flights",
            f"Look for hostels or budget hotels",
            f"Choose free attractions",
            f"Reduce trip duration by 1-2 days"
        ]
    else:
        tips = [f"Great! You have ${difference} buffer in your budget"]
    
    return {
        "total_cost": total,
        "user_budget": budget,
        "difference": difference,
        "status": status,
        "percentage_used": round(percentage, 1),
        "tips": tips
    }


# ============================================
# BUDGET AGENT (Exposed to supervisor as tool)
# ============================================

@tool
def budget_agent(flights_cost: str, hotel_cost: str, num_days: str, activities_cost: str = "0", user_budget: str = "0"):
    """AI-powered budget calculator with intelligent analysis.
    
    Calculates comprehensive trip budget with personalized insights.
    
    Use this agent when you need to calculate the total cost of the trip.
    
    Args:
        flights_cost: Total flight cost
        hotel_cost: Total hotel/accommodation cost
        num_days: Number of days for the trip
        activities_cost: Total cost of activities/attractions (default: '0')
        user_budget: User's budget limit if specified (default: '0')
        
    Returns:
        str: AI-generated budget analysis with recommendations
    """
    # Create sub-agent with its own LLM
    llm = get_llm()
    
    # Define internal tools
    budget_tools = [
        calculate_core_budget,
        estimate_daily_costs,
        calculate_miscellaneous,
        optimize_budget
    ]
    
    # Agent's system prompt
    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert Budget Planning Specialist.

Your internal tools:
- calculate_core_budget: Calculate major expenses (flights, hotel, activities)
- estimate_daily_costs: Estimate food and transport costs
- calculate_miscellaneous: Add 10% buffer for unexpected costs
- optimize_budget: Compare vs user budget and provide tips

Process:
1. Use calculate_core_budget with the major expenses
2. Use estimate_daily_costs for {num_days} days (use 'moderate' level unless specified)
3. Add everything up
4. Use calculate_miscellaneous on the subtotal
5. If user_budget > 0, use optimize_budget to compare
6. Format a professional budget breakdown

Format your output as:
💰 COMPLETE BUDGET BREAKDOWN
Please ALWAYS output your numbers as integers

**Major Expenses:**
- Flights: $X
- Accommodation: $Y
- Activities: $Z

**Daily Expenses:**
- Food & Dining: $X ($Y/day)
- Local Transport: $X ($Y/day)
- Miscellaneous: $X (10% buffer)

━━━━━━━━━━━━━━━━━━━━
💵 TOTAL TRIP COST: $X,XXX
━━━━━━━━━━━━━━━━━━━━

[Include budget analysis if user_budget provided]"""),
        ("placeholder", "{messages}")
    ])
    
    # Bind tools
    agent = agent_prompt | llm.bind_tools(budget_tools)
    
    # Create task
    task = HumanMessage(
        content=f"""Calculate complete trip budget:
- Flights: {flights_cost}
- Hotel: {hotel_cost}
- Activities: {activities_cost}
- Duration: {num_days} days
{f"- User Budget: {user_budget}" if int(user_budget) > 0 else ""}

Use your tools to create a detailed budget breakdown."""
    )
    
    # Execute ReAct loop
    messages = [task]
    max_iterations = 6
    
    print(f"  💭 Budget Agent starting ReAct loop (max {max_iterations} iterations)...")
    
    for iteration in range(max_iterations):
        print(f"\n  🔄 Iteration {iteration + 1}: Reasoning...")
        
        result = agent.invoke({"messages": messages})
        messages.append(result)
        
        if not hasattr(result, 'tool_calls') or not result.tool_calls:
            print(f"  ✅ Budget Agent finished reasoning - no more tools needed")
            break
        
        print(f"  📞 Budget Agent decided to call {len(result.tool_calls)} internal tool(s):")
        for tool_call in result.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            print(f"     🔨 Calling: {tool_name}")
            print(f"        Args: {tool_args}")
            
            tool_map = {
                "calculate_core_budget": calculate_core_budget,
                "estimate_daily_costs": estimate_daily_costs,
                "calculate_miscellaneous": calculate_miscellaneous,
                "optimize_budget": optimize_budget
            }
            
            if tool_name in tool_map:
                tool_result = tool_map[tool_name].invoke(tool_args)
                print(f"     ✓ {tool_name} returned results")
                
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call['id'],
                        name=tool_name
                    )
                )
    
    final_response = messages[-1].content if messages else "Budget calculation failed"
    
    return final_response

