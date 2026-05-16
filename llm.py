"""Unified LLM interface for multi-agent system using Ollama.

This module provides a wrapper around Ollama for consistent LLM calls
with temperature control, seed-based reproducibility, and metadata tracking.
"""

import ollama
import time
from typing import Optional, Tuple
import random


def call_llm(
    prompt: str, 
    model: str = "mistral", 
    temperature: float = 0.9,
    seed: Optional[int] = None
) -> Tuple[str, dict]:
    """Call the Ollama LLM with controlled parameters.
    
    This function provides a unified interface to the Ollama LLM service,
    supporting temperature control for response diversity and seed-based
    reproducibility for deterministic behavior in experiments.
    
    Args:
        prompt (str): The input prompt for the LLM.
        model (str, optional): Model name (e.g., 'mistral'). Defaults to 'mistral'.
        temperature (float, optional): Response diversity (0.0-1.0).
                                      0.0 = deterministic, 1.0 = maximum randomness.
                                      Defaults to 0.9.
        seed (int, optional): Random seed for reproducibility. If provided,
                             ensures deterministic behavior. Defaults to None.
    
    Returns:
        Tuple[str, dict]: A tuple containing:
            - str: The LLM's response text
            - dict: Metadata dictionary with keys:
                - latency_ms (float): Response time in milliseconds
                - model (str): Model used
                - temperature (float): Temperature used
                - input_tokens (int): Approximate input token count
                - output_tokens (int): Approximate output token count
    
    Raises:
        RuntimeError: If the LLM call fails (Ollama service not running, etc.)
    
    Example:
        >>> response, meta = call_llm(
        ...     prompt="Solve 2x + 3 = 7",
        ...     temperature=0.7,
        ...     seed=42
        ... )
        >>> print(f"Response: {response}")
        >>> print(f"Latency: {meta['latency_ms']:.1f}ms")
    """
    
    if seed is not None:
        random.seed(seed)
    
    start_time = time.time()
    
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": temperature
            }
        )
        
        latency_ms = (time.time() - start_time) * 1000
        content = response['message']['content']
        
        metadata = {
            "latency_ms": latency_ms,
            "model": model,
            "temperature": temperature,
            "input_tokens": len(prompt.split()),
            "output_tokens": len(content.split()),
        }
        
        return content, metadata
        
    except Exception as e:
        raise RuntimeError(f"Failed to call LLM model '{model}': {str(e)}")