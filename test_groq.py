"""
Test the ChatGroq LLM wrapper
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append('.')

from utils.llm import get_llm

load_dotenv()

def test_basic_generation():
    """Test basic LLM generation"""
    print("=" * 70)
    print("TEST 1: Basic LLM Generation")
    print("=" * 70)
    
    try:
        llm = get_llm()
        response = llm.generate("Say 'Hello from ChatGroq!' in one sentence.")
        print(f"✅ SUCCESS!")
        print(f"Response: {response}\n")
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
        return False


def test_react_generation():
    """Test ReAct-formatted generation"""
    print("=" * 70)
    print("TEST 2: ReAct Framework")
    print("=" * 70)
    
    try:
        llm = get_llm()
        
        system_prompt = """You are a helpful assistant using the ReAct framework.

ALWAYS respond in this format:
Thought: [Your reasoning]
Action: [What you recommend]
Observation: [Your insights]
"""
        
        prompt = "Recommend a good programming language for beginners."
        
        react_response = llm.generate_react(prompt, system_prompt)
        
        print(f"✅ SUCCESS!")
        print(f"\n💭 Thought: {react_response['thought']}")
        print(f"\n🎯 Action: {react_response['action']}")
        print(f"\n👁️  Observation: {react_response['observation']}\n")
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
        return False


def test_with_system_prompt():
    """Test with system prompt"""
    print("=" * 70)
    print("TEST 3: With System Prompt")
    print("=" * 70)
    
    try:
        llm = get_llm()
        
        system_prompt = "You are a travel expert. Be concise."
        prompt = "Recommend one city in Japan for first-time visitors."
        
        response = llm.generate(prompt, system_prompt)
        print(f"✅ SUCCESS!")
        print(f"Response: {response}\n")
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
        return False


if __name__ == "__main__":
    print("\n🧪 Testing ChatGroq LLM Wrapper\n")
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ ERROR: GROQ_API_KEY not found in environment!")
        print("Make sure you have a .env file with your API key.")
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}\n")
    
    # Run tests
    results = []
    results.append(("Basic Generation", test_basic_generation()))
    results.append(("ReAct Framework", test_react_generation()))
    results.append(("System Prompt", test_with_system_prompt()))
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + ("🎉 All tests passed!" if all_passed else "⚠️  Some tests failed"))
    print("=" * 70)
