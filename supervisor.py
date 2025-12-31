"""
Supervisor Agent - Coordinates all specialist agents via tool calls.
"""

from langchain.prompts import ChatPromptTemplate
from datetime import datetime
from constants import get_llm

# Import specialist agent tools
# from flight_agent import flight_agent
from accommodation_agent import accommodation_agent
from itinerary_agent import itinerary_agent
from budget_agent import budget_agent


def create_supervisor():
    """
    Create the supervisor agent that coordinates specialist agents.
    
    The supervisor has access to 4 specialist agent tools:
    # - flight_agent: For finding and recommending flights
    - accommodation_agent: For finding and recommending hotels
    - itinerary_agent: For creating day-by-day activity plans
    - budget_agent: For calculating total trip costs
    
    The supervisor uses the ReAct pattern:
    - Reasoning: Analyzes user request and decides which agents to call
    - Acting: Calls specialist agent tools with appropriate parameters
    - Observation: Reviews agent outputs and compiles final plan
    """
    llm = get_llm()
    
    # List of agent tools available to supervisor
    agent_tools = [accommodation_agent, itinerary_agent, budget_agent] #add flight_agent
    
    supervisor_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a Travel Planning Supervisor coordinating specialist agents via tool calls.
Today's date: {datetime.now().strftime("%Y-%m-%d")}

**Your Specialist Agent Tools:**
# - flight_agent: Searches flights and recommends best option
- accommodation_agent: Searches hotels and recommends best option  
- itinerary_agent: Creates day-by-day activity schedule
- budget_agent: Calculates complete budget breakdown

**Your Workflow:**
1. Parse the user's travel request
2. Call the appropriate specialist agents using your tools
3. Extract costs from agent responses (look for price amounts in $ format)
4. Compile all responses into ONE complete, well-formatted travel plan

**Default Assumptions (if not specified):**
- Origin: Singapore
- Travel date: 30 days from today ({(datetime.now().replace(year=datetime.now().year + (datetime.now().month == 12), month=datetime.now().month % 12 + 1 if datetime.now().day >= 28 else datetime.now().month)).strftime("%Y-%m-%d")})
- Duration: 3 days
- Passengers/Guests: 1

**When user provides a travel request:**
# 1. Call flight_agent(origin, destination, date, passengers)
2. Call accommodation_agent(destination, check_in, check_out, guests)
3. Call itinerary_agent(destination, num_days, interests)
4. Extract costs from outputs and call budget_agent(hotel_cost, num_days, activities_cost) # add flight_cost
5. Compile everything into a complete plan

**Final Output Format:**
Present a cohesive travel plan combining all agent outputs. Include all details from each agent.

**For casual/non-travel queries:**
Respond politely without calling any tools.

Call the tools now to help the user!"""),
        ("placeholder", "{messages}")
    ])
    
    # Bind the agent tools to the supervisor LLM
    return supervisor_prompt | llm.bind_tools(agent_tools)


