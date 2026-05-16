import json
import logging
import os
import time
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import uuid
from agents import TeacherAgent, StudentAgent, EvaluatorAgent, CoordinatorAgent
from extract_answers import extract_answer_from_response, normalize_answer
from metrics import compute_all_metrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_run_directory(run_id: str) -> str:
    
    base_path = "logs/runs"
    run_path = os.path.join(base_path, run_id)
    os.makedirs(run_path, exist_ok=True)
    return run_path

def save_detailed_log(
    run_id: str,
    problem_id: str,
    logs: List[Dict[str, Any]],
    summary: Dict[str, Any]
) -> None:
    
    run_path = create_run_directory(run_id)
    
    with open(os.path.join(run_path, f"{problem_id}_messages.jsonl"), "w") as f:
        for log_entry in logs:
            f.write(json.dumps(log_entry) + "\n")
    
    with open(os.path.join(run_path, f"{problem_id}_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

def run_simulation(
    question: str,
    problem_id: str,
    expected_answer: str,
    config: str = "B3",
    temperature: float = 0.9,
    seed: Optional[int] = None,
    max_rounds: int = 5,
    run_id: str = None
) -> Tuple[List[Tuple[str, str]], Dict[str, Any]]:
    
    if run_id is None:
        run_id = f"exp_{uuid.uuid4().hex[:8]}"
    
    if seed is not None:
        import random
        random.seed(seed)
    
    teacher = TeacherAgent(temperature=temperature)
    student = StudentAgent(temperature=temperature)
    evaluator = EvaluatorAgent(temperature=temperature)
    coordinator = CoordinatorAgent(temperature=temperature)
    
    logs = []
    detailed_logs = []
    
    original_question = question
    solved = False
    final_answer = None
    convergence_round = None
    
    timestamp_start = datetime.utcnow().isoformat()
    
    logger.info(f"Starting simulation: {problem_id} | Config: {config} | Temp: {temperature} | Seed: {seed}")
    
    teacher_output, teacher_meta = teacher.respond(original_question)
    logger.info(f"Teacher: {teacher_output[:100]}...")
    logs.append(("Teacher", teacher_output))
    detailed_logs.append({
        "round": 0,
        "agent": "Teacher",
        "timestamp_utc": datetime.utcnow().isoformat(),
        "latency_ms": teacher_meta.get("latency_ms", 0),
        "input_tokens": teacher_meta.get("input_tokens", 0),
        "output_tokens": teacher_meta.get("output_tokens", 0),
        "response": teacher_output,
        "temperature": temperature,
        "seed": seed,
        "config": config
    })
    
    for round_num in range(1, max_rounds + 1):
        logger.info(f"Round {round_num}/{max_rounds}")
        
        student_input = original_question + "\n\nTeacher's guidance:\n" + teacher_output
        student_output, student_meta = student.respond(student_input)
        logger.info(f"Student: {student_output[:100]}...")
        logs.append(("Student", student_output))
        
        extracted = extract_answer_from_response(student_output, original_question)
        if not isinstance(extracted, dict):
            logger.warning(f"extract_answer_from_response returned {type(extracted)} instead of dict: {extracted}")
            extracted = {"answer": None, "problem_type": "unknown", "confidence": "none"}
        
        normalized = normalize_answer(extracted.get("answer"), extracted.get("problem_type", "linear"))
        
        detailed_logs.append({
            "round": round_num,
            "agent": "Student",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "latency_ms": student_meta.get("latency_ms", 0),
            "input_tokens": student_meta.get("input_tokens", 0),
            "output_tokens": student_meta.get("output_tokens", 0),
            "response": student_output,
            "extracted_answer": extracted.get("answer"),
            "normalized_answer": normalized,
            "temperature": temperature,
            "seed": seed,
            "config": config
        })
        
        evaluator_input = original_question + "\n\nStudent's solution:\n" + student_output
        eval_output, eval_meta = evaluator.respond(evaluator_input)
        logger.info(f"Evaluator: {eval_output}")
        logs.append(("Evaluator", eval_output))
        
        is_correct = "CORRECT" in eval_output or "FINAL CORRECT" in eval_output
        
        detailed_logs.append({
            "round": round_num,
            "agent": "Evaluator",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "latency_ms": eval_meta.get("latency_ms", 0),
            "input_tokens": eval_meta.get("input_tokens", 0),
            "output_tokens": eval_meta.get("output_tokens", 0),
            "response": eval_output,
            "evaluation_decision": "CORRECT" if is_correct else "WRONG",
            "student_answer": normalized,
            "expected_answer": expected_answer,
            "temperature": temperature,
            "seed": seed,
            "config": config
        })
        
        coord_input = logs.copy()
        coord_decision, coord_meta = coordinator.respond(coord_input, eval_output)
        logger.info(f"Coordinator: {coord_decision}")
        logs.append(("Coordinator", coord_decision))
        
        detailed_logs.append({
            "round": round_num,
            "agent": "Coordinator",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "latency_ms": coord_meta.get("latency_ms", 0),
            "input_tokens": coord_meta.get("input_tokens", 0),
            "output_tokens": coord_meta.get("output_tokens", 0),
            "response": coord_decision,
            "decision": "STOP" if "STOP" in coord_decision else "CONTINUE",
            "temperature": temperature,
            "seed": seed,
            "config": config
        })
        
        if is_correct:
            solved = True
            final_answer = normalized
            convergence_round = round_num
        
        if "STOP" in coord_decision:
            logger.info("Simulation halted by Coordinator")
            break
        
        teacher_input = original_question + "\n\nEvaluator feedback:\n" + eval_output
        teacher_output, teacher_meta = teacher.respond(teacher_input)
        logger.info(f"Teacher (round {round_num}): {teacher_output[:100]}...")
        logs.append(("Teacher", teacher_output))
        detailed_logs.append({
            "round": round_num,
            "agent": "Teacher",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "latency_ms": teacher_meta.get("latency_ms", 0),
            "input_tokens": teacher_meta.get("input_tokens", 0),
            "output_tokens": teacher_meta.get("output_tokens", 0),
            "response": teacher_output,
            "temperature": temperature,
            "seed": seed,
            "config": config
        })
    
    timestamp_end = datetime.utcnow().isoformat()
    
    try:
        is_correct_flag = solved and (final_answer == expected_answer or (normalize_answer(expected_answer) if expected_answer else None) == final_answer)
    except Exception as e:
        logger.warning(f"Error comparing answers: {e}")
        is_correct_flag = solved and final_answer == expected_answer
    
    try:
        metrics = compute_all_metrics(logs, {"problem_id": problem_id}, is_correct_flag)
    except Exception as e:
        logger.error(f"Error computing metrics: {e}, logs type: {type(logs)}, logs: {logs[:3] if isinstance(logs, list) else logs}")
        metrics = {}
    
    summary = {
        "run_id": run_id,
        "problem_id": problem_id,
        "configuration": config,
        "temperature": temperature,
        "seed": seed,
        "timestamp_start": timestamp_start,
        "timestamp_end": timestamp_end,
        "rounds_completed": len([l for l in logs if l[0] == "Coordinator"]),
        "converged": solved,
        "final_answer": final_answer,
        "expected_answer": expected_answer,
        "answer_correct": is_correct_flag,
        "convergence_round": convergence_round,
        "metrics": metrics,
        "agent_message_counts": {
            "Teacher": len([l for l in logs if l[0] == "Teacher"]),
            "Student": len([l for l in logs if l[0] == "Student"]),
            "Evaluator": len([l for l in logs if l[0] == "Evaluator"]),
            "Coordinator": len([l for l in logs if l[0] == "Coordinator"])
        }
    }
    
    save_detailed_log(run_id, problem_id, detailed_logs, summary)
    
    return logs, summary

def main() -> None:
    
    problems = [
        {
            "problem_id": "linear_eq_001",
            "statement": "Solve: 2x + 3 = 7",
            "expected_answer": "x = 2",
            "difficulty": 1,
            "category": "linear"
        },
        {
            "problem_id": "linear_eq_002",
            "statement": "Solve: 3x - 5 = 2x + 7",
            "expected_answer": "x = 12",
            "difficulty": 1,
            "category": "linear"
        },
        {
            "problem_id": "quadratic_001",
            "statement": "Solve: x^2 - 5x + 6 = 0",
            "expected_answer": "x = 2, 3",
            "difficulty": 2,
            "category": "quadratic"
        },
        {
            "problem_id": "recursion_001",
            "statement": "Explain recursion with example",
            "expected_answer": "recursive function calls itself",
            "difficulty": 2,
            "category": "recursion"
        }
    ]
    
    configs = [
        {"name": "B0", "temperature": 0.9, "max_rounds": 5},
        {"name": "B3", "temperature": 0.9, "max_rounds": 5},
        {"name": "B6", "temperature": 0.3, "max_rounds": 5},
        {"name": "B8", "temperature": 0.95, "max_rounds": 5}
    ]
    
    seeds = [1, 42, 123]
    
    logger.info("Multi-Agent Problem-Solving System Initialized")
    
    run_summaries = []
    
    for problem in problems:
        for config in configs:
            for seed in seeds:
                run_id = f"exp_{config['name']}_seed_{seed}"
                
                logs, summary = run_simulation(
                    question=problem["statement"],
                    problem_id=problem["problem_id"],
                    expected_answer=problem["expected_answer"],
                    config=config["name"],
                    temperature=config["temperature"],
                    seed=seed,
                    max_rounds=config["max_rounds"],
                    run_id=run_id
                )
                
                run_summaries.append(summary)
                
                logger.info(f"Completed: {problem['problem_id']} | {config['name']} | Seed {seed} | Accuracy: {summary['answer_correct']}")
    
    aggregate_path = "logs/analysis"
    os.makedirs(aggregate_path, exist_ok=True)
    
    with open(os.path.join(aggregate_path, "all_runs_summary.json"), "w") as f:
        json.dump(run_summaries, f, indent=2)
    
    config_stats = {}
    for config in configs:
        config_name = config["name"]
        config_runs = [s for s in run_summaries if s["configuration"] == config_name]
        
        if config_runs:
            accuracies = [s["answer_correct"] for s in config_runs]
            convergences = [s["convergence_round"] if s["convergence_round"] else 6 for s in config_runs]
            
            config_stats[config_name] = {
                "num_runs": len(config_runs),
                "accuracy_mean": (sum(accuracies) / len(accuracies)) * 100 if accuracies else 0,
                "accuracy_std": (np.std([1 if a else 0 for a in accuracies]) * 100) if accuracies else 0,
                "convergence_mean": float(np.mean(convergences)),
                "convergence_std": float(np.std(convergences))
            }
    
    with open(os.path.join(aggregate_path, "config_statistics.json"), "w") as f:
        json.dump(config_stats, f, indent=2)
    
    logger.info(f"All simulations complete. Results saved to {aggregate_path}")

if __name__ == "__main__":
    import numpy as np
    main()

