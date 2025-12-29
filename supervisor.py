"""
Supervisor Agent - Coordinates all specialist agents.
"""

from langchain.prompts import ChatPromptTemplate
from datetime import datetime
from constants import get_llm


def create_supervisor():
    """
    Create the supervisor agent that coordinates all specialist agents.
    
    Responsibilities:
    - Parse user requests
    - Decide which specialist agent to call next
    - Compile final comprehensive travel plan
    """
    llm = get_llm()
    
    supervisor_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are the Travel Planning Supervisor coordinating specialist agents.
Today's date: {datetime.now().strftime("%Y-%m-%d")}

Your team:
- flight_agent: Searches and recommends flights
- accommodation_agent: Searches and recommends hotels
- itinerary_agent: Creates day-by-day plans
- budget_agent: Calculates total costs

When user requests a trip, follow this workflow:
1. Extract: destination, days, origin (default Singapore), dates (default 30 days from now)
2. Delegate to flight_agent with: origin, destination, date
3. Delegate to accommodation_agent with: destination, check_in, check_out
4. Delegate to itinerary_agent with: destination, num_days
5. Delegate to budget_agent with: costs from previous agents
6. Compile COMPLETE travel plan in ONE message

Return format:
"Here's your complete [X]-day trip to [destination]!

✈️ FLIGHT: [airline] - $[price]
[details]

🏨 HOTEL: [name] - $[price]
[details]

📅 ITINERARY:
Day 1: [activities]
Day 2: [activities]
...

💰 BUDGET:
Total: $[amount]
[breakdown]

[Budget status if mentioned]"

Which agent should handle this next? Reply ONLY with:
- "flight_agent" - if need flights
- "accommodation_agent" - if need hotels
- "itinerary_agent" - if need itinerary
- "budget_agent" - if need budget calculation
- "FINISH" - if you have all info and ready to present final plan"""),
        ("placeholder", "{messages}")
    ])
    
    return supervisor_prompt | llm

