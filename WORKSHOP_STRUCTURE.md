# 🎓 Workshop Structure: Progressive Multi-Agent System

## Overview

This workshop follows a **progressive learning approach** where we start with a simple LLM and gradually build up to a complete multi-agent system with LangGraph and ReAct.

## 📚 Workshop Progression

###

 **Stage 1: The Problem** (Basic LLM Chatbot)
**File**: Create `notebooks/01_basic_llm.ipynb` or demo in terminal

**What to Show:**
```python
from groq import Groq
client = Groq(api_key="...")

# Ask LLM to plan a trip
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{
        "role": "user",
        "content": "Plan a 4-day trip to Tokyo for $1500"
    }]
)
print(response.choices[0].message.content)
```

**Problems to Highlight:**
- ❌ Makes up flight numbers and prices
- ❌ No real data
- ❌ Different results each time
- ❌ Can't verify budget is actually correct
- ❌ No reasoning - just an answer

**Key Takeaway**: "A single LLM is like asking one person to be expert at everything!"

---

### **Stage 2: Adding Specialization** (First Agent)
**File**: `notebooks/02_flight_agent.ipynb`

**What to Show:**
1. Load real flight data from JSON
2. Create a specialized Flight Agent
3. Show it filters data, then uses LLM for selection

```python
# Load real data
with open('data/flights.json') as f:
    flights = json.load(f)

# Flight Agent
def flight_agent(origin, dest, budget):
    # 1. Filter with logic
    available = [f for f in flights 
                 if f['origin']==origin and f['price']<=budget]
    
    # 2. Use LLM for selection
    llm_picks_best_from(available)
    
    return real_bookable_flight
```

**Comparison Side-by-Side:**
- Basic LLM: "Flight XYZ123 for $450" (made up)
- Flight Agent: "Flight FL001 for $450" (real, from data)

**Benefits Shown:**
- ✅ Real data
- ✅ Bookable options
- ✅ Budget guaranteed
- ✅ Consistent results
- ✅ Specialized domain knowledge

**Key Takeaway**: "Hybrid approach: Logic for filtering, AI for selection!"

---

### **Stage 3: Multi-Agent Coordination** (Multiple Agents)
**File**: `notebooks/03_multi_agent.ipynb`

**What to Show:**
Add Accommodation and Itinerary agents, show coordination challenge:

```python
# Problem: How do agents share information?

# Flight agent runs first
flight_result = flight_agent(budget=1500*0.4)  # $600
flight_cost = 450

# Accommodation needs to know remaining budget!
remaining = 1500 - 450  # $1050 left
acc_result = accommodation_agent(budget=remaining*0.5)
```

**The Challenge:**
- Information must flow between agents
- Budget tracking becomes critical
- Order of execution matters
- Hard to modify workflow

**Simple Coordinator:**
```python
def simple_coordinator(user_input):
    # Hard-coded workflow
    flight = flight_agent(...)
    accommodation = accommodation_agent(budget - flight.cost)
    itinerary = itinerary_agent(budget - flight - accommodation)
    return combined_plan
```

**Problems with Simple Approach:**
- ❌ Hard-coded workflow
- ❌ Difficult to add new agents
- ❌ No error handling
- ❌ Can't visualize
- ❌ No retry logic

**Key Takeaway**: "We need better tools for orchestration!"

---

### **Stage 4: LangGraph Workflow** (Professional Orchestration)
**File**: `notebooks/04_langgraph.ipynb`

**What to Show:**
Replace simple coordinator with LangGraph:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

# Define shared state
class TravelState(TypedDict):
    origin: str
    destination: str
    budget: float
    flight_result: dict
    accommodation_result: dict

# Create workflow
workflow = StateGraph(TravelState)

# Add agent nodes
workflow.add_node("flight", flight_agent_node)
workflow.add_node("accommodation", accommodation_agent_node)

# Define flow
workflow.set_entry_point("flight")
workflow.add_edge("flight", "accommodation")
workflow.add_edge("accommodation", END)

# Execute
app = workflow.compile()
result = app.invoke(initial_state)
```

**Visual Comparison:**

Before (Simple):
```
function → function → function
(hidden flow, manual passing)
```

After (LangGraph):
```
    START
      ↓
   [Flight Node]
      ↓
   [Accommodation Node]
      ↓
     END

Clear, visual, modifiable!
```

**Benefits:**
- ✅ Explicit state management
- ✅ Visual workflow
- ✅ Easy to modify
- ✅ Type-safe
- ✅ Can add conditional edges

**Key Takeaway**: "LangGraph makes workflows explicit and manageable!"

---

### **Stage 5: ReAct Framework** (Transparent Reasoning)
**File**: `notebooks/05_react.ipynb`

**What to Show:**
Add ReAct pattern to make decisions transparent:

**Before:**
```
Agent: "I recommend Flight FL001"
User: "Why?" 🤷
```

**After (ReAct):**
```
Agent: 
💭 Thought: Budget is $600. I see 5 options ranging $320-$680.
          Need to balance cost with convenience.

