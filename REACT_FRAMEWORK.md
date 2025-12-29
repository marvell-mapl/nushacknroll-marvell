# 🧠 ReAct Framework Guide

## What is ReAct?

**ReAct** (Reasoning + Acting) is a prompting paradigm that combines **reasoning traces** and **task-specific actions** in an interleaved manner. It makes AI agents' decision-making process transparent and debuggable.

## The ReAct Pattern

Instead of just getting a final answer, ReAct agents show their work:

```
Thought: [Reasoning about the current situation]
Action: [Specific action to take]
Observation: [What was learned from the action]
```

This creates a **transparent reasoning chain** that humans can follow and verify.

## Why Use ReAct?

### Traditional Approach
```
User: "Find me a flight to Tokyo under $500"
Agent: "I recommend Flight FL002 for $320"
```
**Problems:**
- ❌ No insight into why this was chosen
- ❌ Can't debug if wrong
- ❌ Black box decision-making

### ReAct Approach
```
User: "Find me a flight to Tokyo under $500"

Agent:
Thought: I need to compare available flights considering price, timing, and convenience.
         The budget is $500, so I have options ranging from $320 to $450.
         
Action: I recommend Flight FL002 by BudgetFly at $320, departing at 14:00 and 
        arriving at 21:30, with no stops.
        
Observation: This choice saves significant money ($130 below budget) while still 
             providing a direct flight. The afternoon departure may be less ideal 
             than morning flights, but the cost savings are substantial.
```
**Benefits:**
- ✅ See the reasoning process
- ✅ Understand trade-offs
- ✅ Easy to debug and improve
- ✅ Builds trust through transparency

## ReAct in Our Travel Planner

### Every Agent Uses ReAct

#### Flight Agent
```python
Thought: Looking at 5 available flights from Singapore to Tokyo, I need to 
         balance cost, timing, and comfort. Budget is $600.

Action: I recommend FL001 SkyHigh Airlines at $450, departing 08:30, 
        direct flight, 6.5 hours.

Observation: This provides a convenient morning departure within budget, 
             though FL002 at $320 would save money if departure time is flexible.
```

#### Accommodation Agent
```python
Thought: After flights, remaining budget is $800 for 4 nights. Need to balance 
         location and amenities with cost (max $200/night).

Action: I recommend Tokyo Central Hotel at $120/night in Shibuya, 
        totaling $480 for the stay.

Observation: This leaves $320 for activities while providing excellent transit 
             access and breakfast included. Shibuya location ideal for exploring.
```

#### Itinerary Agent
```python
Thought: With 3 days and $200 for activities, I should mix free cultural sites 
         with some paid attractions to stay within budget.

Action: Day 1: Senso-ji Temple (free, 2hrs), Tokyo Skytree ($25, 2hrs)
        Day 2: Meiji Shrine (free, 1.5hrs), Tsukiji Market ($30, 3hrs)
        Day 3: Harajuku/Shibuya exploration (free)

Observation: Total cost $55, leaving substantial buffer. Mixes culture, food, 
             and modern Tokyo without exhausting travelers.
```

#### Budget Agent
```python
Thought: Total budget $1500. Costs: Flights $450 (30%), Accommodation $480 (32%),
         Activities $55 (4%), Estimated extras $300 (20%). Total: $1285.

Action: Validate as WITHIN BUDGET with $215 remaining (14% buffer).

Observation: Budget allocation is well-balanced. The activity spend is 
             conservative, providing flexibility for spontaneous experiences.
```

## Implementation Details

### 1. Prompt Engineering

All our agent prompts include ReAct instructions:

```python
You are a Flight Agent using the ReAct framework.

ALWAYS use this format:
Thought: [Your reasoning]
Action: [Your specific recommendation]
Observation: [Key insights and trade-offs]
```

### 2. LLM Wrapper with ReAct Parsing

```python
# utils/llm.py
def generate_react(self, prompt: str, system_prompt: str) -> Dict:
    """Generate and parse ReAct-formatted responses."""
    raw_response = self.generate(prompt, system_prompt)
    
    # Extract components using regex
    thought = extract_section(raw_response, "Thought:")
    action = extract_section(raw_response, "Action:")
    observation = extract_section(raw_response, "Observation:")
    
    return {
        "thought": thought,
        "action": action,
        "observation": observation,
        "full_reasoning": formatted_output
    }
```

### 3. Agent Integration

```python
# agents/flight_agent.py
def recommend_flight(origin, destination, budget, preferences):
    # ... data loading ...
    
    # Use ReAct prompting
    prompt = f"""
    Analyze flights: {flights_summary}
    Budget: ${budget}
    
    Use ReAct framework:
    1. Thought: Analyze options
    2. Action: Recommend specific flight
    3. Observation: Explain trade-offs
    """
    
    react_response = llm.generate_react(prompt, system_prompt)
    
    return {
        "recommended_flight": selected_flight,
        "reasoning": react_response["full_reasoning"],
        "react_breakdown": react_response  # Structured components
    }
```

### 4. UI Display

```python
# app.py
with st.expander("🧠 Agent Reasoning (ReAct Framework)"):
    st.markdown(f"**💭 Thought:** {react['thought']}")
    st.markdown(f"**🎯 Action:** {react['action']}")
    st.markdown(f"**👁️ Observation:** {react['observation']}")
```

