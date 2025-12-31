"""
ADVANCED Agent Template - LLM-Powered with Multiple Tools

This template creates a sophisticated agent that:
1. Has its own LLM for reasoning
2. Can use multiple internal tools
3. Executes a ReAct loop (Reasoning → Acting → Observation)
4. Is exposed to the supervisor as a single tool

INSTRUCTIONS:
1. Replace TEMPLATE_AGENT_NAME with your agent's name (e.g., "Weather", "Restaurant")
2. Replace template_agent with lowercase_agent_name
3. Replace TEMPLATE_DATA with your data constant
4. Create 2-4 internal tools (@tool decorated)
5. Implement the main agent function
6. Update supervisor.py and agents.py to register
"""

from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage
from constants import get_llm, FLIGHTS_DATA as TEMPLATE_DATA  # ← Replace with your data


# ============================================
# INTERNAL TOOLS (Available to your agent)
# ============================================
# These tools are decorated with @tool and can be called by your agent's LLM

@tool
def internal_tool_1(param1: str, param2: str):
    """First internal tool - describe what it does.
    
    Use this when [specific condition].
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        dict: Structured data
    """
    # TODO: Implement tool logic
    # Query TEMPLATE_DATA
    results = [
        item for item in TEMPLATE_DATA
        if item.get('field', '').lower() == param1.lower()
    ]
    
    if not results:
        return {"results": [], "error": f"No data for {param1}"}
    
    return {"results": results[:5], "tool": "tool_1"}


@tool
def internal_tool_2(param1: str, filter_value: str):
    """Second internal tool - describe what it does.
    
    Use this when [specific condition].
    
    Args:
        param1: Description
        filter_value: Description
        
    Returns:
        dict: Filtered data
    """
    # TODO: Implement tool logic
    results = [
        item for item in TEMPLATE_DATA
        if item.get('field') == param1 and
           item.get('filter_field') == filter_value
    ]
    
    return {"results": results[:5], "tool": "tool_2", "filter": filter_value}


@tool
def internal_tool_3(param1: str):
    """Third internal tool - describe what it does.
    
    Use this when [specific condition].
    
    Args:
        param1: Description
        
    Returns:
        dict: Processed data
    """
    # TODO: Implement tool logic
    results = [item for item in TEMPLATE_DATA if param1.lower() in str(item).lower()]
    
    # Sort or process results
    sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
    
    return {"results": sorted_results[:5], "tool": "tool_3"}


# ============================================
# AGENT (Exposed to supervisor as tool)
# ============================================

@tool
def template_agent(param1: str, param2: str, preferences: str = "balanced"):
    """AI-powered [AGENT_TYPE] specialist with intelligent [CAPABILITY].
    
    Uses multiple search strategies and AI reasoning to [PRIMARY_GOAL].
    
    Use this agent when you need to [USE_CASE].
    
    Args:
        param1: Main parameter (e.g., 'destination', 'category')
        param2: Secondary parameter (e.g., 'date', 'budget')
        preferences: User preference (e.g., 'cheapest', 'fastest', 'balanced')
        
    Returns:
        str: AI-generated recommendation with reasoning
    """
    # Create sub-agent with its own LLM
    llm = get_llm()
    
    # Define internal tools this agent can use
    agent_tools = [
        internal_tool_1,
        internal_tool_2,
        internal_tool_3
    ]
    
    # Agent's system prompt - THIS IS CRITICAL
    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert [AGENT_TYPE] Specialist with intelligent capabilities.

Your internal tools:
- internal_tool_1: [Description of when to use]
- internal_tool_2: [Description of when to use]
- internal_tool_3: [Description of when to use]

User preference: {preferences}

Your strategy based on preference:
- 'cheapest': [Which tools to use and why]
- 'fastest': [Which tools to use and why]
- 'balanced': [Which tools to use and why]

Process:
1. Choose the RIGHT tool(s) based on user preference
2. Analyze the results from your tools
3. Pick the BEST option with clear reasoning
4. Format as a professional recommendation

BE SMART: Don't call unnecessary tools! Choose wisely based on the task.

Output format:
[EMOJI] [SECTION_TITLE]: [Result Name]

**Key Details:**
- Field 1: Value
- Field 2: Value
- Field 3: Value

**Why this choice:** [Clear reasoning]"""),
        ("placeholder", "{messages}")
    ])
    
    # Bind tools to agent's LLM
    agent = agent_prompt | llm.bind_tools(agent_tools)
    
    # Create the agent's task
    task = HumanMessage(
        content=f"""[TASK_DESCRIPTION]

Parameters:
- {param1}
- {param2}
- Preference: {preferences}

Use your tools wisely to find the optimal solution."""
    )
    
    # Execute agent's ReAct loop
    messages = [task]
    max_iterations = 5  # Adjust based on complexity
    
    for iteration in range(max_iterations):
        # Agent reasons and decides which tool(s) to call
        result = agent.invoke({"messages": messages})
        messages.append(result)
        
        # Check if agent is done (no more tool calls)
        if not hasattr(result, 'tool_calls') or not result.tool_calls:
            break
        
        # Execute all tool calls
        for tool_call in result.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            # Map tool names to functions
            tool_map = {
                "internal_tool_1": internal_tool_1,
                "internal_tool_2": internal_tool_2,
                "internal_tool_3": internal_tool_3
            }
            
            if tool_name in tool_map:
                tool_result = tool_map[tool_name].invoke(tool_args)
                
                # Add tool result to conversation
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call['id'],
                        name=tool_name
                    )
                )
    
    # Get the agent's final recommendation
    final_response = messages[-1].content if messages else "No results found"
    
    return final_response


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("Testing template_agent...")
    print("(Implement your test cases here)")
    
    # Uncomment to test:
    # result = template_agent("test_param1", "test_param2", "balanced")
    # print(result)
