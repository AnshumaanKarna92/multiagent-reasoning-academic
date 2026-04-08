# Usage Examples and Case Studies

## Basic Usage

Import and run a simple simulation:

```python
from main import run_simulation
from analysis import analyze

question = "Solve: 2x + 3 = 7"
logs = run_simulation(question)
results = analyze(logs)

print("Total messages exchanged:", results["total_messages"])
print("Irrelevant responses:", results["irrelevant_responses"])
print("Repeated messages:", results["repetitions"])
```

## Custom Problem Set

Create a focused evaluation on specific problem categories:

```python
from main import run_simulation, save_logs
from analysis import analyze

algebraic_problems = [
    "Solve: x + 5 = 12",
    "Solve: 3x - 2 = 10",
    "Solve: 2(x + 3) = 16"
]

for problem in algebraic_problems:
    logs = run_simulation(problem, rounds=4)
    analysis = analyze(logs)
    
    filename = problem.replace(" ", "_").replace(":", "_") + ".json"
    save_logs(logs, filename)
    
    print(f"Problem: {problem}")
    print(f"Efficiency Score: {100 - analysis['repetitions']}")
    print()
```

## Agent Behavior Analysis

Examine how individual agents respond:

```python
from agents import TeacherAgent, StudentAgent, EvaluatorAgent, CoordinatorAgent

teacher = TeacherAgent()
student = StudentAgent()
evaluator = EvaluatorAgent()
coordinator = CoordinatorAgent()

problem = "Solve: x^2 - 5x + 6 = 0"

teacher_guidance = teacher.respond(problem)
print("Teacher's initial guidance:")
print(teacher_guidance)
print()

student_response = student.respond(problem + "\n" + teacher_guidance)
print("Student's attempt:")
print(student_response)
print()

evaluation = evaluator.respond(problem + "\n" + student_response)
print("Evaluator's verdict:", evaluation)
```

## Performance Benchmarking

Compare system performance across different problem types:

```python
from main import run_simulation
from analysis import analyze
import time

problem_categories = {
    "linear_equations": [
        "Solve: x + 3 = 8",
        "Solve: 2x - 1 = 5",
        "Solve: 4x = 12"
    ],
    "quadratic_equations": [
        "Solve: x^2 - 4 = 0",
        "Solve: x^2 - 5x + 6 = 0"
    ],
    "conceptual": [
        "Explain recursion with example",
        "What is logarithm"
    ]
}

results = {}

for category, problems in problem_categories.items():
    category_results = []
    
    for problem in problems:
        start_time = time.time()
        logs = run_simulation(problem, rounds=5)
        elapsed = time.time() - start_time
        
        analysis = analyze(logs)
        analysis["elapsed_time"] = elapsed
        
        category_results.append(analysis)
    
    results[category] = {
        "avg_messages": sum(r["total_messages"] for r in category_results) / len(category_results),
        "total_problems": len(category_results),
        "avg_time": sum(r["elapsed_time"] for r in category_results) / len(category_results)
    }

print("Benchmark Results:")
for category, stats in results.items():
    print(f"\n{category}:")
    print(f"  Average messages: {stats['avg_messages']:.1f}")
    print(f"  Average time: {stats['avg_time']:.1f}s")
```

## Conversation Log Analysis

Deep dive into a conversation to understand agent interactions:

```python
from main import run_simulation
import json

logs = run_simulation("Solve: x + 2 = 5")

print("Complete Conversation Log:")
print("=" * 50)

for turn, (agent, response) in enumerate(logs, 1):
    print(f"\nTurn {turn}: {agent}")
    print("-" * 40)
    print(response[:500])  # First 500 characters
    
print("\n" + "=" * 50)
print(f"Total exchanges: {len(logs)}")

agent_counts = {}
for agent, _ in logs:
    agent_counts[agent] = agent_counts.get(agent, 0) + 1

print("\nAgent participation:")
for agent, count in agent_counts.items():
    print(f"  {agent}: {count} responses")
```

## Extended Iteration Analysis

Study convergence patterns with varying iteration limits:

```python
from main import run_simulation
from analysis import analyze

problem = "Solve: 3x - 7 = 11"

convergence_analysis = {}

for max_rounds in [2, 3, 5, 10]:
    logs = run_simulation(problem, rounds=max_rounds)
    analysis = analyze(logs)
    
    convergence_analysis[max_rounds] = {
        "total_messages": analysis["total_messages"],
        "repetitions": analysis["repetitions"],
        "efficiency": analysis["total_messages"] / max_rounds
    }

print("Convergence Analysis:")
for rounds, metrics in convergence_analysis.items():
    print(f"Max rounds: {rounds}")
    for metric, value in metrics.items():
        print(f"  {metric}: {value}")
    print()
```

