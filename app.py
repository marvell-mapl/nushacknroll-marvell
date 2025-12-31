"""
Multi-Agent Travel Planner - Simplified Streamlit Interface
Basic chat interface using core Streamlit components only.
"""

import streamlit as st
from agents import build_travel_agent
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()


# ============================================
# HELPER FUNCTIONS
# ============================================

def convert_dict_to_lc_message(msg):
    """Convert session state message dict to LangChain message object."""
    if msg["role"] == "user":
        return HumanMessage(content=msg["content"])
    elif msg["role"] == "assistant":
        return AIMessage(content=msg["content"])


# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Travel Agent",
    page_icon="✈️",
    layout="centered"
)


# ============================================
# SESSION STATE INITIALIZATION
# ============================================

# Initialize messages
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize agent
if 'agent' not in st.session_state:
    try:
        st.session_state.agent = build_travel_agent()
    except Exception as e:
        st.error(f"Failed to initialize travel agent: {str(e)}")
        st.stop()


# ============================================
# MAIN INTERFACE
# ============================================

# Title
st.title("✈️ AI Travel Planner")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
prompt = st.chat_input("Ask me anything about travel planning...")

# Process user input
if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Convert to LangChain format
                lc_messages = [convert_dict_to_lc_message(msg) for msg in st.session_state.messages]
                
                # Invoke agent with simplified state (only messages field needed)
                response = st.session_state.agent.invoke({
                    "messages": lc_messages
                })
                
                # Get final response
                assistant_msg = response["messages"][-1].content
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                assistant_msg = error_msg
        
        # Display response after spinner
        st.write(assistant_msg)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
    
    # Rerun to update display
    st.rerun()


# ============================================
# SIDEBAR - SIMPLE CONTROLS
# ============================================

with st.sidebar:
    st.title("Controls")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    st.write(f"Messages: {len(st.session_state.messages)}")
