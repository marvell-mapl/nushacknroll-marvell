"""
Multi-Agent Travel Planner - Streamlit UI
A workshop demo showing agent orchestration for travel planning.
"""

import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from agents.supervisor import orchestrate_planning


def display_flight_section(flight_data):
    """Display flight recommendation in a formatted section."""
    st.subheader("✈️ Flight Recommendation")
    
    if flight_data["recommended_flight"] is None:
        st.error("No suitable flights found.")
        return
    
    flight = flight_data["recommended_flight"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Airline:** {flight['airline']}  
        **Flight ID:** {flight['id']}  
        **Class:** {flight['class']}  
        **Route:** {flight['origin']} → {flight['destination']}
        """)
    
    with col2:
        st.markdown(f"""
        **Price:** ${flight['price']}  
        **Departure:** {flight['departure_time']}  
        **Arrival:** {flight['arrival_time']}  
        **Duration:** {flight['duration_hours']} hours
        """)
    
    # Display ReAct reasoning
    if "react_breakdown" in flight_data and flight_data["react_breakdown"]:
        with st.expander("🧠 Agent Reasoning (ReAct Framework)"):
            react = flight_data["react_breakdown"]
            if react.get("thought"):
                st.markdown(f"**💭 Thought:** {react['thought']}")
            if react.get("action"):
                st.markdown(f"**🎯 Action:** {react['action']}")
            if react.get("observation"):
                st.markdown(f"**👁️ Observation:** {react['observation']}")
    else:
        with st.expander("💡 Why this flight?"):
            st.write(flight_data["reasoning"])
    
    if flight_data["alternatives"]:
        with st.expander("🔄 Alternative options"):
            for alt in flight_data["alternatives"]:
                st.write(f"- {alt['airline']} {alt['id']}: ${alt['price']} ({alt['duration_hours']}hrs)")


def display_accommodation_section(accommodation_data):
    """Display accommodation recommendation in a formatted section."""
    st.subheader("🏨 Accommodation Recommendation")
    
    if accommodation_data["recommended_accommodation"] is None:
        st.error("No suitable accommodations found.")
        return
    
    acc = accommodation_data["recommended_accommodation"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Name:** {acc['name']}  
        **Type:** {acc['type']}  
        **Location:** {acc['location']}  
        **Rating:** {acc['rating']} ⭐
        """)
    
    with col2:
        st.markdown(f"""
        **Price per night:** ${acc['price_per_night']}  
        **Total cost:** ${accommodation_data['total_cost']}  
        **Amenities:** {', '.join(acc['amenities'][:4])}
        """)
    
    st.info(acc['description'])
    
    # Display ReAct reasoning
    if "react_breakdown" in accommodation_data and accommodation_data["react_breakdown"]:
        with st.expander("🧠 Agent Reasoning (ReAct Framework)"):
            react = accommodation_data["react_breakdown"]
            if react.get("thought"):
                st.markdown(f"**💭 Thought:** {react['thought']}")
            if react.get("action"):
                st.markdown(f"**🎯 Action:** {react['action']}")
            if react.get("observation"):
                st.markdown(f"**👁️ Observation:** {react['observation']}")
    else:
        with st.expander("💡 Why this accommodation?"):
            st.write(accommodation_data["reasoning"])


def display_itinerary_section(itinerary_data):
    """Display day-by-day itinerary in a formatted section."""
    st.subheader("📅 Daily Itinerary")
    
    if not itinerary_data["daily_plan"]:
        st.warning("No itinerary created.")
        return
    
    for day_plan in itinerary_data["daily_plan"]:
        with st.expander(f"Day {day_plan['day']}", expanded=True):
            if day_plan["activities"]:
                for activity in day_plan["activities"]:
                    st.markdown(f"""
                    **{activity['name']}** ({activity['category']})  
                    ⏱️ {activity['duration_hours']} hours | 💵 ${activity['cost']}  
                    _{activity['description']}_
                    """)
                    st.divider()
            else:
                st.write("No activities planned for this day.")
    
    st.metric("Total Activities Cost", f"${itinerary_data['total_cost']}")
    
    # Display ReAct reasoning
    if "react_breakdown" in itinerary_data and itinerary_data["react_breakdown"]:
        with st.expander("🧠 Agent Reasoning (ReAct Framework)"):
            react = itinerary_data["react_breakdown"]
            if react.get("thought"):
                st.markdown(f"**💭 Thought:** {react['thought']}")
            if react.get("action"):
                st.markdown(f"**🎯 Action:** {react['action']}")
            if react.get("observation"):
                st.markdown(f"**👁️ Observation:** {react['observation']}")
    else:
        with st.expander("💡 Itinerary Planning Notes"):
            st.write(itinerary_data["summary"])


