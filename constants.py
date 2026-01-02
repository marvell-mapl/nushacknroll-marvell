"""
Constants and shared configuration for the travel planner.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# ============================================
# LLM CONFIGURATION
# ============================================

LLM_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
LLM_TEMPERATURE = 0
LLM_API_KEY = os.getenv("GROQ_API_KEY")


def get_llm():
    """Get configured LLM instance."""
    return ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        groq_api_key=LLM_API_KEY
    )


# ============================================
# DATA LOADING
# ============================================

DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "flights.json", 'r', encoding='utf-8') as f:
    FLIGHTS_DATA = json.load(f)

with open(DATA_DIR / "accommodations.json", 'r', encoding='utf-8') as f:
    ACCOMMODATIONS_DATA = json.load(f)

with open(DATA_DIR / "attractions.json", 'r', encoding='utf-8') as f:
    ATTRACTIONS_DATA = json.load(f)

