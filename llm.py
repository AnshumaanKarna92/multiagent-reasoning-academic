"""
Language model interface for agent communication.

This module handles all interactions with Ollama LLM instances,
providing a unified interface for agent-to-model communication.
"""

from typing import Optional
import ollama


def call_llm(prompt: str, model: str = "mistral") -> str:
    """
    Call the language model with a given prompt.
    
    This function abstracts LLM interaction, allowing agents to communicate
    with the language model using a standardized interface. The temperature
    parameter is set for balanced creativity while maintaining coherence.
    
    Args:
        prompt: The input prompt or instruction for the model
        model: The model identifier (default: "mistral")
        
    Returns:
        The text response from the language model
        
    Raises:
        ollama.RequestError: If the API request fails or model is unavailable
        
    Note:
        Requires Ollama to be running with the specified model available.
        See requirements.txt for setup instructions.
    """
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.9
            }
        )
        return response['message']['content']
    except Exception as e:
        raise RuntimeError(f"Failed to call LLM model '{model}': {str(e)}")