🎯 Action: Recommend Flight FL001 at $450, morning departure, direct.

👁️ Observation: Mid-range price but excellent timing. Saves $130 vs
          business class while maintaining convenience.
```

**Implementation:**
```python
# Update prompts to use ReAct format
prompt = """
Use ReAct framework:

Thought: [Analyze the situation]
Action: [Your specific recommendation]
Observation: [Trade-offs and insights]
"""

# Parse structured output
react_response = llm.generate_react(prompt)
# Returns: {thought: "...", action: "...", observation: "..."}
```

**Benefits:**
- ✅ See agent reasoning
- ✅ Understand trade-offs
- ✅ Debug decisions
- ✅ Build trust
- ✅ Improve prompts

**Key Takeaway**: "ReAct makes AI thinking visible!"

---

### **Stage 6: Complete System** (Production-Ready)
**File**: `notebooks/06_complete.ipynb` + `app.py`

**What to Show:**
Bring everything together:

1. **Multiple specialized agents**
   - Flight, Accommodation, Itinerary, Budget

2. **LangGraph orchestration**
   - Clear workflow
   - State management
   - Node transitions

3. **ReAct reasoning**
   - Every agent shows thinking
   - Transparent decisions

4. **Streamlit UI**
   - User-friendly interface
   - Display all reasoning
   - Interactive

**The Complete Flow:**
```
User Input
    ↓
[Parse Node]  💭 Extract parameters
    ↓          🎯 Identify origin, dest, budget
    ↓          👁️ All params found
    ↓
[Flight Node]  💭 Compare 12 options
    ↓          🎯 Recommend FL001
    ↓          👁️ Best value for morning departure
    ↓
[Accommodation Node]  💭 $1050 remaining
    ↓                  🎯 Recommend Tokyo Central
    ↓                  👁️ Saves budget, central location
    ↓
[Itinerary Node]  💭 Balance free & paid activities
    ↓              🎯 3-day plan, $80 total
    ↓              👁️ Leaves budget buffer
    ↓
[Budget Node]  💭 Calculate all costs
    ↓           🎯 $1310 total
    ↓           👁️ Within budget, $190 remaining
    ↓
Final Plan ✨
```

**Key Takeaway**: "Production-ready multi-agent system!"

---

## 🎯 Workshop Delivery Guide

### **Recommended Flow** (2-3 hours)

**Part 1: The Problem (30 min)**
- Start with basic LLM (Stage 1)
- Run it multiple times, show inconsistency
- Discuss problems
- Set up the motivation

**Part 2: Adding Intelligence (45 min)**
- Introduce first agent (Stage 2)
- Show real data usage
- Compare with basic approach
- Add more agents (Stage 3)
- Show coordination challenges

**BREAK** (15 min)

**Part 3: Professional Patterns (60 min)**
- Introduce LangGraph (Stage 4)
- Live code adding nodes
- Show visual workflow
- Add ReAct (Stage 5)
- See transparent reasoning

**Part 4: Integration (30 min)**
- Show complete system (Stage 6)
- Demo Streamlit app
- Discuss production patterns
- Q&A and extensions

---

## 📝 Instructor Notes

### **Key Points to Emphasize:**

1. **Progressive Improvement**
   - Each stage solves specific problems
   - No stage is "wrong" - just limited

2. **Real-World Patterns**
   - These aren't toy examples
   - Same patterns used in production

3. **Hybrid Approach**
   - Logic + AI is powerful
   - Not everything needs LLM

4. **Transparency Matters**
   - Users need to trust AI
   - ReAct enables debugging

### **Common Questions:**

**Q: Why not just use RAG?**
A: RAG is for knowledge retrieval. Agents are for task execution with reasoning.

**Q: Is this over-engineered?**
A: For simple tasks, yes. But these patterns scale to complex systems.

**Q: Can I use other LLMs?**
A: Yes! Just swap the client. Patterns remain the same.

**Q: What about cost?**
A: Groq is fast and cheap. Production would add caching and smarter routing.

---

## 🚀 Quick Start for Instructors

1. **Setup**:
   ```bash
   pip install -r requirements.txt
   cp env.example .env  # Add your key
   ```

2. **Test the complete system**:
   ```bash
   streamlit run app.py
   ```

3. **Prepare notebooks**:
   - Use Jupyter or VS Code
   - Test all code cells
   - Prepare comparison examples

4. **Have backup**:
   - Pre-run examples in case of API issues
   - Screenshot key comparisons
   - PDF of slides as backup

---

## 📚 Additional Resources

- **LANGGRAPH_GUIDE.md** - Deep dive on LangGraph
- **REACT_FRAMEWORK.md** - Deep dive on ReAct
- **WORKSHOP_OVERVIEW.md** - Big picture architecture
- **README.md** - Setup and running instructions

---

**Ready to teach? Start with Stage 1 and build up!** 🎓

