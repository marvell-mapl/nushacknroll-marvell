"""
Official Groq API Test
Following: https://console.groq.com/docs/quickstart
"""
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize client (official way from Groq docs)
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

print("🧪 Testing Groq API (Official Method)")
print("=" * 70)

try:
    # Official example from Groq documentation
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of fast language models",
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    print("✅ SUCCESS! API is working correctly.\n")
    print("Response:")
    print(chat_completion.choices[0].message.content)
    print("\n" + "=" * 70)
    print("🎉 Your API key is set up correctly!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Check if .env file exists: ls .env")
    print("2. Check API key: Get-Content .env")
    print("3. Verify internet connection")
    print("4. Try regenerating API key at: https://console.groq.com/keys")

