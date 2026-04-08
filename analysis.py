"""
Analysis utilities for multi-agent conversation logs.

This module provides functions to analyze the interactions between agents,
measuring efficiency metrics such as convergence speed and redundancy.
"""

from typing import List, Tuple, Dict, Any


def count_rounds(logs: List[Tuple[str, str]]) -> int:
    """
    Count the total number of message exchanges in the conversation.
    
    Args:
        logs: List of (agent_role, message) tuples from the conversation
        
    Returns:
        Total number of messages exchanged
    """
    return len(logs)


def detect_irrelevance(logs: List[Tuple[str, str]]) -> int:
    """
    Count instances where agents produce irrelevant responses.
    
    Args:
        logs: List of (agent_role, message) tuples from the conversation
        
    Returns:
        Number of irrelevant responses detected
    """
    count = 0
    for role, msg in logs:
        if "irrelevant" in msg.lower():
            count += 1
    return count


def detect_repetition(logs: List[Tuple[str, str]]) -> int:
    """
    Identify duplicate or repeated messages in the conversation.
    
    Repetition indicates either divergence in problem-solving or
    failure to make progress toward solution.
    
    Args:
        logs: List of (agent_role, message) tuples from the conversation
        
    Returns:
        Number of repeated messages detected
    """
    seen = set()
    repeats = 0

    for role, msg in logs:
        if msg in seen:
            repeats += 1
        seen.add(msg)

    return repeats


def analyze(logs: List[Tuple[str, str]]) -> Dict[str, Any]:
    """
    Perform comprehensive analysis on multi-agent conversation logs.
    
    This function aggregates various quality metrics to assess the efficiency
    and coherence of the multi-agent problem-solving process.
    
    Args:
        logs: List of (agent_role, message) tuples from the conversation
        
    Returns:
        Dictionary containing analysis metrics:
            total_messages: Combined number of all agent responses
            irrelevant_responses: Count of off-topic or irrelevant messages
            repetitions: Number of duplicate messages in the conversation
    """
    return {
        "total_messages": count_rounds(logs),
        "irrelevant_responses": detect_irrelevance(logs),
        "repetitions": detect_repetition(logs)
    }