"""
Agent definitions for multi-agent problem-solving system.

This module implements specialized agents that collaborate to solve mathematical
problems through structured conversation and feedback loops.
"""

from typing import Optional, Dict, Any
from llm import call_llm


class TeacherAgent:
    """
    Pedagogical agent responsible for explaining problems and guiding solutions.
    
    The Teacher Agent provides problem context and guidance without directly
    solving, encouraging the Student Agent to work through the problem.
    """
    
    def respond(self, context: str) -> str:
        """
        Generate a teaching response based on problem context.
        
        Args:
            context: The problem statement and current conversation state
            
        Returns:
            Teaching explanation or guidance without direct solutions
        """
        prompt = f"""
        You are a math teacher.

        ORIGINAL problem:
        {context}

        If the problem is already solved → ONLY summarize.
        DO NOT give new problems.

        NEVER introduce new equations.
        """
        return call_llm(prompt)


class StudentAgent:
    """
    Problem-solving agent that works through mathematical problems step by step.
    
    The Student Agent focuses on solving the given problem while avoiding
    the creation of new problems or unnecessary extensions.
    """
    
    def respond(self, context: str) -> str:
        """
        Generate a solution response based on problem context.
        
        Args:
            context: The problem statement and guidance from the Teacher
            
        Returns:
            Solution attempt or confirmation if problem is already solved
        """
        prompt = f"""
        You are solving ONE problem:

        {context}

        If already solved → just confirm.

        DO NOT create new problems.
        """
        return call_llm(prompt)


class EvaluatorAgent:
    """
    Verification agent that independently checks solution correctness.
    
    The Evaluator Agent solves the problem independently and compares
    with the Student Agent's answer to provide objective verification.
    """
    
    def respond(self, context: str) -> str:
        """
        Evaluate solution correctness with strict verification.
        
        Args:
            context: Problem statement and student's proposed solution
            
        Returns:
            Either "FINAL CORRECT" or "WRONG" based on verification
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
        return call_llm(prompt)
    

class CoordinatorAgent:
    """
    Control flow agent that manages simulation progression and termination.
    
    The Coordinator Agent monitors the problem-solving process and decides
    whether to continue iteration or halt based on solution verification.
    """
    
    def respond(self, context: str) -> str:
        """
        Determine whether to continue or stop the problem-solving process.
        
        Args:
            context: Conversation history and evaluation results
            
        Returns:
            Either "CONTINUE" or "STOP" based on problem state
        """
        prompt = f"""
        You are a coordinator.

        Based on this conversation:
        {context}

        Decide:
        - CONTINUE → if problem not solved
        - STOP → if problem solved and verified

        Output ONLY one word: CONTINUE or STOP
        """
        return call_llm(prompt)
