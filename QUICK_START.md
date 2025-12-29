# ⚡ Quick Start Guide

## For Workshop Participants

### 🎯 Goal
Build a multi-agent travel planner from scratch, step by step!

---

## ✅ Setup (5 minutes)

### 1. Clone and Enter Directory
```bash
git clone <repo-url>
cd nushacknroll-marvell
```

### 2. Create Virtual Environment
```bash
# Create
python -m venv venv

# Activate (Windows PowerShell)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup API Key
```bash
# Copy template
Copy-Item env.example .env   # Windows
cp env.example .env          # Mac/Linux

# Edit .env file and add your key:
# GROQ_API_KEY=gsk_your_actual_key_here
```

Get your free API key: https://console.groq.com/keys

---

## 🎓 Workshop Path

### Option A: Code Along (Recommended)

Follow the instructor through 6 stages:

**📍 You Are Here: Stage 1**

1. **Basic LLM** (15 min) - Start here!
2. **First Agent** (20 min) - Add specialization
3. **Multi-Agent** (25 min) - Coordinate agents  
4. **LangGraph** (30 min) - Professional workflow
5. **ReAct** (25 min) - Transparent reasoning
6. **Complete** (15 min) - Put it together

**Detailed guide**: Open `WORKSHOP_STRUCTURE.md`

### Option B: See It Working First

```bash
streamlit run app.py
```

Then go back and follow Stage 1-6 to understand how!

---

## 📝 Stage 1: Your First Task

### Open Python/Jupyter and try:

```python
# Install in your notebook if needed
# !pip install groq python-dotenv

import os
from dotenv import load_dotenv
from groq import Groq

# Load your API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Ask the LLM to plan a trip
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{
        "role": "user",
        "content": "Plan a 4-day trip to Tokyo for $1500. Include flights, hotel, and activities."
    }],
    temperature=0.2
)

print(response.choices[0].message.content)
```

### 🤔 Discussion Questions:
1. Run it multiple times - do you get the same result?
2. Are the flight numbers real?
3. Can you verify the budget is actually $1500?
4. How does it choose between options?

### ❌ Problems You'll Notice:
- Makes up flight numbers
- Prices aren't real
- Can't verify budget math
- No reasoning shown
- Different results each run

**This is WHY we need agents!** → Proceed to Stage 2

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'groq'"
```bash
pip install -r requirements.txt
```

### "GROQ_API_KEY not found"
- Make sure `.env` file exists (not `env.example`)
- Check it has: `GROQ_API_KEY=gsk_...`
- Restart your Python kernel/terminal

### "ImportError: cannot import name 'StateGraph'"
```bash
pip install langgraph
```

### Still stuck?
- Check `SETUP_INSTRUCTIONS.md` for detailed setup
- Ask the instructor
- Verify Python 3.10+ with: `python --version`

---

## 📚 Files You'll Use

### For Learning:
- `WORKSHOP_STRUCTURE.md` - Stage-by-stage guide
- `LANGGRAPH_GUIDE.md` - Deep dive on LangGraph
- `REACT_FRAMEWORK.md` - Deep dive on ReAct

### For Reference:
- `agents/` - Final agent implementations
- `app.py` - Complete Streamlit app
- `data/` - Mock JSON data

### For Help:
- `SETUP_INSTRUCTIONS.md` - Detailed setup
- `README.md` - Overview and architecture

---

## 🎯 Learning Checkpoints

After each stage, you should be able to:

**Stage 1**: ✅ Explain why basic LLM isn't enough  
**Stage 2**: ✅ Create a specialized agent with real data  
**Stage 3**: ✅ Coordinate multiple agents  
**Stage 4**: ✅ Use LangGraph for workflow  
**Stage 5**: ✅ Add ReAct for transparency  
**Stage 6**: ✅ Build production-ready system  

---

## 💪 After the Workshop

### Immediate Next Steps:
1. Run the complete app: `streamlit run app.py`
2. Try different travel requests
3. Read the agent code in `agents/`
4. Explore ReAct reasoning in the UI

### Extension Ideas:
- Add a weather agent
- Add budget optimization loop
- Connect to real flight APIs
- Deploy to Streamlit Cloud

### Share Your Work:
- Push to your GitHub
- Add your own agents
- Show it to friends!

---

**Ready? Let's build! 🚀**

**Start here**: Open `WORKSHOP_STRUCTURE.md` → Stage 1

