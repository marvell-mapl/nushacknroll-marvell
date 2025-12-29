"""
LLM Wrapper for Groq API with ReAct Framework Support
Provides a single, shared interface for all agents to interact with the LLM.
Supports ReAct (Reasoning + Acting) framework for transparent decision-making.

Uses ChatGroq from langchain_groq for better integration and reliability.
"""

import os
import re
from typing import Optional, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


class LLMWrapper:
    """
    Centralized LLM client wrapper using ChatGroq.
    
    Why this exists:
    - Single configuration point for all agents
    - Consistent temperature and model settings
    - Better error handling and connection management
    - Easy to swap providers if needed
    """
    
    def __init__(self, model: str = "llama-3.1-8b-instant", temperature: float = 0.2):
        """
        Initialize the LLM wrapper with ChatGroq.
        
        Args:
            model: Groq model name (default: llama-3.1-8b-instant)
            temperature: Controls randomness (0.2 = more deterministic)
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
        
        # Initialize ChatGroq client
        try:
            self.client = ChatGroq(
                api_key=api_key,
                model_name=model,
                temperature=temperature,
                max_tokens=1024
            )
            self.model = model
            self.temperature = temperature
        except Exception as e:
            raise ConnectionError(
                f"Failed to initialize ChatGroq client: {str(e)}\n"
                "This might be due to:\n"
                "1. Network/proxy issues\n"
                "2. Invalid API key\n"
                "3. Firewall blocking the connection\n"
                "Check your internet connection and API key."
            )
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a completion from the LLM.
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system instructions for the agent
        
        Returns:
            The LLM's text response
        """
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=prompt))
        
        try:
            response = self.client.invoke(messages)
            return response.content.strip()
        
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "network" in error_msg.lower():
                return (
                    "Error calling LLM: Connection error.\n"
                    "Possible causes:\n"
                    "1. Check your internet connection\n"
                    "2. You may be behind a corporate firewall/proxy\n"
                    "3. Groq API may be temporarily unavailable\n"
                    "4. Verify your API key is correct in .env file"
                )
            elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                return (
                    "Error calling LLM: Authentication failed.\n"
                    "Please check your GROQ_API_KEY in the .env file.\n"
                    "Get a free key from: https://console.groq.com/keys"
                )
            return f"Error calling LLM: {error_msg}"
    
    def generate_react(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a ReAct-formatted response from the LLM.
        
        ReAct format expects responses with:
        - Thought: Reasoning about the situation
        - Action: The specific action to take
        - Observation: What was learned from the action
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system instructions (should include ReAct format guidance)
        
        Returns:
            Dictionary with parsed ReAct components:
            {
                "thought": str,
                "action": str,
                "observation": str,
                "raw_response": str,
                "full_reasoning": str
            }
        """
        raw_response = self.generate(prompt, system_prompt)
        
        # Parse ReAct format
        thought = ""
        action = ""
        observation = ""
        
        # Extract Thought
        thought_match = re.search(
            r'Thought:\s*(.+?)(?=\n(?:Action|Observation|$))', 
            raw_response, 
            re.DOTALL | re.IGNORECASE
        )
        if thought_match:
            thought = thought_match.group(1).strip()
        
        # Extract Action
        action_match = re.search(
            r'Action:\s*(.+?)(?=\n(?:Observation|Thought|$))', 
            raw_response, 
            re.DOTALL | re.IGNORECASE
        )
        if action_match:
            action = action_match.group(1).strip()
        
        # Extract Observation
        observation_match = re.search(
            r'Observation:\s*(.+?)(?=\n(?:Thought|Action|$)|$)', 
            raw_response, 
            re.DOTALL | re.IGNORECASE
        )
        if observation_match:
            observation = observation_match.group(1).strip()
        
        return {
            "thought": thought,
            "action": action,
            "observation": observation,
            "raw_response": raw_response,
            "full_reasoning": (
                f"💭 Thought: {thought}\n🎯 Action: {action}\n👁️ Observation: {observation}" 
                if thought else raw_response
            )
        }


# Singleton instance for the entire application
_llm_instance = None


def get_llm() -> LLMWrapper:
    """
    Get or create the shared LLM instance.
    
    Returns:
        Singleton LLMWrapper instance
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMWrapper()
    return _llm_instance
