# System Architecture

## Agent Interaction Flow

The multi-agent system operates through a carefully designed sequence that ensures each agent contributes meaningfully to the problem-solving process.

```
Initial Problem Input
        |
        v
   [Teacher Agent]
   Provides context and guidance
        |
        v
   [Student Agent]
   Attempts solution based on guidance
        |
        v
   [Evaluator Agent]
   Independently verifies correctness
        |
        v
   [Coordinator Agent]
   Decides: Continue or Stop?
        |
        +----> STOP: Process halts, problem solved
        |
        +----> CONTINUE: Feedback loops back to Teacher
              (up to configured max rounds)
```

## Communication Protocol

Agents communicate through a carefully constructed context passing mechanism. Each subsequent agent receives the complete problem statement plus all previous agent outputs, enabling:

* Full conversational context awareness
* Ability to reference previous reasoning
* Consistency checking across agent perspectives
* Progressive refinement through iteration

## Agent Specifications

### TeacherAgent

**Purpose**: Guide without solving, maintain pedagogical integrity

**Constraints**:
* Must not introduce new equations
* Should only summarize if problem already solved
* Provides guidance and problem clarification

**Input**: Original problem statement plus conversation history

**Output**: Teaching explanation or guidance

### StudentAgent

**Purpose**: Solve the problem step-by-step following guidance

**Constraints**:
* Must focus on single problem
* Cannot create new problems
* Should confirm if already solved

**Input**: Problem statement and teacher guidance

**Output**: Solution attempt or confirmation

### EvaluatorAgent

**Purpose**: Independently verify solution correctness without explanation

**Constraints**:
* Must solve independently
* Cannot provide justification
* Binary output only: FINAL CORRECT or WRONG

**Input**: Problem statement and student solution

**Output**: Verification decision (FINAL CORRECT or WRONG)

### CoordinatorAgent

**Purpose**: Monitor process and determine termination

**Constraints**:
* Binary decision output
* Bases decision on conversation state
* Enforces maximum iteration limits

**Input**: Conversation history and evaluation results

**Output**: Control signal (CONTINUE or STOP)

## Data Flow

The system maintains an immutable conversation log throughout execution. Each agent output is appended to this log, creating a complete audit trail of the problem-solving process.

Log Format:
```
[
  (agent_role: str, response: str),
  (agent_role: str, response: str),
  ...
]
```

This structure enables:
* Complete conversation reconstruction
* Temporal analysis of reasoning progression
* Statistical metrics computation
* Reproducibility and debugging

## Parameter Configuration

### Temperature Setting

The LLM temperature parameter (default: 0.9) influences response randomness:
* Lower values (0.0-0.3): Deterministic, focused responses
* Medium values (0.5-0.7): Balanced creativity and coherence
* Higher values (0.8-1.0): Creative, more varied responses

Current setting balances solution accuracy with natural language generation variability.

### Iteration Rounds

Maximum rounds parameter (default: 5) bounds computational cost:
* Prevents infinite loops in non-convergent problems
* Reflects human-realistic conversation length
* Configurable per-problem based on complexity

## Error Handling

The system implements graceful degradation:

1. **LLM Unavailability**: Raises RuntimeError with descriptive message
2. **Malformed Responses**: Agents operate on raw output; downstream agents must handle irregular inputs
3. **Non-convergence**: Process halts at maximum rounds

## Performance Characteristics

Response latencies depend on:
* LLM inference speed (2-30 seconds typical for Mistral)
* Problem complexity and prompt length
* System resources and model quantization

For typical configurations:
* Single problem: 30-150 seconds
* Full benchmark: 2-10 minutes

## Quality Metrics

### Repetition Detection

Identifies complete message duplicates, indicating:
* Circular reasoning patterns
* Insufficient problem differentiation
* Possible convergence failure

### Irrelevance Detection

Counts agent responses containing "irrelevant" keyword:
* Indicates topic drift
* Suggests prompt constraint violations
* Proxy for solution quality issues

### Message Count

Raw conversation length metric:
* Indicates iteration depth required
* Reflects problem complexity
* Lower counts suggest better convergence

## Extensibility Points

The architecture supports extension in several directions:

1. **New Agent Types**: Implement standard respond(context) interface
2. **Alternative LLM Providers**: Extend llm.py with provider abstraction
3. **Enhanced Analysis**: Add metrics to analysis.py
4. **Problem Domain Specialization**: Customize prompt engineering per domain
5. **Agent Composition**: Create composite agents combining multiple roles

## Scalability Considerations

Current implementation is suitable for:
* Single problem-solving instances
* Batch processing with sequential execution
* Research and educational purposes

For production deployment, consider:
* Parallel execution of independent problem instances
* Connection pooling for LLM requests
* Caching frequent responses
* Distributed logging and analysis