## Integration with External Systems

Use the agents as a module in larger applications:

```python
from agents import TeacherAgent, StudentAgent, EvaluatorAgent
from llm import call_llm

class CustomProblemSolver:
    def __init__(self):
        self.teacher = TeacherAgent()
        self.student = StudentAgent()
        self.evaluator = EvaluatorAgent()
    
    def solve_with_explanation(self, problem):
        guidance = self.teacher.respond(problem)
        student_solution = self.student.respond(problem + "\n" + guidance)
        verdict = self.evaluator.respond(problem + "\n" + student_solution)
        
        return {
            "problem": problem,
            "guidance": guidance,
            "solution": student_solution,
            "verified": "FINAL CORRECT" in verdict,
            "verdict": verdict
        }

solver = CustomProblemSolver()
result = solver.solve_with_explanation("Solve: 5x = 25")

print(f"Problem: {result['problem']}")
print(f"Solution verified: {result['verified']}")
print(f"Verdict: {result['verdict']}")
```

## Model Switching

Test with different LLM models:

```python
from llm import call_llm
from agents import StudentAgent

models_to_test = ["mistral", "neural-chat", "orca-mini"]

problem = "Solve: 2x + 8 = 20"

for model in models_to_test:
    try:
        prompt = f"Solve this problem: {problem}"
        response = call_llm(prompt, model=model)
        
        print(f"\n{model}:")
        print(response[:200])
    except Exception as e:
        print(f"\n{model}: Error - {str(e)}")
```

## Production Deployment Pattern

Example structure for integrating into a web service:

```python
from agents import TeacherAgent, StudentAgent, EvaluatorAgent, CoordinatorAgent
from analysis import analyze
import json
from datetime import datetime

class ProblemSolvingService:
    def __init__(self):
        self.teacher = TeacherAgent()
        self.student = StudentAgent()
        self.evaluator = EvaluatorAgent()
        self.coordinator = CoordinatorAgent()
    
    def solve(self, problem_id, problem_text, max_rounds=5):
        logs = []
        context = problem_text
        
        teacher_output = self.teacher.respond(context)
        logs.append(("teacher", teacher_output))
        
        for round_num in range(max_rounds):
            student_output = self.student.respond(problem_text + "\n" + teacher_output)
            logs.append(("student", student_output))
            
            eval_output = self.evaluator.respond(problem_text + "\n" + student_output)
            logs.append(("evaluator", eval_output))
            
            decision = self.coordinator.respond(problem_text + "\n" + eval_output)
            
            if "STOP" in decision:
                break
            
            teacher_output = self.teacher.respond(problem_text + "\n" + eval_output)
            logs.append(("teacher", teacher_output))
        
        analysis_results = analyze(logs)
        
        return {
            "problem_id": problem_id,
            "timestamp": datetime.now().isoformat(),
            "conversation": logs,
            "analysis": analysis_results,
            "success": "FINAL CORRECT" in str(logs)
        }

service = ProblemSolvingService()
result = service.solve("PROB_001", "Solve: x - 3 = 7")
print(json.dumps(result, indent=2))
```

## Testing Framework

Validate system behavior with test cases:

```python
from main import run_simulation
from analysis import analyze

test_cases = [
    {
        "problem": "Solve: x = 5",
        "expected_solved": True,
        "max_rounds": 2
    },
    {
        "problem": "Solve: 2x + 3 = 7",
        "expected_solved": True,
        "max_rounds": 5
    }
]

passed = 0
failed = 0

for test in test_cases:
    logs = run_simulation(test["problem"], rounds=test["max_rounds"])
    analysis = analyze(logs)
    
    last_evaluator_verdict = ""
    for agent, response in reversed(logs):
        if agent == "Evaluator":
            last_evaluator_verdict = response
            break
    
    is_correct = "FINAL CORRECT" in last_evaluator_verdict
    
    if is_correct == test["expected_solved"]:
        print(f"PASS: {test['problem']}")
        passed += 1
    else:
        print(f"FAIL: {test['problem']}")
        failed += 1

print(f"\nResults: {passed} passed, {failed} failed")
```
