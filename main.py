"""
Main entry point for multi-agent problem-solving simulation.

This module orchestrates the interaction between specialized agents
(Teacher, Student, Evaluator, Coordinator) to solve mathematical problems
through iterative conversation and feedback.

Usage:
    python main.py
"""

import json
import logging
from typing import List, Tuple, Dict, Any
from agents import TeacherAgent, StudentAgent, EvaluatorAgent, CoordinatorAgent
from analysis import analyze

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

teacher = TeacherAgent()
student = StudentAgent()
evaluator = EvaluatorAgent()
coordinator = CoordinatorAgent()


def save_logs(logs: List[Tuple[str, str]], filename: str = "logs.json") -> None:
    """
    Persist conversation logs to a JSON file for later analysis.
    
    Args:
        logs: List of (agent_role, message) tuples containing conversation history
        filename: Output file path for the JSON logs
    """
    with open(filename, "w") as f:
        json.dump(logs, f, indent=4)
    logger.info(f"Logs saved to {filename}")


def run_simulation(question: str, rounds: int = 5) -> List[Tuple[str, str]]:
    """
    Execute a complete multi-agent problem-solving simulation.
    
    The simulation follows this flow:
    1. Teacher provides problem context and guidance
    2. Student attempts solution within constraints
    3. Evaluator verifies correctness independently
    4. Coordinator decides to continue or halt
    5. Repeat until solution is verified or max rounds reached
    
    Args:
        question: The mathematical problem to solve
        rounds: Maximum number of iteration rounds (default: 5)
        
    Returns:
        List of (agent_role, message) tuples representing the conversation
    """
    logs = []
    logger.info(f"Starting simulation for: {question}")

    original_question = question
    solved = False

    teacher_output = teacher.respond(original_question)
    logger.info(f"Teacher: {teacher_output[:100]}...")
    logs.append(("Teacher", teacher_output))

    for i in range(rounds):
        logger.info(f"Round {i+1}/{rounds}")

        student_input = original_question + "\n" + teacher_output
        student_output = student.respond(student_input)
        logger.info(f"Student: {student_output[:100]}...")
        logs.append(("Student", student_output))

        if "x =" in student_output.lower():
            solved = True

        evaluator_input = original_question + "\n" + student_output
        eval_output = evaluator.respond(evaluator_input)
        logger.info(f"Evaluator: {eval_output}")
        logs.append(("Evaluator", eval_output))

        coord_input = original_question + "\n" + eval_output
        decision = coordinator.respond(coord_input)
        logger.info(f"Coordinator: {decision}")

        if "STOP" in decision:
            logger.info("Simulation halted by Coordinator")
            break

        teacher_input = original_question + "\n" + eval_output
        teacher_output = teacher.respond(teacher_input)
        logger.info(f"Teacher: {teacher_output[:100]}...")
        logs.append(("Teacher", teacher_output))

    return logs


def main() -> None:
    """
    Execute simulations for a predefined set of mathematical problems
    and generate analysis reports.
    """
    questions = [
        "Solve: 2x + 3 = 7",
        "Solve: 3x - 5 = 2x + 7",
        "Explain recursion with example",
        "Solve: x^2 - 5x + 6 = 0"
    ]

    logger.info("Multi-Agent Problem-Solving System Initialized")

    for q in questions:
        logger.info(f"Processing question: {q}")
        
        logs = run_simulation(q, rounds=5)
        save_logs(logs, filename=f"logs_{q.replace(' ', '_').replace(':', '')}.json")

        results = analyze(logs)
        logger.info(f"Analysis Results: {results}")


if __name__ == "__main__":
    main()