## ReAct + LangGraph = Powerful Combination

```
LangGraph provides:
  ↓
STATE MANAGEMENT - What data flows between agents
  ↓
ReAct provides:
  ↓
REASONING TRANSPARENCY - Why agents made decisions
```

### Combined Architecture

```
START
  ↓
[Parse Node]
  💭 Thought: User wants Tokyo trip, $1500, 4 days
  🎯 Action: Extract parameters
  👁️ Observation: All parameters identified
  ↓
[Flight Node]
  💭 Thought: Need to balance cost and timing
  🎯 Action: Recommend FL001 at $450
  👁️ Observation: Good value with morning departure
  ↓
[Accommodation Node]
  💭 Thought: $1050 remaining, need central location
  🎯 Action: Recommend Tokyo Central Hotel
  👁️ Observation: Well-located, leaves room for activities
  ↓
[Itinerary Node]
  💭 Thought: Mix free and paid attractions
  🎯 Action: 3-day plan with $55 total
  👁️ Observation: Balanced, not overwhelming
  ↓
[Budget Node]
  💭 Thought: Check if within $1500 limit
  🎯 Action: Validate $1285 total
  👁️ Observation: $215 buffer, well-balanced
  ↓
END: Complete Travel Plan with Full Reasoning
```

## Benefits for Workshop Participants

### 1. **Transparency**
See exactly how each agent makes decisions

### 2. **Debugging**
If an agent makes a poor choice, inspect the Thought to understand why

### 3. **Trust**
Users can verify the reasoning aligns with their needs

### 4. **Learning**
Study how expert reasoning should work for each domain

### 5. **Improvement**
Easy to spot where prompts need refinement

## Comparing Approaches

| Aspect | Traditional | ReAct |
|--------|------------|-------|
| Decision Visibility | ❌ Black box | ✅ Transparent |
| Debugging | ❌ Hard | ✅ Easy |
| Trust | ❌ Low | ✅ High |
| Prompt Engineering | ❌ Trial & error | ✅ Structured |
| User Understanding | ❌ "Why did it choose this?" | ✅ Clear reasoning |

## Extension Ideas

### 1. Multi-Step ReAct Loops

Add iteration for complex decisions:

```python
Thought: Initial flight choice might be too expensive
Action: Reconsider with stricter budget
Observation: Found better option

Thought: New choice meets budget better
Action: Select FL002 instead
Observation: Confirmed - saves $130
```

### 2. Inter-Agent ReAct Reasoning

Have the supervisor use ReAct to decide agent order:

```python
Thought: User has tight budget, should validate costs early
Action: Run Budget Agent after Flights to check feasibility before booking
Observation: Budget allows continued planning
```

### 3. User-Facing ReAct

Show reasoning in real-time:

```streamlit
with st.status("Agent is thinking..."):
    st.write("💭 Analyzing 12 flight options...")
    st.write("🎯 Selected best value option...")
    st.write("👁️ Confirmed trade-offs acceptable...")
```

## Common Pitfalls

### ❌ Too Verbose
```
Thought: Looking at flights, I see there are many options including...
         [500 words of analysis]
```

### ✅ Concise and Focused
```
Thought: 12 flights available. Budget $500. Priority: direct flights.
Action: Recommend FL001 at $450, direct, morning departure.
Observation: Best balance of cost and convenience.
```

### ❌ Generic Observations
```
Observation: This is a good choice.
```

### ✅ Specific Insights
```
Observation: Saves $130 vs premium option while maintaining direct route. 
             Trade-off: afternoon vs morning departure.
```

### ❌ Action Without Specifics
```
Action: Choose a flight.
```

### ✅ Concrete Action
```
Action: Recommend Flight FL002 by BudgetFly at $320, departing 14:00.
```

## Testing ReAct Agents

```python
def test_flight_agent_reasoning():
    result = recommend_flight("Singapore", "Tokyo", 500, "prefer morning")
    
    # Check ReAct components exist
    assert "react_breakdown" in result
    assert result["react_breakdown"]["thought"]
    assert result["react_breakdown"]["action"]
    assert result["react_breakdown"]["observation"]
    
    # Check reasoning quality
    thought = result["react_breakdown"]["thought"]
    assert "budget" in thought.lower()
    assert "morning" in thought.lower() or "timing" in thought.lower()
    
    # Check action is specific
    action = result["react_breakdown"]["action"]
    assert "FL" in action  # Should mention specific flight ID
    assert "$" in action   # Should mention price
```

## Resources

- **Original Paper**: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- **LangChain ReAct**: https://python.langchain.com/docs/modules/agents/agent_types/react
- **Prompt Engineering Guide**: https://www.promptingguide.ai/techniques/react

## Quick Reference

### ReAct Template

```
Thought: [What am I trying to accomplish? What do I know?]
Action: [Specific, concrete step I'm taking]
Observation: [What did I learn? What are the implications?]
```

### Integration Checklist

- [ ] Update all agent prompts with ReAct format
- [ ] Add `generate_react()` method to LLM wrapper
- [ ] Parse Thought/Action/Observation from responses
- [ ] Display reasoning in UI
- [ ] Test that reasoning makes sense
- [ ] Refine prompts based on reasoning quality

---

**Remember: ReAct is about making AI thinking visible, not just getting answers!** 🧠✨