def display_budget_section(budget_data):
    """Display budget breakdown and analysis."""
    st.subheader("💰 Budget Analysis")
    
    # Status indicator
    if budget_data["is_within_budget"]:
        st.success(f"✅ Within Budget! ${budget_data['remaining']:.2f} remaining")
    else:
        st.error(f"⚠️ Over Budget by ${abs(budget_data['remaining']):.2f}")
    
    # Budget breakdown
    st.markdown("**Cost Breakdown:**")
    breakdown = budget_data["breakdown"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Flights", f"${breakdown['flights']:.2f}")
        st.metric("Accommodation", f"${breakdown['accommodation']:.2f}")
    
    with col2:
        st.metric("Activities", f"${breakdown['activities']:.2f}")
        st.metric("Estimated Extras", f"${breakdown['estimated_extras']:.2f}")
    
    st.metric("Total Spent", f"${breakdown['total']:.2f}", 
              delta=f"{budget_data['percentage_used']:.1f}% of budget")
    
    # Display ReAct reasoning and analysis
    if "react_breakdown" in budget_data and budget_data["react_breakdown"]:
        with st.expander("🧠 Agent Reasoning (ReAct Framework)"):
            react = budget_data["react_breakdown"]
            if react.get("thought"):
                st.markdown(f"**💭 Thought:** {react['thought']}")
            if react.get("action"):
                st.markdown(f"**🎯 Action:** {react['action']}")
            if react.get("observation"):
                st.markdown(f"**👁️ Observation:** {react['observation']}")
    else:
        with st.expander("📊 Detailed Analysis"):
            st.write(budget_data["analysis"])
    
    if budget_data["suggestions"]:
        with st.expander("💡 Optimization Suggestions"):
            for suggestion in budget_data["suggestions"]:
                st.write(f"- {suggestion}")


def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="Multi-Agent Travel Planner",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Header
    st.title("✈️ Multi-Agent Travel Planner")
    st.markdown("""
    **Workshop Demo:** AI-powered travel planning using multiple specialized agents.  
    Each agent focuses on one aspect: flights, accommodation, itinerary, and budget.
    """)
    
    st.divider()
    
    # Input section
    st.subheader("📝 Describe Your Trip")
    
    # Example requests
    examples = [
        "I want to visit Tokyo for 4 days with a budget of $1500. I love culture and food.",
        "Plan a 5-day trip to Paris with $2000. Prefer central locations.",
        "Beach vacation in Bali for 3 days, budget $800. Looking for relaxation.",
    ]
    
    selected_example = st.selectbox(
        "Try an example (or write your own below):",
        [""] + examples
    )
    
    user_input = st.text_area(
        "Your travel request:",
        value=selected_example if selected_example else "",
        height=100,
        placeholder="Example: I want to visit Tokyo for 4 days with a budget of $1500. I love culture and food."
    )
    
    # Generate button
    generate_button = st.button("🚀 Generate Travel Plan", type="primary", use_container_width=True)
    
    # Process and display results
    if generate_button:
        if not user_input.strip():
            st.warning("Please enter a travel request.")
            return
        
        with st.spinner("🤔 Our agents are working on your travel plan..."):
            try:
                # Orchestrate the planning
                result = orchestrate_planning(user_input)
                
                if not result["success"]:
                    st.error("Unable to create a complete travel plan. Try adjusting your requirements.")
                    return
                
                # Display results
                st.divider()
                st.header("🎯 Your Travel Plan")
                
                # Summary section
                st.info(result["summary"])
                
                # Main content in tabs
                tab1, tab2, tab3, tab4 = st.tabs(["✈️ Flight", "🏨 Accommodation", "📅 Itinerary", "💰 Budget"])
                
                with tab1:
                    display_flight_section(result["flight"])
                
                with tab2:
                    display_accommodation_section(result["accommodation"])
                
                with tab3:
                    display_itinerary_section(result["itinerary"])
                
                with tab4:
                    display_budget_section(result["budget"])
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)
    
    # Footer
    st.divider()
    st.markdown("""
    <small>
    **Tech Stack:** Python • Streamlit • LangChain • Groq (Llama 3.1)  
    **Workshop:** Multi-Agent AI Systems
    </small>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

