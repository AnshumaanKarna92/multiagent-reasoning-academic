"""Four-agent collaborative problem-solving system for mathematical reasoning.

This module implements the core agents in the multi-agent LLM system:
- TeacherAgent: Provides pedagogical guidance and explanations
- StudentAgent: Generates solution attempts and asks clarifying questions
- EvaluatorAgent: Independently verifies solution correctness
- CoordinatorAgent: Manages conversation flow and termination logic
"""

from typing import Optional, Dict, Any, List, Tuple
from llm import call_llm


class TeacherAgent:
    """Pedagogical guidance agent for mathematical problem-solving.
    
    The TeacherAgent provides structured guidance to help students solve problems
    without directly giving answers. It explains concepts, identifies errors,
    and guides the student toward correct solutions.
    
    Attributes:
        temperature (float): LLM temperature controlling response diversity (0.0-1.0).
                           Higher values produce more creative/diverse responses.
    """
    
    def __init__(self, temperature: float = 0.9):
        """Initialize the TeacherAgent with specified temperature.
        
        Args:
            temperature (float, optional): LLM temperature. Defaults to 0.9.
        """
        self.temperature = temperature
    
    def respond(self, context: str) -> Tuple[str, dict]:
        """Generate pedagogical guidance for the given problem context.
        
        Args:
            context (str): The mathematical problem statement or problem + feedback.
                         May include evaluator feedback for guided improvement.
        
        Returns:
            Tuple[str, dict]: A tuple containing:
                - str: The teacher's guidance response
                - dict: Metadata including latency_ms, output_tokens, temperature
        """
        
        prompt = f"""
You are a math teacher.

ORIGINAL problem:
{context}

If the problem is already solved → ONLY summarize.
DO NOT give new problems.

NEVER introduce new equations.
        """
        response, metadata = call_llm(prompt, temperature=self.temperature)
        return response, metadata




class StudentAgent:
    """Problem-solving agent that generates solution attempts.
    
    The StudentAgent attempts to solve mathematical problems based on the
    original problem statement and teacher guidance. It provides step-by-step
    reasoning and extracts the final answer.
    
    Attributes:
        temperature (float): LLM temperature controlling response diversity (0.0-1.0).
                           Higher values increase solution diversity but may reduce coherence.
    """
    
    def __init__(self, temperature: float = 0.9):
        """Initialize the StudentAgent with specified temperature.
        
        Args:
            temperature (float, optional): LLM temperature. Defaults to 0.9.
        """
        self.temperature = temperature
    
    def respond(self, context: str) -> Tuple[str, dict]:
        """Attempt to solve the given problem.
        
        Args:
            context (str): The problem statement and any teacher guidance provided.
                         Contains the original problem and pedagogical hints.
        
        Returns:
            Tuple[str, dict]: A tuple containing:
                - str: The student's solution attempt with step-by-step reasoning
                - dict: Metadata including latency_ms, output_tokens, temperature
        """
        
        prompt = f"""
You are solving ONE problem:

{context}

If already solved → just confirm.

DO NOT create new problems.
        """
        response, metadata = call_llm(prompt, temperature=self.temperature)
        return response, metadata




class EvaluatorAgent:
    """Independent solution verification agent.
    
    The EvaluatorAgent acts as a strict grader, independently solving the problem
    and comparing its solution with the student's answer. This provides independent
    verification to catch errors and prevent error propagation.
    
    Attributes:
        temperature (float): LLM temperature controlling response diversity (0.0-1.0).
                           Typically kept low (0.3) for deterministic verification.
    """
    
    def __init__(self, temperature: float = 0.9):
        """Initialize the EvaluatorAgent with specified temperature.
        
        Args:
            temperature (float, optional): LLM temperature. Typically 0.3-0.5 for determinism.
                                         Defaults to 0.9.
        """
        self.temperature = temperature
    
    def respond(self, context: str) -> Tuple[str, dict]:
        """Evaluate the correctness of the student's solution.
        
        Args:
            context (str): The original problem and the student's solution attempt.
                         Evaluator independently solves and compares answers.
        
        Returns:
            Tuple[str, dict]: A tuple containing:
                - str: Either 'FINAL CORRECT' or 'WRONG' (binary decision)
                - dict: Metadata including latency_ms, output_tokens, temperature
        """
        
        prompt = f"""
You are a STRICT mathematical evaluator.

Problem and solution:
{context}

Steps:
1. Solve the problem independently
2. Extract the answer from the student's response
3. Compare BOTH answers

IMPORTANT RULES:
- If answers do NOT match → output EXACTLY: WRONG
- If answers match → output EXACTLY: FINAL CORRECT

DO NOT explain.
DO NOT justify.
ONLY output one of:
FINAL CORRECT
WRONG
        """
        response, metadata = call_llm(prompt, temperature=self.temperature)
        return response, metadata




class CoordinatorAgent:
    """Flow control and termination decision agent.
    
    The CoordinatorAgent makes decisions about continuing or stopping the
    problem-solving discussion based on the evaluator's verdict and conversation
    history. It prevents infinite loops and unnecessary iterations.
    
    Attributes:
        temperature (float): LLM temperature controlling decision consistency (0.0-1.0).
                           Typically kept low (0.3) for deterministic decisions.
    """
    
    def __init__(self, temperature: float = 0.9):
        """Initialize the CoordinatorAgent with specified temperature.
        
        Args:
            temperature (float, optional): LLM temperature. Typically 0.3 for determinism.
                                         Defaults to 0.9.
        """
        self.temperature = temperature
    
    def respond(self, conversation_history: List[Tuple[str, str]], evaluator_decision: str) -> Tuple[str, dict]:
        """Make STOP/CONTINUE decision based on verification status.
        
        Args:
            conversation_history (List[Tuple[str, str]]): Full conversation history.
                                 Each tuple contains (agent_name, agent_response).
            evaluator_decision (str): The evaluator's verdict ('FINAL CORRECT' or 'WRONG').
        
        Returns:
            Tuple[str, dict]: A tuple containing:
                - str: Either 'CONTINUE' or 'STOP' (binary decision)
                - dict: Metadata including latency_ms, output_tokens, temperature
        """
        
        history_str = "\n".join([f"{role}: {msg[:150]}..." for role, msg in conversation_history[-6:]])
        
        prompt = f"""
You are a coordinator.

Recent conversation:
{history_str}

Evaluator decision: {evaluator_decision}

Decide:
- CONTINUE → if problem not solved
- STOP → if problem solved and verified

Output ONLY one word: CONTINUE or STOP
        """
        response, metadata = call_llm(prompt, temperature=self.temperature)
        return response, metadata
