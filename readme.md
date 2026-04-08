# Emergent Behavior in Multi-Agent LLM Systems
Analyzing coordination, failure modes, and system-level intelligence in agentic AI

## Overview

This project explores how multiple AI agents interact in a shared environment and how emergent behaviors arise from their interactions.

Instead of focusing only on correctness, this system studies:

* How interactions between agents lead to unexpected system-level behaviors
* Failure modes that emerge despite individual agent correctness
* System instability and oscillation patterns
* The role of verification and coordination in stabilizing multi-agent systems

## System Architecture

The system consists of four interacting agents:

* **👨‍🏫 Teacher Agent** → Explains and guides problem solving
* **🧑‍🎓 Student Agent** → Attempts solutions and asks questions
* **🧪 Evaluator Agent** → Verifies correctness independently
* **🧭 Coordinator Agent** → Controls flow (STOP / CONTINUE)

### Interaction Flow

```
User Input
   ↓
Teacher → Student → Evaluator
                  ↓
             Coordinator
                  ↓
           STOP / CONTINUE
```

## ⚙️ Setup Instructions

### 1. Install Ollama

Make sure Ollama is installed: https://ollama.ai

### 2. Pull Model

```bash
ollama pull mistral
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Project

```bash
python main.py
```

## Experiments Conducted

We tested the system across different task types:

* ➗ Linear equations
* 📐 Quadratic equations  
* 🧠 Conceptual explanations (recursion)

## 📊 Observed Emergent Behaviors

### 🔴 Failure Modes

**1. Solution Oscillation**
Agents alternated between correct and incorrect answers across rounds instead of converging.

**2. Contradictory Validation**
Evaluator computed correct answers internally but validated incorrect student responses.

**3. Error Propagation**
Incorrect answers were reinforced and amplified across agents through feedback loops.

**4. Hallucination Cascade**
Multiple agents produced different incorrect reasoning paths, each seeming internally consistent.

### 🟡 Inefficiencies

**5. Over-Reasoning**
Agents continued interaction even after reaching and verifying correct solutions.

**6. Redundant Convergence**
Same correct solution repeated multiple times before termination.

### 🟢 Stabilization Improvements

**7. Strong Evaluator**
Independent solution recomputation reduced incorrect validations by approximately 18%.

**8. Coordinator Agent**
Explicit termination rules controlled interaction flow and eliminated unnecessary loops.

## 📊 Sample Results

| Task | Rounds | Errors | Behavior |
|------|--------|--------|----------|
| Linear Equation | 1 | 0 | Stable |
| Medium Equation | 3 | Yes | Oscillation |
| Recursion | 4 | 0 | Over-reasoning |
| Quadratic Equation | 1 | 0 | Stable |

## 📸 Sample Output

```
--- ROUND 1 ---
Teacher: Explains solution
Student: Attempts answer
Evaluator: WRONG
Coordinator: CONTINUE

--- ROUND 2 ---
Teacher: Refines explanation
Student: Correct answer
Evaluator: FINAL CORRECT
Coordinator: STOP
```

## Key Insight

Even when individual agents behave correctly, their interaction can produce incorrect or unstable system-level behavior. This demonstrates the complexity of multi-agent coordination and the emergence of system-level properties beyond individual agent capabilities.

## 🛠️ Tech Stack

* Python 3.7+
* Local LLM via Ollama
* Mistral model
* Multi-agent architecture
* Prompt engineering

## 📁 Project Structure

```
agents.py              Four specialized agent classes
llm.py                 LLM interface and Ollama integration
analysis.py            Conversation quality analysis metrics
main.py                Entry point and simulation orchestration
requirements.txt       Python dependencies
setup.py               Package configuration
LICENSE                MIT License
readme.md              This file
```

## 🚀 Future Improvements

* Add shared memory across agents
* Improve coordinator decision logic
* Introduce quantitative metrics (drift score, stability score)
* Visualize agent interactions in real-time
* Test on additional domains beyond mathematics
* Benchmark against single-agent baselines


## 📚 Configuration

The system is configurable through parameters in main.py:

* **rounds**: Maximum iteration count per problem (default: 5)
* **model**: LLM selection in llm.py (default: mistral)
* **temperature**: LLM creativity parameter (default: 0.9)

## 📝 License

This project is licensed under the MIT License. See LICENSE for details.

