"""
Multi-Agent Travel Planner - Main orchestration.
Supervisor coordinates specialist agents via tool calls (ReAct pattern).
"""

from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, ToolMessage
from typing import List, TypedDict, Annotated
import operator

# Import specialist agent tools
from flight_agent import flight_agent
from accommodation_agent import accommodation_agent
from itinerary_agent import itinerary_agent
from budget_agent import budget_agent
from supervisor import create_supervisor


# ============================================
# STATE DEFINITION
# ============================================

class TravelState(TypedDict):
    """State passed through the workflow - just messages (ReAct pattern)."""
    messages: Annotated[List, operator.add]


# ============================================
# TOOL MAPPING
# ============================================

# Map tool names to their implementations
TOOL_MAP = {
    "flight_agent": flight_agent,
    "accommodation_agent": accommodation_agent,
    "itinerary_agent": itinerary_agent,
    "budget_agent": budget_agent,
}


# ============================================
# GRAPH NODES
# ============================================

def supervisor_node(state: TravelState):
    """
    Supervisor agent reasons about the request and calls specialist agents.
    This is the REASONING step in the ReAct pattern.
    """
    print("\n" + "="*60)
    print("🧠 SUPERVISOR REASONING...")
    print("="*60)
    
    supervisor = create_supervisor()
    result = supervisor.invoke({"messages": state['messages']})
    
    # Show what supervisor decided
    if hasattr(result, 'tool_calls') and result.tool_calls:
        print(f"\n📋 Supervisor decided to call {len(result.tool_calls)} agent(s):")
        for tool_call in result.tool_calls:
            print(f"   → {tool_call['name']}")
            print(f"      Args: {tool_call['args']}")
    else:
        print("\n✅ Supervisor has all information, preparing final response")
    
    return {"messages": [result]}


def tool_node(state: TravelState):
    """
    Execute tool calls from supervisor.
    This is the ACTING step in the ReAct pattern - executing specialist agents.
    """
    last_message = state['messages'][-1]
    
    # Collect all tool results
    tool_messages = []
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            print(f"\n{'─'*60}")
            print(f"🔧 EXECUTING: {tool_name.upper()}")
            print(f"{'─'*60}")
            
            # Execute the specialist agent tool
            if tool_name in TOOL_MAP:
                result = TOOL_MAP[tool_name].invoke(tool_args)
                
                print(f"✅ {tool_name} completed")
                print(f"{'─'*60}\n")
                
                # Create tool message with result (OBSERVATION step in ReAct)
                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call['id'],
                        name=tool_name
                    )
                )
    
    return {"messages": tool_messages}


# ============================================
# ROUTING
# ============================================

def should_continue(state: TravelState) -> str:
    """
    Decide if we should continue or finish.
    Continue if supervisor made tool calls, otherwise finish.
    """
    last_message = state['messages'][-1]
    
    # If supervisor made tool calls, execute them
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # Otherwise, we're done
    return END


# ============================================
# BUILD GRAPH
# ============================================

def build_travel_agent():
    """
    Build the multi-agent travel planning system using ReAct pattern.
    
    Architecture:
    - Supervisor: Reasons about user request and calls specialist agents (Reasoning)
    - Tool Node: Executes specialist agent tools (Acting)
    - Loop: Supervisor → Tools → Supervisor until no more tool calls (Observation & Re-reasoning)
    
    This is a clean ReAct loop:
    1. Supervisor reasons and decides which agents to call
    2. Tool node executes the agent tools
    3. Results go back to supervisor for observation
    4. Supervisor decides next action (more tools or final response)
    5. Repeat until supervisor finishes with final response
    """
    workflow = StateGraph(TravelState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("tools", tool_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add routing logic
    workflow.add_conditional_edges(
        "supervisor",
        should_continue,
        {
            "tools": "tools",  # If tool calls made, execute them
            END: END  # Otherwise finish
        }
    )
    
    # After tools execute, go back to supervisor for next reasoning step
    workflow.add_edge("tools", "supervisor")
    
    return workflow.compile()


if __name__ == "__main__":
    print("🚀 Building multi-agent travel planner...")
    agent = build_travel_agent()
    print("✅ Multi-agent system ready!")
